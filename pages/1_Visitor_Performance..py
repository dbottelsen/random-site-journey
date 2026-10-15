import streamlit as st


#st.title("Visitor Performance")

from journey_analysis import (
    calculate_headline_metrics,
    calculate_segment_performance,
    build_event_table,
    calculate_page_type_performance,
    build_transition_table,
    calculate_transition_performance,
    calculate_product_performance
)

if "journeys" not in st.session_state:
    st.warning(
        "No simulation has been run yet. "
        "Return to the Simulation Setup screen and run a simulation."
    )
else:
    journeys = st.session_state.journeys

    journeys["bounced"] = (
        journeys["journey"].apply(
            lambda x: len(x) == 2 and x[1] == "exit"
        )
    )

    headline_metrics = calculate_headline_metrics(
        journeys
    )

    user_type_performance = calculate_segment_performance(
        journeys,
        "user_type"
    )

    buyer_intent_performance = calculate_segment_performance(
    journeys,
    "buyer_intent"
)

#st.subheader("Key Metrics")

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric(
    "Visitors",
    f"{headline_metrics['visitors']:,}"
)

col2.metric(
    "Bounces",
    f"{headline_metrics['bounces']:,}"
)

col3.metric(
    "Bounce Rate",
    f"{headline_metrics['bounce_rate']:.1%}"
)

col4.metric(
    "Conversions",
    f"{headline_metrics['conversions']:,}"
)

col5.metric(
    "Engaged Visitors",
    f"{headline_metrics['engaged_visitors']:,}"
)

col6.metric(
    "Engaged Conversion Rate",
    f"{headline_metrics['engaged_conversion_rate']:.1%}"
)


colA, colB = st.columns(2)

with colA:
    
    st.subheader("User Type Performance")

    display_user_type_performance = user_type_performance.rename(
        index={
            "browser": "Browser",
            "deal_seeker": "Deal Seeker",
            "direct_shopper": "Direct Shopper",
            "researcher": "Researcher"
        }
    )

    st.dataframe(
        display_user_type_performance.style.format({
            "bounce_rate": "{:.1%}",
            "engaged_conversion_rate": "{:.1%}"
        }),
        use_container_width=True
    )



with colB:

    st.subheader("Buyer Intent Performance")

    display_buyer_intent_performance = buyer_intent_performance.rename(
        index={
            "low": "Low",
            "medium": "Medium",
            "high": "High"
        }
    )

    st.dataframe(
        display_buyer_intent_performance.style.format({
            "bounce_rate": "{:.1%}",
            "engaged_conversion_rate": "{:.1%}"
        }),
        use_container_width=True
    )

if "journeys" not in st.session_state:
    st.warning(
        "No simulation has been run yet. "
        "Return to the Simulation Setup screen and run a simulation."
    )

else:
    journeys = st.session_state.journeys
    site = st.session_state.site

    # --------------------------------------------------
    # Build event table
    # --------------------------------------------------

    events = build_event_table(journeys)

    # --------------------------------------------------
    # Page Type Performance
    # --------------------------------------------------

    page_type_performance = calculate_page_type_performance(
        events,
        site
    )

    display_page_types = page_type_performance.drop(
        index=["confirmation", "cart", "checkout", "exit"]
    )

    display_page_type_table = (
        display_page_types
        .reset_index()
        .rename(
            columns={
                "page_type": "Page Type",
                "visitors": "Visitors",
                "conversions": "Conversions",
                "conversion_rate": "Conversion Rate"
            }
        )
    )

    display_page_type_table["Page Type"] = (
        display_page_type_table["Page Type"]
        .str.replace("_", " ")
        .str.title()
    )

    # --------------------------------------------------
    # Transition Performance
    # --------------------------------------------------

    transitions = build_transition_table(events)

    transition_performance = calculate_transition_performance(
        transitions,
        site,
        len(journeys)
    )

    display_transitions = transition_performance[
        (transition_performance["visitor_share"] >= 0.05) &
        (~transition_performance.index.get_level_values(
            "target_page_type"
        ).isin([
            "cart",
            "checkout",
            "confirmation",
            "exit"
        ]))
    ].copy()

    
    
    colA, colB = st.columns(2)

    with colA:

        st.subheader("Page Type Performance")

        st.dataframe(
            display_page_type_table.style.format({
                "Conversion Rate": "{:.1%}"
            }),
            use_container_width=True,
            hide_index=True
        )

    with colB:
        st.subheader("Transition Performance")

        display_transition_table = (
            display_transitions
            .reset_index()
            .copy()
        )

        display_transition_table["Transition"] = (
            display_transition_table["source_page_type"]
            .str.replace("_", " ")
            .str.title()
            + " → "
            + display_transition_table["target_page_type"]
            .str.replace("_", " ")
            .str.title()
        )

        display_transition_table = display_transition_table[
            [
                "Transition",
                "visitors",
                "conversions",
                "conversion_rate"
            ]
        ]

        display_transition_table = display_transition_table.rename(
            columns={
                "visitors": "Visitors",
                "conversions": "Conversions",
                "conversion_rate": "Conversion Rate"
            }
        )

        st.dataframe(
            display_transition_table.style.format({
                "Conversion Rate": "{:.1%}"
            }),
            use_container_width=True,
            hide_index=True
        )