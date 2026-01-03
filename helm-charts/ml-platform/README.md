# ML Platform Helm Chart

Complete MLOps platform with Prefect orchestration and JupyterLab for interactive development.

## Architecture

This is an umbrella chart that orchestrates multiple components:

- **Prefect**: Workflow orchestration platform (server, worker, PostgreSQL)
- **JupyterLab**: Interactive notebook environment with ML libraries

## Quick Start

```bash
# Create namespace
kubectl create namespace mlops

# Install the platform
helm install ml-platform ./helm-charts/ml-platform -n mlops -f helm-charts/ml-platform/values-dev.yaml

# Access services
kubectl port-forward -n mlops svc/prefect-server 4200:4200  # Prefect UI
kubectl port-forward -n mlops svc/jupyter 8888:8888         # JupyterLab
```

## Configuration

### Development
```bash
helm install ml-platform ./helm-charts/ml-platform -n mlops -f helm-charts/ml-platform/values-dev.yaml
```

### Production
Create `values-production.yaml` with:
- Strong passwords
- Resource limits tuned for workload
- Ingress configuration
- Persistent storage enabled

```bash
helm install ml-platform ./helm-charts/ml-platform -n mlops -f values-production.yaml
```

## Components

### Prefect (charts/prefect/)
- Prefect Server with UI
- Process-based workers
- PostgreSQL database
- Full configuration in subchart

### JupyterLab (charts/jupyter/)
- Scipy notebook image with ML libraries
- Prefect integration
- Persistent workspace
- Pre-loaded example flows

## Subcharts

This chart uses Helm dependencies. To update subcharts:

```bash
cd helm-charts/ml-platform
helm dependency update
```

## Upgrading

```bash
helm upgrade ml-platform ./helm-charts/ml-platform -n mlops -f helm-charts/ml-platform/values-dev.yaml
```

## Uninstalling

```bash
helm uninstall ml-platform -n mlops
```

## Values

See individual subchart README files for detailed configuration options:
- [Prefect Configuration](charts/prefect/README.md)
- [JupyterLab Configuration](charts/jupyter/README.md)
