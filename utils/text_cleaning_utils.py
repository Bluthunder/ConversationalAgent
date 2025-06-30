import re
import emoji

def remove_with_pattern(text: str, pattern_str: str) -> str:
    pattern = re.compile(pattern_str)
    return pattern.sub("", text).strip()

def remove_emojis(text: str) -> str:
    return emoji.replace_emoji(text, replace="")

def to_lowercase(text: str) -> str:
    return text.lower()

def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def clean_text(text: str, config: dict) -> str:
    """
    Cleans a single text string based on config.

    Args:
        text (str): Input text to clean.
        config (dict): Preprocessing config with optional keys:
            - remove_mentions (bool)
            - remove_urls (bool)
            - remove_emojis (bool)
            - lowercase (bool)
            - mention_patterns (str)
            - url_patterns (str)

    Returns:
        str: Cleaned text.
    """
    if not isinstance(text, str):
        return text

    if config.get("remove_mentions", False):
        mention_pattern = config.get("mention_patterns", r"@\w+")
        text = remove_with_pattern(text, mention_pattern)

    if config.get("remove_urls", False):
        url_pattern = config.get("url_patterns", r"http\S+|www\S+")
        text = remove_with_pattern(text, url_pattern)

    if config.get("remove_emojis", False):
        text = remove_emojis(text)

    if config.get("lowercase", False):
        text = to_lowercase(text)

    text = normalize_whitespace(text)

    return text

def is_too_short(text: str, min_words: int = 3) -> bool:
    return len(text.split()) < min_words
