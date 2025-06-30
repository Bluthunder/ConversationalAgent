from transformers import pipeline
from dask import delayed, compute
import logging
from time import time
import torch

logger = logging.getLogger(__name__)


def label_single(item, intent_pipe, labels):
    try:
        result = intent_pipe(item["message"], labels)["labels"][0]
        return {"intent": result}
    except Exception as e:
        logger.error(f"Intent labeling error: {e}")
        return {"intent": "ERROR"}


def label(data, config):
    logger.info("🚀 Loading intent model...")
    start_time = time()

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    candidate_labels = config["labeling"]["intent"].get("candidate_labels", ["refund", "booking", "cancellation"])
    intent_pipe = pipeline(
        "zero-shot-classification",
        model=config["labeling"]["intent"].get("model", "facebook/bart-large-mnli"),
        device=0 if device.type != "cpu" else -1
    )

    logger.info("✅ Intent model loaded.")
    logger.info("🧵 Starting Dask intent labeling...")

    delayed_tasks = [delayed(label_single)(item, intent_pipe, candidate_labels) for item in data]
    results = compute(*delayed_tasks, scheduler="threads")

    logger.info(f"✅ Intent labeling done in {time() - start_time:.2f} seconds")
    return results
