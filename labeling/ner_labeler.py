from transformers import pipeline
from dask import delayed, compute
import logging
from time import time
import torch

logger = logging.getLogger(__name__)


def label_single(item, ner_pipe):
    try:
        entities = ner_pipe(item["message"])
        named_entities = [e["word"] for e in entities if e["score"] > 0.85]
        return {"entities": named_entities}
    except Exception as e:
        logger.error(f"NER labeling error: {e}")
        return {"entities": []}


def label(data, config):
    logger.info("🚀 Loading NER model...")
    start_time = time()

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    ner_pipe = pipeline(
        "ner",
        model=config["labeling"]["ner"].get("model", "dbmdz/bert-large-cased-finetuned-conll03-english"),
        aggregation_strategy="simple",
        device=0 if device.type != "cpu" else -1
    )

    logger.info("✅ NER model loaded.")
    logger.info("🧵 Starting Dask NER labeling...")

    delayed_tasks = [delayed(label_single)(item, ner_pipe) for item in data]
    results = compute(*delayed_tasks, scheduler="threads")

    logger.info(f"✅ NER labeling done in {time() - start_time:.2f} seconds")
    return results