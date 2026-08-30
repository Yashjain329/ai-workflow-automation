import os
import json
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

def train_and_persist_model():
    root_dir = os.path.dirname(os.path.dirname(__file__))
    train_path = os.path.join(root_dir, "data", "train.json")
    val_path = os.path.join(root_dir, "data", "val.json")
    model_path = os.path.join(root_dir, "backend", "models", "tfidf_logreg_model.pkl")

    if not os.path.exists(train_path):
        from scripts.generate_dataset import main as gen_data
        gen_data()

    with open(train_path, "r") as f:
        train_data = json.load(f)

    with open(val_path, "r") as f:
        val_data = json.load(f)

    X_train = [d["text"] for d in train_data]
    y_train = [d["workflow_category"] for d in train_data]

    X_val = [d["text"] for d in val_data]
    y_val = [d["workflow_category"] for d in val_data]

    print("Training scikit-learn TF-IDF + Logistic Regression Pipeline...")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000, lowercase=True)),
        ('clf', LogisticRegression(C=1.0, max_iter=200, random_state=42))
    ])

    pipeline.fit(X_train, y_train)

    # Validate on validation split
    y_val_pred = pipeline.predict(X_val)
    print("\nValidation Set Performance:")
    print(classification_report(y_val, y_val_pred, zero_division=0))

    # Persist model artifact
    joblib.dump(pipeline, model_path)
    print(f"Trained model artifact persisted successfully to: '{model_path}'")

if __name__ == "__main__":
    train_and_persist_model()
