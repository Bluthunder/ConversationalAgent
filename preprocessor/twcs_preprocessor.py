import pandas as pd
import json
from tqdm import tqdm
from utils.pii_detector import redact_pii
from utils.s3_utils import load_dataframe_from_s3
from core.base_preprocessor import BasePreprocessor

class TWCSPreprocessor(BasePreprocessor):
    def load_data(self) -> pd.DataFrame:
        s3_path = f"{self.config['s3_buckets']['raw_data']}/{self.config['data_sources']['twcs']['path']}"
        df = load_dataframe_from_s3(s3_path)
        return redact_pii(df, ['text'], self.pii_patterns)

    def preprocess(self, df: pd.DataFrame) -> list:
        df.dropna(subset=['in_response_to_tweet_id'], inplace=True)
        df['in_response_to_tweet_id'] = df['in_response_to_tweet_id'].astype(int)
        tweets_indexed = df.set_index('tweet_id')
        agent_replies = df[df['inbound'] == False]

        authors = set(self.config['AIR_TRAVEL_BRANDS'])
        agent_replies = agent_replies[agent_replies['author_id'].isin(authors)]

        conversations = []
        for _, reply in tqdm(agent_replies.iterrows(), total=agent_replies.shape[0]):
            try:
                orig = tweets_indexed.loc[reply['in_response_to_tweet_id']]
                if orig['inbound']:
                    conversations.append({
                        "messages": [
                            {"role": "user", "content": orig['text']},
                            {"role": "assistant", "content": reply['text']}
                        ]
                    })
            except KeyError:
                continue
        return pd.DataFrame(conversations)

    def save(self, processed_data: list, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            for convo in processed_data:
                f.write(json.dumps(convo) + '\n')
