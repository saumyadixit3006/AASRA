
import argparse
from pathlib import Path

import numpy as np
import rasterio
import torch

from train_model import UNet


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument(
        "--model",
        default="ml/flood/model/flood_unet.pt",
    )
    parser.add_argument(
        "--output",
        default="ml/flood/model/predicted_flood_mask.tif",
    )
    args = parser.parse_args()

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    checkpoint = torch.load(
        args.model,
        map_location=device,
        weights_only=True,
    )

    model = UNet().to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    with rasterio.open(args.image) as src:
        image = src.read().astype(np.float32)
        profile = src.profile.copy()

    if image.shape[0] != 2:
        raise ValueError("Expected a two-band Sentinel-1 VV/VH image.")

    image = np.nan_to_num(
        image, nan=-50.0, posinf=1.0, neginf=-50.0
    )
    image = np.clip(image, -50.0, 1.0)
    image = (image + 50.0) / 51.0

    tensor = torch.from_numpy(image.copy()).float()
    tensor = tensor.unsqueeze(0).to(device)

    with torch.no_grad():
        probabilities = torch.softmax(model(tensor), dim=1)
        mask = probabilities.argmax(dim=1)[0].cpu().numpy().astype(
            np.uint8
        )

    profile.update(
        count=1,
        dtype="uint8",
        nodata=255,
        compress="deflate",
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(mask, 1)

    print("Saved predicted mask:", output_path)
    print("0 = predicted non-water; 1 = predicted water")
    print("This is a model prediction, not a live flood warning.")


if __name__ == "__main__":
    main()
