# AgroGuide ML Service

This service provides advisory prediction models for crop recommendation, fertilizer recommendation, and plant leaf disease detection.

## Prerequisites

Ensure you have a Python environment set up with all dependencies installed.

```bash
pip install -r requirements.txt
```

## Running Tests

To run the automated test suite, make sure you are in the repository root directory and execute:

```bash
PYTHONPATH=. pytest ml_service/tests/test_ml.py
```

Or if using the local virtual environment:

```bash
PYTHONPATH=. venv/bin/pytest ml_service/tests/test_ml.py
```

## Running the Service Locally

You can launch the FastAPI server using `uvicorn`:

```bash
uvicorn ml_service.main:app --host 0.0.0.0 --port 8000 --reload
```
