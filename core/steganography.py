"""
core/steganography.py
LSB Steganography Engine with Integrity Validation & Pixel Heatmaps

Embeds Huffman serialized trees and compressed bitstreams into PNG RGB channels.
Extracts payloads with cryptographic-like magic-header validation.
Calculates visual difference heatmaps, MSE, and PSNR for forensic inspection.
Fully vectorized with NumPy for maximum performance.
"""

from pathlib import Path
from typing import Union, Tuple, Dict
from PIL import Image
import numpy as np


class StegoEngine:
    """Least Significant Bit steganography for lossless PNG images."""

    # 16-bit header magic: 0x5354 ('ST' for Stego)
    MAGIC_SIGNATURE: str = "0101001101010100"

    @staticmethod
    def _bits_to_str(bit_slice: np.ndarray) -> str:
        """Vectorized conversion from binary uint8 array (0/1) to ASCII bitstring."""
        return (bit_slice.astype(np.uint8) + 48).tobytes().decode("ascii")

    def get_capacity_info(self, image_path: Union[str, Path]) -> Dict[str, Union[int, float]]:
        """
        Calculates total bit capacity and usable bits for the given image.
        Each pixel RGB channel provides 1 LSB bit.
        Header overhead: 16b MAGIC + 16b TreeLen + 32b PayloadLen = 64 bits.
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Cover image not found: {image_path}")

        with Image.open(image_path) as img:
            rgb_img = img.convert("RGB")
            w, h = rgb_img.size

        total_bits = w * h * 3
        overhead = 64  # Magic (16) + TreeLen (16) + PayloadLen (32)
        usable_bits = max(0, total_bits - overhead)

        return {
            "width": w,
            "height": h,
            "total_pixels": w * h,
            "total_channel_bits": total_bits,
            "overhead_bits": overhead,
            "usable_bits": usable_bits,
            "max_utf8_bytes_approx": usable_bits // 8
        }

    def embed(
        self,
        image_path: Union[str, Path],
        tree_bits: str,
        payload_bits: str,
        output_path: Union[str, Path]
    ) -> Dict[str, Union[int, float]]:
        """
        Embeds Huffman packet into cover image using vectorized LSB substitution.
        Packet format:
        [16b MAGIC] [16b TREE_LEN] [tree_bits] [32b PAYLOAD_LEN] [payload_bits]
        """
        image_path = Path(image_path)
        output_path = Path(output_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Cover image not found: {image_path}")

        tree_len = len(tree_bits)
        if tree_len > 65535:
            raise ValueError(f"Tree bits length ({tree_len}) exceeds 16-bit field limit (65535).")

        payload_len = len(payload_bits)
        if payload_len > 4294967295:
            raise ValueError(f"Payload bits length ({payload_len}) exceeds 32-bit field limit.")

        tree_len_bits = format(tree_len, "016b")
        payload_len_bits = format(payload_len, "032b")

        packet_str = (
            self.MAGIC_SIGNATURE +
            tree_len_bits +
            tree_bits +
            payload_len_bits +
            payload_bits
        )

        with Image.open(image_path) as img:
            rgb_img = img.convert("RGB")
            pixels = np.array(rgb_img, dtype=np.uint8)

        flat = pixels.flatten()
        packet_len = len(packet_str)

        if packet_len > len(flat):
            raise ValueError(
                f"Payload too large for this image: packet requires {packet_len} bits, "
                f"but cover image only holds {len(flat)} bits."
            )

        # High-performance vectorized bit extraction (C-level ASCII offset)
        packet_bits = np.frombuffer(packet_str.encode("ascii"), dtype=np.uint8) - 48

        # Count altered bits before modification
        current_lsbs = flat[:packet_len] & 1
        altered_count = int(np.count_nonzero(current_lsbs != packet_bits))

        # Clear LSB and write new bit
        flat[:packet_len] = (flat[:packet_len] & 0xFE) | packet_bits

        # Reshape & save strictly as PNG
        stego_pixels = flat.reshape(pixels.shape)
        stego_image = Image.fromarray(stego_pixels, mode="RGB")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        stego_image.save(output_path, format="PNG")

        return {
            "total_packet_bits": packet_len,
            "tree_bits": tree_len,
            "payload_bits": payload_len,
            "modified_channel_values": altered_count,
            "capacity_usage_pct": round((packet_len / len(flat)) * 100, 3),
            "width": rgb_img.width,
            "height": rgb_img.height
        }

    def extract(self, stego_path: Union[str, Path]) -> Tuple[str, str]:
        """
        Extracts tree_bits and payload_bits from stego image with vectorized bit slicing.
        Returns: (tree_bits, payload_bits)
        """
        stego_path = Path(stego_path)
        if not stego_path.exists():
            raise FileNotFoundError(f"Stego image not found: {stego_path}")

        with Image.open(stego_path) as img:
            rgb_img = img.convert("RGB")
            flat = np.array(rgb_img, dtype=np.uint8).flatten()

        if len(flat) < 64:
            raise ValueError("Image is too small to contain a valid steganographic packet.")

        lsbs = flat & 1

        # 1. Read & check MAGIC (bits 0..15)
        magic_extracted = self._bits_to_str(lsbs[:16])
        if magic_extracted != self.MAGIC_SIGNATURE:
            raise ValueError(
                "No valid HuffStego watermark found. "
                "This image was not created with this platform or has been recompressed."
            )

        # 2. Read Tree length (bits 16..31)
        tree_len = int(self._bits_to_str(lsbs[16:32]), 2)
        tree_start = 32
        tree_end = tree_start + tree_len

        if tree_end > len(flat):
            raise ValueError("Stego image corruption detected: tree length exceeds image size.")

        tree_bits = self._bits_to_str(lsbs[tree_start:tree_end])

        # 3. Read Payload length (32 bits after tree)
        payload_len_start = tree_end
        payload_len_end = payload_len_start + 32

        if payload_len_end > len(flat):
            raise ValueError("Stego image corruption detected: payload length header truncated.")

        payload_len = int(self._bits_to_str(lsbs[payload_len_start:payload_len_end]), 2)

        payload_start = payload_len_end
        payload_end = payload_start + payload_len

        if payload_end > len(flat):
            raise ValueError("Stego image corruption detected: payload length exceeds image size.")

        payload_bits = self._bits_to_str(lsbs[payload_start:payload_end])

        return tree_bits, payload_bits

    def compute_diff_heatmap(
        self,
        orig_path: Union[str, Path],
        stego_path: Union[str, Path],
        amplification: int = 128
    ) -> np.ndarray:
        """
        Generates an amplified difference heatmap matrix comparing original vs stego.
        Differences of ±1 LSB are multiplied by `amplification` for clear visualization.
        """
        with Image.open(orig_path) as im1, Image.open(stego_path) as im2:
            a = np.array(im1.convert("RGB"), dtype=np.int16)
            b = np.array(im2.convert("RGB"), dtype=np.int16)

        if a.shape != b.shape:
            raise ValueError(f"Image dimensions do not match: {a.shape} vs {b.shape}")

        diff = np.abs(a - b).sum(axis=2)  # sum absolute differences across R, G, B
        heatmap = np.clip(diff * amplification, 0, 255).astype(np.uint8)
        return heatmap

    def compute_metrics(
        self,
        orig_path: Union[str, Path],
        stego_path: Union[str, Path]
    ) -> Dict[str, float]:
        """
        Calculates MSE (Mean Squared Error) and PSNR (Peak Signal-to-Noise Ratio).
        Proves imperceptibility to academic examiners: PSNR > 50 dB indicates human-invisible change.
        """
        with Image.open(orig_path) as im1, Image.open(stego_path) as im2:
            a = np.array(im1.convert("RGB"), dtype=np.float64)
            b = np.array(im2.convert("RGB"), dtype=np.float64)

        mse = float(np.mean((a - b) ** 2))
        if mse == 0.0:
            psnr = 999.0  # Identical images
        else:
            psnr = float(10.0 * np.log10((255.0 ** 2) / mse))

        return {
            "mse": round(mse, 6),
            "psnr_db": round(psnr, 2)
        }
