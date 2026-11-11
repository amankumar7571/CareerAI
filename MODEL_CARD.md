# Model Card — CareerAI Resume-Text Classifier

## Model details
- **Task:** supervised multiclass resume classification — assign an occupational
  label from a fixed taxonomy to the text of a resume.
- **Features:** sublinear TF-IDF over word unigrams + bigrams, capped at 200,000
  features (term frequency scaled as 1 + log(tf)).
- **Classifier:** linear SVM, balanced class weights, squared hinge loss.
- **Calibration:** Platt scaling fitted on a held-out validation split with the
  base estimator frozen, so the artifact holds a single weight matrix.
- **Skill lexicon:** log-odds ratio with an informative Dirichlet prior; top 40
  terms per category that appear in at least 10% of that category's documents.
- **Artifact:** one pickle (vectorizer + calibrated model + label encoder +
  lexicon), ~29.45 MB for the paper's configuration.

## Intended use
Career guidance for students: the interface presents the **top 3** predicted
roles, so top-3 is the operating metric. Every prediction is accompanied by
the resume terms that produced it (exact additive contributions from the
linear model, not a surrogate explanation), and the displayed confidence is
the calibrated probability the model ranked with. The system states **no
salary or job-growth figure**, because it has no sourced data for any.

## Training data
- **Corpus:** ResumeAtlas — 13,389 documents across 43 categories (see the
  paper for the audit: 12.8% exact/near duplicates, 57.3% template resumes
  sharing one fabricated identity block, 19 of 43 categories self-identifying).
- **Leakage-controlled protocol:** documents under 40 usable tokens dropped,
  label-conflicting duplicate groups removed, one representative kept per
  duplicate cluster → **11,507 documents**, stratified 8,054 / 1,151 / 2,302
  (train / validation / test), asserted at build time to share no document
  hash and no duplicate cluster across folds.
- **The ResumeAtlas data is NOT included in this repo.** To reproduce, obtain
  the corpus and run `python ml_pipeline/train_resume_classifier.py --data
  data/resumes.csv --out career_text_model.pkl` (CSV with `text,label` columns).

## Metrics (paper, leakage-controlled test split, n = 2,302)
| Metric | Value |
|---|---|
| Top-1 accuracy | 82.58% |
| Top-3 accuracy | 94.18% |
| Top-5 accuracy | 96.96% |
| Macro-F1 | 82.79% |
| Expected calibration error | 0.119 |
| Artifact size | 29.45 MB |
| End-to-end latency (single doc) | 10.1 ms (p95 12.0 ms) |
| Hardware | 2 vCPU, no GPU |

For comparison, the published transformer baselines on the uncontrolled split
report 91.20% top-1 (BERT-base) and 92.00% (Gemma-1.1-2B). The comparison is
across protocols and therefore favours the baselines; at top-3 the linear
model retains 98.0% of BERT's accuracy at ~1.55 × 10⁶ times fewer arithmetic
operations per inference.

## Limitations
- The corpus is English-only and predominantly US-oriented; the mined lexicon
  transfers only partially to the Indian labour market this system targets.
- The taxonomy is inconsistent, mixing job families (Java Developer) with
  industries (Banking, Aviation). Some confusions are taxonomy artefacts:
  Management reaches only 46.7 F1 because managerial language appears across
  every other category.
- Calibration error is 0.119 — confidence figures are approximate, not exact.
- Energy figures in the paper are estimates from stated power assumptions, not
  instrumented measurements; the efficiency argument rests on the analytic
  operation count, not on those estimates.

## Relation to the live demo in this repo
The running product in this repo (`backend/`, `frontend/`) uses a **separate
6-role tabular model** trained on synthetic structured data
(`backend/ml_pipeline/train_model.py`, 1,500 rows) for the live demo. The
research text classifier in `backend/ml_pipeline/resume_text_classifier.py`
is the system the paper evaluates; its trained artifact is not committed
(model artifacts are gitignored — regenerate with the training script above).

## Reference
Sustainable Career Path Recommendation: A Benchmark Audit, Mathematical
Formalization, and a CPU-Efficient Alternative to Transformer Resume
Classifiers — Abhay Pratap Singh, Aman Kumar, Akhil Singh, Aryan Singh
Rathod, Himanshi Sharma (KIET Group of Institutions), ICCISS 2027.
