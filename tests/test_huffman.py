"""
tests/test_huffman.py
Verification suite for HuffmanEngine:
- Full Unicode fidelity (Bangla, Arabic, Chinese, Emoji)
- Prefix-free code property validation
- Serialization & deserialization roundtrips
- Edge cases (single symbol, long strings)
"""

import pytest
from core.huffman import HuffmanEngine, HuffmanNode


def test_ascii_roundtrip():
    engine = HuffmanEngine()
    original_text = "ABRACADABRA! This is a test of Huffman coding."
    tree_bits, payload_bits = engine.encode_text(original_text)

    # Reconstruct from tree_bits
    reconstructed_root, _ = HuffmanEngine.deserialize_tree(tree_bits)
    decoded_text = engine.decode_to_text(payload_bits, reconstructed_root)

    assert decoded_text == original_text
    assert len(payload_bits) > 0
    assert len(tree_bits) > 0


def test_unicode_bangla_roundtrip():
    engine = HuffmanEngine()
    bangla_text = "আমার সোনার বাংলা, আমি তোমায় ভালোবাসি। চিরদিন তোমার আকাশ, তোমার বাতাস।"
    tree_bits, payload_bits = engine.encode_text(bangla_text)

    reconstructed_root, _ = HuffmanEngine.deserialize_tree(tree_bits)
    decoded_text = engine.decode_to_text(payload_bits, reconstructed_root)

    assert decoded_text == bangla_text


def test_emoji_and_multilingual():
    engine = HuffmanEngine()
    complex_text = "Top Secret 🔒 🚀 | Algorithms: ICE245 | বাংলা + 中文 + العربية | 2026 ✨"
    tree_bits, payload_bits = engine.encode_text(complex_text)

    reconstructed_root, _ = HuffmanEngine.deserialize_tree(tree_bits)
    decoded_text = engine.decode_to_text(payload_bits, reconstructed_root)

    assert decoded_text == complex_text


def test_prefix_free_property():
    """Ensure no assigned prefix code is a prefix of another code."""
    engine = HuffmanEngine()
    text = "The greedy approach always makes the choice that looks best at the moment."
    engine.encode_text(text)

    codes = list(engine.codes.values())
    for i in range(len(codes)):
        for j in range(len(codes)):
            if i != j:
                assert not codes[j].startswith(codes[i]), f"Code {codes[i]} is a prefix of {codes[j]}"


def test_single_unique_character():
    engine = HuffmanEngine()
    text = "ZZZZZZZZZZ"
    tree_bits, payload_bits = engine.encode_text(text)

    reconstructed_root, _ = HuffmanEngine.deserialize_tree(tree_bits)
    decoded = engine.decode_to_text(payload_bits, reconstructed_root)

    assert decoded == text
    assert payload_bits == "0000000000"


def test_empty_string_error():
    engine = HuffmanEngine()
    with pytest.raises(ValueError):
        engine.encode_text("")


def test_tree_merge_history():
    """Verifies that greedy merge history records exactly N-1 merges."""
    engine = HuffmanEngine()
    text = "ABCDE"  # 5 unique bytes
    engine.encode_text(text)

    # step 0 is init, steps 1..4 are 4 merges
    assert len(engine.build_history) == 5
    assert engine.build_history[0]["step"] == 0
    assert engine.build_history[-1]["step"] == 4
    assert engine.build_history[-1]["heap_size"] == 1


def test_reconstructed_tree_frequency_backfill():
    """Ensures decoded trees backfill accurate symbol frequencies instead of remaining 0."""
    engine = HuffmanEngine()
    text = "Huffman coding is an optimal prefix code invented by David Huffman."
    tree_bits, payload_bits = engine.encode_text(text)

    reconstructed_root, _ = HuffmanEngine.deserialize_tree(tree_bits)
    assert reconstructed_root.freq == 0  # initially 0 from bitstream

    decoded = engine.decode_to_text(payload_bits, reconstructed_root)
    assert decoded == text
    assert reconstructed_root.freq == len(text.encode("utf-8"))
    assert reconstructed_root.freq > 0
    # Check that a leaf child also has its true frequency populated
    assert reconstructed_root.left.freq > 0
    assert reconstructed_root.right.freq > 0

