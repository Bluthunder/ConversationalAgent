import pandas as pd
import json
from tqdm import tqdm
from core.base_preprocessor import BasePreprocessor
from utils.pii_detector import redact_pii
from utils.s3_utils import load_dataframe_from_s3


class RCISPreprocessor(BasePreprocessor):
    def load_data(self) -> pd.DataFrame:
        s3_path = f"{self.config['s3_buckets']['raw_data']}/{self.config['data_sources']['rcis']['path']}"
        df =load_dataframe_from_s3(s3_path)
        return redact_pii(df, ['CustomerQuery', 'AgentResponse'], self.pii_patterns)

    def preprocess(self, df: pd.DataFrame) -> list:
        conversations = []
        for _, row in tqdm(df.iterrows(), total=df.shape[0]):
            if pd.notnull(row['CustomerQuery']) and pd.notnull(row['AgentResponse']):
                conversations.append({
                    "messages": [
                        {"role": "user", "content": row['CustomerQuery']},
                        {"role": "assistant", "content": row['AgentResponse']}
                    ]
                })
        return conversations

    def save(self, processed_data: list, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            for convo in processed_data:
                f.write(json.dumps(convo) + '\n')
