# 📐 HuffStego — Technical Architecture & Specifications

## 1. System Data Flow

```
                      +-----------------------------+
                      |   Secret Message (Unicode)  |
                      +--------------+--------------+
                                     |
                             text.encode('utf-8')
                                     |
                                     v
                      +-----------------------------+
                      |     Raw Bytes (0..255)      |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |     Huffman Priority Queue  |
                      |   (Min-Heap Frequency Tree) |
                      +--------------+--------------+
                                     |
                                     +-----------------------+
                                     |                       |
                                     v                       v
                      +-----------------------+   +----------------------+
                      | Compressed Bitstream  |   | Serialized Tree Bits |
                      +-----------+-----------+   +----------+-----------+
                                  |                          |
                                  +------------+-------------+
                                               |
                                               v
                      +--------------------------------------------------+
                      |           Steganographic Bit Packet              |
                      | [MAGIC(16b)][TLEN(16b)][TREE][PLEN(32b)][PAYLOAD]|
                      +------------------------+-------------------------+
                                               |
                                               v
                      +--------------------------------------------------+
                      |       Cover Image LSB Embedder (RGB Plane)       |
                      +------------------------+-------------------------+
                                               |
                                               v
                      +--------------------------------------------------+
                      |            Steganographic PNG Image              |
                      +--------------------------------------------------+
```

---

## 2. Steganographic Packet Specification

The bitstream embedded into the pixel Least Significant Bits follows this precise schema:

| Field | Size | Data Type | Description |
|---|---|---|---|
| `MAGIC_SIGNATURE` | 16 bits | Binary Constant | `0101001101010100` (`0x5354` = ASCII 'ST' for Stego) |
| `TREE_BIT_LENGTH` | 16 bits | Big-endian unsigned int | Number of bits in the serialized Huffman tree ($N_{tree}$) |
| `SERIALIZED_TREE` | $N_{tree}$ bits | Pre-order bitstream | Serialized Huffman tree: `1` + 8-bit byte for leaf, `0` for branch |
| `PAYLOAD_BIT_LENGTH` | 32 bits | Big-endian unsigned int | Number of bits in the compressed payload ($N_{payload}$) |
| `COMPRESSED_PAYLOAD`| $N_{payload}$ bits | Bitstream | The variable-length Huffman encoded message |

---

## 3. Tree Serialization Protocol

- **Leaf Node**: Emits `1` followed immediately by an 8-bit binary representation of the byte value ($0..255$). Total = 9 bits.
- **Internal / Branch Node**: Emits `0`, followed by pre-order serialization of the left child, then the right child.
- **Reconstruction**: Recursive descent reading 1 bit:
  - If `1`, slice the next 8 bits as `byte_val` $\rightarrow$ create leaf node.
  - If `0`, recurse left, then recurse right $\rightarrow$ create internal node.

---

## 4. Algorithmic Modules

### `core/huffman.py`
- `HuffmanNode`: Dataclass with `freq`, `byte_val`, `left`, `right`.
- `HuffmanEngine`:
  - `build_tree_from_bytes(data: bytes) -> HuffmanNode`
  - `encode_text(text: str) -> tuple[str, str]` (returns tree_bits, payload_bits)
  - `decode_to_text(payload_bits: str, tree_root: Optional[HuffmanNode]) -> str`
  - `serialize_tree() -> str`
  - `deserialize_tree(bits: str) -> tuple[HuffmanNode, int]`

### `core/steganography.py`
- `StegoEngine`:
  - `get_capacity_info(image_path) -> dict`
  - `embed(image_path, tree_bits, payload_bits, output_path) -> dict`
  - `extract(stego_path) -> tuple[str, str]`
  - `compute_diff_heatmap(orig_path, stego_path) -> np.ndarray`

### `core/statistics.py`
- `StatsEngine`:
  - `shannon_entropy(data: bytes) -> float`
  - `evaluate(text: str, tree_bits: str, payload_bits: str) -> dict`
