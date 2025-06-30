import pandas as pd
import json
from tqdm import tqdm
from utils.pii_detector import redact_pii
from utils.s3_utils import load_dataframe_from_s3
from utils.text_cleaning_utils import clean_text, is_too_short
from core.base_preprocessor import BasePreprocessor

class TWCSPreprocessor(BasePreprocessor):
    def load_data(self) -> pd.DataFrame:
        """Loads TWCS data from S3 and applies PII redaction."""
        s3_path = f"{self.config['s3_buckets']['raw_data']}/{self.config['data_sources']['twcs']['path']}"
        df = load_dataframe_from_s3(s3_path)
        return redact_pii(df, ['text'], self.pii_patterns)

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Processes the loaded DataFrame into prompt-response pairs suitable for fine-tuning."""

        # Clean nulls and cast types
        df.dropna(subset=['in_response_to_tweet_id'], inplace=True)
        df['in_response_to_tweet_id'] = df['in_response_to_tweet_id'].astype(int)

        # Create lookup and filter agent replies
        tweets_indexed = df.set_index('tweet_id')
        agent_replies = df[df['inbound'] == False]

        # Keep only brand-author replies
        authors = set(self.config['AIR_TRAVEL_BRANDS'])
        agent_replies = agent_replies[agent_replies['author_id'].isin(authors)]

        preprocess_cfg = self.config.get("preprocessing", {})
        min_words = preprocess_cfg.get("min_words", 3)

        conversations = []
        seen_pairs = set()
        
        for _, reply in tqdm(agent_replies.iterrows(), total=agent_replies.shape[0]):
            try:
                orig = tweets_indexed.loc[reply['in_response_to_tweet_id']]
                if orig['inbound']:
                    user_text = clean_text(orig['text'], preprocess_cfg)
                    agent_text = clean_text(reply['text'], preprocess_cfg)

                    if not is_too_short(user_text, min_words) and not is_too_short(agent_text, min_words):
                        continue
                    
                    pair_key = (user_text.strip(), agent_text.strip())
                    if pair_key in seen_pairs:
                        continue

                    conversations.append({
                    "messages": [
                        {"role": "user", "content": user_text},
                        {"role": "assistant", "content": agent_text}
                    ]
                })
                seen_pairs.add(pair_key)
                    
            except KeyError:
                continue

        return pd.DataFrame(conversations)

    def save(self, processed_data: pd.DataFrame, output_path: str):
        """Saves the processed conversation pairs to a JSONL file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for convo in processed_data.to_dict(orient="records"):
                f.write(json.dumps(convo, ensure_ascii=False) + '\n')
