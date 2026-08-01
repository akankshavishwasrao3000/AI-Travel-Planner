import streamlit as st
import requests
import os
import re
import html

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    st.error(
        "Missing OPENROUTER_API_KEY. Please set it in your environment variables."
    )
    st.stop()

st.set_page_config(
    page_title="AI Travel Planner",
    layout="wide",
    initial_sidebar_state="expanded"
)


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

/* Main section headings */
.travel-heading {
    color: #dd2476;
    font-size: 25px;
    font-weight: 800;
    margin-top: 25px;
    margin-bottom: 12px;
    border-bottom: 2px solid #dd2476;
    padding-bottom: 6px;
}

/* Place / activity names */
.travel-subheading {
    color: #1fa2ff;
    font-size: 20px;
    font-weight: 700;
    margin-top: 18px;
    margin-bottom: 5px;
}

/* Normal bullet points */
.travel-point {
    color: #333;
    margin: 5px 0;
    padding-left: 8px;
}

/* Important labels */
.travel-label {
    color: #ff512f;
    font-weight: 700;
}

/* Budget box */
.budget-box {
    background: linear-gradient(
        135deg,
        rgba(255,81,47,0.08),
        rgba(221,36,118,0.08)
    );
    border-left: 5px solid #dd2476;
    padding: 15px 20px;
    border-radius: 10px;
    margin: 10px 0 20px 0;
}

/* Budget total */
.budget-total {
    background: linear-gradient(135deg, #ff512f, #dd2476);
    color: white;
    padding: 12px 18px;
    border-radius: 10px;
    font-size: 19px;
    font-weight: bold;
    margin: 12px 0;
}

/* Normal information */
.travel-text {
    color: #333;
    margin: 7px 0;
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


def format_travel_result(text):

    text = text.replace("**", "")
    text = text.replace("*", "")

    text = re.sub(r"\[\d+\]", "", text)

    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)

    text = html.escape(text)

    lines = text.splitlines()

    output = []

    budget_section = False

    for line in lines:

        line = line.strip()

        if not line:
            continue

        heading_match = re.match(
            r"^(\d+)\.\s*(.+)$",
            line
        )

        if heading_match:

            heading_number = heading_match.group(1)
            heading_text = heading_match.group(2).strip()

            output.append(
                f"""
                <div class="travel-heading">
                    {heading_number}. {heading_text}
                </div>
                """
            )

            budget_section = (
                "BUDGET" in heading_text.upper()
                or "MONEY" in heading_text.upper()
            )

            continue

        if (
            "estimated daily total" in line.lower()
            or "estimated total for 3 days" in line.lower()
        ):

            output.append(
                f"""
                <div class="budget-total">
                    {line}
                </div>
                """
            )

            continue

        budget_keywords = [
            "accommodation:",
            "food:",
            "local transportation:",
            "transportation:",
            "attractions:",
            "miscellaneous:"
        ]

        if any(
            line.lower().startswith(keyword)
            for keyword in budget_keywords
        ):

            parts = line.split(":", 1)

            if len(parts) == 2:

                label = parts[0]
                value = parts[1]

                output.append(
                    f"""
                    <div class="travel-point">
                        <span class="travel-label">
                            {label}:
                        </span>
                        {value}
                    </div>
                    """
                )

            continue

        if line.startswith("-"):

            content = line[1:].strip()

            # Highlight labels before colon
            if ":" in content:

                parts = content.split(":", 1)

                label = parts[0]
                value = parts[1]

                output.append(
                    f"""
                    <div class="travel-point">
                        <span class="travel-label">
                            {label}:
                        </span>
                        {value}
                    </div>
                    """
                )

            else:

                output.append(
                    f"""
                    <div class="travel-point">
                        • {content}
                    </div>
                    """
                )

            continue

        label_match = re.match(
            r"^([^:]{1,50}):\s*(.*)$",
            line
        )

        if label_match:

            label = label_match.group(1).strip()
            value = label_match.group(2).strip()

            output.append(
                f"""
                <div class="travel-text">
                    <span class="travel-label">
                        {label}:
                    </span>
                    {value}
                </div>
                """
            )

            continue

        if re.match(r"^Day\s+\d+", line, re.IGNORECASE):

            output.append(
                f"""
                <div class="travel-subheading">
                    {line}
                </div>
                """
            )

            continue

        if (
            len(line) < 60
            and not line.endswith(".")
            and not line.startswith("₹")
        ):

            output.append(
                f"""
                <div class="travel-subheading">
                    {line}
                </div>
                """
            )

            continue

        output.append(
            f"""
            <div class="travel-text">
                {line}
            </div>
            """
        )

    return "\n".join(output)

st.markdown(
    '<p class="main-title">✈️ AI Travel Planner for Students</p>',
    unsafe_allow_html=True
)

st.write(
    "Discover destinations, costs, and personalized student travel insights using AI."
)

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

if st.button("🚀 Generate Travel Guide"):

    prompt = f"""
You are a professional student travel planner.

Create a practical and human-readable travel guide.

Destination: {destination}
Budget Level: {budget}
Travel Purpose: {purpose}

The information must be useful for a real student planning this trip.

IMPORTANT FORMATTING RULES:

- Do not use asterisks.
- Do not use **.
- Do not use markdown headings such as # or ##.
- Do not use citations such as [1], [2], [3].
- Do not use tables.
- Do not use emojis.
- Use numbered section headings exactly as shown below.
- Use "-" for bullet points.
- Keep sentences short and easy to understand.
- Avoid unnecessary long paragraphs.
- Give practical and realistic information.
- Do not repeat information.

IMPORTANT:
Make the budget realistic for the selected destination and budget level.

Do not invent exact prices when they vary.
Use reasonable price ranges.

For all budget calculations, make sure the totals are mathematically consistent.

Use this exact structure:

1. TRIP OVERVIEW

Give 2-3 short sentences.

- Best for:
- Recommended stay:
- Ideal trip duration:
- Main areas to explore:
- Overall experience:

2. TOP PLACES TO VISIT

Give 6-8 important places.

For each place:

Place Name
- Why visit:
- What to see:
- Approximate visit time:
- Cost:
- Student tip:

3. DAILY BUDGET

Give the estimated daily budget.

Accommodation: ₹X - ₹X
Food: ₹X - ₹X
Local Transportation: ₹X - ₹X
Attractions: ₹X - ₹X
Miscellaneous: ₹X - ₹X

Estimated Daily Total: ₹X - ₹X

- What is included:
- How to save money:

4. TOTAL TRIP BUDGET

Calculate a realistic estimated budget for 3 days.

Accommodation for 3 days: ₹X - ₹X
Food for 3 days: ₹X - ₹X
Transportation for 3 days: ₹X - ₹X
Attractions: ₹X - ₹X
Miscellaneous: ₹X - ₹X

Estimated Total for 3 Days: ₹X - ₹X

5. BEST TIME TO VISIT

- Best months:
- Best weather:
- Budget-friendly period:
- Busy period:
- Period to avoid if possible:

6. FOOD GUIDE

Breakfast
- Food option:
- Approximate cost:

Lunch
- Food option:
- Approximate cost:

Dinner
- Food option:
- Approximate cost:

Budget food tips:
- Tip:
- Tip:
- Tip:

7. TRANSPORTATION GUIDE

- Best public transport:
- Approximate daily cost:
- Payment method:
- When walking is better:
- When public transport is better:
- Transportation saving tip:

8. STUDENT-FRIENDLY ACTIVITIES

Give 5 activities.

Activity Name
- Approximate cost:
- Time required:
- Why students may enjoy it:

Include both free and paid activities.

9. SAFETY AND TRAVEL TIPS

Give 6-8 practical tips.

- Personal safety:
- Money:
- Documents:
- Mobile internet:
- Weather:
- Public transport:
- Tourist scams:
- Emergency situations:

10. QUICK 3-DAY PLAN

Day 1
Morning:
Afternoon:
Evening:

Day 2
Morning:
Afternoon:
Evening:

Day 3
Morning:
Afternoon:
Evening:

11. MONEY-SAVING TIPS

Give 6 practical tips.

- Tip:
- Tip:
- Tip:
- Tip:
- Tip:
- Tip:

12. FINAL RECOMMENDATION

Give a short 3-4 sentence recommendation.

FINAL CHECK:

- No asterisks.
- No citations.
- No tables.
- No emojis.
- No long paragraphs.
- Use numbered headings.
- Use "-" bullets.
- Use realistic costs.
- Ensure all budget totals are mathematically consistent.
- Keep the language simple and student-friendly.
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openrouter/free",

        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],

        "max_tokens": 2500,

        "temperature": 0.5
    }

    with st.spinner("🤖 AI is generating travel guide..."):

        try:

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=90
            )

            if response.status_code == 200:

                response_data = response.json()

                if (
                    "choices" in response_data
                    and len(response_data["choices"]) > 0
                    and "message" in response_data["choices"][0]
                ):

                    result = response_data["choices"][0]["message"]["content"]

                    # Format the AI response
                    formatted_result = format_travel_result(result)

                    st.success("Travel Guide Ready!")

                    col1, col2 = st.columns([3, 1])
                    with col1:

                        st.markdown(
                            "### 📍 Destination Travel Guide"
                        )

                        st.markdown(
                            f"""
                            <div class="card">
                                {formatted_result}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

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


                else:

                    st.error(
                        "The API response did not contain a travel guide."
                    )

                    st.json(response_data)

            else:

                st.error(
                    f"OpenRouter API Error: {response.status_code}"
                )

                try:

                    error_data = response.json()

                    st.json(error_data)

                except Exception:

                    st.write(response.text)

        except requests.exceptions.Timeout:

            st.error(
                "The API request timed out. Please try again."
            )

        except requests.exceptions.RequestException as e:

            st.error(
                f"Connection error: {e}"
            )

        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )