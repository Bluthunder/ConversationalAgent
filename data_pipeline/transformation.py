# ========================================================tra======================
# Date: 21-06-2025
# File: pipeline/transformation.py
# Description: Functions to create final model-ready datasets.
# NOTE: This assumes the data has been annotated and exported from a tool like Label Studio.
# ==============================================================================
import pandas as pd
from sklearn.model_selection import train_test_split
from ..utils.s3_utils import load_config, save_dataframe_to_s3

def transform_for_nlu(annotated_df):
    """Transforms annotated data into a format for BERT (NLU) fine-tuning."""
    print("Transforming data for NLU (BERT)...")
    # This function expects columns from Label Studio like:
    # 'clean_text', 'intent_labels', 'sentiment_label', 'ner_annotations'
    # The exact column names depend on your Label Studio setup.
    
    # Placeholder logic:
    nlu_data = annotated_df[['clean_text', 'intent_labels', 'sentiment_label', 'ner_annotations']].copy()
    nlu_data = nlu_data.rename(columns={
        'clean_text': 'text',
        'intent_labels': 'intents',
        'sentiment_label': 'sentiment',
        'ner_annotations': 'entities'
    })
    
    print("NLU transformation complete.")
    return nlu_data

def transform_for_nlg(annotated_df):
    """Transforms annotated data into a format for SLM (NLG) fine-tuning."""
    print("Transforming data for NLG (SLM)...")
    # This function expects columns like 'clean_text' and 'ideal_response'
    
    # Constructing the instruction and context
    def create_instruction(row):
        # A more sophisticated function could generate more dynamic instructions
        return f"A customer has a query about {row['intent_labels']}. They are feeling {row['sentiment_label']}. Draft a helpful response."

    annotated_df['instruction'] = annotated_df.apply(create_instruction, axis=1)
    
    nlg_data = annotated_df[['instruction', 'clean_text', 'ideal_response']].copy()
    nlg_data = nlg_data.rename(columns={'clean_text': 'context', 'ideal_response': 'response'})

    print("NLG transformation complete.")
    return nlg_data

def split_and_save_datasets(df, transform_func, data_version, output_prefix, s3_fs):
    """Applies a transformation, splits into train/validation, and saves to S3."""
    config = load_config()
    processed_bucket = config['s3_buckets']['processed_data']

    transformed_df = transform_func(df)
    
    train_df, val_df = train_test_split(transformed_df, test_size=0.2, random_state=42)
    
    save_dataframe_to_s3(train_df, processed_bucket, f"{data_version}/{output_prefix}/training.jsonl", s3_fs)
    save_dataframe_to_s3(val_df, processed_bucket, f"{data_version}/{output_prefix}/validation.jsonl", s3_fs)


