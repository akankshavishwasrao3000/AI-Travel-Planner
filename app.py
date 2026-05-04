import streamlit as st
import requests
import os

API_KEY = st.secrets.get("OPENROUTER_API_KEY", None) or os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    st.error("Missing OPENROUTER_API_KEY. Please set it in environment variables.")
    st.stop()

st.set_page_config(
    page_title="AI Travel Planner",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
            
.stApp {
    background-image: url("https://images.unsplash.com/photo-1539635278303-d4002c07eae3?fm=jpg&q=60&w=3000&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8c3R1ZGVudCUyMHRyYXZlbHxlbnwwfHwwfHx8MA%3D%3D");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.65);  /* Darkness level */
    backdrop-filter: blur(6px);      /* Blur effect */
    z-index: -1;
}

.main-title {
    font-size: 150px;
    font-weight: bold;
    text-align: center;
    background: linear-gradient(90deg, #ff512f, #dd2476, #1fa2ff);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientMove 6s ease infinite;
    letter-spacing: 3px;
    text-transform: uppercase;
}

@keyframes gradientMove {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.stApp::before {
    content: "";
    position: fixed;       
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.45);  /* Reduced darkness */
    z-index: -1;
}
            
.card {
    background: white;   /* Solid white for readability */
    color: #222;         /* Dark text */
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.2);
    margin-bottom: 20px;
    line-height: 1.7;    /* Better spacing for text */
    font-size: 16px;
}

.stButton>button {
    background: linear-gradient(135deg, #ff512f, #dd2476);
    color: white;
    font-weight: bold;
    border-radius: 30px;
    padding: 12px 25px;
    border: none;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0px 5px 20px rgba(255, 81, 47, 0.6);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(20,20,20,0.95), rgba(40,40,40,0.95));
    backdrop-filter: blur(10px);
    border-right: 1px solid rgba(255,255,255,0.1);
}

section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] label {
    color: white !important;
    font-weight: 500;
}

section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
    background-color: rgba(255,255,255,0.1) !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}

section[data-testid="stSidebar"] .stButton>button {
    background: linear-gradient(135deg, #ff512f, #dd2476);
    color: white;
    border-radius: 20px;
    font-weight: bold;
}
                        

</style>
""", unsafe_allow_html=True)


st.markdown('<p class="main-title">✈️ AI Travel Planner for Students</p>', unsafe_allow_html=True)
st.write("Discover destinations, costs, and personalized student travel insights using AI.")

API_KEY = st.secrets["OPENROUTER_API_KEY"]

st.sidebar.header("🌍 Trip Details")

destination = st.sidebar.text_input("Destination", "Goa")

budget = st.sidebar.selectbox(
    "Budget Level",
    ["Low", "Medium", "High"]
)

purpose = st.sidebar.selectbox(
    "Travel Purpose",
    [
        "Study Tour",
        "Adventure Trip",
        "Relaxation",
        "Cultural Exploration",
        "Food Exploration",
        "Photography"
    ]
)

if st.button("🚀 Generate Travel Guide"):

    prompt = f"""
    Create a detailed student travel guide.

    Destination: {destination}
    Budget Level: {budget}
    Travel Purpose: {purpose}

    IMPORTANT FORMAT RULES:
    - Do NOT use tables.
    - Do NOT write long paragraphs.
    - Use clear headings.
    - Use bullet points.
    - Keep each point short and structured.
    - For the budget section, show category-wise costs clearly like:
    Accommodation: ₹XXX-₹XXX
    Food: ₹XXX-₹XXX
    Transportation: ₹XXX-₹XXX
    Attractions: ₹XXX-₹XXX
    Miscellaneous: ₹XXX-₹XXX
    Total Per Day: ₹XXX-₹XXX

    Include:

    1. Overview
    2. Top Attractions
    3. Budget Breakdown (bullet format, no table)
    4. Best Time to Visit
    5. Food Recommendations
    6. Transportation Tips
    7. Safety Tips
    """



    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openrouter/auto",
        "messages": [{"role": "user", "content": prompt}]
    }

    with st.spinner("🤖 AI is generating travel guide..."):

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )

        result = response.json()["choices"][0]["message"]["content"]

        st.success("✅ Travel Guide Ready!")

        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown("### 📍 Destination Travel Guide")
            st.markdown(f"<div class='card'>{result}</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("### 💡 Student Travel Tips")

            st.markdown("""
            <div class='card'>
            ✔ Travel in groups to save money<br>
            ✔ Use public transport<br>
            ✔ Book hostels or dorms<br>
            ✔ Eat local food<br>
            ✔ Carry student ID for discounts
            </div>
            """, unsafe_allow_html=True)