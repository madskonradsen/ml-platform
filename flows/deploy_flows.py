"""
Deployment helper for Prefect 3 flows
Works with both dev (mounted flows) and production (baked flows)
"""
import os
from train_model import ml_training_pipeline

def deploy_training_pipeline():
    """Deploy the ML training pipeline"""
    
    deployment = ml_training_pipeline.deploy(
        name="ml-training-scheduled",
        work_pool_name="default-pool",
        cron="0 */6 * * *",  # Every 6 hours
        tags=["ml", "training", "production"],
        description="ML training pipeline with synthetic data",
        version="1.0.0",
        parameters={
            "n_samples": 10000,
            "n_estimators": 100
        }
    )
    
    print(f"✅ Deployment created: {deployment.id}")
    print(f"   Name: ml-training-scheduled")
    print(f"   Schedule: Every 6 hours")
    print(f"   View at: http://localhost:4200/deployments")
    
    return deployment

if __name__ == "__main__":
    # Set Prefect API URL (adjust if running outside cluster)
    if "PREFECT_API_URL" not in os.environ:
        os.environ["PREFECT_API_URL"] = "http://prefect-server:4200/api"
    
    deploy_training_pipeline()
