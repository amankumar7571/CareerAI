"""Resume-text career classifier: the research model from the CareerAI paper.

Implements the deployable system described in
"Sustainable Career Path Recommendation: A Benchmark Audit, Mathematical
Formalization, and a CPU-Efficient Alternative to Transformer Resume
Classifiers" (ICCISS 2027):

* Features: sublinear TF-IDF over word unigrams + bigrams, capped at
  200,000 features (term frequency scaled as 1 + log(tf)).
* Classifier: linear SVM with balanced class weights and squared hinge
  loss, with posterior probabilities from Platt scaling fitted on a
  held-out validation split (base estimator frozen, single weight matrix).
* Skill lexicon: log-odds ratio with an informative Dirichlet prior,
  top 40 terms per category that appear in >= 10% of that category's
  documents.
* Data hygiene: documents shorter than 40 usable tokens are dropped,
  label-conflicting duplicate groups are removed, one representative is
  kept per exact-duplicate cluster, and the train/validation/test split
  is asserted to share no document hash across folds.

This module is the *research* pipeline (43 categories on the ResumeAtlas
corpus in the paper). The live demo in this repo uses a separate 6-role
tabular model (see ``train_model.py``). The ResumeAtlas data itself is
NOT included in this repo; train with a CSV of ``text,label`` rows
(see ``train_resume_classifier.py``).
"""
from __future__ import annotations

import hashlib
import pickle
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

MAX_FEATURES = 200_000
MIN_TOKENS = 40
RANDOM_STATE = 42
TOP_TERMS_PER_CATEGORY = 40
MIN_DOC_FRAC = 0.10

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")


def normalize_text(text: str) -> str:
    """Unicode-normalise, strip OCR artefacts, replace PII with type tokens."""
    text = unicodedata.normalize("NFKC", str(text))
    text = _EMAIL_RE.sub(" EMAIL ", text)
    text = _URL_RE.sub(" URL ", text)
    text = _PHONE_RE.sub(" PHONE ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def _doc_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def build_vectorizer(max_features: int = MAX_FEATURES) -> TfidfVectorizer:
    """Sublinear TF-IDF: 1 + log(tf), word uni + bigrams, capped features."""
    return TfidfVectorizer(
        sublinear_tf=True,
        ngram_range=(1, 2),
        max_features=max_features,
        lowercase=True,
    )


@dataclass
class ResumeTextClassifier:
    """Trained text classifier bundle (saved as one pickle artifact)."""

    vectorizer: TfidfVectorizer
    model: CalibratedClassifierCV  # Platt-calibrated LinearSVC
    label_encoder: LabelEncoder
    lexicon: dict = field(default_factory=dict)  # label -> [(term, log_odds, coverage)]
    metadata: dict = field(default_factory=dict)

    def predict_top_k(self, texts, k: int = 3):
        """Return [(label, probability), ...] top-k per document, best first."""
        X = self.vectorizer.transform([normalize_text(t) for t in texts])
        proba = self.model.predict_proba(X)
        classes = list(self.label_encoder.classes_)
        out = []
        for row in proba:
            order = np.argsort(row)[::-1][:k]
            out.append([(classes[i], float(row[i])) for i in order])
        return out

    def explain_terms(self, text: str, label: str, top_n: int = 10):
        """Exact additive contributions of terms to one predicted label.

        For a linear model the score is a sum over features, so the listed
        terms are the true reasons for the prediction, not a surrogate.
        """
        norm = normalize_text(text)
        X = self.vectorizer.transform([norm])
        # CalibratedClassifierCV wraps the base estimator; reach the raw SVC
        # (unwrap FrozenEstimator on sklearn >= 1.6).
        est = self.model.calibrated_classifiers_[0].estimator
        svc = getattr(est, "estimator", est)
        label_idx = int(np.where(self.label_encoder.classes_ == label)[0][0])
        coefs = svc.coef_[label_idx]
        row = X.tocoo()
        terms = []
        feature_names = self.vectorizer.get_feature_names_out()
        for col, value in zip(row.col, row.data):
            terms.append((feature_names[col], float(value * coefs[col])))
        terms.sort(key=lambda t: t[1], reverse=True)
        return terms[:top_n]


def _stratified_or_plain_split(frame: pd.DataFrame, test_size: float, random_state: int):
    """Stratified split when every class has >= 2 members, else plain split.

    The paper's corpus (11,507 docs) always stratifies; tiny inputs (unit
    tests, smoke runs) fall back to an unstratified split with the same seed
    instead of crashing.
    """
    try:
        return train_test_split(
            frame, test_size=test_size, random_state=random_state,
            stratify=frame["label"],
        )
    except ValueError:
        return train_test_split(frame, test_size=test_size, random_state=random_state)


def leakage_controlled_split(df: pd.DataFrame, random_state: int = RANDOM_STATE):
    """Clean + split a ``text,label`` frame the way the paper specifies.

    Steps: drop docs with < 40 usable tokens; drop label-conflicting
    duplicate groups; keep one representative per exact-duplicate cluster;
    stratified 70/10/20 split; assert no document hash is shared across
    folds (the pipeline stops instead of training if it is).
    Returns (train, val, test) DataFrames with a ``doc_hash`` column.
    """
    frame = df[["text", "label"]].copy()
    frame["text"] = frame["text"].map(normalize_text)
    frame["doc_hash"] = frame["text"].map(_doc_hash)
    frame["n_tokens"] = frame["text"].str.split().str.len()
    frame = frame[frame["n_tokens"] >= MIN_TOKENS].copy()

    # Label-conflicting groups: same text, different labels -> drop all.
    conflict_hashes = (
        frame.groupby("doc_hash")["label"].nunique()
        .loc[lambda s: s > 1].index
    )
    frame = frame[~frame["doc_hash"].isin(conflict_hashes)]
    # One representative per exact-duplicate cluster.
    frame = frame.drop_duplicates(subset=["doc_hash"], keep="first")

    train, rest = _stratified_or_plain_split(frame, test_size=0.30, random_state=random_state)
    val, test = _stratified_or_plain_split(rest, test_size=2 / 3, random_state=random_state)
    overlap = (
        set(train["doc_hash"]) & set(val["doc_hash"])
        | set(train["doc_hash"]) & set(test["doc_hash"])
        | set(val["doc_hash"]) & set(test["doc_hash"])
    )
    if overlap:
        raise ValueError(
            f"Leakage-controlled split failed: {len(overlap)} hashes shared across folds"
        )
    return train, val, test


def build_log_odds_lexicon(texts, labels, vectorizer, top_n: int = TOP_TERMS_PER_CATEGORY,
                           min_doc_frac: float = MIN_DOC_FRAC):
    """Log-odds skill lexicon with an informative Dirichlet prior.

    For category c and term w (paper eq. 1):
      delta_w(c) = ln[(y_w(c) + a_w) / (n(c) + a0 - y_w(c) - a_w)]
                 - ln[(y_w(!c) + a_w) / (n(!c) + a0 - y_w(!c) - a_w)]
    where a_w is the prior background frequency of w and a0 its sum.
    Keeps the top `top_n` terms per category that also appear in at least
    `min_doc_frac` of that category's documents.
    Returns {label: [(term, log_odds, coverage), ...]}.
    """
    counter = CountVectorizer(
        vocabulary=vectorizer.vocabulary_,
        lowercase=True,
        token_pattern=r"(?u)\b\w+\b",
    )
    counts = counter.transform([normalize_text(t) for t in texts]).tocsc()
    labels = np.asarray(labels)
    feature_names = vectorizer.get_feature_names_out()
    total_docs = counts.shape[0]
    # Background prior: overall document frequency of each term.
    doc_freq = np.asarray((counts > 0).sum(axis=0)).ravel()
    alpha_w = doc_freq / max(total_docs, 1)
    alpha_0 = float(alpha_w.sum())

    lexicon = {}
    for label in sorted(set(labels)):
        mask = labels == label
        n_c = int(mask.sum())
        y_w_c = np.asarray(counts[mask].sum(axis=0)).ravel()
        y_w_not = np.asarray(counts[~mask].sum(axis=0)).ravel()
        n_not = total_docs - n_c
        with np.errstate(divide="ignore", invalid="ignore"):
            delta = np.log((y_w_c + alpha_w) / (n_c + alpha_0 - y_w_c - alpha_w)) - np.log(
                (y_w_not + alpha_w) / (n_not + alpha_0 - y_w_not - alpha_w)
            )
        coverage = np.asarray((counts[mask] > 0).sum(axis=0)).ravel() / max(n_c, 1)
        order = np.argsort(delta)[::-1]
        terms = []
        for idx in order:
            if coverage[idx] < min_doc_frac:
                continue
            terms.append((feature_names[idx], float(delta[idx]), float(coverage[idx])))
            if len(terms) >= top_n:
                break
        lexicon[label] = terms
    return lexicon


def train_text_classifier(train_texts, train_labels, val_texts, val_labels,
                          max_features: int = MAX_FEATURES):
    """Fit the paper's configuration and return a ResumeTextClassifier."""
    vectorizer = build_vectorizer(max_features)
    X_train = vectorizer.fit_transform([normalize_text(t) for t in train_texts])
    X_val = vectorizer.transform([normalize_text(t) for t in val_texts])

    le = LabelEncoder()
    y_train = le.fit_transform(train_labels)
    y_val = le.transform(val_labels)

    base = LinearSVC(class_weight="balanced")  # squared hinge loss (default)
    base.fit(X_train, y_train)
    # Platt scaling on the validation split, base estimator frozen.
    # sklearn >= 1.6 removed cv="prefit": wrapping the fitted estimator in
    # FrozenEstimator is the replacement -- the calibrator then uses it as-is
    # and cv only partitions the calibration data (needs >= 2 samples per
    # class in the validation split).
    model = CalibratedClassifierCV(FrozenEstimator(base), method="sigmoid", cv=2)
    model.fit(X_val, y_val)

    lexicon = build_log_odds_lexicon(train_texts, train_labels, vectorizer)
    return ResumeTextClassifier(
        vectorizer=vectorizer,
        model=model,
        label_encoder=le,
        lexicon=lexicon,
        metadata={
            "max_features": max_features,
            "n_train": len(train_texts),
            "n_val": len(val_texts),
            "labels": sorted(set(train_labels)),
        },
    )


def evaluate(classifier: ResumeTextClassifier, texts, labels):
    """Top-1 / top-3 / top-5 accuracy and macro-F1 on a labelled set."""
    top3 = classifier.predict_top_k(texts, k=5)
    y_true = list(labels)
    y_pred = [row[0][0] for row in top3]
    out = {
        "top1": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }
    for k in (3, 5):
        hits = sum(1 for row, true in zip(top3, y_true) if true in [l for l, _ in row[:k]])
        out[f"top{k}"] = hits / max(len(y_true), 1)
    return out


def save_artifact(classifier: ResumeTextClassifier, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(classifier, f)
    return path


def load_artifact(path: str | Path) -> ResumeTextClassifier:
    with open(path, "rb") as f:
        return pickle.load(f)
