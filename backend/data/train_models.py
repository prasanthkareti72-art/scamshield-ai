"""
ScamShield AI - Model Training Pipeline
Trains:
1. Fake News Classifier (TF-IDF + Calibrated Classifier)
2. Scam & Phishing Text Classifier (TF-IDF + Logistic Regression)
Generates evaluation metrics (accuracy, precision, recall, F1, confusion matrix)
and exports serialized model artifacts.
"""

import json
import os
import joblib
import numpy as np
from datetime import datetime, timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def train_fake_news_classifier():
    data_path = os.path.join(BASE_DIR, "fake_news_dataset.json")
    with open(data_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    texts = [item["text"] for item in dataset]
    labels = [item["label"] for item in dataset]

    # Stratified train/test split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )

    # ML Pipeline: TF-IDF Vectorizer with unigrams & bigrams + Logistic Regression
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            lowercase=True,
            stop_words="english",
            min_df=1,
            max_features=2500
        )),
        ("classifier", LogisticRegression(
            C=2.0,
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        ))
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    p, r, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="binary")
    cm = confusion_matrix(y_test, y_pred).tolist()

    # Save artifact
    model_save_path = os.path.join(MODELS_DIR, "fake_news_model.pkl")
    joblib.dump(pipeline, model_save_path)
    print(f"[OK] Fake News Model saved -> {model_save_path}")

    return {
        "model_name": "Fake News Classifier (TF-IDF + Logistic Regression)",
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "accuracy": round(acc, 4),
        "precision": round(float(p), 4),
        "recall": round(float(r), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": {
            "tn": cm[0][0], "fp": cm[0][1],
            "fn": cm[1][0], "tp": cm[1][1]
        },
        "classes": ["Genuine News (0)", "Misinformation / Fake News (1)"]
    }

def train_scam_classifier():
    data_path = os.path.join(BASE_DIR, "scam_dataset.json")
    with open(data_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    texts = [item["text"] for item in dataset]
    labels = [item["label"] for item in dataset]

    # Stratified train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            lowercase=True,
            min_df=1,
            max_features=3000
        )),
        ("classifier", LogisticRegression(
            C=2.5,
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        ))
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    p, r, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="binary")
    cm = confusion_matrix(y_test, y_pred).tolist()

    model_save_path = os.path.join(MODELS_DIR, "scam_model.pkl")
    joblib.dump(pipeline, model_save_path)
    print(f"[OK] Scam Classifier saved -> {model_save_path}")

    return {
        "model_name": "Scam & Phishing Classifier (TF-IDF + Logistic Regression)",
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "accuracy": round(acc, 4),
        "precision": round(float(p), 4),
        "recall": round(float(r), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": {
            "tn": cm[0][0], "fp": cm[0][1],
            "fn": cm[1][0], "tp": cm[1][1]
        },
        "classes": ["Safe Conversational (0)", "Scam / Phishing (1)"]
    }

def main():
    print("=" * 60)
    print("ScamShield AI - Training Machine Learning Models")
    print("=" * 60)

    fn_metrics = train_fake_news_classifier()
    scam_metrics = train_scam_classifier()

    metrics_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "framework": "scikit-learn",
        "vectorizer": "TF-IDF (1, 2 n-grams with sublinear term frequency)",
        "models": {
            "fake_news": fn_metrics,
            "scam_phishing": scam_metrics
        }
    }

    metrics_path = os.path.join(MODELS_DIR, "model_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    print(f"\n[SUCCESS] Model training complete! Metrics written to {metrics_path}")
    print(f"Fake News Accuracy: {fn_metrics['accuracy'] * 100:.1f}%, F1: {fn_metrics['f1_score']:.4f}")
    print(f"Scam Detection Accuracy: {scam_metrics['accuracy'] * 100:.1f}%, F1: {scam_metrics['f1_score']:.4f}")

if __name__ == "__main__":
    main()
