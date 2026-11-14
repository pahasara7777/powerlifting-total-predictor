import streamlit as st
import streamlit.components.v1 as components

import predictor as P

st.set_page_config(page_title="Powerlifting Total Predictor", page_icon="🏋️", layout="centered")

# ------------------------------------------------------------------ styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Inter', system-ui, sans-serif; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.stApp { background: #0f1115; }
.block-container { padding-top: 2.5rem; max-width: 760px; }

/* hero */
.hero { padding: 0 0 20px; }
.hero h1 { font-size: 2rem; font-weight: 700; letter-spacing: -.5px; margin: 0 0 6px; color:#f3f4f6; }
.hero p { color:#8b909c; font-size: .98rem; margin: 0; }

/* stat tiles */
.tiles { display:grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin: 0 0 24px; }
.tile { background:#171a21; border:1px solid #242832; border-radius: 12px; padding: 14px 16px; }
.tile b { display:block; font-size: 1.4rem; font-weight: 700; color:#f3f4f6; }
.tile span { color:#8b909c; font-size:.78rem; }

/* tabs */
.stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #242832; }
.stTabs [data-baseweb="tab"] { height:auto; padding: 10px 16px !important; font-weight: 600; color:#8b909c; }
.stTabs [aria-selected="true"] { color:#f3f4f6 !important; }
.stTabs [data-baseweb="tab-highlight"] { background:#ff6b3d; height:2px; }
.stTabs [data-baseweb="tab-border"] { display:none; }

/* form card */
[data-testid="stForm"] { background:#171a21; border: 1px solid #242832; border-radius: 14px; padding: 20px 20px 8px; }
.sec { font-size:.72rem; font-weight:600; letter-spacing:.1em; text-transform:uppercase; color:#8b909c; margin: 10px 0 4px; }
[data-testid="stForm"] label p { color:#c4c8d2; font-weight:500; font-size:.86rem; }
[data-testid="stNumberInput"] input, [data-baseweb="select"] > div { border-radius: 8px !important; }

/* button */
[data-testid="stFormSubmitButton"], [data-testid="stFormSubmitButton"] > div { width:100% !important; }
[data-testid="stFormSubmitButton"] button { width:100% !important; border:0; border-radius: 10px; padding: 12px 0; font-weight: 600; font-size: 1rem; color:#fff; background:#ff6b3d; transition: background .15s; }
[data-testid="stFormSubmitButton"] button:hover { background:#ff805a; color:#fff; }
[data-testid="stExpander"] { border-radius: 10px; border-color: #242832; }
.foot { text-align:center; color:#6b707c; font-size:.8rem; margin: 28px 0 6px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>Powerlifting Total Predictor</h1>
  <p>Estimate your squat + bench + deadlift total, trained on 285,000 real meet results</p>
</div>
""", unsafe_allow_html=True)

nx, tt = P.META["next"], P.META["total"]
st.markdown(f"""
<div class="tiles">
  <div class="tile"><b>{nx['MAE']:.0f} kg</b><span>avg error, next-meet model</span></div>
  <div class="tile"><b>{nx['R2']*100:.0f}%</b><span>variance explained</span></div>
  <div class="tile"><b>{nx['n']:,}</b><span>unseen results tested</span></div>
</div>""", unsafe_allow_html=True)


# ------------------------------------------------------------------ animated result card
def result_card(kind, pred, lo, hi, last=None, shares=None):
    delta_html = ""
    if last:
        d = pred - last
        cls = "up" if d >= 0 else "down"
        delta_html = f'<div class="chip {cls}">{"▲" if d >= 0 else "▼"} {d:+.0f} kg vs your last meet ({last:.0f} kg)</div>'
    split_html = ""
    if shares:
        names = [("Squat", "#ff6b3d"), ("Bench", "#6b9bff"), ("Deadlift", "#3ecf8e")]
        rows = "".join(
            f'<div class="srow"><span>{n}</span><div class="sbar"><i data-w="{s*100:.1f}" style="background:{c}"></i></div>'
            f'<em data-v="{pred*s:.1f}">0</em></div>' for (n, c), s in zip(names, shares))
        split_html = ('<div class="split"><div class="lab">If your lift ratios stay the same (illustration)</div>' + rows + '</div>')
    span = hi - lo
    axis_lo, axis_hi = lo - span * .6, hi + span * .6
    html = f"""
<style>
 * {{ box-sizing:border-box; font-family: Inter, system-ui, sans-serif; }}
 body {{ margin:0; background:transparent; color:#e8ecf6; }}
 .card {{ background:#171a21; border:1px solid #242832; border-radius:14px; padding:26px 26px 20px; text-align:center; }}
 .kind {{ color:#ff6b3d; font-size:.75rem; letter-spacing:.12em; text-transform:uppercase; font-weight:600; }}
 .big {{ font-size:4.2rem; font-weight:700; line-height:1.05; margin: 4px 0 2px; letter-spacing:-2px; color:#fff;  }}
 .big small {{ font-size:1.5rem; color:#cbd3ea; margin-left:6px; letter-spacing:0; font-weight:600; }}
 .chip {{ display:inline-block; padding:6px 14px; border-radius: 99px; font-size:.86rem; font-weight:600; margin: 4px 0 14px; }}
 .chip.up {{ background: rgba(46,204,143,.15); color:#47e5a6; }} .chip.down {{ background: rgba(255,90,90,.15); color:#ff8a8a; }}
 .range {{ margin: 16px 6px 4px; }}
 .track {{ position:relative; height:12px; border-radius: 99px; background: rgba(255,255,255,.09); }}
 .fill {{ position:absolute; top:0; bottom:0; border-radius:99px; background:#ff6b3d; left:50%; width:0;
         transition: left 1.2s .4s cubic-bezier(.2,.8,.2,1), width 1.2s .4s cubic-bezier(.2,.8,.2,1); }}
 .dot {{ position:absolute; top:50%; width:24px; height:24px; margin:-12px 0 0 -12px; border-radius:50%; background:#fff; left:50%;
        box-shadow: 0 0 0 5px rgba(255,255,255,.2), 0 4px 14px rgba(0,0,0,.4); transition: left 1.2s .4s cubic-bezier(.2,.8,.2,1); }}
 .ends {{ display:flex; justify-content:space-between; font-size:.9rem; color:#cbd3ea; margin-top:12px; font-weight:600; }}
 .ends span small {{ display:block; font-size:.7rem; color:#8b97b8; font-weight:500; letter-spacing:.06em; text-transform:uppercase; }}
 .note {{ color:#8b97b8; font-size:.8rem; margin-top:10px; }}
 .split {{ margin-top:18px; text-align:left; }} .lab {{ font-size:.72rem; color:#8b97b8; letter-spacing:.08em; text-transform:uppercase; margin-bottom:8px; text-align:center; }}
 .srow {{ display:grid; grid-template-columns: 64px 1fr 54px; align-items:center; gap:10px; margin:7px 0; font-size:.86rem; }}
 .srow span {{ color:#cbd3ea; font-weight:600; }} .srow em {{ font-style:normal; font-weight:700; text-align:right; }}
 .sbar {{ height:9px; border-radius:99px; background: rgba(255,255,255,.08); overflow:hidden; }}
 .sbar i {{ display:block; height:100%; width:0; border-radius:99px; transition: width 1.2s .7s cubic-bezier(.2,.8,.2,1); }}
</style>
<div class="card">
  <div class="kind">{kind}</div>
  <div class="big"><span id="n">0</span><small>kg</small></div>
  {delta_html}
  <div class="range">
    <div class="track"><div class="fill" id="fill"></div><div class="dot" id="dot"></div></div>
    <div class="ends"><span><small>Low (10%)</small>{lo:.0f} kg</span><span><small>Likely range</small>8 in 10 land here</span><span><small>High (90%)</small>{hi:.0f} kg</span></div>
  </div>
  {split_html}
  <div class="note">Statistical estimate, not training advice.</div>
</div>
<script>
 const target = {pred:.2f}, lo={lo:.2f}, hi={hi:.2f}, A={axis_lo:.2f}, B={axis_hi:.2f};
 const pos = v => Math.min(100, Math.max(0, (v-A)/(B-A)*100));
 const n = document.getElementById('n'), t0 = performance.now(), dur = 1500;
 function tick(t) {{ const p = Math.min(1, (t-t0)/dur), e = 1 - Math.pow(1-p, 4); n.textContent = Math.round(target*e); if (p<1) requestAnimationFrame(tick); }}
 requestAnimationFrame(tick);
 setTimeout(() => {{
   const f = document.getElementById('fill'); f.style.left = pos(lo)+'%'; f.style.width = (pos(hi)-pos(lo))+'%';
   document.getElementById('dot').style.left = pos(target)+'%';
   document.querySelectorAll('.sbar i').forEach(i => i.style.width = i.dataset.w + '%');
   document.querySelectorAll('.srow em').forEach(el => {{ const v=+el.dataset.v, s=performance.now();
     (function k(t){{ const p=Math.min(1,(t-s)/1300); el.textContent = Math.round(v*(1-Math.pow(1-p,3)))+' kg'; if(p<1) requestAnimationFrame(k); }})(s); }});
 }}, 80);
</script>"""
    h = 470 if shares else 290
    if hasattr(st, "iframe"):          # newer Streamlit
        st.iframe(html, height=h)
    else:                              # older Streamlit
        components.html(html, height=h)


def submit(label):
    try:
        return st.form_submit_button(label, width="stretch")
    except TypeError:                       # older Streamlit
        return st.form_submit_button(label, use_container_width=True)


def advanced_block(prefix):
    with st.expander("Advanced: federation, country, year"):
        c1, c2, c3 = st.columns(3)
        fed = c1.selectbox("Federation", P.FED_SORTED, index=0, key=prefix + "fed")
        country = c2.selectbox("Meet country", P.COUNTRY_SORTED, index=0, key=prefix + "country")
        year = c3.number_input("Year", 1974, 2030, P.LATEST_YEAR, key=prefix + "year")
    return fed, country, int(year)


tab1, tab2 = st.tabs(["🔮 Next meet prediction", "⚡ Quick estimate"])

# ------------------------------------------------------------------ tab 1: next meet
with tab1:
    st.caption("Uses your last meet and history. This is the most accurate model.")
    with st.form("next"):
        st.markdown('<div class="sec">About you</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        sex = c1.selectbox("Sex", ["Male", "Female"], key="n_sex")
        equip = c2.selectbox("Equipment", P.EQUIPMENT, index=P.EQUIPMENT.index("Raw"), key="n_eq")
        age = c3.number_input("Age at next meet", 12, 90, 25, key="n_age")

        st.markdown('<div class="sec">Your last meet</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        sq = c1.number_input("Squat (kg)", 20.0, 600.0, 180.0, 2.5, key="n_sq")
        bp = c2.number_input("Bench (kg)", 10.0, 500.0, 120.0, 2.5, key="n_bp")
        dl = c3.number_input("Deadlift (kg)", 30.0, 520.0, 220.0, 2.5, key="n_dl")
        c1, c2, c3 = st.columns(3)
        pbw = c1.number_input("Bodyweight then (kg)", 30.0, 250.0, 83.0, 0.5, key="n_pbw")
        bw = c2.number_input("Bodyweight now (kg)", 30.0, 250.0, 83.0, 0.5, key="n_bw")
        days = c3.number_input("Days since last meet", 1, 5000, 120, key="n_days")

        st.markdown('<div class="sec">Your history</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        n_prior = c1.number_input("Meets done so far", 1, 100, 3, key="n_n")
        best = c2.number_input("Best total ever (kg, 0 = last meet)", 0.0, 1500.0, 0.0, 2.5, key="n_best")
        c1, c2, c3 = st.columns(3)
        t2 = c1.number_input("Total 2 meets ago (0 = n/a)", 0.0, 1500.0, 0.0, 2.5, key="n_t2")
        t3 = c2.number_input("Total 3 meets ago (0 = n/a)", 0.0, 1500.0, 0.0, 2.5, key="n_t3")
        avg = c3.number_input("Average of all totals (0 = auto)", 0.0, 1500.0, 0.0, 2.5, key="n_avg")
        fed, country, year = advanced_block("n_")
        go = submit("Predict my next total 🚀")

    if go:
        st.session_state["next_res"] = P.predict_next(sex, equip, age, bw, pbw, sq, bp, dl, days, n_prior,
                                                      best, avg, t2, t3, fed, country, year)
    r = st.session_state.get("next_res")
    if r:
        result_card("Predicted next meet total", r["pred"], r["lo"], r["hi"], last=r["prev_total"], shares=r["shares"])
        if r["pred"] > r["prior_max"] * 1.12:
            st.warning("This is well above your best ever total, so treat it as an optimistic estimate.")

# ------------------------------------------------------------------ tab 2: quick estimate
with tab2:
    st.caption("No meet history needed. Just who you are. Less accurate, because it cannot see your training level.")
    with st.form("quick"):
        c1, c2 = st.columns(2)
        q_sex = c1.selectbox("Sex", ["Male", "Female"], key="q_sex")
        q_eq = c2.selectbox("Equipment", P.EQUIPMENT, index=P.EQUIPMENT.index("Raw"), key="q_eq")
        c1, c2 = st.columns(2)
        q_bw = c1.number_input("Bodyweight (kg)", 30.0, 250.0, 83.0, 0.5, key="q_bw")
        q_age = c2.number_input("Age", 12, 90, 25, key="q_age")
        q_unknown = st.checkbox("I would rather not give my age", key="q_unk")
        qfed, qcountry, qyear = advanced_block("q_")
        go2 = submit("Estimate my total ⚡")
    if go2:
        st.session_state["quick_res"] = P.predict_total(q_sex, q_eq, q_bw, None if q_unknown else q_age, qfed, qcountry, qyear)
    r2 = st.session_state.get("quick_res")
    if r2:
        result_card("Estimated total for a lifter like you", r2["pred"], r2["lo"], r2["hi"])
        st.caption(f"This model's average error is about {tt['MAE']:.0f} kg, much wider than the next-meet model, "
                   "because two lifters with the same bodyweight can train very differently.")

st.markdown('<div class="foot">Built with LightGBM + Streamlit · Data: OpenPowerlifting (1974-2018)</div>', unsafe_allow_html=True)
