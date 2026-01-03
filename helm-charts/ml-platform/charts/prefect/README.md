# Prefect MLOps Helm Chart

This Helm chart deploys Prefect orchestration platform on Kubernetes for MLOps workflows. It includes:
- Prefect Server (API and UI)
- Prefect Workers for executing flows
- PostgreSQL database for Prefect metadata
- Optional ingress configuration

## Prerequisites

- Kubernetes cluster (1.24+)
- Helm 3.x
- kubectl configured to access your cluster
- (Optional) Ingress controller for external access
- (Optional) cert-manager for TLS certificates

## Quick Start

### 1. Install the chart

```bash
# Create namespace
kubectl create namespace prefect

# Install with default values
helm install prefect ./helm-charts/prefect -n prefect

# Or install with custom values
helm install prefect ./helm-charts/prefect -n prefect -f custom-values.yaml
```

### 2. Access Prefect UI

```bash
# Port forward to access UI locally
kubectl port-forward -n prefect svc/prefect-server 4200:4200

# Access at: http://localhost:4200
```

### 3. Configure Prefect CLI

```bash
# Set API URL
prefect config set PREFECT_API_URL="http://localhost:4200/api"

# Verify connection
prefect server version
```

## Configuration

### Database Configuration

The chart deploys PostgreSQL by default. **IMPORTANT**: Change the default password!

```yaml
postgresql:
  auth:
    password: "your-secure-password-here"
```

For production, consider using an external managed database:

```yaml
postgresql:
  enabled: false

prefect:
  server:
    env:
      - name: PREFECT_API_DATABASE_CONNECTION_URL
        value: "postgresql+asyncpg://user:pass@external-db:5432/prefect"
```

### Ingress Configuration

Enable ingress for external access:

```yaml
ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: prefect.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: prefect-tls
      hosts:
        - prefect.yourdomain.com
```

### Worker Configuration

Adjust worker replicas based on workload:

```yaml
prefect:
  worker:
    enabled: true
    replicas: 3  # Scale as needed
    resources:
      requests:
        memory: "512Mi"
        cpu: "500m"
      limits:
        memory: "2Gi"
        cpu: "2000m"
```

### Resource Requests and Limits

Adjust based on your workload:

```yaml
prefect:
  server:
    resources:
      requests:
        memory: "1Gi"
        cpu: "1000m"
      limits:
        memory: "4Gi"
        cpu: "4000m"
```

## Persistence

PostgreSQL uses persistent volumes by default:

```yaml
postgresql:
  persistence:
    enabled: true
    storageClass: "fast-ssd"  # Use your storage class
    size: 20Gi
```

## Upgrading

```bash
# Update the chart
helm upgrade prefect ./helm-charts/prefect -n prefect

# Or with new values
helm upgrade prefect ./helm-charts/prefect -n prefect -f custom-values.yaml
```

## Uninstalling

```bash
# Delete the release
helm uninstall prefect -n prefect

# Clean up namespace
kubectl delete namespace prefect
```

## Monitoring and Troubleshooting

### Check pod status
```bash
kubectl get pods -n prefect
```

### View logs
```bash
# Prefect server logs
kubectl logs -n prefect -l app.kubernetes.io/component=server

# Worker logs
kubectl logs -n prefect -l app.kubernetes.io/component=worker

# Database logs
kubectl logs -n prefect -l app.kubernetes.io/component=database
```

### Common Issues

1. **Database connection fails**: Check PostgreSQL is running and credentials are correct
2. **Workers not picking up flows**: Verify worker pool name matches your flow deployments
3. **UI not accessible**: Check ingress configuration or use port-forward

## Security Considerations

1. **Change default passwords** in `values.yaml`
2. **Use Kubernetes secrets** for sensitive data
3. **Enable RBAC** for service accounts
4. **Use network policies** to restrict traffic
5. **Enable TLS** for ingress

## Next Steps

After deploying Prefect:

1. Create your first flow
2. Deploy flows to the Kubernetes work pool
3. Set up monitoring and alerting
4. Configure additional workers for scaling
5. Integrate with your ML pipelines

## Support

For issues and questions:
- Prefect Documentation: https://docs.prefect.io
- Prefect Community: https://prefect.io/slack
