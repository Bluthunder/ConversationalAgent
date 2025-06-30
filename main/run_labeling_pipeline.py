import sys
import os
import logging
from pathlib import Path
from tqdm import tqdm
from dask import delayed, compute
from datetime import datetime

sys.path.append(os.getcwd())

from utils.config_loader import load_config
from utils.s3_utils import get_s3_fs, load_jsonl_from_s3, save_jsonl_to_s3
from labeling import (
    sentiment_labeler,
    intent_labeler,
    topic_modeler,
    ner_labeler,
)

from labeling.label_utils import flatten_user_messages



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_label(label_fn, config, label_type):
    def wrapper(inputs):
        results = []
        for item in inputs:
            try:
                result = label_fn([item], config)[0]
            except Exception as e:
                logger.error(f"{label_type} labeling error: {e}")
                result = {
                    label_type: "ERROR",
                    **({"sentiment_score": 0.0} if label_type == "sentiment" else {}),
                    **({"entities": []} if label_type == "entities" else {})
                }
            results.append(result)
        return results
    return wrapper



def run_labeling_pipeline():


    config = load_config("config/labeling_config.yaml")
    labeling_cfg = config.get("labeling", {})
    s3_fs = get_s3_fs()
    s3_path = config['s3']['preprocessed_data']

    logger.info(f"📥 Loading preprocessed data from: {s3_path}")
    data = load_jsonl_from_s3(s3_path, s3_fs)

    logger.info(f"🔧 Extracting user messages from chat format...")
    user_inputs, user_index_map = flatten_user_messages(data=data)
    
    logger.info(f"🔧 Running labelers with parallel Dask threads...")
  

    tasks = [
        delayed(safe_label(sentiment_labeler.label, config, "sentiment"))(user_inputs),
        delayed(safe_label(intent_labeler.label, config, "intent"))(user_inputs),
        delayed(safe_label(topic_modeler.label, config, "topic"))(user_inputs),
        delayed(safe_label(ner_labeler.label, config, "entities"))(user_inputs)
    ]

    sentiment_results, intent_results, topic_results, ner_results = compute(*tasks, scheduler="threads")

    logger.info("🧩 Merging labeled results...")

    # labeled_data = []
    # for i, item in enumerate(data):
    #     merged = {
    #         "messages": item["messages"],
    #         "sentiment": sentiment_results[i]["sentiment"],
    #         "sentiment_score": sentiment_results[i]["sentiment_score"],
    #         "intent": intent_results[i]["intent"],
    #         "topic": topic_results[i]["topic"],
    #         "entities": ner_results[i]["entities"],
    #     }
    #     labeled_data.append(merged)

    # Path(config["data"]["processed"]).mkdir(parents=True, exist_ok=True)

    for entry in data:
        entry["sentiment"] = []
        entry["sentiment_score"] = []
        entry["intent"] = []
        entry["topic"] = []
        entry["entities"] = []

    for i, entry_idx in enumerate(user_index_map):
        data[entry_idx]["sentiment"].append(sentiment_results[i]["sentiment"])
        data[entry_idx]["sentiment_score"].append(sentiment_results[i]["sentiment_score"])
        data[entry_idx]["intent"].append(intent_results[i]["intent"])
        data[entry_idx]["topic"].append(topic_results[i]["topic"])
        data[entry_idx]["entities"].extend(ner_results[i]["entities"])


    today = datetime.now().strftime("%Y-%m-%d")
    out_path = f"{config['s3']['labeled_output']}/labeled_{today}.jsonl"
    save_jsonl_to_s3(data, out_path, s3_fs)

    logger.info(f"✅ Labeled data saved to: {out_path}")


if __name__ == "__main__":
    run_labeling_pipeline()
