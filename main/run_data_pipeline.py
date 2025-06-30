# ==============================================================================
# Date: 21-06-2025
# File: scripts/run_pipeline_locally.py
# Description: A script to run the preprocessing steps locally.
# To run: python scripts/run_pipeline_locally.py
# ==============================================================================

import sys
import os
from datetime import datetime
import pandas as pd

# Add project root to path to allow imports
sys.path.append(os.getcwd())

from utils.s3_utils import get_s3_fs, save_dataframe_to_s3
from utils.config_loader import load_config
from core.dataset_factory import DatasetFactory


def run_preprocessing_pipeline():
    """Executes the data acquisition and preprocessing steps."""
    s3_fs = get_s3_fs()
    config = load_config()

    # Initialize factory
    factory = DatasetFactory(config=config, fs=s3_fs)

    # Load and preprocess all datasets defined in config
    all_datasets = factory.load_all()

    # Combine all datasets into one for annotation or fine-tuning
    # combined_df = pd.concat(all_datasets.values(), ignore_index=True)

    # Save to staging area
    today = datetime.now().strftime("%Y-%m-%d")
    staging_bucket = config['s3_buckets']['staging_area']

    for dataset_name, df in all_datasets.items():
        save_key = f"for-annotation/{today}/{dataset_name}.jsonl"
        save_path = f"{staging_bucket}/{save_key}"
        save_dataframe_to_s3(df, save_path, s3_fs)
        print(f"✅ Saved {dataset_name} to s3://{staging_bucket}/{save_key}")

    print(f"\n🎯 Pipeline complete. All datasets are saved in `{staging_bucket}/for-annotation/{today}/`\n")


    # save_key = f"for-annotation/{today}/combined_for_annotation.jsonl"
    # save_path = f"{staging_bucket}/{save_key}"

    # save_dataframe_to_s3(combined_df, save_path, s3_fs)
    # print(f"\n✅ Pipeline complete. Data ready for annotation at s3://{staging_bucket}/{save_key}\n")


if __name__ == '__main__':
    run_preprocessing_pipeline()
