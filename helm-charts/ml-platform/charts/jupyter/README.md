# JupyterLab Chart

Interactive notebook environment for ML development with Prefect integration.

## Features

- Pre-configured with ML libraries (scikit-learn, numpy, pandas, matplotlib, seaborn, xgboost)
- Prefect client installed and configured
- Persistent workspace storage
- Example flows loaded on startup
- Easy access via port-forward or ingress

## Configuration

### Image
```yaml
image:
  repository: jupyter/scipy-notebook
  tag: "latest"
  pullPolicy: IfNotPresent
```

### Bundled Flows
Flows are loaded from a container image on pod startup:

```yaml
bundledFlowsImage:
  repository: bundled-flows
  tag: "latest"
  pullPolicy: IfNotPresent
```

### Persistence
```yaml
persistence:
  enabled: true
  storageClass: ""  # Use default
  size: 5Gi
  accessMode: ReadWriteOnce
```

### Access Token
```yaml
token: "your-secure-token"  # Change in production!
```

## Accessing JupyterLab

```bash
kubectl port-forward -n mlops svc/jupyter 8888:8888
# Visit: http://localhost:8888?token=<your-token>
```

## Updating Flows

See main README for local development workflow with `copy-flows-to-jupyter.ps1`.
