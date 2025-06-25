# ==============================================================================
# Date: 21-06-2025
# File: pipeline/acquisition.py
# Description: Functions to acquire data from raw sources.
# ==============================================================================
import pandas as pd
from ..utils.s3_utils import load_config

# def acquire_rcis_data(s3_fs):
#     """Loads and consolidates all 38 RCIS files from S3."""
#     config = load_config()
#     raw_bucket = config['s3_buckets']['raw_data']
#     twcs_path = config['data_sources']['twcs']['path']
#     full_path = f"{raw_bucket}/{twcs_path}"
    
#     print(f"Acquiring TWCS data from {full_path}...")
#     with s3_fs.open(full_path, 'r') as f:
#         df = pd.read_csv(f)
#     print(f"Successfully loaded TWCS data with {len(df)} rows.")
#     return df

def acquire_twcs_data(s3_fs):
    """Loads the TWCS dataset from S3."""
    config = load_config()
    raw_bucket = config['s3_buckets']['raw_data']
    twcs_path = config['data_sources']['twcs']['path']
    full_path = f"{raw_bucket}/{twcs_path}"
    
    print(f"Acquiring TWCS data from {full_path}...")
    with s3_fs.open(full_path, 'r') as f:
        df = pd.read_csv(f)
    print(f"Successfully loaded TWCS data with {len(df)} rows.")
    return df

def acquire_conv_3k_data(s3_fs):
    """Loads the Conv-3K dataset from S3."""
    config = load_config()
    raw_bucket = config['s3_buckets']['raw_data']
    conv_3k_path = config['data_sources']['conv_3k']['path']
    full_path = f"{raw_bucket}/{conv_3k_path}"
    
    print(f"Acquiring Conv-3K data from {full_path}...")
    with s3_fs.open(full_path, 'r') as f:
        df = pd.read_csv(f)
    print(f"Successfully loaded Conv-3K data with {len(df)} rows.")
    return df