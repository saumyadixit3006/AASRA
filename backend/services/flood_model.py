"""
AASRA flood-model inference service.

Place this file at backend/services/flood_model.py.
Expected checkpoint: backend/models/aasra_flood_unet_improved.pth

IMPORTANT: The U-Net class and preprocessing below must match the training notebook.
If load_state_dict reports a mismatch, use the exact class from that notebook.
Do not change app.py for this step.
"""
from pathlib import Path
from typing import Any, Dict

import numpy as np
import rasterio
import torch
import torch.nn as nn

BACKEND_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BACKEND_DIR / "models" / "aasra_flood_unet_improved.pth"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_MODEL = None


class DoubleConv(nn.Module):
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.block(x)


class UNet(nn.Module):
    """Conventional two-band U-Net; must match the training architecture exactly."""
    def __init__(self, in_channels=2, out_channels=1, base=32):
        super().__init__()
        self.enc1 = DoubleConv(in_channels, base)
        self.enc2 = DoubleConv(base, base * 2)
        self.enc3 = DoubleConv(base * 2, base * 4)
        self.enc4 = DoubleConv(base * 4, base * 8)
        self.pool = nn.MaxPool2d(2)
        self.bottleneck = DoubleConv(base * 8, base * 16)
        self.up4 = nn.ConvTranspose2d(base * 16, base * 8, 2, 2)
        self.dec4 = DoubleConv(base * 16, base * 8)
        self.up3 = nn.ConvTranspose2d(base * 8, base * 4, 2, 2)
        self.dec3 = DoubleConv(base * 8, base * 4)
        self.up2 = nn.ConvTranspose2d(base * 4, base * 2, 2, 2)
        self.dec2 = DoubleConv(base * 4, base * 2)
        self.up1 = nn.ConvTranspose2d(base * 2, base, 2, 2)
        self.dec1 = DoubleConv(base * 2, base)
        self.output = nn.Conv2d(base, out_channels, 1)

    @staticmethod
    def _resize(x, ref):
        if x.shape[-2:] != ref.shape[-2:]:
            x = nn.functional.interpolate(x, size=ref.shape[-2:], mode="bilinear", align_corners=False)
        return x

    def forward(self, x):
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))
        e4 = self.enc4(self.pool(e3))
        b = self.bottleneck(self.pool(e4))
        d4 = self.dec4(torch.cat([self._resize(self.up4(b), e4), e4], 1))
        d3 = self.dec3(torch.cat([self._resize(self.up3(d4), e3), e3], 1))
        d2 = self.dec2(torch.cat([self._resize(self.up2(d3), e2), e2], 1))
        d1 = self.dec1(torch.cat([self._resize(self.up1(d2), e1), e1], 1))
        return self.output(d1)


def _state_dict(checkpoint: Any) -> Dict[str, torch.Tensor]:
    if isinstance(checkpoint, dict):
        for key in ("model_state_dict", "state_dict", "model"):
            if isinstance(checkpoint.get(key), dict):
                checkpoint = checkpoint[key]
                break
    if not isinstance(checkpoint, dict):
        raise RuntimeError("Unsupported checkpoint format; expected a PyTorch state_dict.")
    return {
        (k[7:] if k.startswith("module.") else k): v
        for k, v in checkpoint.items()
        if isinstance(k, str)
    }


def _load_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. Put the .pth file in backend/models/."
        )
    try:
        checkpoint = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True)
    except TypeError:
        checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
    model = UNet(in_channels=2, out_channels=1, base=32)
    try:
        model.load_state_dict(_state_dict(checkpoint), strict=True)
    except RuntimeError as exc:
        raise RuntimeError(
            "Checkpoint architecture does not match this U-Net. Copy the exact U-Net "
            "class from the Colab training notebook into this file. app.py does not "
            "need to be changed. Details: " + str(exc)
        ) from exc
    model.to(DEVICE).eval()
    _MODEL = model
    return model


def _normalise(image: np.ndarray) -> np.ndarray:
    output = np.zeros_like(image, dtype=np.float32)
    for i, band in enumerate(image):
        valid = np.isfinite(band)
        if not valid.any():
            continue
        low, high = np.percentile(band[valid], [2, 98])
        if high > low:
            output[i] = np.clip(np.nan_to_num((band - low) / (high - low)), 0, 1)
        output[i][~valid] = 0
    return output


def predict_flood(geotiff_path: str) -> Dict[str, Any]:
    """Predict a binary water mask from a two-band Sentinel-1 GeoTIFF."""
    model = _load_model()
    with rasterio.open(geotiff_path) as src:
        if src.count != 2:
            raise ValueError(f"Expected a two-band GeoTIFF; received {src.count} bands.")
        image = src.read().astype(np.float32)
        height, width = src.height, src.width
        crs = str(src.crs) if src.crs else None

    tensor = torch.from_numpy(_normalise(image)).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        probabilities = torch.sigmoid(model(tensor))[0, 0]
        mask = (probabilities >= 0.5).to(torch.uint8).cpu().numpy()

    water_pixels = int(mask.sum())
    total_pixels = int(mask.size)
    return {
        "success": True,
        "model": "aasra_flood_unet_improved",
        "height": int(height),
        "width": int(width),
        "water_pixels": water_pixels,
        "total_pixels": total_pixels,
        "water_pixel_percentage": round(100 * water_pixels / max(total_pixels, 1), 2),
        "threshold": 0.5,
        "crs": crs,
        "mask": mask.reshape(-1).tolist(),
        "note": "Model output is a segmentation estimate, not an official emergency warning."
    }
