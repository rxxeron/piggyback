# Live Project State

- **Project Brand**: **Piggyback** — Invisible Payload Carrier & Algorithm Workbench
- **Last Updated**: 2026-10-13 18:34
- **Current Phase**: Brand Identity Established + 60 FPS Tweening Engine + De-AI-ified Workbench
- **Active Status**: Production Ready & Fully Verified
- **Tests Passing**: 18 / 18 passed in 0.15s (100% pass)
- **Architecture Highlights**:
  1. **Brand Identity**: **Piggyback** (Human connect: carrying secret data on the back of ordinary image pixels without altering how the photo looks).
  2. **60 FPS Smooth Tweening Engine ([`gui/tree_widget.py`](file:///e:/ICE245/Project/gui/tree_widget.py))**: Frame-by-frame cubic ease-out tweening ($t = 1 - (1-p)^3$) for node positions, opacities, and camera zoom/pan. Nodes glide smoothly into position instead of teleporting.
  3. **Zero-Clipping 2D Auto-Fit ([`gui/tree_widget.py`](file:///e:/ICE245/Project/gui/tree_widget.py))**: Viewport bounds calculation takes both Width and Height into account (`fit_zoom = min(zoom_x, zoom_y)`), guaranteeing tree branches and child nodes are never clipped off at the bottom or sides.
  4. **Complete De-AI-ification**: All tabs, buttons, dialogs, and headers stripped of emojis. Sleek, high-contrast Technical Slate Dark Theme applied (JetBrains/Wireshark style) in [`gui/styles.py`](file:///e:/ICE245/Project/gui/styles.py) and [`gui/main_window.py`](file:///e:/ICE245/Project/gui/main_window.py).
  5. **Textbook Huffman vs Steganography Separation**: Tab 1 dedicated to ICE245 Lab 4 textbook text compression; Tabs 2 & 3 dedicated to Lab 13 Steganography showcase.
  6. **Presentation Defense Guide**: [`PRESENTATION_GUIDE.md`](file:///e:/ICE245/Project/PRESENTATION_GUIDE.md) prepared with 3-minute presentation script, code pointers, and teacher Q&A answers.

---

### Instructions for Any Incoming Agent or Desktop Shift:
1. **To run the GUI**: Run `python main.py` or double-click `run.bat`.
2. **To run tests**: Run `python -m pytest tests/ -v` or double-click `test.bat`.
3. **Continuity Protocol**: Read `AGENT_PLAYBOOK.md`. All paths are portable and relative.
