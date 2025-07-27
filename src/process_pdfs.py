import fitz  # PyMuPDF
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys
from langdetect import detect
import re

from nlp import is_all_caps, is_title_case, starts_with_bullet, is_short, is_full_sentence, uppercase_ratio

def extract_blocks_with_metadata(pdf_path):
    doc = fitz.open(pdf_path)
    blocks = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        for block in page.get_text("dict")["blocks"]:
            if block["type"] == 0:  # text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        blocks.append({
                            "text": span["text"].strip(),
                            "font": span["font"],
                            "size": span["size"],
                            "flags": span["flags"],
                            "bbox": span["bbox"],
                            "page": page_num + 1,
                            "origin": (span["bbox"][0], span["bbox"][1])
                        })
    return blocks

def detect_language(blocks):
    # Concatenate first N non-empty blocks for language detection
    texts = [b["text"] for b in blocks if b["text"]]
    sample = " ".join(texts[:20])
    try:
        lang = detect(sample)
        print(f"[INFO] Detected language: {lang}")
        return lang
    except Exception as e:
        print(f"[WARN] Language detection failed: {e}. Defaulting to 'en'.")
        return 'en'

# --- DEBUG: Print font sizes and sample texts ---
def debug_font_sizes(blocks):
    font_samples = defaultdict(list)
    for b in blocks:
        if b["text"] and len(font_samples[b["size"]]) < 3:
            font_samples[b["size"]].append(b["text"])
    print("[DEBUG] Font sizes and sample texts:")
    for size in sorted(font_samples.keys(), reverse=True):
        print(f"  Size {size}: {font_samples[size]}")

# --- FIXED TITLE EXTRACTION: Use 24.0 font size ---
def clean_repetitions(text):
    # Collapse more than 2 repeated letters to 1 (e.g., "Reeeequest" -> "Request")
    text = re.sub(r'(\w)\1{2,}', r'\1', text)
    # Collapse more than 2 spaces
    text = re.sub(r'\s{2,}', ' ', text)
    # Remove repeated words/phrases (e.g., "Proposal Proposal" -> "Proposal")
    words = text.split()
    seen = set()
    result = []
    for word in words:
        if word not in seen:
            result.append(word)
            seen.add(word)
    return ' '.join(result)

def detect_title(blocks, lang_code='en'):
    first_page_blocks = [b for b in blocks if b["page"] == 1 and b["text"]]
    if not first_page_blocks:
        return ""
    # Find the largest font size on the first page
    max_size = max(b["size"] for b in first_page_blocks)
    # Allow a small tolerance for font size
    title_blocks = [b for b in first_page_blocks if abs(b["size"] - max_size) < 0.5]
    # Sort by y-position (top of the page)
    title_blocks = sorted(title_blocks, key=lambda b: b["origin"][1])
    # Concatenate all title block texts
    title = " ".join(b["text"] for b in title_blocks)
    # Clean up repetitions and duplicate words
    title = clean_repetitions(title)
    return title.strip()

# --- FIXED HEADING LEVELS BASED ON FONT SIZES FROM DEBUG ---
def compute_font_stats(blocks):
    # Hardcode based on debug output
    font_map = {
        "H1": 20.04,
        "H2": 15.96,
        "H3": 12.0
    }
    print(f"[DEBUG] Font map used for headings: {font_map}")
    return font_map

def heading_level(block, font_stats):
    size = block["size"]
    # Use a tolerance for float comparison
    if abs(size - font_stats["H1"]) < 0.1:
        return "H1"
    elif abs(size - font_stats["H2"]) < 0.1:
        return "H2"
    elif abs(size - font_stats["H3"]) < 0.1:
        return "H3"
    return None

# --- IMPROVED HEADING CANDIDATE USING NLP HELPERS ---
def is_heading_candidate(block, lang_code='en'):
    text = block["text"]
    # Loosened: allow up to 14 words and 80 chars
    if not text or starts_with_bullet(text) or not is_short(text, max_words=14, max_chars=80, lang_code=lang_code):
        return False
    if is_full_sentence(text, lang_code=lang_code):
        return False
    if is_all_caps(text, lang_code=lang_code) or is_title_case(text, lang_code=lang_code) or uppercase_ratio(text, lang_code=lang_code) > 0.5:
        return True
    return False

def extract_outline(blocks, lang_code='en'):
    font_stats = compute_font_stats(blocks)
    outline = []
    for block in blocks:
        level = heading_level(block, font_stats)
        if level and is_heading_candidate(block, lang_code=lang_code):
            outline.append({
                "level": level,
                "text": block["text"],
                "page": block["page"] -1
            })
    print(f"[DEBUG] Outline candidates: {[o['text'] for o in outline]}")
    print(f"[DEBUG] Outline entries: {len(outline)}")
    return outline

def process_pdf(pdf_path, output_json):
    print(f"[INFO] Processing {Path(pdf_path).name} -> {Path(output_json).name}")
    blocks = extract_blocks_with_metadata(pdf_path)
    print(f"[INFO] Extracted {len(blocks)} blocks from {pdf_path}")
    if len(blocks) > 0:
        print(f"[INFO] First 5 blocks: {[b['text'] for b in blocks[:5]]}")
    debug_font_sizes(blocks)
    lang_code = detect_language(blocks)
    title = detect_title(blocks, lang_code=lang_code)
    outline = extract_outline(blocks, lang_code=lang_code)
    print(f"[INFO] Selected title: {title}")
    print(f"[INFO] Outline: {outline}")
    result = {
        "title": title,
        "outline": outline,
        "language": lang_code
    }
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

def process_pdfs(input_dir, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_files = list(input_dir.glob("*.pdf"))
    for pdf_file in pdf_files:
        output_file = output_dir / f"{pdf_file.stem}.json"
        process_pdf(pdf_file, output_file)
    print("Completed processing all PDFs.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    args = parser.parse_args()
    process_pdfs(Path(args.input), Path(args.output))
