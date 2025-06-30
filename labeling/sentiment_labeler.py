from transformers import pipeline
from dask import delayed, compute
import logging
from time import time
import torch

logger = logging.getLogger(__name__)


def label_single(item, sentiment_pipe):
    try:
        result = sentiment_pipe(item["message"])[0]
        return {"sentiment": result["label"], "sentiment_score": result["score"]}
    except Exception as e:
        logger.error(f"Sentiment labeling error: {e}")
        return {"sentiment": "ERROR", "sentiment_score": 0.0}


def label(data, config):
    logger.info("🚀 Loading sentiment model...")
    start_time = time()

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    sentiment_pipe = pipeline(
        "sentiment-analysis",
        model=config["labeling"]["sentiment"].get("model", "distilbert-base-uncased-finetuned-sst-2-english"),
        device=0 if device.type != "cpu" else -1
    )

    logger.info("✅ Sentiment model loaded.")
    logger.info("🧵 Starting Dask sentiment labeling...")

    delayed_tasks = [delayed(label_single)(item, sentiment_pipe) for item in data]
    results = compute(*delayed_tasks, scheduler="threads")

    logger.info(f"✅ Sentiment labeling done in {time() - start_time:.2f} seconds")
    return results