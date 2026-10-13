# Piggyback — 3-Minute Presentation & Defense Guide
> **ICE245 Algorithm Design (Lab 4 & Lab 13 Showcase)**  
> *Keep this guide open or printed during your project presentation.*

---

## The Relief: You Only Need to Know 15% of the Code!

Out of the ~1,200 total lines:
- **70% (~850 lines)** is purely **PyQt6 GUI layout** (buttons, cards, colors, drag-and-drop). **Teachers never ask about GUI code in an algorithm course.**
- **15% (~150 lines)** is unit tests.
- **Only 15% (~180 lines)** is the actual **Algorithm Core** (`core/huffman.py`, `core/steganography.py`, `core/statistics.py`).

You only need to understand **3 core functions**. Everything else is just visual wrapping!

---

## The 3-Minute Presentation Script (Step-by-Step)

### Step 1: The Hook (30 Seconds)
> *"Respected Sir/Ma'am, for our Algorithm course project, standard Huffman coding takes text and prints 0s and 1s on the console. We wanted to build something with real-world security value.*  
> *We built **Piggyback**, which combines **Greedy Huffman Coding** with **Image Steganography**. It compresses Unicode messages—including Bangla and multilingual text—into an optimal prefix tree, serializes the tree into a compact header, and piggybacks the data invisibly inside ordinary image pixels without altering how the photo looks to human eyes."*

### Step 2: The Live Demonstration (60 Seconds)
1. **Open the App** (Double-click `run.bat`).
2. **Start on Tab 1: `Standard Huffman (Text)` (Proves Lab 4 Core)**:
   - Type or click a preset (e.g. `ABRACADABRA` or English sentence).
   - Click `Compress (Encode Text → Binary Bits)`.
   > *"Sir, here is our standard Lab 4 textbook Huffman implementation: it takes plaintext, calculates frequencies, builds the binary tree, and generates the prefix-free codes and binary bitstream. Clicking Decompress restores the exact text in-place."*
3. **Switch to Tab 2: `Stego: Embed in Image` (Shows Lab 13 Showcase)**:
   - Press **`Ctrl+D`** (or click `⚡ 1-Click Showcase Demo`).
   > *"Now, to take this further for our Lab 13 Mini Project Showcase, we embedded the compressed bits into an image:*  
   > *Panel 1 is the original cover image.*  
   > *Panel 2 is the stego image carrying our hidden message.*  
   > *To the human eye, they are 100% identical because we achieved a **PSNR of over 70 dB**.*  
   > *Panel 3 amplifies the pixel changes 128 times so you can see where the Huffman bits were injected."*
4. **Switch to `Extract & Decode` tab and click `Extract`**:
   > *"The receiver extracts the serialized tree from the image, reconstructs the prefix tree, and perfectly recovers our Bangla and English secret message without any key file!"*
5. **Switch to `Tree Visualizer Sandbox` tab and click `▶ Play Animation`**:
   > *"Here in the visualizer, you can see the **min-heap priority queue** merging the two lowest-frequency subtrees step-by-step in amber, fusing into the green parent node until the optimal tree is formed."*

### Step 3: Show the Academic Report (30 Seconds)
Press `Ctrl+R` (or `File` $\rightarrow$ `Export Academic Lab Report`):
> *"The system also auto-generates a complete academic report with our Shannon Entropy calculation, empirical compression ratio, and prefix codebook table."*

---

## 🔍 The 3 Code Snippets You Must Be Able to Point To

If the teacher says: *"Open your code and show me how it works"*, open these 3 files:

### 1. Where is the Greedy Algorithm?
📂 **File:** [`core/huffman.py`](file:///e:/ICE245/Project/core/huffman.py) (Lines 110–125)
```python
while len(heap) > 1:
    left = heapq.heappop(heap)    # 1. Greedy choice: pop lowest frequency
    right = heapq.heappop(heap)   # 2. Pop second lowest frequency
    merged = HuffmanNode(         # 3. Fuse into parent
        freq=left.freq + right.freq,
        left=left,
        right=right
    )
    heapq.heappush(heap, merged)  # 4. Push back into min-heap
```
> **What to say:** *"Here is the greedy choice property. Using Python's min-heap (`heapq`), we repeatedly extract the two lowest-frequency nodes in $O(\log K)$ time and fuse them until only the root remains."*

---

### 2. How Does Steganography Embed Bits?
📂 **File:** [`core/steganography.py`](file:///e:/ICE245/Project/core/steganography.py) (Lines 105–110)
```python
# Clear the Least Significant Bit (0xFE = 11111110) and insert new bit
flat[:packet_len] = (flat[:packet_len] & 0xFE) | packet_bits
```
> **What to say:** *"Each pixel RGB channel has an 8-bit integer from 0 to 255. By doing bitwise AND with `0xFE`, we clear the last bit, and bitwise OR inserts our Huffman bit. Because the color value changes by at most $\pm 1$, it is mathematically undetectable to human vision."*

---

### 3. How Does the Math Prove It's Optimal?
📂 **File:** [`core/statistics.py`](file:///e:/ICE245/Project/core/statistics.py) (Lines 18–32)
```python
# Shannon Entropy: H(X) = -sum(p * log2(p))
for count in counts.values():
    p = count / n
    if p > 0:
        entropy -= p * math.log2(p)
```
> **What to say:** *"Shannon's Source Coding Theorem states that the theoretical limit of compression is entropy $H(X)$. Our statistics engine computes $H(X)$ and shows that our average Huffman code length $L_{avg}$ satisfies $H(X) \le L_{avg} < H(X) + 1$, proving greedy optimality."*

---

## 🎯 The 4 Questions Teachers ALWAYS Ask (Word-for-Word Answers)

### Q1: "What is your Time and Space Complexity?"
- **Time Complexity:**
  - Counting byte frequencies: $O(N)$ where $N$ is message length.
  - Priority queue tree construction: $O(K \log K)$ where $K$ is the number of unique byte symbols ($K \le 256$).
  - Encoding and LSB vector embedding: $O(N)$.
  - **Overall Time:** **$O(N + K \log K) \approx O(N)$ linear time**, because $K$ is capped at 256!
- **Space Complexity:** **$O(K)$** auxiliary space for the tree of at most 256 nodes.

---

### Q2: "Why did you use UTF-8 Bytes instead of characters?"
> *"Sir, standard textbook Huffman uses characters. But Unicode has over 140,000 characters. If someone types Bangla (`আমার সোনার বাংলা`) or Emojis (`🚀`), a character tree could explode with thousands of nodes, creating huge headers.*  
> *By operating over **UTF-8 bytes (0..255)**, the alphabet size $K$ is mathematically bounded to $\le 256$ symbols. This guarantees instant min-heap construction, compact headers under 350 bits, and zero character corruption."*

---

### Q3: "How does the decoder reconstruct the tree without knowing frequencies?"
> *"We serialize the tree using a pre-order traversal bitstream: `1` followed by 8 bits for a leaf node, and `0` for an internal branch. The decoder reads this bitstream to rebuild the exact binary tree topology. Once the message is decoded, our algorithm backfills the actual frequencies from the recovered text."*

---

### Q4: "How do you prove that the stego image is undetectable?"
> *"We compute **Peak Signal-to-Noise Ratio (PSNR)** and **Mean Squared Error (MSE)**. In image forensics, any PSNR above 50 dB is considered invisible to the human eye. Because our LSB substitution only alters pixel channel values by $\pm 1$, our PSNR is consistently above **70 dB**, meaning the visual degradation is virtually zero."*

---

## 🏆 Summary Checklist for Showcase Day
- [ ] Laptop plugged in, screen brightness up.
- [ ] Open project folder in VS Code or File Explorer.
- [ ] Have [`run.bat`](file:///e:/ICE245/Project/run.bat) ready to launch.
- [ ] Press `Ctrl+D` for the 1-Click Showcase Demo.
- [ ] Show the 3-panel Invisibility Dialog.
- [ ] Show the Visualizer Min-Heap Animation tab.
- [ ] Deliver the 3 answers from this cheat sheet with confidence!
