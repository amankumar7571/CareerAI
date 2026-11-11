"""Train the CareerAI research text classifier (TF-IDF + calibrated linear SVM).

Usage:
    python ml_pipeline/train_resume_classifier.py --data data/resumes.csv \
        --out career_text_model.pkl

The CSV must have two columns: ``text`` (resume text) and ``label``
(category). The ResumeAtlas data used in the paper is NOT included in
this repo; supply your own labelled resume corpus. The script prints
leakage-controlled test metrics and saves one pickle artifact containing
the vectorizer, calibrated model, label encoder and log-odds lexicon.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from resume_text_classifier import (  # noqa: E402
    evaluate,
    leakage_controlled_split,
    load_artifact,  # noqa: F401  (re-exported for API users)
    save_artifact,
    train_text_classifier,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, help="CSV with text,label columns")
    parser.add_argument("--out", default="career_text_model.pkl",
                        help="Output artifact path (default: career_text_model.pkl)")
    parser.add_argument("--max-features", type=int, default=200_000)
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    if not {"text", "label"}.issubset(df.columns):
        parser.error("CSV must have 'text' and 'label' columns")
    print(f"Loaded {len(df)} rows from {args.data}")

    train, val, test = leakage_controlled_split(df)
    print(f"After cleaning: train={len(train)} val={len(val)} test={len(test)} "
          f"({train['label'].nunique()} categories)")

    clf = train_text_classifier(
        train["text"], train["label"], val["text"], val["label"],
        max_features=args.max_features,
    )
    metrics = evaluate(clf, test["text"], test["label"])
    print("Test metrics (leakage-controlled split):")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")

    clf.metadata["metrics"] = metrics
    out = save_artifact(clf, args.out)
    print(f"Artifact saved: {out} ({out.stat().st_size / 1e6:.2f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
