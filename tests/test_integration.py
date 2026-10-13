"""
tests/test_integration.py
End-to-End Pipeline Integration Test

Tests complete cycle:
Unicode Message -> Huffman Compression -> PNG Stego Embedding ->
LSB Extraction -> Tree Deserialization -> Unicode Decoding -> Exact Match Check
"""

from pathlib import Path
from core.huffman import HuffmanEngine
from core.steganography import StegoEngine
from core.statistics import StatsEngine


def test_full_pipeline_unicode_roundtrip(tmp_path):
    project_root = Path(__file__).resolve().parent.parent
    cover_image = project_root / "assets" / "sample_images" / "cover_landscape.png"
    assert cover_image.exists(), "Sample cover image must exist"

    stego_output = tmp_path / "integration_stego.png"

    # Multilingual Unicode secret message
    secret_text = (
        "🔐 Confidential Algorithm Report [ICE245]:\n"
        "Huffman Coding produces an optimal prefix code using a greedy min-heap.\n"
        "Bangla: আমাদের প্রোগ্রাম সফলভাবে তথ্য লুকিয়ে রাখতে সক্ষম। 🇧🇩\n"
        "Emoji Payload: 🚀 🎯 💡 🌟 ✨"
    )

    # 1. Encode with Huffman
    huffman = HuffmanEngine()
    tree_bits, payload_bits = huffman.encode_text(secret_text)

    assert len(tree_bits) > 0
    assert len(payload_bits) > 0

    # 2. Embed into Cover Image
    stego = StegoEngine()
    meta = stego.embed(cover_image, tree_bits, payload_bits, stego_output)

    assert stego_output.exists()
    assert meta["modified_channel_values"] > 0
    assert meta["capacity_usage_pct"] > 0

    # 3. Extract back from Stego Image
    extracted_tree_bits, extracted_payload_bits = stego.extract(stego_output)

    assert extracted_tree_bits == tree_bits
    assert extracted_payload_bits == payload_bits

    # 4. Reconstruct tree and decode
    reconstructed_root, _ = HuffmanEngine.deserialize_tree(extracted_tree_bits)
    recovered_text = huffman.decode_to_text(extracted_payload_bits, reconstructed_root)

    # 5. Perfect Fidelity Check
    assert recovered_text == secret_text

    # 6. Heatmap generation check
    heatmap = stego.compute_diff_heatmap(cover_image, stego_output)
    assert heatmap.shape == (300, 400)
    assert heatmap.max() > 0

    # 7. Statistical Report check
    stats = StatsEngine.evaluate(secret_text, tree_bits, payload_bits)
    assert stats["byte_count"] == len(secret_text.encode("utf-8"))
    assert stats["compression_ratio"] > 0
    assert stats["shannon_entropy"] > 0
