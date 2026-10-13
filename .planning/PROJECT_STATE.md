# Live Project State

- **Project Brand**: **Piggyback** — Invisible Payload Carrier & Algorithm Workbench
- **Last Updated**: 2026-10-13 19:02
- **Current Phase**: Web Workbench Deployed to GitHub Pages (hm.rxxeron.iam.bd) + Dynamic Payload Fix
- **Active Status**: Production Ready & Fully Verified
- **Tests Passing**: 18 / 18 passed (100% pass)
- **Architecture Highlights**:
  1. **Brand Identity**: **Piggyback** (Carrying secret payload data on ordinary image pixels without altering visual appearance).
  2. **60 FPS Smooth Tweening Engine ([`gui/tree_widget.py`](file:///g:/ICE245/Project/gui/tree_widget.py))**: Frame-by-frame cubic ease-out tweening ($t = 1 - (1-p)^3$) for node positions, opacities, and camera zoom/pan.
  3. **Zero-Clipping 2D Auto-Fit ([`gui/tree_widget.py`](file:///g:/ICE245/Project/gui/tree_widget.py))**: Viewport bounds calculation takes both Width and Height into account (`fit_zoom = min(zoom_x, zoom_y)`).
  4. **Complete De-AI-ification**: Sleek, high-contrast Technical Slate Dark Theme applied (JetBrains/Wireshark style) in [`gui/styles.py`](file:///g:/ICE245/Project/gui/styles.py) and [`gui/main_window.py`](file:///g:/ICE245/Project/gui/main_window.py).
  5. **Textbook Huffman vs Steganography Separation**: Tab 1 dedicated to ICE245 Lab 4 textbook text compression; Tabs 2 & 3 dedicated to Lab 13 Steganography showcase.
  6. **Web Client & GitHub Pages ([`index.html`](file:///g:/ICE245/Project/index.html))**: Pure client-side HTML5 canvas + Web Crypto + JS Huffman engine deployed to `hm.rxxeron.iam.bd` with dynamic 64-bit header bounds parsing.
  7. **Presentation Defense Guide**: [`PRESENTATION_GUIDE.md`](file:///g:/ICE245/Project/PRESENTATION_GUIDE.md) prepared with 3-minute presentation script, code pointers, and teacher Q&A answers.

---

### Instructions for Any Incoming Agent or Desktop Shift:
1. **Git Path on this machine**: `C:\Users\Student\AppData\Local\Programs\Git\cmd`
2. **To run the GUI**: Run `python main.py` or double-click `run.bat`.
3. **To run Web App**: Open `index.html` in browser or `python -m streamlit run web_app.py`.
4. **Continuity Protocol**: Read `AGENT_PLAYBOOK.md`. All paths are portable and relative.
