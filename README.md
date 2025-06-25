Project: Customer Service Agent Data Pipeline

This folder contains the complete code for the Phase 1 data acquisition and preprocessing pipeline. It's designed to be containerized with Docker and orchestrated by a tool like Apache Airflow.

Folder Structure Explained
airline_data_pipeline/
├── dags/                     # Airflow DAG definition file
│   └── data_processing_dag.py
│
├── docker/                   # Docker setup
│   └── Dockerfile
│
├── pipeline/                 # Core pipeline source code
│   ├── __init__.py
│   ├── acquisition.py        # Functions to get data from sources (RCIS, TWCS)
│   ├── preprocessing.py      # Functions for cleaning, PII anonymization, etc.
│   ├── transformation.py     # Functions to create final BERT and SLM datasets
│   └── utils.py              # Helper functions (e.g., S3 interactions)
│
├── tests/                    # Unit tests for your pipeline functions
│   ├── test_preprocessing.py
│   └── test_transformation.py
│
├── config/                   # Configuration files
│   └── config.yaml
│
├── scripts/                  # Standalone scripts for manual execution
│   └── run_pipeline_locally.py
│
└── requirements.txt          # Python package dependencies

dags/: This directory is specifically for your Airflow DAG definition. Airflow will scan this folder to find and schedule your workflows.

docker/: Contains the Dockerfile which defines the exact environment (OS, Python version, dependencies) to run your pipeline. This ensures perfect reproducibility.

pipeline/: The heart of your application. The code is broken into logical modules for clarity and maintainability.

acquisition.py: Pulls data from raw sources.

preprocessing.py: Cleans and standardizes the raw data.

transformation.py: Converts annotated data into model-ready formats.

utils.py: Contains reusable helper code, especially for interacting with AWS S3.

tests/: Essential for a maintainable project. You would write unit tests here to verify your logic, especially for the complex data transformations.

config/: Separates configuration (like file paths, S3 bucket names, model parameters) from your code. This makes it easy to change settings without touching the application logic.

scripts/: Useful for development. This allows you to run the entire pipeline or parts of it from your local machine without needing Airflow.

requirements.txt: Lists all Python dependencies, ensuring a consistent environment.

This structure provides a clean separation of concerns, making the project easy to understand, test, and scale.