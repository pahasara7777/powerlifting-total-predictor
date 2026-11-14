"""Model loading and prediction. No UI code here, so it is easy to test."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import lightgbm as lgb

HERE = Path(__file__).parent
META = json.loads((HERE / "model_meta.json").read_text())

_TOTAL = lgb.Booster(model_file=str(HERE / "model" / "model_total.txt"))
_NEXT = lgb.Booster(model_file=str(HERE / "model" / "model_next_meet.txt"))

EQUIPMENT, FEDERATIONS, COUNTRIES = _TOTAL.pandas_categorical
TOTAL_FEATS, NEXT_FEATS = META["total_feats"], META["next_feats"]
# dropdown lists: most common first
FED_SORTED = sorted(FEDERATIONS, key=lambda f: -META["fed_counts"].get(f, 0))
COUNTRY_SORTED = sorted(COUNTRIES, key=lambda c: -META["country_counts"].get(c, 0))
LATEST_YEAR = 2018


def _frame(row, feats):
    df = pd.DataFrame([row])[feats]
    df["Equipment"] = pd.Categorical(df["Equipment"], categories=EQUIPMENT)
    df["Federation"] = pd.Categorical(df["Federation"], categories=FEDERATIONS)
    df["MeetCountry"] = pd.Categorical(df["MeetCountry"], categories=COUNTRIES)
    return df


def predict_total(sex, equipment, bodyweight, age=None, federation="USAPL", country="USA", year=LATEST_YEAR):
    """Estimate a total from who you are (no meet history)."""
    row = dict(BodyweightKg=bodyweight, Age=np.nan if age is None else age, AgeMissing=int(age is None),
               SexM=int(sex == "Male"), Year=year, Equipment=equipment, Federation=federation, MeetCountry=country)
    pred = float(_TOTAL.predict(_frame(row, TOTAL_FEATS))[0])
    lo_q, hi_q = META["total"]["q"]["M" if sex == "Male" else "F"]
    return dict(pred=pred, lo=max(pred + lo_q, 0), hi=pred + hi_q)


def predict_next(sex, equipment, age, bodyweight, prev_bodyweight, squat, bench, deadlift, days_since,
                 n_prior, best_ever=0.0, avg_total=0.0, total_2=0.0, total_3=0.0,
                 federation="USAPL", country="USA", year=LATEST_YEAR):
    """Predict the next meet total from the last meet and history."""
    prev_total = squat + bench + deadlift
    p2 = total_2 if (total_2 > 0 and n_prior >= 2) else np.nan
    p3 = total_3 if (total_3 > 0 and n_prior >= 3) else np.nan
    hist = [prev_total] + [x for x in (p2, p3) if not np.isnan(x)]
    prior_max = max([best_ever] + hist)
    prior_mean = avg_total if avg_total > 0 else float(np.mean(hist))
    row = dict(prev_total=prev_total, prev2_total=p2, prev3_total=p3, prior_max=prior_max, prior_mean=prior_mean,
               roll3_mean=float(np.mean(hist)), delta_prev=prev_total - p2 if not np.isnan(p2) else np.nan,
               n_prior=n_prior, days_since=days_since, BodyweightKg=bodyweight, prev_bw=prev_bodyweight,
               bw_change=bodyweight - prev_bodyweight, AgeFilled=age, AgeMissing=0,
               sq_share=squat / prev_total, bp_share=bench / prev_total, dl_share=deadlift / prev_total,
               SexM=int(sex == "Male"), Year=year, Equipment=equipment, Federation=federation, MeetCountry=country)
    delta = float(_NEXT.predict(_frame(row, NEXT_FEATS))[0])
    pred = prev_total + delta
    bucket = "short" if days_since <= 120 else "mid" if days_since <= 365 else "long"
    lo_q, hi_q = META["next"]["q"][bucket]
    return dict(pred=pred, lo=pred + lo_q, hi=pred + hi_q, prev_total=prev_total, prior_max=prior_max,
                shares=(squat / prev_total, bench / prev_total, deadlift / prev_total))
