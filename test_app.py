"""Quick checks: python test_app.py"""
from streamlit.testing.v1 import AppTest
import predictor as P

# model sanity: more bodyweight/younger/equipped => bigger totals; layoff widens the range
a = P.predict_total("Male", "Raw", 83, 25)["pred"]; b = P.predict_total("Male", "Raw", 105, 25)["pred"]
assert b > a, (a, b)
assert P.predict_total("Female", "Raw", 63, 25)["pred"] < a
s = P.predict_next("Male", "Raw", 25, 83, 83, 180, 120, 220, 90, 3)
l = P.predict_next("Male", "Raw", 25, 83, 83, 180, 120, 220, 1100, 3)
assert (l["hi"] - l["lo"]) > (s["hi"] - s["lo"])

at = AppTest.from_file("app.py", default_timeout=60).run()
assert not at.exception
for btn in at.button:   # submit both forms
    btn.click()
    at.run(); assert not at.exception, at.exception
print("all good")
