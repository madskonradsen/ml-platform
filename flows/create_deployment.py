"""
Create a Prefect 3 deployment for the ML training flow
Run this script to register the flow as a deployment in Prefect
"""
from train_model import ml_training_pipeline
import asyncio

async def main():
    # Using deploy() method to create a deployment
    deployment_id = await ml_training_pipeline.to_deployment(
        name="ml-training-scheduled",
        tags=["ml", "training", "classification"],
        parameters={"n_samples": 1000, "n_estimators": 50},
        work_pool_name="default-pool"
    )
    print(f"✓ Deployment created successfully!")
    print(f"Deployment ID: {deployment_id}")
    print(f"\nView in Prefect UI: http://localhost:4200/deployments")
    print(f"\nTo run manually:")
    print(f"  prefect deployment run 'ml-training-pipeline/ml-training-scheduled'")

if __name__ == "__main__":
    asyncio.run(main())
