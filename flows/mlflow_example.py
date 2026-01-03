"""
MLflow integration example with Prefect
This flow trains a model and logs metrics/artifacts to MLflow
"""
import os
import mlflow
import mlflow.sklearn
from prefect import flow, task
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import numpy as np

# MLflow tracking server
MLFLOW_TRACKING_URI = "http://mlflow:5000"

# Configure AWS credentials for MinIO access
os.environ["AWS_ACCESS_KEY_ID"] = "admin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "dev-minio-123"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio:9000"

@task(name="load-data", retries=2)
def load_data():
    """Load and split the Iris dataset"""
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test, iris.feature_names, iris.target_names

@task(name="train-model", retries=1)
def train_model(X_train, y_train, n_estimators=100, max_depth=5):
    """Train a Random Forest classifier"""
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42
    )
    model.fit(X_train, y_train)
    return model

@task(name="evaluate-model")
def evaluate_model(model, X_test, y_test, target_names):
    """Evaluate the model and return metrics"""
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=target_names)
    return accuracy, report, y_pred

@flow(name="mlflow-iris-training", log_prints=True)
def mlflow_iris_training(n_estimators: int = 100, max_depth: int = 5):
    """
    Train Iris classifier with MLflow experiment tracking
    
    Args:
        n_estimators: Number of trees in the forest
        max_depth: Maximum depth of trees
    """
    # Set MLflow tracking URI
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    
    # Set experiment
    experiment_name = "iris-classification"
    mlflow.set_experiment(experiment_name)
    
    print(f"🔬 Starting MLflow experiment: {experiment_name}")
    print(f"📊 MLflow tracking URI: {MLFLOW_TRACKING_URI}")
    
    # Start MLflow run
    with mlflow.start_run(run_name=f"rf-n{n_estimators}-d{max_depth}"):
        # Log parameters
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("model_type", "RandomForest")
        
        # Load data
        print("📥 Loading data...")
        X_train, X_test, y_train, y_test, feature_names, target_names = load_data()
        
        # Log dataset info
        mlflow.log_param("n_samples_train", len(X_train))
        mlflow.log_param("n_samples_test", len(X_test))
        mlflow.log_param("n_features", len(feature_names))
        
        # Train model
        print(f"🏋️ Training model (n_estimators={n_estimators}, max_depth={max_depth})...")
        model = train_model(X_train, y_train, n_estimators, max_depth)
        
        # Evaluate model
        print("📈 Evaluating model...")
        accuracy, report, y_pred = evaluate_model(model, X_test, y_test, target_names)
        
        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("n_samples", len(X_test))
        
        # Log model
        print("💾 Logging model to MLflow...")
        mlflow.sklearn.log_model(
            model,
            "model",
            input_example=X_train[:5],
            registered_model_name="iris-classifier"
        )
        
        # Log classification report as artifact
        with open("/tmp/classification_report.txt", "w") as f:
            f.write(report)
        mlflow.log_artifact("/tmp/classification_report.txt")
        
        # Log feature importance
        feature_importance = dict(zip(feature_names, model.feature_importances_))
        for feature, importance in feature_importance.items():
            mlflow.log_metric(f"feature_importance_{feature}", importance)
        
        print(f"\n✅ Model training complete!")
        print(f"🎯 Accuracy: {accuracy:.4f}")
        print(f"📊 MLflow Run ID: {mlflow.active_run().info.run_id}")
        print(f"\n📋 Classification Report:\n{report}")
        
        return {
            "accuracy": accuracy,
            "model_type": "RandomForest",
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "run_id": mlflow.active_run().info.run_id
        }

if __name__ == "__main__":
    # Run with default parameters
    result = mlflow_iris_training()
    print(f"\n🎉 Final result: {result}")
