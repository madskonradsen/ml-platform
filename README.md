# MLOps Kubernetes Platform

Complete MLOps platform with Prefect orchestration, JupyterLab, and extensible architecture for adding additional ML components.

## Current Components

### ✅ Prefect Orchestration
- Prefect Server (API + UI)
- Prefect Workers (process-based)
- PostgreSQL database
- Full Helm chart with customizable values

### ✅ JupyterLab
- Interactive notebook environment
- Pre-configured with Prefect and ML libraries
- Bundled example flows
- Persistent workspace storage

### ✅ MLFlow
- Experiment tracking and model registry
- MinIO backend for artifact storage
- PostgreSQL database for metadata
- Full Helm chart with customizable values

## Quick Start

### Deploy the Platform

```bash
# Create namespace
kubectl create namespace mlops

# Deploy the ML Platform with Prefect and JupyterLab
helm install ml-platform ./helm-charts/ml-platform -n mlops -f helm-charts/ml-platform/values-dev.yaml

# Access Prefect UI
kubectl port-forward -n mlops svc/prefect-server 4200:4200
# Visit: http://localhost:4200

# Access JupyterLab
kubectl port-forward -n mlops svc/jupyter 8888:8888
# Visit: http://localhost:8888 (token: dev-token-123)

# Access MLFlow
kubectl port-forward -n mlops svc/mlflow 5000:5000
# Visit: http://localhost:5000
```

### Local Development: Managing Bundled Flows

This platform uses a **hybrid approach** for flow distribution:
- **Development**: Flows are mounted into workers from a local image (fast iteration)
- **Production**: Flows are baked into the worker image (immutable, versioned)

#### Development Workflow (Quick Iteration)

**1. Edit flows in JupyterLab**
- Open http://localhost:8888 (token: dev-token-123)
- Edit files in `work/flows/` directory
- Test flows interactively

**2. Update flows in development cluster**
```powershell
# Copy updated flows to Jupyter AND restart workers to pick up changes
.\copy-flows-to-jupyter.ps1
```

**3. Run flows directly from JupyterLab**
```python
# In JupyterLab terminal or notebook
cd /home/jovyan/work/flows
python train_model.py
```

**How it works:**
- Script copies flow files directly to Jupyter pod
- Workers restart automatically to pick up any changes
- No Docker image rebuilds needed during development
- Flows run directly (Prefect deployments require production setup)
- Configured via `values-dev.yaml` with `prefect.worker.flows.mountFromImage.enabled: false`

#### Production Workflow (Immutable Deployments)

**1. Build production worker image with flows baked in**
```powershell
# Build image with flows embedded (immutable)
.\build-production-worker.ps1 -Registry your-registry.com -Version v1.0.0 -Push
```

**2. Update production configuration**
```yaml
# In values-production.yaml
prefect:
  worker:
    image:
      repository: your-registry.com/prefect-worker-with-flows
      tag: "v1.0.0"
    flows:
      mountFromImage:
        enabled: false  # Flows are baked into the image
```

**3. Deploy to production**
```bash
helm upgrade ml-platform ./helm-charts/ml-platform \
  -n mlops-prod \
  -f helm-charts/ml-platform/values-production.yaml
```

**How it works:**
- Flows are copied into the worker image at build time
- Each version is immutable and traceable
- Workers don't need init containers or image mounts
- Configured via `values-production.yaml` with `prefect.worker.flows.mountFromImage.enabled: false`

#### Why This Approach?

**Development:**
- ✅ Fast iteration without image rebuilds
- ✅ Workers automatically get updated flows on restart
- ✅ Works with Docker Desktop Kubernetes

**Production:**
- ✅ Immutable deployments (flows can't change without rebuilding)
- ✅ Version controlled (image tags = flow versions)
- ✅ Better security (no external image mounts)
- ✅ Faster startup (no init container overhead)

## Repository Structure

```
ml-setup-experiments/
├── helm-charts/
│   └── ml-platform/          # Main MLOps platform chart
│       ├── Chart.yaml
│       ├── values.yaml       # Default configuration
│       ├── values-dev.yaml   # Development settings
│       ├── values-production.yaml  # Production settings
│       ├── README.md
│       └── charts/           # Subcharts
│           ├── prefect/      # Prefect orchestration
│           │   ├── Chart.yaml
│           │   ├── values.yaml
│           │   └── templates/
│           ├── jupyter/      # JupyterLab environment
│           │   ├── Chart.yaml
│           │   ├── values.yaml
│           │   └── templates/
│           ├── mlflow/       # MLFlow tracking & registry
│           │   ├── Chart.yaml
│           │   ├── values.yaml
│           │   └── templates/
│           ├── minio/        # S3-compatible artifact storage
│           │   ├── Chart.yaml
│           │   ├── values.yaml
│           │   └── templates/
│           └── postgresql/   # Database for Prefect & MLFlow
│               ├── Chart.yaml
│               ├── values.yaml
│               └── templates/
├── flows/                    # Example Prefect flows (source of truth)
│   ├── train_model.py
│   ├── titanic.ipynb
│   ├── requirements.txt
│   └── README.md
├── flows-container/          # Dockerfile for packaging flows
│   ├── Dockerfile
│   └── README.md
├── copy-flows-to-jupyter.ps1 # Local dev: Copy files to running pod
└── build-and-deploy-flows.ps1 # Local dev: Build image and redeploy
```

## Next Steps

The following components can be added for specific use cases:

- [ ] **Distributed Training**: Kubeflow Training Operator (only if we need multi-GPU/multi-node training beyond what Prefect handles)
- [ ] **Feature Store**: Feast (for feature engineering and serving)
- [ ] **Model Serving**: KServe, Seldon Core, or BentoML (for production inference endpoints)
- [ ] **Monitoring**: Prometheus + Grafana (for model performance and drift monitoring)
- [ ] **Data Processing**: Spark on K8s or Ray (for large-scale data pipelines)
- [ ] **CI/CD**: ArgoCD or Tekton (for GitOps-based deployments)

**Note**: Prefect + MLFlow already handle most model training workflows. Add Kubeflow only if we need distributed training capabilities.

## Prerequisites

- Kubernetes cluster (1.24+)
- Helm 3.x
- kubectl configured
- Storage class for persistent volumes

## Documentation

- [ML Platform Overview](./helm-charts/ml-platform/README.md)
- [Prefect Setup Guide](./helm-charts/ml-platform/charts/prefect/README.md)
- [JupyterLab Guide](./helm-charts/ml-platform/charts/jupyter/README.md)
- [MLFlow Guide](./helm-charts/ml-platform/charts/mlflow/README.md)

## Deployment Patterns

### Development
```bash
helm install ml-platform ./helm-charts/ml-platform -n mlops -f helm-charts/ml-platform/values-dev.yaml
```

### Production
```bash
helm install ml-platform ./helm-charts/ml-platform -n mlops -f helm-charts/ml-platform/values-production.yaml
```

## Contributing

When adding new components:
1. Create a new Helm chart or manifest directory
2. Include comprehensive README
3. Provide example values files for different environments
4. Update this main README with the new component

## Support

Each component has its own README with detailed documentation, troubleshooting guides, and examples.
