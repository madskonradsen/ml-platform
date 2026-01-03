# Flows Container Image

This directory contains the Dockerfile for building a container image with bundled Prefect flows.

The actual flow source code is in `../flows/` - this is just the build context.

## Building

```bash
# Build from this directory (includes parent context for flows)
docker build -t bundled-flows:latest -f Dockerfile ..

# Or use the helper script
cd ..
.\build-and-deploy-flows.ps1
```

## Usage

The init container will copy flows from this image to the JupyterLab workspace.

## Production

Push to your container registry:

```bash
docker tag bundled-flows:latest your-registry.com/bundled-flows:1.0.0
docker push your-registry.com/bundled-flows:1.0.0
```
