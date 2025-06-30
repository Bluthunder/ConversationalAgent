import pandas as pd
import s3fs
import json

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



def load_jsonl_from_s3(s3_path, s3_fs):
    """
    Load a .jsonl file from S3 into a list of dictionaries.

    Args:
        s3_path (str): S3 path to the .jsonl file.
        s3_fs (s3fs.S3FileSystem): Authenticated S3 file system.

    Returns:
        List[dict]: A list of JSON records.
    """
    records = []
    with s3_fs.open(s3_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # Avoid blank lines
                records.append(json.loads(line))
    return records



def save_jsonl_to_s3(data, s3_path, s3_fs):
    """
    Save a list of dictionaries to a .jsonl file on S3.

    Args:
        data (List[dict]): The data to save.
        s3_path (str): Destination path on S3.
        s3_fs (s3fs.S3FileSystem): Authenticated S3 file system.
    """
    with s3_fs.open(s3_path, 'w') as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
