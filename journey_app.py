import streamlit as st
from build_site import build_summit_outfitters
from Behaviour import all_behavior_rules
from simulation import simulate_visitors

def reset_simulation_settings():
    st.session_state.number_of_visitors = 1000
    st.session_state.browser = 35
    st.session_state.researcher = 30
    st.session_state.deal_seeker = 20
    st.session_state.direct_shopper = 15
    st.session_state.low_intent = 30
    st.session_state.medium_intent = 40
    st.session_state.high_intent = 30
    st.session_state.journeys = journeys
    st.session_state.site = site


st.set_page_config(
    page_title="Website Journey Analysis Demo",
    layout="wide"
)


st.title("Website Journey Analysis Demo")

st.write(
    """
    This interactive demonstration simulates visitor journeys through
    **Summit Outfitters**, a synthetic ecommerce website created to
    demonstrate website journey analysis.

    The site contains product categories, individual products, search,
    sale, support, account, cart, checkout, and other common ecommerce
    pages. Connections between pages define the site's structure and
    determine where a visitor can move from each page.

    Each simulated visitor is assigned a **User Type** and **Buyer Intent**.
    These characteristics influence the probability of the visitor's next
    action. The site's structure then determines which of those actions are
    actually available, producing an individual journey from landing page
    through conversion or exit.

    Use the controls below to change the number and mix of visitors, then
    select **Run Simulation**. A single simulation creates all visitor
    journeys and produces the complete Journey Analysis report.
    """
)

st.write("")
st.write("")

st.header("Simulation Settings")

number_of_visitors = st.slider(
    "Number of Visitors",
    min_value=500,
    max_value=10000,
    value=1000,
    step=500,
    key="number_of_visitors"
)

st.write(f"Simulation will create **{number_of_visitors:,} visitors**.")

st.subheader("User Type Distribution")

browser = st.slider(
    "Browser",
    min_value=0,
    max_value=100,
    value=35,
    step=5,
    key="browser"
)

researcher = st.slider(
    "Researcher",
    min_value=0,
    max_value=100,
    value=30,
    step=5,
    key="researcher"
)

deal_seeker = st.slider(
    "Deal Seeker",
    min_value=0,
    max_value=100,
    value=20,
    step=5,
    key="deal_seeker"
)

direct_shopper = st.slider(
    "Direct Shopper",
    min_value=0,
    max_value=100,
    value=15,
    step=5,
    key="direct_shopper"
)

user_type_total = (
    browser
    + researcher
    + deal_seeker
    + direct_shopper
)

if user_type_total == 100:
    st.success(f"Total: {user_type_total}%")
else:
    st.error(
        f"Total: {user_type_total}% — "
        "User Type Distribution must equal 100%."
    )

st.subheader("Buyer Intent Distribution")

low_intent = st.slider(
    "Low",
    min_value=0,
    max_value=100,
    value=30,
    step=5,
    key="low_intent"
)

medium_intent = st.slider(
    "Medium",
    min_value=0,
    max_value=100,
    value=40,
    step=5,
    key="medium_intent"
)

high_intent = st.slider(
    "High",
    min_value=0,
    max_value=100,
    value=30,
    step=5,
    key="high_intent"
)

buyer_intent_total = (
    low_intent
    + medium_intent
    + high_intent
)

if buyer_intent_total == 100:
    st.success(f"Total: {buyer_intent_total}%")
else:
    st.error(
        f"Total: {buyer_intent_total}% — "
        "Buyer Intent Distribution must equal 100%."
    )

user_type_distribution = {
    "browser": browser / 100,
    "researcher": researcher / 100,
    "deal_seeker": deal_seeker / 100,
    "direct_shopper": direct_shopper / 100
}

buyer_intent_distribution = {
    "low": low_intent / 100,
    "medium": medium_intent / 100,
    "high": high_intent / 100
}

inputs_valid = (
    user_type_total == 100
    and buyer_intent_total == 100
)

col1, col2 = st.columns(2)

with col1:
    st.button(
        "Reset to Defaults",
        on_click=reset_simulation_settings
    )

with col2:
    run_button = st.button(
        "Run Simulation",
        disabled=not inputs_valid,
        type="primary"
    )

if run_button:

    site = build_summit_outfitters()

    journeys = simulate_visitors(
        site=site,
        rules=all_behavior_rules,
        number_of_visitors=number_of_visitors,
        user_type_distribution=user_type_distribution,
        buyer_intent_distribution=buyer_intent_distribution,
        seed=42
    )

    st.session_state.site = site
    st.session_state.journeys = journeys

    st.success(
        f"Simulation complete: {len(journeys):,} visitor journeys created."
    )

    st.subheader("Simulation Summary")

    st.write(
        f"""
        **Visitors:** {number_of_visitors:,}

        **User Type Distribution**

        Browser: {browser}% | Researcher: {researcher}% | 
        Deal Seeker: {deal_seeker}% | Direct Shopper: {direct_shopper}%

        **Buyer Intent Distribution**

        Low: {low_intent}% | Medium: {medium_intent}% | High: {high_intent}%
        """
    )