"""
gui/tree_widget.py
High-Performance Animated Huffman Tree & Forest Canvas (PyQt6 QPainter)

Features:
- 60 FPS Smooth Position & Camera Interpolation (Cubic Ease-Out Tweening)
- Dynamic 2D Auto-Fit: Automatically scales both Width and Height (zero clipping)
- Non-overlapping hierarchical layout for single trees and priority queue forests
- Smooth branch morphing and fade-in for newly merged parent nodes
- Path highlighting on hover with variable-length prefix code display
- Interactive zoom (wheel) and pan (drag) with viewport bounds safety
"""

import time
from typing import Optional, Dict, List, Tuple
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPointF, QRectF, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont

from core.huffman import HuffmanNode


class VisualNode:
    """Positioned node with frame-by-frame 60 FPS tweening state."""

    def __init__(self, node: HuffmanNode, x: float, y: float, depth: int):
        self.node = node
        self.depth = depth
        self.radius = 20.0

        # Current interpolated state (drawn every frame)
        self.x = x
        self.y = y
        self.opacity = 1.0

        # Tween endpoints
        self.start_x = x
        self.start_y = y
        self.target_x = x
        self.target_y = y

        self.start_opacity = 1.0
        self.target_opacity = 1.0

        # Visual flags
        self.highlighted = False
        self.is_merged = False
        self.is_popped = False
        self.active_code = ""

    def contains(self, pt: QPointF) -> bool:
        dx = self.x - pt.x()
        dy = self.y - pt.y()
        return (dx * dx + dy * dy) <= (self.radius * self.radius)


class AnimatedTreeWidget(QWidget):
    """
    Hardware-accelerated QPainter canvas supporting 60 FPS smooth interpolation,
    automatic vertical & horizontal aspect fitting, and interactive inspection.
    """

    node_selected = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setMinimumSize(420, 320)

        self.forest_roots: List[HuffmanNode] = []
        self.nodes_map: Dict[int, VisualNode] = {}
        self.visual_edges: List[Tuple[VisualNode, VisualNode, str]] = []

        # Viewport Navigation & Camera
        self.zoom: float = 1.0
        self.offset: QPointF = QPointF(0, 0)
        self.start_zoom: float = 1.0
        self.target_zoom: float = 1.0
        self.start_offset: QPointF = QPointF(0, 0)
        self.target_offset: QPointF = QPointF(0, 0)

        self.is_panning: bool = False
        self.last_mouse_pos: QPointF = QPointF(0, 0)

        # Highlight State
        self.highlighted_leaf: Optional[VisualNode] = None
        self.highlighted_path: List[VisualNode] = []

        # 60 FPS Animation Engine
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(16)  # ~60 FPS
        self.anim_timer.timeout.connect(self._on_anim_step)
        self.anim_start_time: float = 0.0
        self.anim_duration: float = 0.35  # 350 ms smooth transition

    def set_tree(self, root: Optional[HuffmanNode], animate: bool = True):
        """Renders a single complete Huffman tree."""
        self.set_forest([root] if root else [], animate=animate)

    def set_forest(
        self,
        trees: List[HuffmanNode],
        active_merged: Optional[HuffmanNode] = None,
        popped: Optional[Tuple[HuffmanNode, HuffmanNode]] = None,
        animate: bool = True
    ):
        """
        Calculates target coordinates for all trees in the Priority Queue
        and smoothly interpolates nodes from their previous positions.
        """
        self.forest_roots = [t for t in trees if t is not None]
        self.highlighted_leaf = None
        self.highlighted_path = []

        if not self.forest_roots:
            self.nodes_map.clear()
            self.visual_edges.clear()
            self.update()
            return

        # 1. Compute target coordinates for all nodes in the forest
        target_positions: Dict[int, Tuple[float, float, int, str]] = {}
        new_edges: List[Tuple[int, int, str]] = []
        leaf_x = [0.0]

        popped_ids = {id(p) for p in popped} if popped else set()

        def compute_layout(node: HuffmanNode, depth: int, code: str) -> Tuple[float, float]:
            if node.is_leaf or (not node.left and not node.right):
                x = leaf_x[0]
                leaf_x[0] += 56.0  # Horizontal spacing between leaves
                y = depth * 72.0   # Vertical spacing between levels
                target_positions[id(node)] = (x, y, depth, code)
                return x, y

            left_pos = compute_layout(node.left, depth + 1, code + "0") if node.left else None
            right_pos = compute_layout(node.right, depth + 1, code + "1") if node.right else None

            if left_pos and right_pos:
                x = (left_pos[0] + right_pos[0]) / 2.0
            elif left_pos:
                x = left_pos[0]
            elif right_pos:
                x = right_pos[0]
            else:
                x = leaf_x[0]

            y = depth * 72.0
            target_positions[id(node)] = (x, y, depth, code)

            if node.left:
                new_edges.append((id(node), id(node.left), "0"))
            if node.right:
                new_edges.append((id(node), id(node.right), "1"))

            return x, y

        for tree_root in self.forest_roots:
            compute_layout(tree_root, depth=0, code="")
            leaf_x[0] += 40.0  # Gap between trees in the priority queue forest

        # 2. Update visual nodes dictionary with tween endpoints
        new_nodes_map: Dict[int, VisualNode] = {}

        def traverse_and_register(node: HuffmanNode):
            if not node:
                return
            nid = id(node)
            tx, ty, depth, code = target_positions[nid]

            if nid in self.nodes_map:
                # Existing node smoothly glides to new position
                vn = self.nodes_map[nid]
                vn.start_x = vn.x
                vn.start_y = vn.y
                vn.target_x = tx
                vn.target_y = ty
                vn.start_opacity = vn.opacity
                vn.target_opacity = 1.0
            else:
                # Newly spawned node (e.g. parent of merge)
                # Starts at midpoint of children with 0 opacity, glides and fades in
                start_x = tx
                start_y = ty
                if node.left and id(node.left) in self.nodes_map and node.right and id(node.right) in self.nodes_map:
                    l_vn = self.nodes_map[id(node.left)]
                    r_vn = self.nodes_map[id(node.right)]
                    start_x = (l_vn.x + r_vn.x) / 2.0
                    start_y = (l_vn.y + r_vn.y) / 2.0

                vn = VisualNode(node, start_x, start_y, depth)
                vn.start_x = start_x
                vn.start_y = start_y
                vn.target_x = tx
                vn.target_y = ty
                vn.opacity = 0.0
                vn.start_opacity = 0.0
                vn.target_opacity = 1.0

            vn.active_code = code
            vn.is_merged = (node == active_merged)
            vn.is_popped = (nid in popped_ids)

            new_nodes_map[nid] = vn
            if node.left:
                traverse_and_register(node.left)
            if node.right:
                traverse_and_register(node.right)

        for tree_root in self.forest_roots:
            traverse_and_register(tree_root)

        self.nodes_map = new_nodes_map

        # Rebuild edge references
        self.visual_edges = []
        for pid, cid, bit in new_edges:
            if pid in self.nodes_map and cid in self.nodes_map:
                self.visual_edges.append((self.nodes_map[pid], self.nodes_map[cid], bit))

        # 3. Calculate target camera viewport (both Width and Height auto-fit)
        all_targets = list(target_positions.values())
        if all_targets:
            min_x = min(p[0] for p in all_targets)
            max_x = max(p[0] for p in all_targets)
            min_y = min(p[1] for p in all_targets)
            max_y = max(p[1] for p in all_targets)

            total_w = max(60.0, max_x - min_x + 90.0)
            total_h = max(60.0, max_y - min_y + 110.0)
            center_x = (min_x + max_x) / 2.0
            center_y = (min_y + max_y) / 2.0

            vw = max(200.0, float(self.width()))
            vh = max(200.0, float(self.height()))

            zoom_x = (vw - 60.0) / total_w
            zoom_y = (vh - 70.0) / total_h
            fit_zoom = max(0.18, min(1.0, zoom_x, zoom_y))

            self.start_zoom = self.zoom
            self.target_zoom = fit_zoom

            self.start_offset = QPointF(self.offset.x(), self.offset.y())
            self.target_offset = QPointF(
                vw / 2.0 - center_x * fit_zoom,
                vh / 2.0 - center_y * fit_zoom
            )
        else:
            self.target_zoom = 1.0
            self.target_offset = QPointF(0, 0)

        # 4. Trigger 60 FPS animation loop
        if animate:
            self.anim_start_time = time.time()
            self.anim_timer.start()
        else:
            # Immediate snap
            for vn in self.nodes_map.values():
                vn.x = vn.target_x
                vn.y = vn.target_y
                vn.opacity = 1.0
            self.zoom = self.target_zoom
            self.offset = self.target_offset
            self.update()

    def reset_view(self):
        """Explicitly re-centers the current viewport."""
        if not self.nodes_map:
            self.offset = QPointF(0, 0)
            self.zoom = 1.0
            self.update()
            return

        min_x = min(n.x for n in self.nodes_map.values())
        max_x = max(n.x for n in self.nodes_map.values())
        min_y = min(n.y for n in self.nodes_map.values())
        max_y = max(n.y for n in self.nodes_map.values())

        total_w = max(60.0, max_x - min_x + 90.0)
        total_h = max(60.0, max_y - min_y + 110.0)
        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0

        vw = max(200.0, float(self.width()))
        vh = max(200.0, float(self.height()))

        zoom_x = (vw - 60.0) / total_w
        zoom_y = (vh - 70.0) / total_h
        self.zoom = max(0.18, min(1.0, zoom_x, zoom_y))
        self.offset = QPointF(vw / 2.0 - center_x * self.zoom, vh / 2.0 - center_y * self.zoom)
        self.update()

    def _on_anim_step(self):
        """Frame-by-frame 60 FPS tweening callback."""
        elapsed = time.time() - self.anim_start_time
        progress = min(1.0, elapsed / self.anim_duration) if self.anim_duration > 0 else 1.0

        # Smooth Cubic Ease-Out curve: t = 1 - (1 - progress)^3
        t = 1.0 - (1.0 - progress) ** 3

        # Interpolate node positions and opacities
        for vn in self.nodes_map.values():
            vn.x = vn.start_x + (vn.target_x - vn.start_x) * t
            vn.y = vn.start_y + (vn.target_y - vn.start_y) * t
            vn.opacity = vn.start_opacity + (vn.target_opacity - vn.start_opacity) * t

        # Interpolate camera zoom and pan smoothly
        self.zoom = self.start_zoom + (self.target_zoom - self.start_zoom) * t
        self.offset = QPointF(
            self.start_offset.x() + (self.target_offset.x() - self.start_offset.x()) * t,
            self.start_offset.y() + (self.target_offset.y() - self.start_offset.y()) * t
        )

        self.update()

        if progress >= 1.0:
            self.anim_timer.stop()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.anim_timer.isActive() and self.nodes_map:
            self.reset_view()

    def _find_path_to_leaf(self, target_vn: VisualNode) -> List[VisualNode]:
        path = [target_vn]
        curr = target_vn
        while True:
            parent_found = None
            for p, c, bit in self.visual_edges:
                if c == curr:
                    parent_found = p
                    break
            if parent_found:
                path.append(parent_found)
                curr = parent_found
            else:
                break
        path.reverse()
        return path

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Technical Slate Canvas Background (De-AI-ified dark engineering palette)
        painter.fillRect(self.rect(), QColor("#111827"))

        if not self.nodes_map:
            painter.setPen(QColor("#64748B"))
            painter.setFont(QFont("Segoe UI", 11))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "Ready for Priority Queue Simulation\nEnter text above to build & inspect the Min-Heap forest."
            )
            return

        painter.save()
        painter.translate(self.offset)
        painter.scale(self.zoom, self.zoom)

        # 1. Draw Edges
        for parent_vn, child_vn, bit in self.visual_edges:
            is_edge_highlighted = (
                parent_vn in self.highlighted_path and child_vn in self.highlighted_path
            )
            alpha = int(min(parent_vn.opacity, child_vn.opacity) * 255)

            if is_edge_highlighted:
                pen_color = QColor(16, 185, 129, alpha)  # Emerald
                pen_width = 2.8
            else:
                pen_color = QColor(51, 65, 85, alpha)   # Slate border
                pen_width = 1.6

            painter.setPen(QPen(pen_color, pen_width))
            painter.drawLine(QPointF(parent_vn.x, parent_vn.y), QPointF(child_vn.x, child_vn.y))

            # Edge Bit Label Pill (0 or 1)
            mid_x = (parent_vn.x + child_vn.x) / 2.0
            mid_y = (parent_vn.y + child_vn.y) / 2.0

            pill_bg = QColor(15, 23, 42, alpha)
            painter.setBrush(QBrush(pill_bg))
            painter.setPen(QPen(QColor(51, 65, 85, alpha), 1.0))
            painter.drawRoundedRect(QRectF(mid_x - 8, mid_y - 8, 16, 16), 3, 3)

            painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
            painter.setPen(QColor(56, 189, 248, alpha) if is_edge_highlighted else QColor(148, 163, 184, alpha))
            painter.drawText(QRectF(mid_x - 8, mid_y - 8, 16, 16), Qt.AlignmentFlag.AlignCenter, bit)

        # 2. Draw Nodes
        font_main = QFont("Consolas", 9, QFont.Weight.Bold)
        font_sub = QFont("Consolas", 7)

        for vn in self.nodes_map.values():
            alpha = int(vn.opacity * 255)
            is_path_node = vn in self.highlighted_path
            node = vn.node

            # Color hierarchy
            if is_path_node:
                bg_color = QColor(6, 78, 59, alpha)
                border_color = QColor(16, 185, 129, alpha)
                border_width = 2.5
            elif vn.is_merged:
                bg_color = QColor(15, 23, 42, alpha)
                border_color = QColor(52, 211, 153, alpha)  # Mint
                border_width = 2.5
            elif vn.is_popped:
                bg_color = QColor(30, 27, 75, alpha)
                border_color = QColor(245, 158, 11, alpha)  # Amber
                border_width = 2.5
            elif node.is_leaf:
                bg_color = QColor(15, 23, 42, alpha)
                border_color = QColor(56, 189, 248, alpha)  # Cyan
                border_width = 1.6
            else:
                bg_color = QColor(15, 23, 42, alpha)
                border_color = QColor(100, 116, 139, alpha) # Slate
                border_width = 1.4

            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(border_color, border_width))
            painter.drawEllipse(QPointF(vn.x, vn.y), vn.radius, vn.radius)

            # Labels
            painter.setFont(font_main)
            if node.is_leaf:
                b = node.byte_val
                if 32 <= b <= 126 and b != ord("'") and b != ord("\\"):
                    sym = chr(b)
                elif b == ord(" "):
                    sym = "SPC"
                else:
                    sym = f"{b:02X}"

                painter.setPen(QColor(248, 250, 252, alpha))
                painter.drawText(QRectF(vn.x - 16, vn.y - 12, 32, 14), Qt.AlignmentFlag.AlignCenter, sym)

                painter.setFont(font_sub)
                painter.setPen(QColor(148, 163, 184, alpha))
                painter.drawText(QRectF(vn.x - 16, vn.y + 1, 32, 12), Qt.AlignmentFlag.AlignCenter, str(node.freq))
            else:
                painter.setFont(font_sub)
                painter.setPen(QColor(226, 232, 240, alpha))
                label_text = f"Σ={node.freq}" if node.freq > 0 else "ROOT"
                painter.drawText(QRectF(vn.x - 18, vn.y - 7, 36, 14), Qt.AlignmentFlag.AlignCenter, label_text)

        painter.restore()

        # 3. Canvas HUD (Technical Info)
        painter.setPen(QColor("#64748B"))
        painter.setFont(QFont("Consolas", 8))
        hud_text = f"VIEW: {int(self.zoom * 100)}% | HEAP FORESTS: {len(self.forest_roots)}"
        if self.highlighted_leaf:
            hud_text += f" | SYMBOL CODE: {self.highlighted_leaf.active_code}"
        painter.drawText(12, self.height() - 10, hud_text)

    # Mouse Navigation
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        factor = 1.12 if delta > 0 else 0.89
        new_zoom = self.zoom * factor
        if 0.15 <= new_zoom <= 4.0:
            cursor_pos = event.position()
            self.offset = cursor_pos - (cursor_pos - self.offset) * factor
            self.zoom = new_zoom
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_panning = True
            self.last_mouse_pos = event.position()

    def mouseMoveEvent(self, event):
        if self.is_panning:
            delta = event.position() - self.last_mouse_pos
            self.offset += delta
            self.last_mouse_pos = event.position()
            self.update()
        else:
            world_pos = (event.position() - self.offset) / self.zoom
            hovered = None
            for vn in self.nodes_map.values():
                if vn.contains(world_pos) and vn.node.is_leaf:
                    hovered = vn
                    break

            if hovered != self.highlighted_leaf:
                self.highlighted_leaf = hovered
                self.highlighted_path = self._find_path_to_leaf(hovered) if hovered else []
                self.update()
                if hovered:
                    self.node_selected.emit({
                        "byte": hovered.node.byte_val,
                        "label": hovered.node.display_label(),
                        "code": hovered.active_code,
                        "freq": hovered.node.freq
                    })

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_panning = False
