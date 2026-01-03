"""
Script to deploy the ML training flow to Prefect
Run this after the Prefect server is accessible
"""
from train_model import ml_training_pipeline

if __name__ == "__main__":
    # Deploy the flow to the work pool
    ml_training_pipeline.deploy(
        name="ml-training-bundled",
        work_pool_name="default-pool",
        image="prefect-bundled-flows:latest",  # Update with your registry
        push=False,  # Set to True if pushing to a registry
        cron="0 */6 * * *",  # Run every 6 hours
        description="Bundled ML training pipeline with synthetic data",
        version="1.0.0",
    )
    print("✅ Flow deployed successfully!")
    print("View it at: http://localhost:4200/deployments")
