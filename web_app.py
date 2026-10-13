"""
web_app.py
Piggyback Web Workbench — Streamlit Web Interface
Deployable to Cloud (Streamlit Community Cloud, Docker, VPS, or custom domain hm.rxxeron.iam.bd)
"""

import io
from pathlib import Path
from PIL import Image
import numpy as np
import streamlit as st

from core.huffman import HuffmanEngine
from core.steganography import StegoEngine
from core.statistics import StatsEngine

# Page Configuration
st.set_page_config(
    page_title="Piggyback — Invisible Payload Carrier",
    page_icon="🎒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Contrast Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .metric-val {
        font-size: 20px;
        font-weight: 700;
        color: #38BDF8;
        font-family: monospace;
    }
    .metric-lbl {
        font-size: 11px;
        color: #94A3B8;
        text-transform: uppercase;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.title("Piggyback — Invisible Payload Carrier & Algorithm Workbench")
st.caption("ICE245 Algorithm Design | Universal UTF-8 Huffman Engine & 24-bit Lossless LSB Steganography")

# Sidebar
with st.sidebar:
    st.header("Project Info")
    st.markdown("""
    **Course:** ICE245 Algorithm Design  
    **Lab 4:** Greedy Huffman Coding  
    **Lab 13:** Mini Project Showcase  
    
    ---
    **Modules:**
    - Universal Byte-Level Huffman (0..255)
    - 24-bit RGB LSB Digital Steganography
    - Shannon Entropy & Optimality Bounds
    - 128x Difference Heatmap & PSNR Proof
    """)
    st.info("Deployed for host: `hm.rxxeron.iam.bd`")

tabs = st.tabs([
    "Standard Huffman (Text)",
    "Steganography: Embed Carrier",
    "Steganography: Extract Payload",
    "Priority Queue Step-by-Step"
])

# ==========================================
# TAB 1: STANDARD HUFFMAN (TEXTBOOK MODE)
# ==========================================
with tabs[0]:
    st.subheader("1. Standard Huffman Coding (Lab 4 Textbook Mode)")
    st.write("Pure text compression. Takes plaintext, computes frequencies, builds min-heap binary tree, and outputs bitstream.")

    col1, col2 = st.columns([1, 1])

    with col1:
        preset = st.selectbox(
            "Load Quick Preset:",
            ["Custom Input", "ABRACADABRA", "The greedy choice property ensures optimal prefix codes.", "আমাদের অ্যালগরিদম সফলভাবে বাংলায় কাজ করছে।"]
        )
        default_val = "BEEP BOOP BEER! Huffman coding achieves optimal prefix codes." if preset == "Custom Input" else preset
        user_text = st.text_area("Plaintext Input Payload:", value=default_val, height=120)

        if st.button("Compress (Encode Payload → Bitstream)", type="primary"):
            if not user_text.strip():
                st.error("Please enter plaintext to compress.")
            else:
                engine = HuffmanEngine()
                tree_bits, payload_bits = engine.encode_text(user_text)
                stats = StatsEngine.evaluate(user_text, tree_bits, payload_bits)
                code_table = engine.get_code_table_display()

                st.session_state["text_engine"] = engine
                st.session_state["text_payload_bits"] = payload_bits
                st.session_state["text_tree_bits"] = tree_bits
                st.session_state["text_stats"] = stats
                st.session_state["text_codes"] = code_table
                st.session_state["orig_text"] = user_text

    with col2:
        if "text_payload_bits" in st.session_state:
            st.success("Encoding Complete!")
            st.text_area(
                "Encoded Bitstream (0s and 1s):",
                value=st.session_state["text_payload_bits"],
                height=120
            )

            # Metrics row
            stats = st.session_state["text_stats"]
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Compression Ratio", f"{stats['compression_ratio']}x")
            m2.metric("Space Savings", f"{stats['space_savings_pct']}%")
            m3.metric("Entropy H(X)", f"{stats['shannon_entropy']:.2f} b/B")
            m4.metric("Efficiency", f"{stats['shannon_efficiency_pct']:.1f}%")

            # Decompress in-place verification
            st.markdown("---")
            if st.button("Decompress Bitstream → Recover Plaintext"):
                engine = st.session_state["text_engine"]
                bits = st.session_state["text_payload_bits"]
                recovered = engine.decode_to_text(bits, engine.root)
                st.info(f"**Recovered Payload:** `{recovered}`")
                if recovered == st.session_state["orig_text"]:
                    st.success("Mathematical Lossless Roundtrip Verified (100% Fidelity)")

    # Display Codebook Table
    if "text_codes" in st.session_state:
        st.markdown("### Prefix-Free Codebook")
        st.dataframe(
            st.session_state["text_codes"],
            column_config={
                "byte": "Byte (Hex)",
                "char": "Symbol Representation",
                "code": "Prefix Code",
                "length": "Bit Length"
            },
            hide_index=True,
            use_container_width=True
        )

# ==========================================
# TAB 2: STEGANOGRAPHY: EMBED CARRIER
# ==========================================
with tabs[1]:
    st.subheader("2. Invisible Carrier Steganography: Embed (Lab 13 Showcase)")
    st.write("Piggybacks compressed Huffman payload directly onto the least significant bits of a lossless 24-bit PNG carrier.")

    col_emb1, col_emb2 = st.columns([1, 1])

    with col_emb1:
        stego_msg = st.text_area(
            "Secret Payload Message:",
            value="Piggyback confidential message: আমাদের গোপন বার্তা সফলভাবে ছবিতে লুকানো হয়েছে।",
            height=100
        )
        uploaded_cover = st.file_uploader("Upload Carrier Image (PNG / BMP):", type=["png", "bmp"])

        # Default sample image if none uploaded
        sample_path = Path(__file__).resolve().parent / "assets" / "sample_images" / "cover_landscape.png"
        cover_image = None

        if uploaded_cover is not None:
            cover_image = Image.open(uploaded_cover).convert("RGB")
            st.image(cover_image, caption="Uploaded Carrier", use_container_width=True)
        elif sample_path.exists():
            st.info("Using default landscape carrier sample.")
            cover_image = Image.open(sample_path).convert("RGB")
            st.image(cover_image, caption="Default Sample Carrier", use_container_width=True)

    with col_emb2:
        if cover_image is not None and st.button("Embed Payload into Carrier", type="primary"):
            if not stego_msg.strip():
                st.error("Please enter a secret message to embed.")
            else:
                # Save temp cover
                temp_cover_path = Path("temp_carrier.png")
                cover_image.save(temp_cover_path, "PNG")

                huff = HuffmanEngine()
                tree_bits, payload_bits = huff.encode_text(stego_msg)

                stego = StegoEngine()
                out_path = Path("temp_stego.png")
                meta = stego.embed(str(temp_cover_path), tree_bits, payload_bits, str(out_path))
                metrics = stego.compute_metrics(str(temp_cover_path), str(out_path))
                diff_heatmap = stego.compute_diff_heatmap(str(temp_cover_path), str(out_path))

                st.success("Embedding Succeeded!")
                q1, q2 = st.columns(2)
                q1.metric("PSNR Quality (dB)", f"{metrics['psnr_db']} dB", help="PSNR > 50 dB guarantees human invisibility")
                q2.metric("MSE Variance", f"{metrics['mse']:.5f}")

                st.image(str(out_path), caption="Stego Carrier Image (Carrying Secret Payload)", use_container_width=True)

                # Download button
                with open(out_path, "rb") as f:
                    st.download_button(
                        label="Download Stego Carrier PNG",
                        data=f,
                        file_name="piggyback_stego.png",
                        mime="image/png"
                    )

                # Difference Heatmap
                st.markdown("### Forensic Inspection: 128x Difference Gain")
                st.image(diff_heatmap, caption="128x Amplified Modified LSB Pixels", use_container_width=True)

# ==========================================
# TAB 3: STEGANOGRAPHY: EXTRACT PAYLOAD
# ==========================================
with tabs[2]:
    st.subheader("3. Steganographic Extraction (Lab 13)")
    st.write("Extracts pre-order serialized tree header, reconstructs prefix tree, and recovers secret payload.")

    ext_upload = st.file_uploader("Upload Stego Carrier Image to Inspect (.png):", type=["png"], key="extract_uploader")

    if ext_upload is not None:
        temp_ext_path = Path("temp_inspect.png")
        Image.open(ext_upload).save(temp_ext_path, "PNG")

        stego_eng = StegoEngine()
        # Watermark check
        flat = np.array(Image.open(temp_ext_path).convert("RGB"), dtype=np.uint8).flatten()
        magic = "".join(str(b & 1) for b in flat[:16])

        if magic == stego_eng.MAGIC_SIGNATURE:
            st.success("AUTHENTICATED: Valid Piggyback Watermark Header (0x5354) Found!")
        else:
            st.warning("WARNING: Missing Piggyback Magic Header (0x5354).")

        if st.button("Extract & Decode Secret Payload", type="primary"):
            try:
                tree_bits, payload_bits = stego_eng.extract(str(temp_ext_path))
                rec_root, _ = HuffmanEngine.deserialize_tree(tree_bits)
                h_eng = HuffmanEngine()
                extracted_text = h_eng.decode_to_text(payload_bits, rec_root)

                st.subheader("Recovered Plaintext Payload:")
                st.code(extracted_text)

                st.caption(f"Extracted payload length: {len(extracted_text):,} characters | Tree header: {len(tree_bits)} bits")
            except Exception as e:
                st.error(f"Extraction failed: {str(e)}")

# ==========================================
# TAB 4: PRIORITY QUEUE STEP-BY-STEP
# ==========================================
with tabs[3]:
    st.subheader("4. Priority Queue Greedy Merge Simulation")
    st.write("Step-by-step telemetry of min-heap extractions and pairwise forest merges.")

    sim_text = st.text_input("Simulation Alphabet:", value="ICE245 ALGORITHMS")
    if sim_text:
        sim_eng = HuffmanEngine()
        sim_eng.build_tree_from_bytes(sim_text.encode("utf-8"))

        step_idx = st.slider("Select Greedy Merge Step:", 0, len(sim_eng.build_history) - 1, len(sim_eng.build_history) - 1)
        step_data = sim_eng.build_history[step_idx]

        st.info(f"**Step {step_idx}:** {step_data['description']}")

        remaining = step_data.get("remaining", [])
        st.write(f"**Min-Heap State ({len(remaining)} elements remaining):**")
        st.write(" -> ".join([r['label'] for r in remaining]))
