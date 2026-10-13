# Live Project State

- **Project Brand**: **Piggyback** — Invisible Payload Carrier & Algorithm Workbench
- **Last Updated**: 2026-10-13 19:16
- **Current Phase**: Live on GitHub Pages (`hm.rxxeron.iam.bd`) | Author Identity Cleaned | Production Ready
- **Active Status**: 100% Complete & Globally Deployed
- **Tests Passing**: 18 / 18 passed (100% pass)
- **Deployment Status**:
  - Domain `hm.rxxeron.iam.bd` CNAME updated to `rxxeron.github.io`.
  - Verified HTTP 200 OK direct response from GitHub Anycast CDN (`185.199.108.153`).
  - Global DNS resolved on Cloudflare (`1.1.1.1`) and Google (`8.8.8.8`).
  - Note for EWU local network: DNS cache on `bdc.ewubd.edu` expires in ~1 hour or can be bypassed via Chrome Secure DNS (1.1.1.1).
- **Architecture Highlights**:
  1. **Brand Identity**: **Piggyback** (Carrying secret payload data on ordinary image pixels without altering visual appearance).
  2. **Author Identity**: Cleaned and rewritten to `rxxeron <rhrakibulhasan279@gmail.com>` across all commits.
  3. **60 FPS Smooth Tweening Engine ([`gui/tree_widget.py`](file:///g:/ICE245/Project/gui/tree_widget.py))**: Frame-by-frame cubic ease-out tweening ($t = 1 - (1-p)^3$) for node positions, opacities, and camera zoom/pan.
  4. **Zero-Clipping 2D Auto-Fit ([`gui/tree_widget.py`](file:///g:/ICE245/Project/gui/tree_widget.py))**: Viewport bounds calculation takes both Width and Height into account (`fit_zoom = min(zoom_x, zoom_y)`).
  5. **Complete De-AI-ification**: Sleek, high-contrast Technical Slate Dark Theme applied (JetBrains/Wireshark style) in [`gui/styles.py`](file:///g:/ICE245/Project/gui/styles.py) and [`gui/main_window.py`](file:///g:/ICE245/Project/gui/main_window.py).
  6. **Textbook Huffman vs Steganography Separation**: Tab 1 dedicated to ICE245 Lab 4 textbook text compression; Tabs 2 & 3 dedicated to Lab 13 Steganography showcase.
  7. **Web Client & GitHub Pages ([`index.html`](file:///g:/ICE245/Project/index.html))**: Pure client-side HTML5 canvas + Web Crypto + JS Huffman engine deployed to `hm.rxxeron.iam.bd` with dynamic 64-bit header bounds parsing.
  8. **Presentation Defense Guide**: [`PRESENTATION_GUIDE.md`](file:///g:/ICE245/Project/PRESENTATION_GUIDE.md) prepared with 3-minute presentation script, code pointers, and teacher Q&A answers.

---

### Instructions for Any Incoming Agent or Desktop Shift:
1. **Git Path on this machine**: `C:\Users\Student\AppData\Local\Programs\Git\cmd`
2. **Git Author**: `rxxeron <rhrakibulhasan279@gmail.com>`
3. **To run the GUI**: Run `python main.py` or double-click `run.bat`.
4. **To run Web App locally**: Open `index.html` in browser or `python -m streamlit run web_app.py`.
5. **Live URL**: `https://hm.rxxeron.iam.bd/` (GitHub Pages) or `https://github.com/rxxeron/piggyback`
6. **Next Action**: Review and rehearse with `PRESENTATION_GUIDE.md` for Lab 13 defense.
7. **Continuity Protocol**: Read `AGENT_PLAYBOOK.md`. All paths are portable and relative.
