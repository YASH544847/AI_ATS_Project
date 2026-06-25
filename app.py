import streamlit as st
import pandas as pd
import joblib
import os
from groq_helper import generate_questions
from pdf_generator import create_pdf


# --- Paths for models and data ---
DATA_FILE = "cleaned_interview_dataset.csv"
MODEL_ROUND_FILE = "model_round.pkl"
MODEL_DIFFICULTY_FILE = "model_difficulty.pkl"
MODEL_ROUNDTYPE_FILE = "model_roundtype.pkl"
LE_COMPANY_FILE = "le_company.pkl"
LE_ROLE_FILE = "le_role.pkl"
LE_EXP_FILE = "le_exp.pkl"
LE_ROUNDTYPE_FILE = "le_roundtype.pkl"
LE_DIFFICULTY_FILE = "le_difficulty.pkl"

# Check if files exist
if not os.path.exists(DATA_FILE):
    st.error(f"Error: Data file '{DATA_FILE}' not found. Please ensure it's in the same directory as the app.")
    st.stop()

for f in [MODEL_ROUND_FILE, MODEL_DIFFICULTY_FILE, MODEL_ROUNDTYPE_FILE, LE_COMPANY_FILE, LE_ROLE_FILE, LE_EXP_FILE, LE_ROUNDTYPE_FILE, LE_DIFFICULTY_FILE]:
    if not os.path.exists(f):
        st.error(f"Error: Model/Encoder file '{f}' not found. Please ensure all .pkl files are in the same directory as the app.")
        st.stop()

# ==========================
# LOAD DATA, MODELS AND ENCODERS
# ==========================

@st.cache_data 
def load_data(file_path):
    return pd.read_csv(file_path)

df = load_data(DATA_FILE)

@st.cache_resource 
def load_model_and_encoders():
    model_round = joblib.load(MODEL_ROUND_FILE)
    model_difficulty = joblib.load(MODEL_DIFFICULTY_FILE)
    model_roundtype = joblib.load(MODEL_ROUNDTYPE_FILE)

    le_company = joblib.load(LE_COMPANY_FILE)
    le_role = joblib.load(LE_ROLE_FILE)
    le_exp = joblib.load(LE_EXP_FILE)
    le_roundtype = joblib.load(LE_ROUNDTYPE_FILE)
    le_difficulty = joblib.load(LE_DIFFICULTY_FILE)
    return model_round, model_difficulty, model_roundtype, le_company, le_role, le_exp, le_roundtype, le_difficulty

model_round, model_difficulty, model_roundtype, le_company, le_role, le_exp, le_roundtype, le_difficulty = load_model_and_encoders()

unique_company_names = sorted(df['Company_name'].dropna().unique())

# ==========================
# PREDICTION FUNCTIONS
# ==========================

def predict_total_rounds(company_type, role, experience):
    sample = pd.DataFrame({
        "Company_type": [company_type],
        "Job_role": [role],
        "Experience_level": [experience]
    })
    sample["Company_type"] = le_company.transform(sample["Company_type"])
    sample["Job_role"] = le_role.transform(sample["Job_role"])
    sample["Experience_level"] = le_exp.transform(sample["Experience_level"])
    prediction = model_round.predict(sample)
    return int(prediction[0])

def predict_difficulty(company_type, role, experience):
    sample = pd.DataFrame({
        "Company_type": [company_type],
        "Job_role": [role],
        "Experience_level": [experience]
    })
    sample["Company_type"] = le_company.transform(sample["Company_type"])
    sample["Job_role"] = le_role.transform(sample["Job_role"])
    sample["Experience_level"] = le_exp.transform(sample["Experience_level"])
    prediction = model_difficulty.predict(sample)
    return le_difficulty.inverse_transform(prediction)[0]

def predict_round_type(company_type, role, experience, round_no):
    sample = pd.DataFrame({
        "Company_type": [company_type],
        "Job_role": [role],
        "Experience_level": [experience],
        "Round_no": [round_no]
    })
    sample["Company_type"] = le_company.transform(sample["Company_type"])
    sample["Job_role"] = le_role.transform(sample["Job_role"])
    sample["Experience_level"] = le_exp.transform(sample["Experience_level"])
    prediction = model_roundtype.predict(sample)
    return le_roundtype.inverse_transform(prediction)[0]

def predict_round_flow(company_type, role, experience, total_rounds):
    round_flow = []
    for r in range(1, total_rounds + 1):
        round_name = predict_round_type(company_type, role, experience, r)
        round_flow.append(round_name)
    return round_flow

def recommend_topics(company, role, top_n=10):
    if company and role:
        result = df[(df["Company_name"] == company) & (df["Job_role"] == role)]
        if not result.empty:
            topics = result["Topics"].value_counts()
            return (topics / topics.sum() * 100).round(2).head(top_n)

    if company:
        result = df[df["Company_name"] == company]
        if not result.empty:
            topics = result["Topics"].value_counts()
            return (topics / topics.sum() * 100).round(2).head(top_n)

    if role:
        result = df[df["Job_role"] == role]
        if not result.empty:
            topics = result["Topics"].value_counts()
            return (topics / topics.sum() * 100).round(2).head(top_n)

    topics = df["Topics"].value_counts()
    return (topics / topics.sum() * 100).round(2).head(top_n)

def predict_interview(company_name, company_type, role, experience):
    total_rounds = predict_total_rounds(company_type, role, experience)
    difficulty = predict_difficulty(company_type, role, experience)
    round_flow = predict_round_flow(company_type, role, experience, total_rounds)
    topics = recommend_topics(company_name, role)
    return {
        "Total Rounds": total_rounds,
        "Difficulty": difficulty,
        "Round Flow": round_flow,
        "Topics": topics
    }

# ==========================
# STREAMLIT UI
# ==========================

st.set_page_config(layout="wide", page_title="AI-ATS Interview Predictor", initial_sidebar_state="auto")

col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:
    st.title("AI-ATS Interview Predictor")
    st.markdown("Unlock your interview potential with AI-ATS! This tool predicts interview rounds, difficulty, flow, and relevant topics based on company type, role, and experience. \n\n**How it works:** Simply input your desired company, job role, and experience level below, then click 'Predict Interview' to get instant insights.")

    st.header("Input Your Details")

    company_name = st.selectbox(
        "🏢 Company Name",
        options=[''] + unique_company_names,
        index=0,
        help="Select a company from the list or type to filter."
    )

    if company_name == '':
        st.warning("Please select a Company Name.")

    company_type = st.selectbox(
        "💼 Company Type",
        list(le_company.classes_)
    )

    job_role = st.selectbox(
        "🧑‍💻 Job Role",
        list(le_role.classes_)
    )

    experience = st.selectbox(
        "🎓 Experience Level",
        list(le_exp.classes_)
    )
    
    # FIX: Actually defining the prediction button inside the center column layout
    predict_btn = st.button("🔮 Predict Interview", type="primary")

# ==========================
# OUTPUT (Kept outside columns for wider results display, or indent it into `with col_center:` if preferred)
# ==========================

if predict_btn:
    if not company_name:
        st.error("❌ Please select a Company Name from the dropdown.")
        st.stop()

    with st.spinner("🔮 Predicting your interview insights..."):
        result = predict_interview(
            company_name,
            company_type,
            job_role,
            experience
        )

    # Save prediction in session_state
    st.session_state.result = result

# -------------------------------
# Show prediction if available
# -------------------------------

if "result" in st.session_state:
    result = st.session_state.result

    st.markdown("## ✨ Prediction Results")

    with st.container(border=True):
        st.markdown("### 📊 Key Insights")
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Total Rounds Expected",
                result["Total Rounds"]
            )

        with col2:
            st.metric(
                "Overall Difficulty",
                result["Difficulty"]
            )

    st.markdown("### 📋 Predicted Round Flow")

    with st.container(border=True):
        for i, round_name in enumerate(result["Round Flow"], start=1):
            st.markdown(f"**Round {i}:** `{round_name}`")

    st.markdown("### 📚 Key Topics to Prepare")

    with st.container(border=True):
        topics = result["Topics"]

        if topics is not None and not topics.empty:
            for topic, percent in topics.items():
                st.markdown(f"**{topic}** - `{percent}%`")
                st.progress(min(int(float(percent)), 100)) # Cast to float safely before int conversion

    # ---------------------------
    # AI Questions
    # ---------------------------


    st.markdown("---")
    st.markdown("## 🤖 AI Interview Coach")

if "ai_questions" not in st.session_state:
    st.session_state["ai_questions"] = ""

if st.button("🚀 Generate Expected Questions"):

    prompt = f"""
    You are an interview expert.

    Company: {company_name}

    Role: {job_role}

    Difficulty: {result['Difficulty']}

    Round Flow: {result['Round Flow']}

    Topics: {list(result['Topics'].keys())}

    Generate exactly 5 interview questions
    for each round.
    """

    with st.spinner("Generating Questions..."):

        questions = generate_questions(prompt)

        st.session_state["ai_questions"] = questions

        pdf_file = create_pdf(
            company_name,
            job_role,
            experience,
            result,
            questions
        )

        st.session_state["pdf_file"] = pdf_file


if "pdf_file" in st.session_state:

    with open(
        st.session_state["pdf_file"],
        "rb"
    ) as file:

        st.download_button(
            label="📄 Download Interview Report PDF",
            data=file,
            file_name="Interview_Report.pdf",
            mime="application/pdf"
        )


if "ai_questions" in st.session_state and st.session_state["ai_questions"]:

    st.markdown("## 🎯 Expected Interview Questions")

    st.markdown(
        st.session_state["ai_questions"]
    )