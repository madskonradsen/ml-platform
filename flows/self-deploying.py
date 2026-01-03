"""
Self-deploying flow example for Prefect 3 with MLflow Integration
This flow automatically deploys itself when run and logs to MLflow
"""
import os
from prefect import flow, task, serve
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import mlflow
import mlflow.sklearn

# MLflow tracking server
MLFLOW_TRACKING_URI = "http://mlflow:5000"

# Configure AWS credentials for MinIO access
os.environ["AWS_ACCESS_KEY_ID"] = "admin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "dev-minio-123"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio:9000"

@task
def generate_data(n_samples: int = 1000):
    """Generate synthetic classification data"""
    X = np.random.randn(n_samples, 10)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    return train_test_split(X, y, test_size=0.2, random_state=42)

@task
def train_classifier(X_train, y_train, n_estimators: int = 100):
    """Train a random forest classifier"""
    clf = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
    clf.fit(X_train, y_train)
    return clf

@task
def evaluate_model(clf, X_test, y_test):
    """Evaluate model performance"""
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    return {"accuracy": accuracy, "predictions": y_pred}

@flow(name="self-deploying-pipeline", log_prints=True)
def my_new_pipeline(n_samples: int = 1000, n_estimators: int = 100):
    """A self-deploying ML pipeline with MLflow tracking"""
    print(f"🚀 Starting pipeline with {n_samples} samples and {n_estimators} estimators")
    
    # Set MLflow tracking URI and experiment
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    experiment_name = "self-deploying-pipeline"
    mlflow.set_experiment(experiment_name)
    
    print(f"🔬 MLflow Tracking URI: {MLFLOW_TRACKING_URI}")
    print(f"🧪 MLflow Experiment: {experiment_name}")
    
    # Start MLflow run
    with mlflow.start_run(run_name=f"autodeploy-n{n_samples}-est{n_estimators}"):
        # Log parameters
        mlflow.log_param("n_samples", n_samples)
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("model_type", "RandomForest")
        mlflow.log_param("deployment_type", "self-deploying")
        
        # Generate and split data
        X_train, X_test, y_train, y_test = generate_data(n_samples)
        print(f"📊 Data generated: {len(X_train)} training samples")
        
        # Log data split info
        mlflow.log_param("train_samples", len(X_train))
        mlflow.log_param("test_samples", len(X_test))
        mlflow.log_param("n_features", X_train.shape[1])
        
        # Train model
        clf = train_classifier(X_train, y_train, n_estimators)
        print("🎯 Model trained successfully")
        
        # Log feature importances
        for idx, importance in enumerate(clf.feature_importances_):
            mlflow.log_metric(f"feature_importance_{idx}", importance)
        
        # Evaluate
        results = evaluate_model(clf, X_test, y_test)
        print(f"✅ Model accuracy: {results['accuracy']:.2%}")
        
        # Log metrics to MLflow
        mlflow.log_metric("accuracy", results["accuracy"])
        mlflow.log_metric("test_samples", len(X_test))
        
        # Log model to MLflow
        print("💾 Logging model to MLflow...")
        mlflow.sklearn.log_model(
            clf,
            "model",
            input_example=X_train[:5],
            registered_model_name="self-deploying-classifier"
        )
        
        # Log MLflow run info
        run_id = mlflow.active_run().info.run_id
        results["mlflow_run_id"] = run_id
        print(f"📊 MLflow Run ID: {run_id}")
    
    return results

# Self-deploying using serve() for local development
if __name__ == "__main__":
    # Option 1: Just run once
    # my_new_pipeline()
    
    # Option 2: Serve with schedule (keeps running)
    serve(
        my_new_pipeline.to_deployment(
            name="self-deploying-scheduled",
            cron="0 */6 * * *",  # Every 6 hours
            tags=["ml", "self-deploying", "example"],
            description="Self-deploying ML pipeline example",
            version="1.0.0"
        )
    )