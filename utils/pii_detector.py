import re
import yaml

def redact_pii(text, pii_patterns: dict) -> str:
    for label, pattern in pii_patterns.items():
        text = re.sub(pattern, f"[REDACTED_{label}]", text)
    return text

# need to refactor this and remove
def load_pii_patterns(config):
    path = config["pii_patterns_file"]
    with open(path, 'r') as f:
        return yaml.safe_load(f)