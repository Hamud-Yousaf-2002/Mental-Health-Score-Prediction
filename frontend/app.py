"""
Mental Health Score Prediction — Streamlit frontend.

Run from the project root (with FastAPI already running):
    python -m streamlit run frontend/app.py
"""

import plotly.graph_objects as go
import streamlit as st

import api_client
import styles

# ----------------------------------------------------------------------------
# Options copied from the Pydantic model `StudentData` in main.py.
# Keep these in sync with the backend; they are the only accepted values.
# ----------------------------------------------------------------------------
GENDERS = ["Male", "Female"]
ACADEMIC_LEVELS = ["High School", "Undergraduate", "Graduate"]
PLATFORMS = ["Facebook", "LinkedIn", "Instagram", "Snapchat", "Twitter", "YouTube",
             "TikTok", "LINE", "KakaoTalk", "VKontakte", "WhatsApp", "WeChat"]
PURPOSES = ["Networking", "Education", "Entertainment", "News"]
STRESS_LEVELS = ["Low", "Medium", "High", "Very High"]

# Country is a free-text field in the backend. These are the countries the
# model keeps as separate groups; anything else is grouped as "Other".
TOP_COUNTRIES = ["India", "USA", "Canada", "Australia", "UK",
                 "Germany", "Mexico", "Turkey", "France"]

# Mental_Health_Score statistics from
# "Student Social Media And Mental Health Impact.csv" (5,000 rows).
SCORE_MIN, SCORE_MAX, SCORE_MEAN = 3.6, 9.4, 6.23


# ----------------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Mental Health Score Prediction", page_icon="🧠",
                   layout="wide", initial_sidebar_state="collapsed")
st.markdown(styles.global_css(), unsafe_allow_html=True)

st.session_state.setdefault("api_base_url", api_client.DEFAULT_API_BASE_URL)
st.session_state.setdefault("result", None)   # {"score": float, "payload": dict}
st.session_state.setdefault("error", None)    # api_client.ApiResult


@st.cache_data(ttl=10, show_spinner=False)
def cached_health(base_url: str) -> api_client.ApiResult:
    """Health check, cached briefly so every rerun doesn't hit the API."""
    return api_client.check_health(base_url)


# ----------------------------------------------------------------------------
# Sidebar: API settings
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ API settings")
    st.text_input("FastAPI base URL", key="api_base_url",
                  help="Change this if the backend runs on another host or port.")
    if st.button("🔄 Recheck connection", width="stretch"):
        cached_health.clear()
    st.caption("Endpoints used: `GET /` for status, `POST /predict` for predictions.")

base_url = st.session_state.api_base_url.strip() or api_client.DEFAULT_API_BASE_URL
health = cached_health(base_url)

# ----------------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------------
st.markdown(styles.hero_html(), unsafe_allow_html=True)
if not health.ok:
    st.warning(f"**Backend unavailable:** {health.error}  \n"
               "Start it from the project folder with `python -m uvicorn main:app --reload`. "
               "This page reconnects automatically once it is up.", icon="🔌")

    @st.fragment(run_every=4)
    def wait_for_backend() -> None:
        """While disconnected, poll GET / and reload the page once it answers."""
        if api_client.check_health(base_url).ok:
            cached_health.clear()
            st.rerun(scope="app")

    wait_for_backend()


# ----------------------------------------------------------------------------
# Form
# ----------------------------------------------------------------------------
def render_form() -> dict | None:
    """Draw the input form. Returns the payload when submitted, else None."""
    with st.form("predict_form", border=False):
        with st.container(key="card-personal"):
            st.markdown(styles.section_header("👤", "Personal information",
                                              "Who the student is."), unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            age = c1.slider("Age", min_value=20, max_value=23, value=21,
                            help="The API accepts ages 20 to 23.")
            gender = c2.radio("Gender", GENDERS, horizontal=True)
            c3, c4 = st.columns(2)
            country = c3.selectbox(
                "Country", TOP_COUNTRIES + ["Other"], index=0, accept_new_options=True,
                help="Pick from the list or type any country. Countries outside the list "
                     "are grouped as 'Other' by the model.")
            academic = c4.selectbox("Academic level", ACADEMIC_LEVELS, index=1)

        with st.container(key="card-social"):
            st.markdown(styles.section_header("📱", "Social media usage",
                                              "Platform habits and screen time."),
                        unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            platform = c1.selectbox("Most used platform", PLATFORMS, index=PLATFORMS.index("Instagram"))
            purpose = c2.selectbox("Purpose of use", PURPOSES, index=PURPOSES.index("Entertainment"))
            c3, c4 = st.columns(2)
            usage = c3.slider("Avg. daily usage (hours)", 0.0, 8.8, 5.0, step=0.1,
                              help="The API accepts 0 to 8.8 hours.")
            unlocks = c4.number_input("Daily phone unlocks", min_value=0, value=80, step=1,
                                      help="How many times the phone is unlocked per day.")

        with st.container(key="card-lifestyle"):
            st.markdown(styles.section_header("🌙", "Lifestyle",
                                              "Study, movement, rest and stress."),
                        unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            study = c1.slider("Study hours / day", 0.0, 24.0, 3.0, step=0.5)
            activity = c2.slider("Physical activity hours / day", 0.0, 24.0, 1.0, step=0.5)
            sleep = c3.slider("Sleep hours / night", 0.0, 24.0, 6.5, step=0.5)
            stress = st.select_slider("Stress level", STRESS_LEVELS, value="Medium")

        submitted = st.form_submit_button("🔮  Predict Mental Health Score",
                                          disabled=not health.ok, width="stretch")

    if not submitted:
        return None

    # Client-side checks before sending
    country = (country or "").strip()
    if not country:
        st.session_state.error = api_client.ApiResult(ok=False, error="Please enter a country.")
        return None
    total = usage + study + activity + sleep
    if total > 24:
        st.toast(f"Heads up: usage, study, activity and sleep add up to {total:g} hours a day.",
                 icon="⏱️")

    # Exact JSON shape expected by StudentData
    return {
        "Age": int(age),
        "Gender": gender,
        "Country": country,
        "Academic_Level": academic,
        "Most_Used_Platform": platform,
        "Purpose_Of_Use": purpose,
        "Avg_Daily_Usage_Hours": round(float(usage), 2),
        "Daily_Unlocks": int(unlocks),
        "Study_Hours": float(study),
        "Physical_Activity_Hours": float(activity),
        "Sleep_Hours_Per_Night": float(sleep),
        "Stress_Level": stress,
    }


# ----------------------------------------------------------------------------
# Results
# ----------------------------------------------------------------------------
def gauge_figure(score: float) -> go.Figure:
    """Gauge across the training-data score range, with the dataset average marked."""
    c = styles.COLORS
    lo, hi = min(SCORE_MIN, score), max(SCORE_MAX, score)
    fig = go.Figure(go.Indicator(
        mode="gauge+delta",
        value=score,
        delta={"reference": SCORE_MEAN, "valueformat": ".2f",
               "increasing": {"color": c["teal"]}, "decreasing": {"color": c["rose"]},
               "suffix": " vs dataset avg"},
        gauge={
            "axis": {"range": [lo, hi], "tickcolor": c["muted"], "tickfont": {"color": c["muted"]}},
            "bar": {"color": c["violet"], "thickness": 0.32},
            "bgcolor": "rgba(255,255,255,0.04)",
            "borderwidth": 0,
            "steps": [{"range": [lo, hi], "color": "rgba(255,255,255,0.05)"}],
            "threshold": {"line": {"color": c["teal"], "width": 4}, "thickness": 0.85,
                          "value": SCORE_MEAN},
        },
    ))
    fig.update_layout(height=230, margin=dict(l=25, r=25, t=10, b=0),
                      paper_bgcolor="rgba(0,0,0,0)", font={"color": c["text"], "family": "DM Sans"})
    return fig


def render_results() -> None:
    err = st.session_state.error
    res = st.session_state.result

    if err is not None:
        msg = f"**{err.error}**"
        if err.details:
            msg += "\n\n" + "\n".join(f"- {d}" for d in err.details)
        st.error(msg, icon="🚫")

    if res is None:
        if err is None:
            st.markdown('<div class="mh-empty"><div class="big">🔮</div>Fill in the form and press '
                        '<b>Predict</b> to see the score here.</div>', unsafe_allow_html=True)
        return

    st.markdown(styles.score_card_html(res["score"], SCORE_MIN, SCORE_MAX, SCORE_MEAN),
                unsafe_allow_html=True)
    st.plotly_chart(gauge_figure(res["score"]), width="stretch",
                    config={"displayModeBar": False}, key="score_gauge")
    st.caption("Teal marker = dataset average score (6.23).")
    st.markdown(styles.disclaimer_html(), unsafe_allow_html=True)


def render_summary(payload: dict) -> None:
    """Show exactly which inputs produced the prediction."""
    with st.container(key="card-summary"):
        st.markdown(styles.section_header("🧾", "Input summary",
                                          "The exact values sent to POST /predict."),
                    unsafe_allow_html=True)
        groups = {
            "Personal": {
                "Age": str(payload["Age"]),
                "Gender": payload["Gender"],
                "Country": payload["Country"],
                "Model country group": payload["Country"] if payload["Country"] in TOP_COUNTRIES else "Other",
                "Academic level": payload["Academic_Level"],
            },
            "Social media": {
                "Platform": payload["Most_Used_Platform"],
                "Purpose": payload["Purpose_Of_Use"],
                "Daily usage": f'{payload["Avg_Daily_Usage_Hours"]:g} h',
                "Daily unlocks": f'{payload["Daily_Unlocks"]:,}',
            },
            "Lifestyle": {
                "Study": f'{payload["Study_Hours"]:g} h',
                "Physical activity": f'{payload["Physical_Activity_Hours"]:g} h',
                "Sleep": f'{payload["Sleep_Hours_Per_Night"]:g} h',
                "Stress level": payload["Stress_Level"],
            },
        }
        for name, items in groups.items():
            st.markdown(f'<div class="mh-group-label">{name}</div>{styles.chips_html(items)}',
                        unsafe_allow_html=True)
        with st.expander("Raw JSON request"):
            st.json(payload)


# ----------------------------------------------------------------------------
# Layout
# ----------------------------------------------------------------------------
left, right = st.columns([1.45, 1], gap="large")

with left:
    payload = render_form()

if payload is not None:
    with right, st.spinner("Asking the model…"):
        result = api_client.predict(base_url, payload)
    if result.ok:
        st.session_state.result = {"score": result.data["score"], "payload": payload}
        st.session_state.error = None
    else:
        # Keep no stale score next to new inputs; never show a fake prediction
        st.session_state.result = None
        st.session_state.error = result
        if result.status_code is None:
            cached_health.clear()  # connection problem: refresh the status pill next run

with right:
    with st.container(key="card-result"):
        st.markdown(styles.section_header("📊", "Prediction", "Live result from your model."),
                    unsafe_allow_html=True)
        render_results()

if st.session_state.result:
    render_summary(st.session_state.result["payload"])

st.markdown('<div class="mh-footer">Built with Streamlit · Powered by FastAPI and a scikit-learn '
            'Random Forest pipeline</div>', unsafe_allow_html=True)
