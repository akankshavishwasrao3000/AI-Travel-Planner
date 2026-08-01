import streamlit as st
import requests
import os


# ---------------- API KEY ----------------

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    st.error("Missing OPENROUTER_API_KEY. Please set it in your environment variables.")
    st.stop()


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Travel Planner",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>

.stApp {
    background-image: url("https://images.unsplash.com/photo-1539635278303-d4002c07eae3?fm=jpg&q=60&w=3000&auto=format&fit=crop");
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
    background: rgba(0, 0, 0, 0.45);
    z-index: -1;
}

.main-title {
    font-size: 80px;
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
    0% {
        background-position: 0% 50%;
    }

    50% {
        background-position: 100% 50%;
    }

    100% {
        background-position: 0% 50%;
    }
}

.card {
    background: white;
    color: #222;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.2);
    margin-bottom: 20px;
    line-height: 1.7;
    font-size: 16px;
}

.stButton > button {
    background: linear-gradient(135deg, #ff512f, #dd2476);
    color: white;
    font-weight: bold;
    border-radius: 30px;
    padding: 12px 25px;
    border: none;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0px 5px 20px rgba(255, 81, 47, 0.6);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        rgba(20,20,20,0.95),
        rgba(40,40,40,0.95)
    );

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

</style>
""", unsafe_allow_html=True)


# ---------------- TITLE ----------------

st.markdown(
    '<p class="main-title">✈️ AI Travel Planner for Students</p>',
    unsafe_allow_html=True
)

st.write(
    "Discover destinations, costs, and personalized student travel insights using AI."
)


# ---------------- SIDEBAR ----------------

st.sidebar.header("🌍 Trip Details")

destination = st.sidebar.text_input(
    "Destination",
    "Goa"
)

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


# ---------------- GENERATE BUTTON ----------------

if st.button("🚀 Generate Travel Guide"):

    # -------- PROMPT --------

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

For the budget section, show category-wise costs clearly like:

Accommodation: ₹XXX-₹XXX
Food: ₹XXX-₹XXX
Transportation: ₹XXX-₹XXX
Attractions: ₹XXX-₹XXX
Miscellaneous: ₹XXX-₹XXX
Total Per Day: ₹XXX-₹XXX

Include:

1. Overview
2. Top Attractions
3. Budget Breakdown
4. Best Time to Visit
5. Food Recommendations
6. Transportation Tips
7. Safety Tips
"""


    # -------- API HEADERS --------

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }


    # -------- API DATA --------

    data = {
        "model": "openrouter/auto",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }


    # -------- API REQUEST --------

    with st.spinner("🤖 AI is generating travel guide..."):

        try:

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )


            # -------- SUCCESS --------

            if response.status_code == 200:

                response_data = response.json()

                result = response_data["choices"][0]["message"]["content"]

                st.success("✅ Travel Guide Ready!")


                # -------- COLUMNS --------

                col1, col2 = st.columns([3, 1])


                # -------- TRAVEL GUIDE --------

                with col1:

                    st.markdown(
                        "### 📍 Destination Travel Guide"
                    )

                    st.markdown(
                        f"""
                        <div class="card">
                        {result}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                # -------- TRAVEL TIPS --------

                with col2:

                    st.markdown(
                        "### 💡 Student Travel Tips"
                    )

                    st.markdown(
                        """
                        <div class="card">

                        ✔ Travel in groups to save money<br><br>

                        ✔ Use public transport<br><br>

                        ✔ Book hostels or dorms<br><br>

                        ✔ Eat local food<br><br>

                        ✔ Carry student ID for discounts

                        </div>
                        """,
                        unsafe_allow_html=True
                    )


            # -------- API ERROR --------

            else:

                st.error(
                    f"OpenRouter API Error: {response.status_code}"
                )

                try:
                    st.json(response.json())

                except Exception:
                    st.write(response.text)


        # -------- CONNECTION ERROR --------

        except requests.exceptions.Timeout:

            st.error(
                "The API request timed out. Please try again."
            )


        except requests.exceptions.RequestException as e:

            st.error(
                f"Connection error: {e}"
            )


        # -------- OTHER ERROR --------

        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )