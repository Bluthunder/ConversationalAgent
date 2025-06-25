import re
import pandas as pd # For type hinting and Dask map_partitions compatibility
from config import load_config

def anonymize_text(text, patterns):
    """
    Replaces PII (Personally Identifiable Information) in text based on provided regex patterns.
    This function is generic and can be used for any text string.
    """
    if not isinstance(text, str):
        return text
    for pii_type, pattern in patterns.items():
        # Using uppercase placeholders (e.g., [USERIDMENTION]) for clarity
        text = re.sub(pattern, f'[{pii_type.upper().replace("_", "")}]', text)
    return text

def clean_text_series(text_series):
    """
    Applies comprehensive text cleaning and anonymization to a Pandas Series of texts.
    Designed to be used with Dask's map_partitions, operating on each partition.
    """
    config = load_config()
    pii_patterns = config['pii_patterns']
    
    # Pre-compile common regex patterns for efficiency
    agent_mention_pattern = re.compile(r'@(sprintcare|Ask_Spectrum|(?![0-9]))\w+', flags=re.IGNORECASE)
    url_pattern = re.compile(r'https?://\S+')
    whitespace_pattern = re.compile(r'\s+')

    def _clean_single_text(text):
        if not isinstance(text, str):
            return text
        
        # 1. Apply PII anonymization using the centralized patterns
        anonymized_text = anonymize_text(text, pii_patterns)

        # 2. General cleaning on the anonymized text
        # Remove Twitter handles that are not numerical user IDs (e.g., @sprintcare, @Ask_Spectrum)
        # Note: @\d+ would already be handled by anonymize_text as [USERIDMENTION]
        cleaned_text = agent_mention_pattern.sub('', anonymized_text)
        # Remove URLs
        cleaned_text = url_pattern.sub('', cleaned_text)
        # Remove multiple spaces and strip leading/trailing whitespace
        cleaned_text = whitespace_pattern.sub(' ', cleaned_text).strip()
        
        return cleaned_text

    # Apply the cleaning function to each text in the Series
    return text_series.apply(_clean_single_text)

