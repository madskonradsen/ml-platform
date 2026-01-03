"""
Bundled ML Training Flow for Prefect 3 with MLflow Integration
Trains a simple model on synthetic data and logs to MLflow
"""
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
from datetime import datetime
from prefect import flow, task
from prefect.artifacts import create_markdown_artifact
import mlflow
import mlflow.sklearn

# MLflow tracking server
MLFLOW_TRACKING_URI = "http://mlflow:5000"

# Configure AWS credentials for MinIO access
os.environ["AWS_ACCESS_KEY_ID"] = "admin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "dev-minio-123"
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://minio:9000"


@task(name="generate_dummy_data", log_prints=True)
def generate_dummy_data(n_samples=1000, n_features=20, random_state=42):
    """Generate synthetic classification dataset"""
    print(f"Generating {n_samples} samples with {n_features} features...")
    
    np.random.seed(random_state)
    X = np.random.randn(n_samples, n_features)
    
    # Create non-linear decision boundary
    y = (X[:, 0]**2 + X[:, 1]**2 > 1).astype(int)
    
    print(f"Dataset shape: {X.shape}")
    print(f"Class distribution: {np.bincount(y)}")
    
    return X, y


@task(name="split_data", log_prints=True)
def split_data(X, y, test_size=0.2, random_state=42):
    """Split data into train and test sets"""
    print(f"Splitting data: {100*(1-test_size):.0f}% train, {100*test_size:.0f}% test")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    print(f"Train set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    return X_train, X_test, y_train, y_test


@task(name="train_model", log_prints=True)
def train_model(X_train, y_train, n_estimators=100, max_depth=5, random_state=42):
    """Train a Random Forest classifier"""
    print(f"Training Random Forest with {n_estimators} estimators...")
    
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    print("Training completed!")
    print(f"Feature importances: {model.feature_importances_[:5]}")
    
    return model


@task(name="evaluate_model", log_prints=True)
def evaluate_model(model, X_test, y_test):
    """Evaluate model performance"""
    print("Evaluating model...")
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    
    print(f"Test Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(report)
    
    metrics = {
        "accuracy": accuracy,
        "test_samples": len(y_test),
        "timestamp": datetime.now().isoformat(),
        "classification_report": report
    }
    
    return metrics


@task(name="save_model", log_prints=True)
def save_model(model, metrics, model_path="/tmp/model.pkl"):
    """Save trained model and metrics"""
    print(f"Saving model to {model_path}...")
    
    model_data = {
        "model": model,
        "metrics": metrics,
        "trained_at": datetime.now().isoformat()
    }
    
    with open(model_path, "wb") as f:
        pickle.dump(model_data, f)
    
    print(f"Model saved successfully!")
    return model_path


@task(name="create_report")
def create_report(metrics):
    """Create a markdown artifact with results"""
    mlflow_run_id = metrics.get('mlflow_run_id', 'N/A')
    
    markdown_content = f"""# ML Training Report

## Training Summary
- **Timestamp**: {metrics['timestamp']}
- **Test Samples**: {metrics['test_samples']}
- **MLflow Run ID**: {mlflow_run_id}

## Model Performance
- **Accuracy**: {metrics['accuracy']:.4f}

## MLflow Integration
- Experiment tracking enabled
- Model logged to MLflow registry
- Artifacts stored in MinIO

## Status
✅ Model training completed successfully!
"""
    
    create_markdown_artifact(
        key="training-report",
        markdown=markdown_content,
        description="ML model training results"
    )


@flow(name="ml-training-pipeline", log_prints=True)
def ml_training_pipeline(
    n_samples: int = 1000,
    n_features: int = 20,
    n_estimators: int = 100,
    max_depth: int = 5
):
    """
    Complete ML training pipeline using Prefect 3 with MLflow tracking
    
    Args:
        n_samples: Number of samples to generate
        n_features: Number of features per sample
        n_estimators: Number of trees in Random Forest
        max_depth: Maximum depth of trees
    """
    print("=" * 60)
    print("Starting ML Training Pipeline with MLflow")
    print("=" * 60)
    
    # Set MLflow tracking URI and experiment
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    experiment_name = "synthetic-classification"
    mlflow.set_experiment(experiment_name)
    
    print(f"🔬 MLflow Tracking URI: {MLFLOW_TRACKING_URI}")
    print(f"🧪 MLflow Experiment: {experiment_name}")
    
    # Start MLflow run
    with mlflow.start_run(run_name=f"rf-synthetic-n{n_estimators}-d{max_depth}"):
        # Log parameters
        mlflow.log_param("n_samples", n_samples)
        mlflow.log_param("n_features", n_features)
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("model_type", "RandomForest")
        
        # Generate data
        X, y = generate_dummy_data(n_samples=n_samples, n_features=n_features)
        
        # Split data
        X_train, X_test, y_train, y_test = split_data(X, y)
        
        # Log data split info
        mlflow.log_param("train_samples", len(X_train))
        mlflow.log_param("test_samples", len(X_test))
        
        # Train model
        model = train_model(X_train, y_train, n_estimators=n_estimators, max_depth=max_depth)
        
        # Log feature importances
        for idx, importance in enumerate(model.feature_importances_):
            mlflow.log_metric(f"feature_importance_{idx}", importance)
        
        # Evaluate model
        metrics = evaluate_model(model, X_test, y_test)
        
        # Log metrics to MLflow
        mlflow.log_metric("accuracy", metrics["accuracy"])
        mlflow.log_metric("test_samples", metrics["test_samples"])
        
        # Save classification report as artifact
        with open("/tmp/classification_report.txt", "w") as f:
            f.write(metrics["classification_report"])
        mlflow.log_artifact("/tmp/classification_report.txt")
        
        # Log model to MLflow
        print("💾 Logging model to MLflow...")
        mlflow.sklearn.log_model(
            model,
            "model",
            input_example=X_train[:5],
            registered_model_name="synthetic-classifier"
        )
        
        # Save model locally (for backward compatibility)
        model_path = save_model(model, metrics)
        
        # Log MLflow run info
        run_id = mlflow.active_run().info.run_id
        metrics["mlflow_run_id"] = run_id
        print(f"📊 MLflow Run ID: {run_id}")
        
        # Create report
        create_report(metrics)
        
        print("=" * 60)
        print(f"Pipeline completed! Model saved to {model_path}")
        print(f"Final Accuracy: {metrics['accuracy']:.4f}")
        print(f"MLflow Run: {run_id}")
        print("=" * 60)
    
    return metrics


if __name__ == "__main__":
    # Run the flow locally
    result = ml_training_pipeline(
        n_samples=1000,
        n_features=20,
        n_estimators=50,
        max_depth=5
    )
    print(f"\nFinal result: {result}")
