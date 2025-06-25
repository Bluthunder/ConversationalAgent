from abc import ABC, abstractmethod
import pandas as pd

class BasePreprocessor(ABC):
    def __init__(self, config: dict, pii_patterns: dict):
        self.config = config
        self.pii_patterns = pii_patterns

    @abstractmethod
    def load_data(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def preprocess(self, df: pd.DataFrame) -> list:
        pass

    @abstractmethod
    def save(self, processed_data: list, output_path: str):
        pass

    def run(self, output_path: str):
        df = self.load_data()
        processed_data = self.preprocess(df)
        self.save(processed_data, output_path)


