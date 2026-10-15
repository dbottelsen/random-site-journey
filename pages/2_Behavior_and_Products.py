import streamlit as st

from journey_analysis import (
    build_event_table,
    calculate_page_type_performance,
    build_transition_table,
    calculate_transition_performance,
    calculate_product_performance,
    summarize_transitions_by_step,
    build_step_sankey
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

#    
#    
#    colA, colB = st.columns(2)
#
# #   with colA:
#
#        st.subheader("Page Type Performance")
#
#        st.dataframe(
#            display_page_type_table.style.format({
#                "Conversion Rate": "{:.1%}"
#            }),
#            use_container_width=True,
#            hide_index=True
#        )
#
#    with colB:
#        st.subheader("Transition Performance")
#
#        display_transition_table = (
#            display_transitions
#            .reset_index()
#            .copy()
#        )
#
#        display_transition_table["Transition"] = (
#            display_transition_table["source_page_type"]
#            .str.replace("_", " ")
#            .str.title()
#            + " → "
#            + display_transition_table["target_page_type"]
#            .str.replace("_", " ")
#            .str.title()
#        )
#
#        display_transition_table = display_transition_table[
#            [
#                "Transition",
#                "visitors",
#                "conversions",
#                "conversion_rate"
#            ]
#        ]
#
#        display_transition_table = display_transition_table.rename(
#            columns={
#                "visitors": "Visitors",
#                "conversions": "Conversions",
#                "conversion_rate": "Conversion Rate"
#            }
#        )
#
#        display_transition_table["Transition"] = (
#            display_transition_table["Transition"]
#            .str.replace("_", " ")
#            .str.title()
#        )
#
#        st.dataframe(
#            display_transition_table.style.format({
#                "Conversion Rate": "{:.1%}"
#            }),
#            use_container_width=True,
#            hide_index=True
#        )
#
    # --------------------------------------------------
    # Journey Flow
    # --------------------------------------------------

    step_transition_summary = summarize_transitions_by_step(
        events,
        site
    )

    product_performance = calculate_product_performance(
    events,
    site,
    len(journeys)
    )

    display_products = product_performance[
        product_performance["visitor_share"] >= 0.025
    ].copy()

    st.subheader("Product Performance")

    display_product_table = (
        display_products
        .reset_index()
        .copy()
    )

    display_product_table["Product"] = display_product_table["product_name"]

    display_product_table = display_product_table[
        [
            "Product",
            "visitors",
            "conversions",
            "conversion_rate",
            "visitor_share"
        ]
    ]

    display_product_table = display_product_table.rename(
        columns={
            "visitors": "Visitors",
            "conversions": "Conversions",
            "conversion_rate": "Conversion Rate",
            "visitor_share": "Visitor Share"
        }
    )

    st.dataframe(
        display_product_table.style.format({
            "Conversion Rate": "{:.1%}",
            "Visitor Share": "{:.1%}"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Journey Flow")

    sankey_fig = build_step_sankey(
        step_transition_summary,
        max_step=5,
        min_count=30
    )

    sankey_fig.update_layout(
        height=600
    )

    st.plotly_chart(
        sankey_fig,
        use_container_width=True
    )