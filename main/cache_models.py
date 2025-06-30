from transformers import AutoModel, AutoTokenizer, pipeline
from sentence_transformers import SentenceTransformer

def download_model(model_name, task):
    print(f"🔽 Downloading {model_name} for {task}")
    _ = pipeline(task, model=model_name)

if __name__ == "__main__":
    # Sentiment analysis
    download_model("cardiffnlp/twitter-roberta-base-sentiment", "sentiment-analysis")

    # Intent detection (zero-shot classification)
    download_model("facebook/bart-large-mnli", "zero-shot-classification")

    # NER
    download_model("dslim/bert-base-NER", "ner")  # You can change this model if needed

    # Topic Modeling (BERTopic doesn't use Hugging Face under the hood for transformer)
    # But it depends on SentenceTransformer which uses HF behind the scenes
    
    print("🔽 Downloading SentenceTransformer model for BERTopic")
    SentenceTransformer("all-MiniLM-L6-v2")
