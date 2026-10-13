"""
tests/test_steganography.py
Verification suite for StegoEngine:
- PNG LSB embedding and extraction roundtrips
- Capacity limits and overflow protection
- Magic watermark authentication
- Pixel difference heatmap boundaries
"""

import pytest
from pathlib import Path
from PIL import Image
import numpy as np
from core.steganography import StegoEngine


@pytest.fixture
def sample_cover_image(tmp_path) -> Path:
    """Creates a temporary 100x100 RGB image for testing."""
    img_path = tmp_path / "test_cover.png"
    # Create smooth gradient
    arr = np.zeros((100, 100, 3), dtype=np.uint8)
    for y in range(100):
        for x in range(100):
            arr[y, x] = [x * 2, y * 2, (x + y) % 256]
    img = Image.fromarray(arr, mode="RGB")
    img.save(img_path, format="PNG")
    return img_path


def test_embed_and_extract_roundtrip(sample_cover_image, tmp_path):
    stego = StegoEngine()
    out_path = tmp_path / "stego_out.png"

    sample_tree_bits = "1010000010"  # mock serialized tree bits
    sample_payload_bits = "11010110101111000101010101"

    meta = stego.embed(sample_cover_image, sample_tree_bits, sample_payload_bits, out_path)
    assert out_path.exists()
    assert meta["payload_bits"] == len(sample_payload_bits)
    assert meta["tree_bits"] == len(sample_tree_bits)

    # Extract back
    ext_tree, ext_payload = stego.extract(out_path)
    assert ext_tree == sample_tree_bits
    assert ext_payload == sample_payload_bits


def test_capacity_overflow_guard(sample_cover_image, tmp_path):
    stego = StegoEngine()
    out_path = tmp_path / "overflow.png"

    # Image is 100x100x3 = 30,000 bits. Payload of 35,000 bits must fail.
    large_payload = "1" * 35000
    with pytest.raises(ValueError, match="Payload too large"):
        stego.embed(sample_cover_image, "1010", large_payload, out_path)


def test_magic_watermark_rejection(sample_cover_image):
    """Cover image before embedding should fail extraction due to missing magic."""
    stego = StegoEngine()
    with pytest.raises(ValueError, match="No valid HuffStego watermark"):
        stego.extract(sample_cover_image)


def test_pixel_diff_heatmap(sample_cover_image, tmp_path):
    stego = StegoEngine()
    out_path = tmp_path / "stego_diff.png"

    stego.embed(sample_cover_image, "10101", "111000111", out_path)
    heatmap = stego.compute_diff_heatmap(sample_cover_image, out_path)

    assert heatmap.shape == (100, 100)
    assert heatmap.dtype == np.uint8
    # Modified pixels should be amplified, untouched should be 0
    assert np.max(heatmap) > 0


def test_stego_metrics_mse_psnr(sample_cover_image, tmp_path):
    stego = StegoEngine()
    out_path = tmp_path / "stego_metrics.png"

    stego.embed(sample_cover_image, "10101", "111000111", out_path)
    metrics = stego.compute_metrics(sample_cover_image, out_path)

    assert "mse" in metrics
    assert "psnr_db" in metrics
    # Because only LSBs are touched, MSE must be small (<= 1.0) and PSNR high (>= 40 dB)
    assert metrics["mse"] < 1.0
    assert metrics["psnr_db"] >= 40.0

