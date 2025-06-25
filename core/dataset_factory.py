# data_pipeline/factory/dataset_factory.py

from preprocessor.twcs_preprocessor import TWCSPreprocessor
from preprocessor.rcis_preprocessor import RCISPreprocessor
from preprocessor.convo3k_preprocessor import Convo3KPreprocessor
from utils.s3_utils import load_dataframe_from_s3

class DatasetFactory:
    def __init__(self, config: dict, fs=None):
        self.config = config
        self.fs = fs
        self.bucket = config["s3_buckets"]["raw_data"]
        self.pii_patterns = config.get("pii_patterns", {})
        self.dataset_map = {
            "twcs": TWCSPreprocessor,
            "rcis": RCISPreprocessor,
            "convo3k": Convo3KPreprocessor
        }

    def load_dataset(self, name: str):
        if name not in self.dataset_map:
            raise ValueError(f"Unsupported dataset: {name}")

        dataset_path = self.config["data_sources"][name]["path"]
        full_path = f"{self.bucket}/{dataset_path}"
        df = load_dataframe_from_s3(full_path, fs=self.fs)

        preprocessor_cls = self.dataset_map[name]
        preprocessor = preprocessor_cls(config=self.config, pii_patterns=self.pii_patterns)
        return preprocessor.preprocess(df)
    

    def load_all(self):
        return {
            name: self.load_dataset(name)
            for name in self.config["data_sources"].keys()
        }
