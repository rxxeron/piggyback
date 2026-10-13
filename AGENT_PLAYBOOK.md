# 🤖 HuffStego — AI Agent Continuity Playbook

Welcome to **HuffStego** (ICE245 Algorithm Course Project — Huffman Coding Steganography Platform).
This document is the **universal cold-start contract** for ANY AI agent (Claude, Gemini, Cursor, Copilot, ChatGPT, Antigravity) or developer picking up this repository on any workstation.

---

## 1. Quick-Start (15-Second Protocol)

Whenever you open this directory or switch to a new machine:

1. **Step 1: Check Current State**
   Read `.planning/PROJECT_STATE.md` immediately. It tells you:
   - What phase/task is currently active.
   - What tests are passing.
   - What the last agent finished.
   - The exact **Next Immediate Action** you must perform.

2. **Step 2: Check Roadmap**
   Read `.planning/ROADMAP.md` to see the broader context and upcoming milestones.

3. **Step 3: Verify Environment & Tests**
   Run the test suite:
   ```powershell
   python -m pytest tests/ -v
   ```
   All tests must pass before making changes.

4. **Step 4: Execute Work**
   Follow the architecture outlined in `.planning/ARCHITECTURE.md`.

5. **Step 5: Handover Protocol (MANDATORY)**
   Before concluding your response/turn, update `.planning/PROJECT_STATE.md`:
   - Update **Current Phase & Task**.
   - Record test results (e.g., `18 passed in 0.35s`).
   - State the **Next Immediate Action** clearly so the next agent can resume instantly.

---

## 2. Immutable Architecture Laws

1. **Zero Hardcoded Paths**:
   - NEVER hardcode absolute paths (`C:\...`, `E:\...`, `/home/...`).
   - ALWAYS use `pathlib.Path(__file__).resolve().parent`.
   - Asset loading must always resolve relative to package root.

2. **Clean Separation of Concerns**:
   - `core/` contains **PURE algorithmic code** (Huffman, LSB steganography, statistics).
   - `core/` must NEVER import `PyQt6` or any UI framework. It must run 100% headless.
   - `gui/` handles visual presentation and user interaction, importing from `core/`.

3. **Universal Unicode Handling**:
   - All text inputs must be converted to UTF-8 bytes (`text.encode('utf-8')`).
   - The Huffman tree operates on byte values `0..255`.
   - Decoded bytes are restored via `bytes.decode('utf-8')`.
   - This guarantees zero corruption for English, Bangla (`আমার সোনার বাংলা`), Arabic, Emojis (`🚀🔒`), and special characters.

4. **Lossless Images Only**:
   - Steganography MUST use lossless image formats (`PNG` or `BMP`).
   - Never save steganographic outputs as JPEG (lossy compression destroys LSB data).

---

## 3. Directory Layout

```
ICE245_HuffStego/
├── AGENT_PLAYBOOK.md               # [THIS FILE] Universal Cold-Start Protocol
├── README.md                       # Human documentation & user guide
├── requirements.txt                # Pinned dependencies
├── .gitignore                      # Git cleanliness
├── run.bat                         # Portable 1-click launcher (Windows)
├── test.bat                        # Portable 1-click test runner (Windows)
│
├── .planning/                      # Persistent state machine & design contracts
│   ├── PROJECT_STATE.md            # Live status & next steps
│   ├── ROADMAP.md                  # Milestone checklists
│   └── ARCHITECTURE.md             # Data packet formats & class contracts
│
├── core/                           # Pure algorithmic engines (0 GUI dependencies)
│   ├── __init__.py
│   ├── huffman.py                  # UTF-8 Byte-level Huffman engine + serializer
│   ├── steganography.py            # LSB image embedding & extraction
│   └── statistics.py               # Shannon entropy, compression ratio, savings
│
├── gui/                            # Modern PyQt6 Desktop GUI
│   ├── __init__.py
│   ├── main_window.py              # Main tabbed window
│   ├── encode_tab.py               # Message + cover image + embed flow
│   ├── decode_tab.py               # Stego image + extract + reveal flow
│   ├── visualizer_tab.py           # Interactive step-by-step tree visualizer
│   ├── tree_widget.py              # Custom QPainter animated tree canvas
│   ├── stats_widget.py             # Metric display cards
│   └── styles.py                   # Clean Modern Material theme
│
├── assets/                         # Assets & icons
│   ├── icons/
│   └── sample_images/              # Preloaded PNGs for quick testing
│
└── tests/                          # Automated Pytest suite
    ├── __init__.py
    ├── test_huffman.py
    ├── test_steganography.py
    └── test_statistics.py
```
