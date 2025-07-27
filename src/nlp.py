import re
import spacy
from functools import lru_cache

# Supported language codes and spaCy models
LANG_MODELS = {
    'en': 'en_core_web_sm',
    'es': 'es_core_news_sm',
    'ja': 'ja_core_news_sm',
}

@lru_cache(maxsize=3)
def get_nlp(lang_code):
    """
    Load and cache the appropriate spaCy model for the given language code.
    Defaults to English if unsupported.
    """
    model = LANG_MODELS.get(lang_code, LANG_MODELS['en'])
    try:
        return spacy.load(model)
    except Exception:
        return spacy.load(LANG_MODELS['en'])

# --- Language-aware helpers ---
def is_full_sentence(text, lang_code='en'):
    """
    Returns True if text has at least one full sentence with >2 tokens and ends with punctuation.
    Uses the appropriate spaCy model for the language.
    """
    nlp = get_nlp(lang_code)
    doc = nlp(text)
    for sent in doc.sents:
        tokens = [t.text for t in sent if not t.is_space]
        if len(tokens) > 2 and re.search(r"[.!?。！？]$", sent.text.strip()):
            return True
    return False

def is_all_caps(text, lang_code='en'):
    """
    Returns True if text is all uppercase letters (ignoring non-letters).
    Only meaningful for Latin scripts (English, Spanish).
    """
    if lang_code == 'ja':
        return False  # Not meaningful for Japanese
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)

def is_title_case(text, lang_code='en'):
    """
    Returns True if the text is in strict title case.
    Only meaningful for Latin scripts (English, Spanish).
    """
    if lang_code == 'ja':
        return False
    words = [w for w in text.split() if w.isalpha()]
    if not words:
        return False
    for w in words:
        if not (w[0].isupper() and w[1:].islower()):
            return False
    return True

def starts_with_bullet(text):
    """
    Returns True if the text starts with a bullet or dash character.
    """
    bullets = {'\u2022', '\u25cf', '-', '*', '\u25aa', '\u2023', '\u2013', '\u2014'}
    return text and text[0] in bullets

def is_short(text, max_words=12, max_chars=70, lang_code='en'):
    """
    Returns True if text is short enough to be a heading candidate.
    For Japanese, only use character count.
    """
    if lang_code == 'ja':
        return len(text) <= max_chars
    return len(text) <= max_chars and len(text.split()) <= max_words

def uppercase_ratio(text, lang_code='en'):
    """
    Returns ratio of uppercase letters to total letters.
    Only meaningful for Latin scripts.
    """
    if lang_code == 'ja':
        return 0
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0
    return sum(1 for c in letters if c.isupper()) / len(letters)

def starts_with_numbering(text):
    """
    Detect if text starts with numbering schemes like:
    1., 1.1, I., A), etc.
    """
    numbering_patterns = [
        r'^\d+(\.\d+)*',    # e.g. 1, 1.1, 1.2.3
        r'^[IVXLCDM]+\.',   # Roman numerals like I., II., III.
        r'^[A-Z]\)',        # Letter + parenthesis like A), B)
    ]
    text = text.strip()
    for pat in numbering_patterns:
        if re.match(pat, text):
            return True
    return False
