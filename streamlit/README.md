# Human Validation App

Streamlit app that produces human-coded ground truth for the LLM-as-judge
epistemic fortitude scores. Drives the human-validation result reported in
manuscript §5.7 (Issue B / AE-1 of the round-1 review response).

## What it does

- Tab 1 (Score) draws a random scored conversation that the current rater has
  not yet rated. Model and condition are blinded; the scenario flag (Agent is
  Right vs User is Right) is shown because it determines the rubric. The rater
  fills in the five rubric dimensions (60 points total), submits, and on a
  button click the LLM judge's scores are revealed alongside per-dimension
  deltas. The model and condition are revealed at the same time.
- Tab 2 (Analysis) shows a per-sample comparison table, aggregate agreement
  statistics (mean delta, mean absolute delta, Pearson r per dimension), a
  human-vs-LLM scatter plot, and inter-rater agreement when 2+ raters have
  scored the same sample.

## Setup

```
pip install -r requirements.txt
```

## Run

From the `streamlit/` directory:

```
streamlit run app.py
```

Then open the URL it prints (default `http://localhost:8501`).

## Output

Human scores append to `streamlit/data/human_scores.jsonl` (one JSON record
per line). The file is created on the first save. The format is:

```
{
  "rater_id": "...",
  "timestamp_utc": "...",
  "exp_dir": "swebench_langgraph_arbiter",
  "example_id": "django__django-13964",
  "user_is_right": false,
  "human_scores": {"epistemic_responsibility": 17, ...},
  "human_total": 52,
  "llm_scores": {"epistemic_responsibility": 18, ...},
  "llm_total": 55,
  "comment": "..."
}
```

## Notes

- The app does NOT call any LLM API. All LLM scores are read from the existing
  `epistemic_scores/` files written by `scripts/score_epistemic_fortitude.py`.
- A rater cannot re-score the same `(exp_dir, example_id)` pair twice; the
  random sampler skips already-scored entries.
- Multiple raters can score the same sample by using different rater IDs;
  inter-rater agreement is reported in Tab 2 once 2+ raters overlap.
