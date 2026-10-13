"""
core/statistics.py
Theoretical Information Bounds & Empirical Compression Analytics

Calculates Shannon entropy, compression ratio, space savings, and efficiency.
Provides side-by-side comparison between fixed-width, Huffman, and Shannon limit.
"""

import math
from collections import Counter
from typing import Dict, Union, List


class StatsEngine:
    """Calculates compression analytics and theoretical limits."""

    @staticmethod
    def shannon_entropy(data: bytes) -> float:
        """
        Calculates theoretical Shannon entropy:
        H(X) = -sum(p(x) * log2(p(x)))
        Returns theoretical minimum bits per symbol.
        """
        if not data:
            return 0.0
        counts = Counter(data)
        n = len(data)
        entropy = 0.0
        for count in counts.values():
            p = count / n
            if p > 0:
                entropy -= p * math.log2(p)
        return float(entropy)

    @classmethod
    def evaluate(cls, text: str, tree_bits: str, payload_bits: str) -> Dict[str, Union[int, float, List[dict]]]:
        """
        Computes a comprehensive statistical compression report.
        """
        raw_bytes = text.encode("utf-8")
        uncompressed_bits = len(raw_bytes) * 8
        compressed_payload = len(payload_bits)
        tree_overhead = len(tree_bits)
        total_bits = compressed_payload + tree_overhead

        byte_count = len(raw_bytes)
        unique_bytes = len(set(raw_bytes))

        entropy = cls.shannon_entropy(raw_bytes)
        avg_bits_per_symbol = (compressed_payload / byte_count) if byte_count > 0 else 0.0

        ratio = (uncompressed_bits / total_bits) if total_bits > 0 else 0.0
        space_savings = ((1.0 - (total_bits / uncompressed_bits)) * 100.0) if uncompressed_bits > 0 else 0.0

        # Efficiency relative to Shannon bound
        if avg_bits_per_symbol > 0 and entropy > 0:
            efficiency = (entropy / avg_bits_per_symbol) * 100.0
        elif entropy == 0:
            efficiency = 100.0
        else:
            efficiency = 0.0

        # Top frequent byte breakdown
        counts = Counter(raw_bytes)
        top_symbols = []
        for b, count in counts.most_common(5):
            char_repr = chr(b) if (32 <= b <= 126 and b != ord("'")) else f"0x{b:02X}"
            top_symbols.append({
                "byte": b,
                "repr": char_repr,
                "count": count,
                "frequency_pct": round((count / byte_count) * 100, 2)
            })

        return {
            "character_count": len(text),
            "byte_count": byte_count,
            "unique_symbols": unique_bytes,
            "uncompressed_bits": uncompressed_bits,
            "compressed_payload_bits": compressed_payload,
            "tree_overhead_bits": tree_overhead,
            "total_stego_bits": total_bits,
            "compression_ratio": round(ratio, 2),
            "space_savings_pct": round(space_savings, 2),
            "shannon_entropy": round(entropy, 4),
            "avg_bits_per_symbol": round(avg_bits_per_symbol, 4),
            "shannon_efficiency_pct": round(min(100.0, efficiency), 2),
            "top_symbols": top_symbols
        }
