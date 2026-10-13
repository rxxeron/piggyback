"""
tests/test_statistics.py
Verification suite for StatsEngine:
- Shannon Entropy theoretical calculations
- Compression ratio & space savings
- Efficiency bounds
"""

from core.statistics import StatsEngine


def test_shannon_entropy_homogeneous():
    """All identical symbols -> Entropy must be 0."""
    data = b"AAAAAAAAAA"
    entropy = StatsEngine.shannon_entropy(data)
    assert entropy == 0.0


def test_shannon_entropy_binary_uniform():
    """Equal probability of two symbols -> Entropy must be exactly 1.0 bit."""
    data = b"ABABABAB"
    entropy = StatsEngine.shannon_entropy(data)
    assert round(entropy, 4) == 1.0


def test_compression_evaluation():
    text = "Huffman coding is an optimal prefix code invented by David A. Huffman."
    mock_tree_bits = "101" * 20
    mock_payload_bits = "011" * 40

    report = StatsEngine.evaluate(text, mock_tree_bits, mock_payload_bits)

    assert "compression_ratio" in report
    assert "space_savings_pct" in report
    assert "shannon_entropy" in report
    assert "shannon_efficiency_pct" in report
    assert report["byte_count"] == len(text.encode("utf-8"))
    assert report["shannon_entropy"] > 0
    assert report["shannon_efficiency_pct"] <= 100.0
