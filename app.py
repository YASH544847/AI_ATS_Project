import streamlit as st
import pandas as pd
import joblib
import os

# --- Paths for models and data ---
# Ensure these files are in the same directory as this script
DATA_FILE = "cleaned_interview_dataset.csv"
MODEL_ROUND_FILE = "model_round.pkl"
MODEL_DIFFICULTY_FILE = "model_difficulty.pkl"
MODEL_ROUNDTYPE_FILE = "model_roundtype.pkl"
LE_COMPANY_FILE = "le_company.pkl"
LE_ROLE_FILE = "le_role.pkl"
LE_EXP_FILE = "le_exp.pkl"
LE_ROUNDTYPE_FILE = "le_roundtype.pkl"
LE_DIFFICULTY_FILE = "le_difficulty.pkl"

# Check if files exist (optional, for debugging)
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

@st.cache_data # Cache the dataframe loading for performance
def load_data(file_path):
    return pd.read_csv(file_path)

df = load_data(DATA_FILE)

@st.cache_resource # Cache model loading for performance
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

# Get unique company names for display
unique_company_names = sorted(df['Company_name'].unique())

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
    result = df[
        (df["Company_name"] == company) &
        (df["Job_role"] == role)
    ]
    if len(result) > 0:
        topics = result["Topics"].value_counts()
        topic_percent = (topics / topics.sum() * 100).round(2)
        return topic_percent.head(top_n)

    result = df[df["Company_name"] == company]
    if len(result) > 0:
        topics = result["Topics"].value_counts()
        topic_percent = (topics / topics.sum() * 100).round(2)
        return topic_percent.head(top_n)

    result = df[df["Job_role"] == role]
    if len(result) > 0:
        topics = result["Topics"].value_counts()
        topic_percent = (topics / topics.sum() * 100).round(2)
        return topic_percent.head(top_n)

    topics = df["Topics"].value_counts()
    topic_percent = (topics / topics.sum() * 100).round(2)
    return topic_percent.head(top_n)

def predict_interview(
    company_name, company_type, role, experience
):
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

# Custom CSS for styling (Darker theme with orange accents)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: #ecf0f1; /* Light gray for general text */
    }
    .main {
        background: linear-gradient(to right, #2c3e50, #34495e); /* Dark blue-gray gradient background */
        padding: 20px;
        border-radius: 8px;
    }
    .stApp {
        background: linear-gradient(to right, #2c3e50, #34495e);
    }
    .stButton>button {
        background-color: #e67e22; /* Orange */
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        border: none;
        transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .stButton>button:hover {
        background-color: #d35400; /* Darker orange */
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        border-radius: 8px;
        border: 1px solid #7f8c8d; /* Muted gray border */
        padding: 8px;
        background-color: #3f5567; /* Slightly lighter dark background for inputs */
        color: #ecf0f1; /* Light text in inputs */
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
        transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
    }
    .stTextInput>div>div>input:focus, .stSelectbox>div>div>select:focus {
        border-color: #e67e22; /* Orange focus */
        outline: 0;
        box-shadow: 0 0 0 0.2rem rgba(230, 126, 34, 0.25);
    }
    h1, h2, h3, h4, h5, h6 {
        color: #f39c12; /* Orange for headings */
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    .stMetric > div[data-testid="stMetricLabel"] > div {
        font-size: 1.1em;
        color: #bdc3c7; /* Muted gray for labels */
        font-weight: 400;
    }
    .stMetric > div[data-testid="stMetricValue"] {
        font-size: 2.2em;
        font-weight: 600;
        color: #f1c40f; /* Yellowish orange for values */
    }
    .result-card {
        background-color: #34495e; /* Darker background for result card */
        border-left: 5px solid #e67e22; /* Orange accent */
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
        margin-bottom: 20px;
    }
    .stProgress > div > div > div > div {
        background-color: #e67e22 !important; /* Orange for progress bar */
    }
    .sidebar .sidebar-content {
        background-color: #2c3e50; /* Dark blue-gray for sidebar */
        padding: 20px;
        border-right: 1px solid #34495e;
    }
    .stAlert {
        border-radius: 8px;
        background-color: #444; /* Darker alert background */
        color: #ecf0f1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Use columns to center the main content area
col_left, col_center, col_right = st.columns([1, 2, 1]) # Adjust ratios as needed

with col_center:
    st.title("AI-ATS Interview Predictor") # Removed emoji
    st.markdown("Unlock your interview potential with AI-ATS! This tool predicts interview rounds, difficulty, flow, and relevant topics based on company type, role, and experience. \n\n**How it works:** Simply input your desired company, job role, and experience level below, then click 'Predict Interview' to get instant insights.")

    st.header("Input Your Details") # Removed emoji

    company_name = st.selectbox(
        "🏢 Company Name",
        options=[''] + unique_company_names, # Add an empty option
        index=0, # Default to the empty option
        help="Select a company from the list or type to filter."
    )

    # Display a warning if no company is selected after prediction attempt
    if company_name == '':
        st.warning("Please select a Company Name.") # Removed arrow, as per previous fix

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

    st.markdown("--- Say Hi! --- 👋")
    predict_btn = st.button("🚀 Predict Interview")

    st.markdown("---")
    with st.expander("Available Companies for Reference"): # Removed emoji
        st.write("Here's a list of companies in our dataset:")
        for company in unique_company_names:
            st.markdown(f"- `{company}`") # Use code block for company names


    # ==========================
    # OUTPUT
    # ==========================

    if predict_btn:
        if not company_name:
            st.error("❌ Please select a Company Name from the dropdown before predicting.")
        else:
            with st.spinner("🔮 Predicting your interview insights..."):
                result = predict_interview(
                    company_name, company_type, job_role, experience
                )

            st.markdown("## ✨ Prediction Results")

            # Use a container for better visual grouping
            with st.container(border=True):
                st.markdown("### Key Insights")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label="Total Rounds Expected", value=result['Total Rounds'])
                with col2:
                    st.metric(label="Overall Difficulty", value=result['Difficulty'])

            st.markdown("### 📋 Predicted Round Flow")
            with st.container(border=True):
                for i, round_name in enumerate(result["Round Flow"], start=1):
                    st.markdown(f"**Round {i}:** `{round_name}`")

            st.markdown("### 📚 Key Topics to Prepare")
            with st.container(border=True):
                topics = result["Topics"]
                if not topics.empty:
                    for topic, percent in topics.items():
                        st.markdown(f"**{topic}** - `{percent}%` ")
                        st.progress(min(int(percent), 100))
                else:
                    st.info("ℹ️ No specific topics found for this company and role combination in our dataset. Displaying general top topics:")
                    global_topics = recommend_topics("", "") # Get global topics
                    for topic, percent in global_topics.items():
                        st.markdown(f"**{topic}** - `{percent}%` ")
                        st.progress(min(int(percent), 100))

    st.markdown("--- Developed by Yash Raygade --- ")