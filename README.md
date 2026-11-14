# Powerlifting Total Predictor

Clean, minimal Streamlit web app with two LightGBM models trained on OpenPowerlifting (1974-2018):

| Tab | Model file | Input | Avg error on unseen lifters |
|---|---|---|---|
| Next meet prediction | `model/model_next_meet.txt` | last meet + history | 21.9 kg (R² 0.95) |
| Quick estimate | `model/model_total.txt` | sex, equipment, bodyweight, age | 64.8 kg (R² 0.73) |

The "likely range" shown under each result comes from the models' real errors on held-out lifters
(10th to 90th percentile, 80% coverage). Values are stored in `model_meta.json`.

## Run on your computer
```
pip install -r requirements.txt
streamlit run app.py
```

## Put it online (free)
1. Upload this whole folder to a GitHub repo (keep the `.streamlit` folder).
2. Go to share.streamlit.io, sign in, click "Create app", choose the repo, main file `app.py`, Deploy.

## Files
- `app.py` UI and styling
- `predictor.py` loads the models and makes predictions
- `model/` trained models
- `model_meta.json` metrics and category counts
- `test_app.py` quick checks: `PYTHONPATH=. python test_app.py`

Not training advice. Injuries, programming and meet conditions are not in the data.
