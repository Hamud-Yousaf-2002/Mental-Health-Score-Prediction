"""
Visual layer for the Streamlit dashboard: CSS theme plus small HTML builders.

Design: deep midnight background with slow "aurora" gradients, frosted glass
cards that tilt slightly in 3D on hover, and a rotating orb in the hero.
"""

from html import escape

# Colour tokens (kept in one place so the CSS and Plotly charts match)
COLORS = {
    "bg": "#070b18",
    "panel": "rgba(255, 255, 255, 0.055)",
    "border": "rgba(255, 255, 255, 0.12)",
    "text": "#e8ecf8",
    "muted": "#9aa3c0",
    "teal": "#2dd4bf",
    "violet": "#8b5cf6",
    "rose": "#f472b6",
    "ok": "#34d399",
    "bad": "#fb7185",
}


def global_css() -> str:
    c = COLORS
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700;800&family=DM+Sans:wght@400;500;700&display=swap');

/* ---------- Base & background ---------- */
html, body, [class*="css"], .stMarkdown, .stText, label, input, button, textarea {{
    font-family: 'DM Sans', sans-serif;
}}
h1, h2, h3, h4, .mh-title, .mh-section-title {{ font-family: 'Sora', sans-serif; }}

[data-testid="stAppViewContainer"] {{
    background:
        radial-gradient(900px 600px at 10% -10%, rgba(139, 92, 246, .28), transparent 60%),
        radial-gradient(800px 500px at 100% 10%, rgba(45, 212, 191, .18), transparent 60%),
        radial-gradient(700px 500px at 50% 110%, rgba(244, 114, 182, .14), transparent 60%),
        {c['bg']};
    background-attachment: fixed;
}}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 2rem; padding-bottom: 4rem; max-width: 1240px; }}

/* ---------- Hero ---------- */
.mh-hero {{
    position: relative; overflow: hidden;
    display: grid; grid-template-columns: 1.5fr 1fr; gap: 1.5rem; align-items: center;
    padding: 2.4rem 2.6rem; margin-bottom: 1.6rem;
    border-radius: 28px;
    background: linear-gradient(135deg, rgba(139,92,246,.20), rgba(45,212,191,.10) 60%, rgba(255,255,255,.03));
    border: 1px solid {c['border']};
    box-shadow: 0 30px 80px -30px rgba(139, 92, 246, .55), inset 0 1px 0 rgba(255,255,255,.12);
    backdrop-filter: blur(18px);
    animation: mh-rise .7s ease-out both;
}}
.mh-eyebrow {{
    display: inline-flex; gap: .5rem; align-items: center;
    font-size: .78rem; letter-spacing: .14em; text-transform: uppercase;
    color: {c['teal']}; font-weight: 700; margin-bottom: .8rem;
}}
.mh-title {{
    font-size: clamp(2rem, 4.2vw, 3.3rem); line-height: 1.05; font-weight: 800; margin: 0 0 .9rem;
    background: linear-gradient(100deg, #fff 10%, #c4b5fd 45%, {c['teal']} 90%);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}}
.mh-hero h1.mh-title {{ font-family: 'Sora', sans-serif !important; padding: 0; }}
.mh-hero [data-testid="stHeaderActionElements"] {{ display: none; }}
.mh-status {{ white-space: nowrap; flex-wrap: wrap; }}
.mh-sub {{ color: {c['muted']}; font-size: 1.05rem; line-height: 1.6; max-width: 38rem; margin: 0 0 1.3rem; }}

.mh-status {{
    display: inline-flex; align-items: center; gap: .55rem;
    padding: .45rem .9rem; border-radius: 999px; font-size: .86rem; font-weight: 600;
    border: 1px solid {c['border']}; background: rgba(0,0,0,.25);
}}
.mh-dot {{ width: 9px; height: 9px; border-radius: 50%; }}
.mh-status.ok  .mh-dot {{ background: {c['ok']};  box-shadow: 0 0 0 0 {c['ok']};  animation: mh-pulse 1.8s infinite; }}
.mh-status.bad .mh-dot {{ background: {c['bad']}; }}
.mh-status.ok  {{ color: {c['ok']}; }}
.mh-status.bad {{ color: {c['bad']}; }}
.mh-status code {{ color: {c['muted']}; background: transparent; font-size: .8rem; }}

/* 3D orb: layered gradients + tilted rotating rings */
.mh-orb-wrap {{ display: flex; justify-content: center; perspective: 900px; }}
.mh-orb {{
    position: relative; width: 210px; height: 210px; transform-style: preserve-3d;
    animation: mh-float 6s ease-in-out infinite;
}}
.mh-core {{
    position: absolute; inset: 28px; border-radius: 50%;
    background: radial-gradient(circle at 32% 28%, #fff 0%, #c4b5fd 14%, {c['violet']} 42%, #1e1b4b 78%);
    box-shadow: 0 0 60px rgba(139,92,246,.75), inset -18px -24px 50px rgba(0,0,0,.55);
}}
.mh-ring {{
    position: absolute; inset: 0; border-radius: 50%;
    border: 2px solid rgba(45,212,191,.55); border-left-color: transparent; border-bottom-color: transparent;
}}
.mh-ring.r1 {{ transform: rotateX(70deg); animation: mh-spin1 7s linear infinite; }}
.mh-ring.r2 {{ inset: -14px; border-color: rgba(244,114,182,.45); border-right-color: transparent;
               transform: rotateY(65deg); animation: mh-spin2 11s linear infinite; }}
.mh-ring.r3 {{ inset: 12px; border-color: rgba(196,181,253,.5); border-top-color: transparent;
               transform: rotateX(-55deg) rotateY(25deg); animation: mh-spin3 9s linear infinite; }}

/* ---------- Glass section cards (st.container(key="card-...")) ---------- */
div[class*="st-key-card-"] {{
    background: {c['panel']};
    border: 1px solid {c['border']};
    border-radius: 22px; padding: 1.4rem 1.4rem 1.1rem;
    backdrop-filter: blur(16px);
    box-shadow: 0 18px 45px -22px rgba(0,0,0,.8), inset 0 1px 0 rgba(255,255,255,.08);
    transform: perspective(1000px) translateZ(0);
    transition: transform .35s ease, box-shadow .35s ease, border-color .35s ease;
}}
div[class*="st-key-card-"]:hover {{
    transform: perspective(1000px) rotateX(2deg) translateY(-4px);
    border-color: rgba(139,92,246,.45);
    box-shadow: 0 28px 60px -24px rgba(139,92,246,.55), inset 0 1px 0 rgba(255,255,255,.12);
}}
.mh-section-title {{ display: flex; align-items: center; gap: .65rem; font-size: 1.05rem; font-weight: 700;
                     color: {c['text']}; margin: 0 0 .2rem; }}
.mh-section-icon {{
    display: grid; place-items: center; width: 36px; height: 36px; border-radius: 11px; font-size: 1.1rem;
    background: linear-gradient(135deg, rgba(139,92,246,.45), rgba(45,212,191,.35));
    box-shadow: 0 8px 18px -8px rgba(139,92,246,.9);
}}
.mh-section-hint {{ color: {c['muted']}; font-size: .85rem; margin: 0 0 .8rem 2.9rem; }}

/* Remove the default form frame; cards supply the visuals */
[data-testid="stForm"] {{ border: none; padding: 0; background: transparent; }}

/* Inputs */
[data-baseweb="select"] > div, [data-testid="stNumberInput"] input, [data-testid="stTextInput"] input {{
    background: rgba(10, 14, 30, .55) !important; border-radius: 12px !important;
    border-color: rgba(255,255,255,.14) !important; transition: border-color .2s, box-shadow .2s;
}}
[data-baseweb="select"] > div:hover, [data-testid="stNumberInput"] input:focus {{
    border-color: rgba(45,212,191,.6) !important; box-shadow: 0 0 0 3px rgba(45,212,191,.12);
}}
[data-testid="stSlider"] [role="slider"] {{ box-shadow: 0 0 0 6px rgba(139,92,246,.25); }}

/* ---------- Predict button ---------- */
[data-testid="stFormSubmitButton"] button {{
    width: 100%; padding: .95rem 1rem; border: 0; border-radius: 16px;
    font-family: 'Sora', sans-serif; font-size: 1.08rem; font-weight: 700; letter-spacing: .02em; color: #fff;
    background: linear-gradient(100deg, {c['violet']}, #6366f1 45%, {c['teal']});
    background-size: 200% 100%;
    box-shadow: 0 16px 40px -14px rgba(139,92,246,.9), inset 0 1px 0 rgba(255,255,255,.3);
    transition: transform .2s ease, box-shadow .2s ease, background-position .6s ease;
}}
[data-testid="stFormSubmitButton"] button:hover {{
    transform: translateY(-3px) scale(1.01); background-position: 100% 0; color: #fff;
    box-shadow: 0 22px 50px -14px rgba(45,212,191,.75), inset 0 1px 0 rgba(255,255,255,.35);
}}
[data-testid="stFormSubmitButton"] button:active {{ transform: translateY(0) scale(.99); }}

/* ---------- Result ---------- */
.mh-score-card {{
    position: relative; text-align: center; padding: 2rem 1.2rem 1.6rem; border-radius: 24px;
    background: radial-gradient(circle at 50% 0%, rgba(139,92,246,.35), transparent 65%), rgba(255,255,255,.05);
    border: 1px solid rgba(139,92,246,.4);
    box-shadow: 0 30px 70px -30px rgba(139,92,246,.8);
    animation: mh-pop .6s cubic-bezier(.2,.9,.3,1.3) both;
}}
.mh-score-label {{ color: {c['muted']}; text-transform: uppercase; letter-spacing: .14em; font-size: .78rem; font-weight: 700; }}
.mh-score-value {{
    font-family: 'Sora', sans-serif; font-weight: 800; font-size: clamp(3.6rem, 9vw, 5.6rem); line-height: 1;
    margin: .6rem 0 .5rem;
    background: linear-gradient(180deg, #fff, #c4b5fd 60%, {c['teal']});
    -webkit-background-clip: text; background-clip: text; color: transparent;
    filter: drop-shadow(0 10px 30px rgba(139,92,246,.55));
}}
.mh-score-meta {{ color: {c['muted']}; font-size: .9rem; line-height: 1.5; }}
.mh-score-meta b {{ color: {c['text']}; }}

.mh-disclaimer {{
    display: flex; gap: .7rem; align-items: flex-start; margin-top: 1rem;
    padding: .9rem 1rem; border-radius: 14px; font-size: .88rem; line-height: 1.5; color: #fde68a;
    background: rgba(251, 191, 36, .08); border: 1px solid rgba(251, 191, 36, .28);
}}

/* Summary chips */
.mh-chip-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: .7rem; }}
.mh-chip {{
    padding: .75rem .9rem; border-radius: 14px; background: rgba(10,14,30,.5);
    border: 1px solid rgba(255,255,255,.09); transition: transform .25s, border-color .25s;
}}
.mh-chip:hover {{ transform: translateY(-3px); border-color: rgba(45,212,191,.5); }}
.mh-chip-k {{ color: {c['muted']}; font-size: .74rem; text-transform: uppercase; letter-spacing: .08em; }}
.mh-chip-v {{ color: {c['text']}; font-weight: 700; font-size: 1.02rem; margin-top: .2rem; word-break: break-word; }}
.mh-group-label {{ color: {c['teal']}; font-weight: 700; font-size: .82rem; letter-spacing: .1em;
                   text-transform: uppercase; margin: 1rem 0 .55rem; }}

.mh-empty {{ text-align: center; color: {c['muted']}; padding: 2.4rem 1rem; }}
.mh-empty .big {{ font-size: 2.6rem; margin-bottom: .6rem; animation: mh-float 5s ease-in-out infinite; }}

.mh-footer {{ text-align: center; color: {c['muted']}; font-size: .8rem; margin-top: 2.5rem; opacity: .8; }}

/* ---------- Animations ---------- */
@keyframes mh-rise  {{ from {{ opacity: 0; transform: translateY(16px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes mh-pop   {{ from {{ opacity: 0; transform: scale(.88) translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes mh-float {{ 0%,100% {{ transform: translateY(0) rotateX(8deg); }} 50% {{ transform: translateY(-12px) rotateX(-6deg); }} }}
@keyframes mh-pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(52,211,153,.6); }} 100% {{ box-shadow: 0 0 0 10px rgba(52,211,153,0); }} }}
@keyframes mh-spin1 {{ to {{ transform: rotateX(70deg) rotateZ(360deg); }} }}
@keyframes mh-spin2 {{ to {{ transform: rotateY(65deg) rotateZ(-360deg); }} }}
@keyframes mh-spin3 {{ to {{ transform: rotateX(-55deg) rotateY(25deg) rotateZ(360deg); }} }}

@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{ animation: none !important; transition: none !important; }}
}}

/* ---------- Mobile ---------- */
@media (max-width: 820px) {{
    .mh-hero {{ grid-template-columns: 1fr; padding: 1.6rem 1.3rem; text-align: left; }}
    .mh-orb-wrap {{ display: none; }}
    .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
}}
</style>
"""


def hero_html() -> str:
    return """
<div class="mh-hero">
  <div>
    <div class="mh-eyebrow">🧠 Machine learning · Random Forest</div>
    <h1 class="mh-title">Mental Health Score Prediction</h1>
    <p class="mh-sub">Estimate a student's mental health score from their social media habits,
       study routine, sleep and stress level. Predictions come live from your trained
       model served by FastAPI.</p>
  </div>
  <div class="mh-orb-wrap">
    <div class="mh-orb">
      <div class="mh-ring r2"></div><div class="mh-ring r1"></div>
      <div class="mh-core"></div><div class="mh-ring r3"></div>
    </div>
  </div>
</div>
"""


def section_header(icon: str, title: str, hint: str) -> str:
    return (f'<div class="mh-section-title"><span class="mh-section-icon">{icon}</span>{escape(title)}</div>'
            f'<p class="mh-section-hint">{escape(hint)}</p>')


def score_card_html(score: float, data_min: float, data_max: float, data_mean: float) -> str:
    return f"""
<div class="mh-score-card">
  <div class="mh-score-label">Predicted Mental Health Score</div>
  <div class="mh-score-value">{score:.2f}</div>
  <div class="mh-score-meta">Training data scores ranged from <b>{data_min}</b> to <b>{data_max}</b>
     (average <b>{data_mean}</b>).</div>
</div>
"""


def disclaimer_html() -> str:
    return ('<div class="mh-disclaimer">⚠️ <div>This score is a machine learning estimate based on '
            'patterns in survey data. It is <b>not a medical diagnosis</b>. If you are struggling, '
            'please talk to a qualified mental health professional.</div></div>')


def chips_html(items: dict[str, str]) -> str:
    chips = "".join(
        f'<div class="mh-chip"><div class="mh-chip-k">{escape(k)}</div>'
        f'<div class="mh-chip-v">{escape(v)}</div></div>'
        for k, v in items.items()
    )
    return f'<div class="mh-chip-grid">{chips}</div>'
