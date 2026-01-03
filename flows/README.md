# Bundled ML Flows for Prefect

This directory contains bundled ML training pipelines that are deployed with your Prefect server.

## What's Included

- **train_model.py**: Complete ML training pipeline using Prefect 3
  - Generates synthetic classification data
  - Trains a Random Forest model
  - Evaluates and saves the model
  - Creates markdown artifacts for results

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run the flow locally
python train_model.py
```

## Build Docker Image

```bash
cd bundled-flows
docker build -t prefect-bundled-flows:latest .
```

## Deploy to Kubernetes

### Option 1: Using ConfigMap (Recommended)

The bundled scripts are automatically included as a ConfigMap when you install the Helm chart. Access them from within the cluster:

```bash
# Run the bundled flow from within a Prefect worker pod
kubectl exec -n mlops deployment/prefect-worker -- python /app/bundled-flows/train_model.py
```

### Option 2: Deploy as a Prefect Deployment

```bash
# Make sure you're connected to the Prefect server
export PREFECT_API_URL="http://localhost:4200/api"

# Deploy the flow
python deploy_flow.py
```

Then trigger it from the Prefect UI or CLI:

```bash
prefect deployment run ml-training-pipeline/ml-training-bundled
```

## Flow Features

- ✅ Uses Prefect 3 tasks and flows
- ✅ Generates synthetic data (no external dependencies)
- ✅ Trains a scikit-learn Random Forest
- ✅ Creates performance reports as Prefect artifacts
- ✅ Saves model to persistent storage
- ✅ Fully containerized and Kubernetes-ready

## Parameters

You can customize the training run:

```python
ml_training_pipeline(
    n_samples=2000,      # Number of samples
    n_features=30,       # Number of features
    n_estimators=200,    # Number of trees
    max_depth=10         # Tree depth
)
```

## Next Steps

1. View the flow runs in the Prefect UI at http://localhost:4200
2. Check the training artifacts and reports
3. Modify the script to use real data sources
4. Add MLflow integration for experiment tracking
5. Connect to MinIO for model storage
