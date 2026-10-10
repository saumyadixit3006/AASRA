
from pathlib import Path
import re

import numpy as np
import pandas as pd
import rasterio
import torch
from torch.utils.data import Dataset


def normalize_name(value):
    """Convert a CSV entry or filename into a comparable chip ID."""
    value = str(value).strip().replace("\\", "/").split("/")[-1]
    value = re.sub(r"\.(tif|tiff|csv)$", "", value, flags=re.I)

    for suffix in ("_S1Hand", "_LabelHand"):
        if value.endswith(suffix):
            value = value[:-len(suffix)]

    return value


def read_split(csv_path):
    """Read chip IDs from an official split CSV."""
    frame = pd.read_csv(csv_path, dtype=str)

    identifiers = set()

    for value in frame.fillna("").values.flatten():
        name = normalize_name(value)

        # Keep entries that look like chip identifiers rather than
        # column headings or arbitrary metadata.
        if re.search(r"[A-Za-z].*\d", name):
            identifiers.add(name)

    if not identifiers:
        raise ValueError(
            f"No chip identifiers found in split file: {csv_path}. "
            "Inspect the CSV columns and adapt read_split()."
        )

    return identifiers


class Sen1FloodsDataset(Dataset):
    def __init__(self, data_root, split_root, split="train"):
        self.data_root = Path(data_root)
        self.split_root = Path(split_root)

        split_names = {
            "train": "flood_train_data.csv",
            "valid": "flood_valid_data.csv",
            "test": "flood_test_data.csv",
        }

        if split not in split_names:
            raise ValueError(f"Unknown split: {split}")

        split_file = self.split_root / split_names[split]

        if not split_file.exists():
            raise FileNotFoundError(
                f"Missing split file: {split_file}"
            )

        ids = read_split(split_file)

        image_dir = self.data_root / "S1Hand"
        label_dir = self.data_root / "LabelHand"

        if not image_dir.exists() or not label_dir.exists():
            raise FileNotFoundError(
                "Expected S1Hand and LabelHand directories under "
                f"{self.data_root}"
            )

        images = sorted(image_dir.glob("*.tif"))
        if not images:
            images = sorted(image_dir.glob("*.tiff"))

        pairs = []

        for image_path in images:
            chip_id = normalize_name(image_path.name)

            if chip_id not in ids:
                continue

            label_path = label_dir / f"{chip_id}_LabelHand.tif"

            if not label_path.exists():
                label_path = label_dir / f"{chip_id}_LabelHand.tiff"

            if label_path.exists():
                pairs.append((image_path, label_path))

        if not pairs:
            raise ValueError(
                f"No matching image/label pairs for split '{split}'. "
                f"Found {len(images)} Sentinel-1 images and "
                f"{len(ids)} split identifiers. Check your folder paths "
                "and inspect the split CSV schema."
            )

        self.pairs = pairs
        print(f"{split}: loaded {len(self.pairs)} image/label pairs")

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        image_path, label_path = self.pairs[index]

        with rasterio.open(image_path) as src:
            image = src.read().astype(np.float32)

        with rasterio.open(label_path) as src:
            label = src.read(1).astype(np.int16)

        if image.shape[0] != 2:
            raise ValueError(
                f"Expected VV/VH two-band image: {image_path}; "
                f"got shape {image.shape}"
            )

        if image.shape[1:] != label.shape:
            raise ValueError(
                f"Image and label dimensions differ: {image_path}"
            )

        # Normalize Sentinel-1 backscatter in dB to [0, 1].
        image = np.nan_to_num(
            image, nan=-50.0, posinf=1.0, neginf=-50.0
        )
        image = np.clip(image, -50.0, 1.0)
        image = (image + 50.0) / 51.0

        # Sen1Floods11 labels: -1 = invalid, 0 = non-water, 1 = water.
        # PyTorch CrossEntropyLoss ignores class 255.
        valid = np.isin(label, [0, 1, -1])

        if not valid.all():
            raise ValueError(
                f"Unexpected label values in {label_path}: "
                f"{np.unique(label)}"
            )

        label = np.where(label == -1, 255, label).astype(np.int64)

        return (
            torch.from_numpy(image.copy()).float(),
            torch.from_numpy(label.copy()).long(),
        )
