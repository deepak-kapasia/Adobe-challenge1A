# Adobe-challenge1A

# PDF Outline Extractor – Round 1A Submission

##  Challenge: Understand Your Document  
**Theme**: *Connecting the Dots Through Docs*

This project is a solution for Round 1A of the Adobe India Hackathon 2025. The goal is to **automatically extract the Title and a hierarchical structure of Headings (H1, H2, H3)** from any input PDF — enabling smarter document understanding.


## 🚀 Approach

Our pipeline processes PDF files using the following steps:

1. **Text and Font Extraction**:  
   Using `PyMuPDF`, we extract all text spans along with font size, font flags, bounding boxes, and page numbers.

2. **Title Detection**:  
   The title is detected from the first page using heuristics such as:
   - Largest font size
   - Layout positioning
   - Duplicate text filtering
   - Subtitles grouped by vertical/horizontal proximity

3. **Heading Detection**:  
   Headings are classified based on:
   - Font size hierarchy (second-largest = H1, third = H2, etc.)
   - Pattern matching (`1.`, `1.1`, `Chapter 2`, `ALL CAPS`, etc.)
   - Grouping by position and font style
   - Filtering out long blocks that resemble body text

4. **Output Generation**:  
   Produces a JSON output in the expected format with the detected title and heading structure including:
   - `"level"`: H1/H2/H3
   - `"text"`: heading text
   - `"page"`: page number



## 📚 Libraries & Tools Used

- [`PyMuPDF`](https://pymupdf.readthedocs.io/) (fitz) – for PDF parsing with fonts and layout.
- [`pdfplumber`](https://github.com/jsvine/pdfplumber) – optional layout support.
- `regex` – for matching heading patterns.
- `Python 3.9+` – implementation language.
- **No external APIs or internet dependencies** used. Works entirely offline.



## 🐳 How to Build and Run (Dockerized)

### 🔨 Build the Docker Image

```bash
docker build --platform linux/amd64 -t pdf-processor .
````

### ▶️ Run the Container

```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-processor
```

> 📂 Place your input PDFs inside the `input/` directory.
> 📄 For each `filename.pdf`, a corresponding `filename.json` will be created inside `output/`.



## 📁 Directory Structure

```
.
├── Dockerfile
├── main.py
├── requirements.txt
├── README.md
├── input/              # Place PDFs here
├── output/             # JSON outputs appear here
└── src/
    ├── pdf_processor.py
    └── heading_detector.py
```



## ✅ Compliance with Challenge Constraints

| Constraint             | Compliant                |
| ---------------------- | ------------------------ |
| ⏱ Execution Time ≤ 10s | ✅ Yes                    |
| 💾 Model Size ≤ 200MB  | ✅ Yes (no ML model used) |
| 🌐 Offline Execution   | ✅ Fully Offline          |
| ⚙️ CPU-Only (amd64)    | ✅ Compatible             |
| 🛠 Dockerized          | ✅ Fully Dockerized       |



## 📦 Output Format Example

```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
```


## 📝 Notes

* This solution is modular and can be enhanced further by:

  * Adding multilingual heading detection (e.g., Japanese)
  * Integrating a lightweight ML classifier for better heading classification
  * Improving font-style-based detection using `pdfplumber` layout heuristics

