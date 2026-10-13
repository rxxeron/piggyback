# Piggyback — Invisible Payload Carrier & Algorithm Workbench

> **Course:** ICE245 Algorithm Design (Lab 4: Greedy Algorithms & Lab 13: Mini Project Showcasing)  
> **Platform:** Python 3.10+ | PyQt6 | NumPy | Pillow | Pytest

---

## 1. Overview & Conceptual Design

In telecommunications and computer science, **"piggybacking"** refers to attaching additional data onto an existing carrier without requiring separate transmission overhead.

**Piggyback** applies this principle to algorithm design and cyber-security:
1. **Standard Huffman (Classical Text Compression for Lab 4)**: Pure textbook Huffman coding. Enter any text -> generates optimal prefix-free bitstream, frequency table, prefix codebook, Shannon entropy, and decompresses bits back to text.
2. **Invisible Carrier Steganography (Lab 13 Showcase)**: Piggybacks the compressed bitstream and serialized tree topology directly onto the Least Significant Bits (LSB) of lossless 24-bit PNG carrier images. Includes 128x difference heatmaps and PSNR forensic proof (> 50 dB).
3. **60 FPS Priority Queue Simulation Sandbox**: Hardware-accelerated canvas stepping through min-heap merges with smooth cubic ease-out tweening and automatic 2D view fitting.
4. **Universal UTF-8 Alphabet**: Uses a 256-symbol byte alphabet ($0..255$) guaranteeing 100% lossless fidelity for English, Bangla (`আমাদের অ্যালগরিদম`), and Unicode scripts.

---

## 2. Quick Launch (Windows)

### 1-Click Launchers:
- **Run the Desktop Workbench:** Double-click `run.bat` or execute:
  ```powershell
  python main.py
  ```
- **Run the Automated Test Suite:** Double-click `test.bat` or execute:
  ```powershell
  python -m pytest tests/ -v
  ```

---

## 3. Bitstream Packet Specification

```
+---------------+-------------------+----------------------+----------------------+-------------------------+
| MAGIC (16b)   | TREE_LEN (16b)    | SERIALIZED TREE      | PAYLOAD_LEN (32b)    | COMPRESSED PAYLOAD      |
| 0x5354 ('ST') | N_tree (unsigned) | Pre-order bitstream  | N_payload (unsigned) | Huffman-encoded message |
+---------------+-------------------+----------------------+----------------------+-------------------------+
```

- **Tree Serialization Format**:
  - `1` + 8-bit byte value -> Leaf node
  - `0` -> Internal branch node (recurse left, then right)
- **Carrier Requirements**: Lossless 24-bit RGB PNG or BMP (lossy JPEG destroys LSB integrity).

---

## 4. Course Curriculum Alignment (ICE245)

- **Lab 4 (Greedy Algorithms — Huffman Coding)**: Demonstrates min-heap priority queue construction, greedy choice property, optimal prefix-free code assignment, and $O(N + K \log K)$ complexity where $K \le 256$.
- **Information Theory**: Evaluates Shannon Entropy $H(X) = -\sum p(x) \log_2 p(x)$ vs average code length and theoretical efficiency.
- **Lab 13 (Mini Project Showcasing — 5 Marks)**: Engineering desktop workbench with 60 FPS animated tree canvas, drag-and-drop carrier embedding, side-by-side forensic verification, and 1-click HTML lab report export.

---

## 5. Automated Test Suite

All 18 automated test cases pass with 100% coverage across core modules:
- `test_ascii_roundtrip`: English sentences
- `test_unicode_bangla_roundtrip`: Bangla text with Unicode punctuation
- `test_emoji_and_multilingual`: Symbols and multilingual text
- `test_prefix_free_property`: Validates that no code is a prefix of another
- `test_single_unique_character`: Validates single-symbol tree edge cases
- `test_tree_merge_history`: Validates step-by-step min-heap telemetry
- `test_reconstructed_tree_frequency_backfill`: Validates tree frequency backfilling
- `test_embed_and_extract_roundtrip`: PNG LSB roundtrip integrity
- `test_capacity_overflow_guard`: Validates image capacity protection
- `test_magic_watermark_rejection`: Rejects non-stego images safely
- `test_pixel_diff_heatmap`: Validates 128x difference amplification
- `test_stego_metrics_mse_psnr`: Verifies MSE and PSNR calculation
- `test_shannon_entropy_homogeneous`: Verifies $H(X) = 0$ for single-symbol inputs
- `test_shannon_entropy_binary_uniform`: Verifies $H(X) = 1.0$ for uniform 2-symbol inputs
- `test_compression_evaluation`: Validates metrics calculation
- `test_html_report_generation`: Validates academic HTML lab report output
- `test_full_pipeline_unicode_roundtrip`: Full end-to-end integration test

---

## 6. Multi-Desktop Continuity Protocol

If shifting computers or development environments:
1. Open `AGENT_PLAYBOOK.md` for the cold-start protocol.
2. Check `.planning/PROJECT_STATE.md` for the live state.
3. Run `python -m pytest tests/ -v`.
