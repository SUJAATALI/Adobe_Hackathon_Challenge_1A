# PDF Processor

A Python-based tool to extract titles, headings, and outlines from PDF files using **PyMuPDF** and **spaCy**.  
Supports English, Spanish, and Japanese documents.  
Can be run locally or in Docker for reproducible, isolated processing.

---

## ✨ Features

- Extracts text blocks and font metadata from PDFs
- Automatically detects document language
- Identifies headings and outlines using NLP
- Outputs results as structured JSON
- Docker-ready for portable deployment
- CLI support for custom input/output paths

---

## 📁 Folder Structure

```
final 1A/
│
├── src/
│   ├── process_pdfs.py   # Main script
│   └── nlp.py            # NLP utilities
│
├── sample_dataset/
│   ├── pdf/              # Input PDF files go here
│   └── outputs/          # JSON output files are saved here
│
├── Dockerfile
└── requirements.txt
```

---

## 🚀 Quick Start


### 🐳 Run with Docker

#### 1. Build the Docker Image

```bash
docker build --platform linux/amd64 -t pdf-processor .
```

#### 2. Run the Processor in Docker
##Recommended:
```bash
python src/process_pdfs.py --input sample_dataset/pdf --output sample_dataset/outputs
```

```bash
docker run --rm \
  -v ${PWD}/sample_dataset/pdf:/app/input:ro \
  -v ${PWD}/sample_dataset/outputs:/app/output \
  --network none \
  pdf-processor \
  --input /app/input --output /app/output
```

> 💡 On Windows PowerShell, use `${PWD}` instead of `$PWD`.

---


### 🐍 Run Locally (No Docker)

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Install spaCy Language Models

```bash
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm
python -m spacy download ja_core_news_sm
```

> 💡 You only need to install the models for the languages you're working with.

#### 3. Add Your PDFs

Place your `.pdf` files into the `sample_dataset/pdf/` folder.

#### 4. Run the Processor

```bash
python src/process_pdfs.py --input sample_dataset/pdf --output sample_dataset/outputs
```

---



## 📤 Output Format

For each PDF processed, a corresponding JSON file is created. Each file contains:

```json
{
  "title": "Application form for grant of LTC advance",
  "outline": [
    {
      "text": "Section 1: Overview",
      "level": 1,
      "page": 0
    }
  ],
  "language": "en"
}
```

---

## 🧠 Dependencies

- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) – PDF parsing and text extraction
- [spaCy](https://spacy.io/) – NLP tasks: tokenization, sentence splitting
- [langdetect](https://pypi.org/project/langdetect/) – Language detection

---

## 🛠 Troubleshooting

- Ensure PDFs are placed inside `sample_dataset/pdf/`
- Output directory `sample_dataset/outputs/` must exist (or will be created)
- If using Docker, check file permission issues on Linux
- Make sure spaCy language models are downloaded before running

---

## 📝 License

MIT License

---

## 🙌 Credits

- PyMuPDF developers for fast PDF parsing  
- spaCy community for robust NLP tools  
- This project was developed as part of a document intelligence challenge
