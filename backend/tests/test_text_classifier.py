"""Tests for the research text classifier (TF-IDF + calibrated linear SVM).

Trains on a tiny toy corpus so the suite stays fast and needs no external
data; the point is to prove the pipeline code paths (cleaning, split,
training, calibration, explanation, save/load) work, not to reproduce the
paper's 82.58% top-1 on ResumeAtlas.
"""
import pandas as pd
import pytest

from ml_pipeline.resume_text_classifier import (
    build_log_odds_lexicon,
    build_vectorizer,
    evaluate,
    leakage_controlled_split,
    load_artifact,
    normalize_text,
    save_artifact,
    train_text_classifier,
)

def _pad(text: str, target: int = 45) -> str:
    """Repeat a short toy text until it clears the 40-token minimum.

    Real resumes average ~620 tokens; the toy corpus is padded so the
    production cleaning rule (drop < 40 tokens) is exercised honestly
    instead of being bypassed.
    """
    words = text.split()
    out = list(words)
    while len(out) < target:
        out.extend(words)
    return " ".join(out[: max(target, len(words))])


# Phrase pools per label; docs are deterministic combinations, so the
# corpus is reproducible and every doc is unique (sample<i> marker).
PHRASES = {
    "Software Engineer": [
        "Python Django Flask REST API backend developer",
        "Java Spring Boot microservices MySQL Hibernate",
        "C++ algorithms data structures problem solving",
        "FastAPI backend services Docker Kubernetes deployment",
        "Git version control code review agile scrum",
        "SQL PostgreSQL database design indexing queries",
    ],
    "Data Analyst": [
        "Python pandas NumPy data analysis SQL Excel statistics",
        "SQL Tableau Power BI data visualization Excel reporting",
        "Python pandas data cleaning ETL pipelines statistics",
        "Excel SQL business intelligence dashboards data analysis",
        "statistics hypothesis testing regression data exploration",
        "data warehousing reporting automation spreadsheets metrics",
    ],
    "Frontend Developer": [
        "JavaScript React HTML CSS frontend TypeScript Tailwind",
        "React TypeScript frontend components state management CSS",
        "HTML CSS JavaScript Vue frontend responsive design web",
        "Angular TypeScript RxJS frontend components HTML Sass",
        "user interface accessibility performance optimization frontend",
        "CSS grid flexbox animations responsive layouts design",
    ],
    "Machine Learning Engineer": [
        "Python machine learning scikit-learn TensorFlow PyTorch",
        "TensorFlow PyTorch neural networks deep learning NLP",
        "machine learning model training evaluation deployment MLOps",
        "NLP transformers BERT embeddings language models Python",
        "feature engineering cross validation hyperparameter tuning models",
        "computer vision convolutional networks image classification",
    ],
    "DevOps Engineer": [
        "AWS DevOps Docker Kubernetes CI CD Terraform Linux",
        "Docker Kubernetes Jenkins CI CD AWS Azure infrastructure",
        "Linux Bash scripting cloud infrastructure monitoring Terraform",
        "GitHub Actions CI CD deployment pipelines Docker containers",
        "observability logging metrics alerting incident response SRE",
        "infrastructure as code security networking cloud architecture",
    ],
}


def _toy_frame(n_per_label=20):
    rows = []
    for label, phrases in PHRASES.items():
        for i in range(n_per_label):
            picked = [phrases[(i + k) % len(phrases)] for k in range(4)]
            rows.append((_pad(" ".join(picked) + f" sample{i}"), label))
    return pd.DataFrame(rows, columns=["text", "label"])


def test_normalize_text_masks_pii():
    out = normalize_text("John Doe  john@example.com  https://example.com  +91 98765 43210  Python")
    assert "john@example.com" not in out
    assert "example.com" not in out
    assert "98765" not in out
    assert "python" in out


def test_leakage_split_drops_short_docs_and_dupes():
    frame = _toy_frame()
    rows = list(frame.itertuples(index=False, name=None)) + [
        ("tiny doc", "Software Engineer"),  # < 40 tokens -> dropped
        (frame["text"].iloc[0], "Data Analyst"),  # same text, different label -> conflict, dropped
        (frame["text"].iloc[1], "Software Engineer"),  # exact duplicate -> one kept
    ]
    train, val, test = leakage_controlled_split(pd.DataFrame(rows, columns=["text", "label"]))
    # 100 originals + 3 extras, minus tiny doc (1), conflict group (2), duplicate (1)
    assert len(train) + len(val) + len(test) == 99
    all_hashes = set(train["doc_hash"]) | set(val["doc_hash"]) | set(test["doc_hash"])
    assert len(all_hashes) == 99  # no hash appears twice
    assert not (set(train["doc_hash"]) & set(val["doc_hash"]))
    assert not (set(train["doc_hash"]) & set(test["doc_hash"]))
    assert not (set(val["doc_hash"]) & set(test["doc_hash"]))


def test_train_predict_and_explain():
    df = _toy_frame()
    train, val, test = leakage_controlled_split(df)
    clf = train_text_classifier(train["text"], train["label"], val["text"], val["label"])
    top3 = clf.predict_top_k(list(test["text"]), k=3)
    assert len(top3) == len(test)
    for row in top3:
        assert len(row) == 3
        probs = [p for _, p in row]
        assert probs == sorted(probs, reverse=True)
        assert all(0.0 <= p <= 1.0 for p in probs)
    metrics = evaluate(clf, test["text"], test["label"])
    assert 0.0 <= metrics["top1"] <= 1.0
    assert 0.0 <= metrics["top3"] <= 1.0
    # Explanation returns real contributing terms for the top label.
    label = top3[0][0][0]
    terms = clf.explain_terms(test["text"].iloc[0], label, top_n=5)
    assert terms
    assert all(isinstance(t, str) and isinstance(s, float) for t, s in terms)


def test_save_load_round_trip(tmp_path):
    df = _toy_frame()
    train, val, _ = leakage_controlled_split(df)
    clf = train_text_classifier(train["text"], train["label"], val["text"], val["label"])
    path = save_artifact(clf, tmp_path / "model.pkl")
    assert path.exists()
    loaded = load_artifact(path)
    sample = ["Python Django REST API backend SQL"]
    assert loaded.predict_top_k(sample, k=3) == clf.predict_top_k(sample, k=3)


def test_log_odds_lexicon_has_terms_per_label():
    df = _toy_frame()
    vectorizer = build_vectorizer(max_features=5000)
    vectorizer.fit(df["text"].map(normalize_text))
    lexicon = build_log_odds_lexicon(df["text"], df["label"], vectorizer, top_n=5)
    assert set(lexicon) == set(df["label"].unique())
    for label, terms in lexicon.items():
        assert terms  # each label gets at least one term
        assert all(0.0 <= coverage <= 1.0 for _, _, coverage in terms)
