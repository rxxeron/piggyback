"""
core/huffman.py
Universal UTF-8 Byte-Level Huffman Coding Engine

Supports any language (English, Bangla, Arabic, Chinese), symbols, and emojis.
Constructs prefix-free binary trees via Greedy Priority Queue (min-heap).
Records complete step-by-step merge history for GUI playback.
"""

import heapq
from dataclasses import dataclass, field
from typing import Optional, Union, Tuple, List, Dict


@dataclass(order=True)
class HuffmanNode:
    """A node in the byte-level Huffman tree."""
    freq: int
    byte_val: Optional[int] = field(default=None, compare=False)
    left: Optional['HuffmanNode'] = field(default=None, compare=False)
    right: Optional['HuffmanNode'] = field(default=None, compare=False)

    @property
    def is_leaf(self) -> bool:
        return self.byte_val is not None

    def __hash__(self) -> int:
        return id(self)

    def display_label(self) -> str:
        """Human-readable representation for visualization."""
        if not self.is_leaf or self.byte_val is None:
            return f"Σ={self.freq}"
        b = self.byte_val
        if 32 <= b <= 126 and b != ord("'") and b != ord("\\"):
            return f"'{chr(b)}' ({self.freq})"
        elif b == ord(" "):
            return f"'␣' ({self.freq})"
        elif b == ord("\n"):
            return f"'\\n' ({self.freq})"
        elif b == ord("\t"):
            return f"'\\t' ({self.freq})"
        return f"0x{b:02X} ({self.freq})"

    def to_dict(self) -> dict:
        """Serializes node structure for GUI rendering."""
        return {
            "freq": self.freq,
            "byte_val": self.byte_val,
            "is_leaf": self.is_leaf,
            "label": self.display_label(),
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None
        }


class HuffmanEngine:
    """
    Greedy Huffman encoding/decoding engine with full animation telemetry
    and compact tree bitstream serialization.
    """

    def __init__(self):
        self.root: Optional[HuffmanNode] = None
        self.codes: Dict[int, str] = {}
        self.build_history: List[dict] = []

    def build_tree_from_bytes(self, data: bytes) -> HuffmanNode:
        """
        Builds the Huffman tree from a byte stream using a min-heap.
        Records step-by-step merges in `self.build_history`.
        """
        if not data:
            raise ValueError("Input data cannot be empty.")

        # 1. Frequency calculation
        freq_map: Dict[int, int] = {}
        for b in data:
            freq_map[b] = freq_map.get(b, 0) + 1

        self.build_history = []

        # 2. Initialize priority queue with leaf nodes
        heap: List[HuffmanNode] = [
            HuffmanNode(freq=f, byte_val=b) for b, f in freq_map.items()
        ]
        heapq.heapify(heap)

        self.build_history.append({
            "step": 0,
            "description": f"Initialized {len(heap)} leaf symbols in priority queue",
            "heap_size": len(heap),
            "merged": None,
            "active_merged": None,
            "popped": None,
            "forest": [n for n in sorted(heap, key=lambda x: (x.freq, x.byte_val if x.byte_val is not None else -1))],
            "remaining": [
                {"label": n.display_label(), "freq": n.freq, "byte_val": n.byte_val}
                for n in sorted(heap, key=lambda x: (x.freq, x.byte_val if x.byte_val is not None else -1))
            ]
        })

        # Edge case: single unique symbol
        if len(heap) == 1:
            sole_leaf = heapq.heappop(heap)
            self.root = sole_leaf
            self.codes = {sole_leaf.byte_val: "0"}
            self.build_history.append({
                "step": 1,
                "description": f"Single unique symbol: assigned prefix code '0'",
                "heap_size": 1,
                "merged": None,
                "remaining": [{"label": self.root.display_label(), "freq": self.root.freq}]
            })
            return self.root

        # 3. Greedy algorithm: repeatedly merge two lowest-frequency trees
        step = 1
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)

            merged = HuffmanNode(
                freq=left.freq + right.freq,
                left=left,
                right=right
            )
            heapq.heappush(heap, merged)

            self.build_history.append({
                "step": step,
                "description": f"Merged {left.display_label()} and {right.display_label()} → (Σ={merged.freq})",
                "heap_size": len(heap),
                "merged": {
                    "left": left.to_dict(),
                    "right": right.to_dict(),
                    "parent_freq": merged.freq
                },
                "active_merged": merged,
                "popped": (left, right),
                "forest": [n for n in sorted(heap, key=lambda x: (x.freq, x.byte_val if x.byte_val is not None else -1))],
                "remaining": [
                    {"label": n.display_label(), "freq": n.freq, "byte_val": n.byte_val}
                    for n in sorted(heap, key=lambda x: (x.freq, x.byte_val if x.byte_val is not None else -1))
                ]
            })
            step += 1

        self.root = heap[0]
        self.codes = {}
        self._generate_codes(self.root, "")
        return self.root

    def _generate_codes(self, node: Optional[HuffmanNode], current_code: str):
        """Recursively generates variable-length prefix-free codes."""
        if node is None:
            return
        if node.is_leaf and node.byte_val is not None:
            self.codes[node.byte_val] = current_code if current_code else "0"
            return
        self._generate_codes(node.left, current_code + "0")
        self._generate_codes(node.right, current_code + "1")

    def encode_text(self, text: str) -> Tuple[str, str]:
        """
        Encodes a Unicode string into:
        (tree_bits, payload_bits)
        """
        raw_bytes = text.encode("utf-8")
        self.build_tree_from_bytes(raw_bytes)
        payload_bits = "".join(self.codes[b] for b in raw_bytes)
        tree_bits = self.serialize_tree()
        return tree_bits, payload_bits

    def decode_to_text(self, payload_bits: str, tree_root: Optional[HuffmanNode] = None) -> str:
        """
        Decodes a binary payload string back into a Unicode text string
        using the provided (or current) Huffman tree.
        """
        root = tree_root or self.root
        if not root:
            raise ValueError("No Huffman tree provided for decoding.")

        if not payload_bits:
            return ""

        decoded_bytes = bytearray()

        # Handle single unique symbol
        if root.is_leaf and root.byte_val is not None:
            return (bytes([root.byte_val]) * len(payload_bits)).decode("utf-8")

        curr = root
        for bit in payload_bits:
            curr = curr.left if bit == "0" else curr.right
            if curr is None:
                raise ValueError("Corrupted bitstream: encountered non-existent path in tree.")
            if curr.is_leaf and curr.byte_val is not None:
                decoded_bytes.append(curr.byte_val)
                curr = root

        # Automatically backfill leaf and internal node frequencies from decoded stream
        self.populate_frequencies(root, bytes(decoded_bytes))

        return decoded_bytes.decode("utf-8", errors="replace")

    @classmethod
    def populate_frequencies(cls, root: Optional[HuffmanNode], data: bytes) -> None:
        """
        Backfills accurate leaf and internal node frequencies from decoded raw bytes.
        Restores the full statistical state of the reconstructed tree.
        """
        if not root or not data:
            return
        from collections import Counter
        freq_map = Counter(data)

        def update(node: Optional[HuffmanNode]) -> int:
            if node is None:
                return 0
            if node.is_leaf and node.byte_val is not None:
                node.freq = freq_map.get(node.byte_val, 0)
                return node.freq
            node.freq = update(node.left) + update(node.right)
            return node.freq

        update(root)

    def serialize_tree(self) -> str:
        """
        Serializes tree to pre-order bitstream.
        Leaf: '1' + 8-bit byte value
        Internal node: '0'
        """
        if not self.root:
            raise ValueError("Cannot serialize an empty tree.")
        bits: List[str] = []
        self._serialize(self.root, bits)
        return "".join(bits)

    def _serialize(self, node: Optional[HuffmanNode], bits: List[str]):
        if node is None:
            return
        if node.is_leaf and node.byte_val is not None:
            bits.append("1")
            bits.append(format(node.byte_val, "08b"))
        else:
            bits.append("0")
            self._serialize(node.left, bits)
            self._serialize(node.right, bits)

    @classmethod
    def deserialize_tree(cls, bits: str, pos: int = 0) -> Tuple[HuffmanNode, int]:
        """
        Reconstructs Huffman tree from pre-order bitstream.
        Returns: (reconstructed_root_node, next_bit_position)
        """
        if pos >= len(bits):
            raise ValueError(f"Corrupted tree data: end of bitstream reached at index {pos}.")

        if bits[pos] == "1":
            if pos + 9 > len(bits):
                raise ValueError("Corrupted tree data: truncated leaf byte value.")
            byte_val = int(bits[pos + 1: pos + 9], 2)
            return HuffmanNode(freq=0, byte_val=byte_val), pos + 9
        else:
            left, next_pos = cls.deserialize_tree(bits, pos + 1)
            right, final_pos = cls.deserialize_tree(bits, next_pos)
            return HuffmanNode(freq=0, left=left, right=right), final_pos

    def get_code_table_display(self) -> List[dict]:
        """
        Returns sorted list of symbols, their character representation,
        frequency, and Huffman code for UI display.
        """
        if not self.codes or not self.root:
            return []

        rows = []
        for byte_val, code in sorted(self.codes.items(), key=lambda x: (len(x[1]), x[0])):
            if 32 <= byte_val <= 126 and byte_val != ord("'") and byte_val != ord("\\"):
                char_repr = chr(byte_val)
            elif byte_val == ord(" "):
                char_repr = "[Space]"
            elif byte_val == ord("\n"):
                char_repr = "[Newline]"
            elif byte_val == ord("\t"):
                char_repr = "[Tab]"
            else:
                char_repr = f"0x{byte_val:02X}"

            rows.append({
                "byte": byte_val,
                "char": char_repr,
                "code": code,
                "length": len(code)
            })
        return rows
