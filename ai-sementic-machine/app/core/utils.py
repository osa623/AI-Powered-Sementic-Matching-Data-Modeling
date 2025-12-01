import re

def clean_text(text: str) -> str:
    """Basic text cleaning for Singlish/English inputs"""
    text = text.lower().strip()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text