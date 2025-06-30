from transformers import pipeline
from dask import delayed, compute
import logging
from time import time
import torch

logger = logging.getLogger(__name__)


def label_single(item, topic_pipe, candidate_labels):
    try:
        result = topic_pipe(item["message"], candidate_labels)["labels"][0]
        return {"topic": result}
    except Exception as e:
        logger.error(f"Topic labeling error: {e}")
        return {"topic": "ERROR"}


def label(data, config):
    logger.info("🚀 Loading topic model...")
    start_time = time()

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    candidate_labels = config["labeling"]["topic"].get("candidate_labels", ["service", "billing", "technical"])
    topic_pipe = pipeline(
        "zero-shot-classification",
        model=config["labeling"]["topic"].get("model", "facebook/bart-large-mnli"),
        device=0 if device.type != "cpu" else -1
    )

    logger.info("✅ Topic model loaded.")
    logger.info("🧵 Starting Dask topic labeling...")

    delayed_tasks = [delayed(label_single)(item, topic_pipe, candidate_labels) for item in data]
    results = compute(*delayed_tasks, scheduler="threads")

    logger.info(f"✅ Topic labeling done in {time() - start_time:.2f} seconds")
    return results