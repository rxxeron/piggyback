"""
tests/test_report.py
Verification suite for Academic Lab Report Generator
"""

from pathlib import Path
from core.report import ReportGenerator
from core.huffman import HuffmanEngine
from core.statistics import StatsEngine


def test_html_report_generation(tmp_path):
    out_file = tmp_path / "test_report.html"

    text = "ICE245 Algorithm Course: Huffman Coding & Image Steganography"
    engine = HuffmanEngine()
    tree_bits, payload_bits = engine.encode_text(text)
    stats = StatsEngine.evaluate(text, tree_bits, payload_bits)
    code_table = engine.get_code_table_display()

    metrics = {"psnr_db": 72.5, "mse": 0.003}
    stego_meta = {"capacity_usage_pct": 2.5, "modified_channel_values": 450}

    saved_path = ReportGenerator.generate_html_report(
        student_name="Test Student",
        student_id="ICE-1234",
        stats=stats,
        stego_meta=stego_meta,
        metrics=metrics,
        code_table=code_table,
        output_file=str(out_file)
    )

    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "ICE245" in content
    assert "Test Student" in content
    assert "Shannon Entropy" in content
    assert "PSNR" in content
    assert "Prefix-Free Code" in content
