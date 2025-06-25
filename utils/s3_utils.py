import pandas as pd
import s3fs

def get_s3_fs():
    """Initializes and returns an S3 filesystem object."""
    return s3fs.S3FileSystem()

def load_dataframe_from_s3(s3_path: str, fs=None) -> pd.DataFrame:
    if fs is None:
        fs = get_s3_fs()
    with fs.open(s3_path, 'r') as f:
        return pd.read_csv(f)

def save_dataframe_to_s3(df, s3_path: str, fs=None):
    if fs is None:
        fs = get_s3_fs()
    print(f"Saving DataFrame to {s3_path}...")
    with fs.open(s3_path, 'w') as f:
        df.to_json(f, orient='records', lines=True)
    print("✅ Save complete.")

