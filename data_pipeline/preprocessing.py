# ==============================================================================
# Date: 21-06-2025
# File: pipeline/preprocessing.py
# Description: Functions for data cleaning and anonymization.
# ==============================================================================
import pandas as pd
import re
from ..utils.s3_utils import load_config

# def anonymize_text(text, patterns):
#     """Replaces PII in text based on regex patterns."""
#     if not isinstance(text, str):
#         return text
#     for pii_type, pattern in patterns.items():
#         text = re.sub(pattern, f'[{pii_type}]', text)
#     return text


# def preprocess_twcs(twcs_df):
#     """Cleans and prepares the TWCS DataFrame."""
#     config = load_config()
#     pii_patterns = config['pii_patterns']
    
#     print("Preprocessing TWCS data...")
#     # Assuming the main text is in a column named 'text'
#     # You might need to filter for first-turn customer tweets
#     twcs_df = twcs_df.rename(columns={'text': 'original_text'})

#     # For non-RCIS data, the 'clean_text' is just the cleaned original text
#     twcs_df['clean_text'] = twcs_df['original_text'].apply(lambda x: anonymize_text(x, pii_patterns))
    
#     twcs_df['source'] = 'twcs'
    
#     final_df = twcs_df[['original_text', 'clean_text', 'source']].copy()
#     print("TWCS preprocessing complete.")
#     return final_df


