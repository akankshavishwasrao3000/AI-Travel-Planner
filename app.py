import os
import re
import requests
import streamlit as st

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    st.error(
        "Missing OPENROUTER_API_KEY. Please set it in your environment variables."
    )
    st.stop()


st.set_page_config(
    page_title="AI Travel Planner", layout="wide", initial_sidebar_state="expanded"
)


st.markdown(
    """
<style>

/* ================= BACKGROUND ================= */

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
    background: rgba(0, 0, 0, 0.35);
    z-index: -1;
}


/* ================= MAIN TITLE ================= */

.main-title {
    font-size: 55px;
    font-weight: 800;
    text-align: center;

    background: linear-gradient(
        90deg,
        #ff512f,
        #dd2476,
        #1fa2ff
    );

    background-size: 300% 300%;

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;

    animation: gradientMove 6s ease infinite;

    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 5px;
}

.sub-title {
    text-align: center;
    color: #ffffff !important;
    font-size: 18px;
    font-weight: 500;
    margin-bottom: 25px;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.9);
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


/* ================= TRANSPARENT BLACK RECTANGLE CONTAINER ================= */

div[data-testid="stColumn"] > div > div[data-testid="stVerticalBlock"] > div[data-testid="stMarkdownContainer"] {
    color: #ffffff !important;
}

/* Base Card Style for Generated Content */
.travel-guide-card {
    background: rgba(0, 0, 0, 0.75) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-radius: 18px !important;
    padding: 30px !important;
    margin-top: 10px !important;
    margin-bottom: 25px !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.6) !important;
    color: #ffffff !important;
}

/* Headings within the dark card */
.travel-guide-card h1, 
.travel-guide-card h2 {
    color: #ff512f !important;
    font-size: 26px !important;
    font-weight: 800 !important;
    letter-spacing: 1px;
    border-bottom: 2px solid rgba(255, 81, 47, 0.4);
    padding-bottom: 8px;
    margin-top: 25px !important;
    margin-bottom: 15px !important;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.8);
}

.travel-guide-card h3 {
    color: #1fa2ff !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    margin-top: 18px !important;
    margin-bottom: 10px !important;
}

/* Normal Text & Bullets inside dark card */
.travel-guide-card p, 
.travel-guide-card li {
    color: #f1f5f9 !important;
    font-size: 16px !important;
    line-height: 1.7 !important;
}

.travel-guide-card ul {
    padding-left: 22px !important;
    margin-top: 8px !important;
    margin-bottom: 18px !important;
}

.travel-guide-card li {
    margin-bottom: 8px !important;
}

.travel-guide-card strong {
    color: #ff758c !important;
    font-weight: 700 !important;
}


/* ================= BUTTON ================= */

.stButton > button {
    background: linear-gradient(
        135deg,
        #ff512f,
        #dd2476
    );
    color: white !important;
    font-weight: bold;
    border-radius: 30px;
    padding: 12px 25px;
    border: none;
    transition: 0.3s;
    width: 100%;
    font-size: 18px;
    box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.4);
}

.stButton > button:hover {
    transform: scale(1.02);
    box-shadow: 0px 5px 20px rgba(255, 81, 47, 0.6);
}


/* ================= SIDEBAR ================= */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        rgba(10, 10, 15, 0.95),
        rgba(25, 25, 35, 0.95)
    );
    backdrop-filter: blur(10px);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}

section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] label {
    color: #ffffff !important;
    font-weight: 600;
}


/* ================= RIGHT TIPS CARD (TRANSPARENT BLACK) ================= */

.tips-card {
    background: rgba(0, 0, 0, 0.75) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    color: #ffffff !important;
    padding: 25px;
    border-radius: 18px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0px 8px 25px rgba(0,0,0,0.5);
    margin-bottom: 20px;
}

.tips-title {
    color: #1fa2ff !important;
    font-size: 20px;
    font-weight: 700;
    margin-top: 15px;
    margin-bottom: 10px;
}

.tip-item {
    background: rgba(255, 255, 255, 0.08);
    color: #f1f5f9;
    border-left: 4px solid #dd2476;
    padding: 10px 12px;
    margin-bottom: 10px;
    border-radius: 6px;
    font-size: 14px;
    line-height: 1.5;
}

</style>
""",
    unsafe_allow_html=True,
)


# ================= TITLE =================

st.markdown(
    '<p class="main-title">✈️ AI Travel Planner for Students</p>',
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="sub-title">Discover destinations, budget insights, and personalized travel guides powered by AI.</p>',
    unsafe_allow_html=True,
)


# ================= SIDEBAR =================

st.sidebar.header("🌍 Trip Details")

destination = st.sidebar.text_input("Destination", "Goa")

budget = st.sidebar.selectbox("Budget Level", ["Low", "Medium", "High"])

purpose = st.sidebar.selectbox(
    "Travel Purpose",
    [
        "Study Tour",
        "Adventure Trip",
        "Relaxation",
        "Cultural Exploration",
        "Food Exploration",
        "Photography",
    ],
)


# ================= GENERATE BUTTON =================

if st.button("🚀 Generate Travel Guide"):

    prompt = f"""
First, analyze the destination input: "{destination}".

DETERMINE VALIDITY:
- Check if "{destination}" is a real geographic travel destination, city, region, state, or country.
- If it is gibberish, a random set of numbers (e.g. "78979874645"), a person's name, or a non-existent place, reply ONLY with this exact HTML structure:

<div style="text-align: center; padding: 20px;">
    <h2 style="color: #ff512f !important; border: none;">⚠️ Invalid Destination</h2>
    <p>Sorry, <strong>"{destination}"</strong> does not appear to be a recognized travel destination.</p>
    <p>Please enter a valid city, place, or tourist location in the sidebar (e.g., Goa, Manali, Jaipur, Tokyo) to generate your travel guide!</p>
</div>

IF IT IS A VALID DESTINATION:
Generate a professional, structured student travel guide for {destination} (Budget: {budget}, Purpose: {purpose}).

Format using HTML headings and bullet points for clean rendering inside a card:

<h2>📍 DESTINATION OVERVIEW</h2>
<ul>
  <li>Explain what the destination is known for.</li>
  <li>Why it fits a {purpose}.</li>
  <li>Best student-friendly areas to stay.</li>
  <li>Ideal trip duration.</li>
</ul>

<h2>🏛️ TOP ATTRACTIONS</h2>
<ul>
  <li><strong>Attraction Name 1</strong>: Description. Approx cost: ₹X</li>
  <li><strong>Attraction Name 2</strong>: Description. Approx cost: ₹X</li>
  <li><strong>Attraction Name 3</strong>: Description. Approx cost: ₹X</li>
  <li><strong>Attraction Name 4</strong>: Description. Approx cost: ₹X</li>
  <li><strong>Attraction Name 5</strong>: Description. Approx cost: ₹X</li>
</ul>

<h2>💰 BUDGET BREAKDOWN</h2>
<ul>
  <li><strong>Accommodation</strong>: ₹X - ₹Y</li>
  <li><strong>Food</strong>: ₹X - ₹Y</li>
  <li><strong>Local Transportation</strong>: ₹X - ₹Y</li>
  <li><strong>Attractions & Activities</strong>: ₹X - ₹Y</li>
  <li><strong>Miscellaneous</strong>: ₹X - ₹Y</li>
  <li><strong>Estimated Total Daily Cost</strong>: ₹X - ₹Y</li>
</ul>

<h2>☀️ BEST TIME TO VISIT</h2>
<ul>
  <li>Best months and weather conditions.</li>
  <li>Off-peak discount periods vs. peak pricing months.</li>
</ul>

<h2>🍲 LOCAL FOOD TO TRY</h2>
<ul>
  <li><strong>Dish Name 1</strong>: Description (₹Price).</li>
  <li><strong>Dish Name 2</strong>: Description (₹Price).</li>
  <li><strong>Dish Name 3</strong>: Description (₹Price).</li>
</ul>

<h2>🚆 TRANSPORTATION</h2>
<ul>
  <li>Airport and Railway connections.</li>
  <li>Daily local transport options and cheapest student modes.</li>
</ul>

<h2>💡 STUDENT TIPS & SAFETY</h2>
<ul>
  <li>5 money-saving tips for students.</li>
  <li>4 practical safety precautions.</li>
</ul>

<h2>🗓️ SAMPLE ONE-DAY ITINERARY</h2>
<ul>
  <li><strong>Morning</strong>: Planned activity.</li>
  <li><strong>Afternoon</strong>: Planned activity.</li>
  <li><strong>Evening</strong>: Planned activity.</li>
  <li><strong>Night</strong>: Planned activity.</li>
</ul>

Rules:
- Keep the exact HTML structure provided above.
- Make all prices mathematically accurate in Indian Rupees (₹).
- Do not use markdown backticks or markdown headers (##). Use HTML tags directly.
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "openrouter/auto",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4000,
        "temperature": 0.4,
    }

    with st.spinner("🤖 AI is generating your travel guide..."):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60,
            )

            if response.status_code == 200:
                response_data = response.json()
                result = response_data["choices"][0]["message"]["content"]

                # Clean up citations or unwanted markdown block symbols
                result = re.sub(r"\[\d+\]", "", result)
                result = re.sub(r"```html", "", result)
                result = re.sub(r"```", "", result)

                # Check if output is the invalid destination message
                if "Invalid Destination" in result:
                    st.warning("⚠️ Invalid input detected.")
                else:
                    st.success("✅ Travel Guide Generated Successfully!")

                col1, col2 = st.columns([3, 1])

                # MAIN GUIDE IN TRANSPARENT BLACK CARD
                with col1:
                    st.markdown(
                        f'<div class="travel-guide-card">{result}</div>',
                        unsafe_allow_html=True,
                    )

                # RIGHT SIDEBAR TIPS IN TRANSPARENT BLACK CARD
                with col2:
                    tips_html = (
                        '<div class="tips-card">'
                        '<div class="tips-title">💰 Save Money</div>'
                        '<div class="tip-item">• Compare accommodation prices before booking</div>'
                        '<div class="tip-item">• Use public transportation whenever possible</div>'
                        '<div class="tip-item">• Look for student discounts</div>'
                        '<div class="tips-title">🎒 Travel Smart</div>'
                        '<div class="tip-item">• Keep your important documents safely stored</div>'
                        '<div class="tip-item">• Carry a reusable water bottle</div>'
                        '<div class="tip-item">• Plan nearby attractions together</div>'
                        '<div class="tips-title">📱 Before You Travel</div>'
                        '<div class="tip-item">• Save important addresses offline</div>'
                        '<div class="tip-item">• Check local transport routes</div>'
                        "</div>"
                    )
                    st.markdown(tips_html, unsafe_allow_html=True)

            else:
                st.error(f"OpenRouter API Error: {response.status_code}")
                try:
                    error_data = response.json()
                    if response.status_code == 402:
                        st.warning(
                            "Your OpenRouter account does not have enough credits. Please add credits."
                        )
                    st.json(error_data)
                except Exception:
                    st.write(response.text)

        except requests.exceptions.Timeout:
            st.error("The API request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")
        except Exception as e:
            st.error(f"Something went wrong: {e}")