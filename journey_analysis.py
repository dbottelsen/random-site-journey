import pandas as pd
import plotly.graph_objects as go

from plotly.subplots import make_subplots


def build_event_table(journeys):

    events = []

    for _, row in journeys.iterrows():

        for step_number, page_id in enumerate(row["journey"]):

            events.append({
                "visitor_id": row["visitor_id"],
                "user_type": row["user_type"],
                "buyer_intent": row["buyer_intent"],
                "step": step_number,
                "page_id": page_id,
                "converted": row["converted"],
                "end_reason": row["end_reason"]
            })

    return pd.DataFrame(events)

def build_transition_table(events):

    transitions = events.copy()

    transitions["next_page_id"] = (
        transitions
        .groupby("visitor_id")["page_id"]
        .shift(-1)
    )

    transitions = transitions.dropna(
        subset=["next_page_id"]
    )

    return transitions

def summarize_transitions(transitions):

    summary = (
        transitions
        .groupby(["page_id", "next_page_id"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .reset_index(drop=True)
    )

    return summary

def summarize_transitions_by_page_type(transitions, site):

    page_type_map = (
        site.pages
        .set_index("page_id")["page_type"]
        .to_dict()
    )

    summary = transitions.copy()

    summary["page_type"] = summary["page_id"].map(page_type_map)
    summary["next_page_type"] = summary["next_page_id"].map(page_type_map)

    summary = (
        summary
        .groupby(["page_type", "next_page_type"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .reset_index(drop=True)
    )

    return summary

def build_sankey_old(
    transition_summary,
    source_col="page_id",
    target_col="next_page_id"
):

    source_pages = transition_summary[source_col].tolist()
    target_pages = transition_summary[target_col].tolist()

    all_pages = list(
        dict.fromkeys(source_pages + target_pages)
    )

    page_to_index = {
        page: i
        for i, page in enumerate(all_pages)
    }

    source_indices = [
        page_to_index[page]
        for page in source_pages
    ]

    target_indices = [
        page_to_index[page]
        for page in target_pages
    ]

    values = transition_summary["count"].tolist()

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    label=all_pages
                ),
                link=dict(
                    source=source_indices,
                    target=target_indices,
                    value=values
                )
            )
        ]
    )

    fig.update_layout(
        title_text="Summit Outfitters Visitor Journeys",
        font_size=10
    )

    return fig

def build_sankey(
    transition_summary,
    source_col="page_id",
    target_col="next_page_id"
):

    source_pages = transition_summary[source_col].tolist()
    target_pages = transition_summary[target_col].tolist()

    all_pages = list(dict.fromkeys(source_pages + target_pages))

    page_to_index = {
        page: i
        for i, page in enumerate(all_pages)
    }

    source_indices = [
        page_to_index[page]
        for page in source_pages
    ]

    target_indices = [
        page_to_index[page]
        for page in target_pages
    ]

    values = transition_summary["count"].tolist()

    x_positions = []
    y_positions = []

    checkout_positions = {
        "checkout_shipping": 0.58,
        "checkout_payment": 0.70,
        "checkout_review": 0.82,
        "confirmation": 0.94
    }

    for page in all_pages:

        if page in checkout_positions:
            x_positions.append(checkout_positions[page])
            y_positions.append(0.50)

        else:
            x_positions.append(None)
            y_positions.append(None)

    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    label=all_pages,
                    x=x_positions,
                    y=y_positions
                ),
                link=dict(
                    source=source_indices,
                    target=target_indices,
                    value=values
                )
            )
        ]
    )

    fig.update_layout(
        title_text="Summit Outfitters Visitor Journeys",
        font_size=14,
        width=1000,
        height=700
    )

    return fig

def summarize_transitions_for_sankey(transitions, site):

    page_type_map = (
        site.pages
        .set_index("page_id")["page_type"]
        .to_dict()
    )

    def display_node(page_id):
        page_type = page_type_map[page_id]

        if page_type == "checkout":
            return page_id

        return page_type

    summary = transitions.copy()

    summary["source_node"] = summary["page_id"].apply(display_node)
    summary["target_node"] = summary["next_page_id"].apply(display_node)

    summary = (
        summary
        .groupby(["source_node", "target_node"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .reset_index(drop=True)
    )

    return summary

def summarize_transitions_by_step(events, site):

    page_type_map = (
        site.pages
        .set_index("page_id")["page_type"]
        .to_dict()
    )

    step_events = events.copy()

    step_events["display_node"] = step_events["page_id"].map(page_type_map)

    checkout_mask = step_events["display_node"] == "checkout"

    step_events.loc[checkout_mask, "display_node"] = (
        step_events.loc[checkout_mask, "page_id"]
    )

    step_events["next_step"] = (
        step_events
        .groupby("visitor_id")["step"]
        .shift(-1)
    )

    step_events["next_display_node"] = (
        step_events
        .groupby("visitor_id")["display_node"]
        .shift(-1)
    )

    step_summary = step_events.dropna(
        subset=["next_display_node"]
    ).copy()

    step_summary["source_node"] = (
        "Step "
        + step_summary["step"].astype(str)
        + ": "
        + step_summary["display_node"]
    )

    step_summary["target_node"] = (
        "Step "
        + step_summary["next_step"].astype(int).astype(str)
        + ": "
        + step_summary["next_display_node"]
    )

    step_summary = (
        step_summary
        .groupby(["source_node", "target_node"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .reset_index(drop=True)
    )

    return step_summary

def build_step_sankey(
    step_transition_summary,
    max_step=7,
    min_count=10
):

    summary = step_transition_summary[
       step_transition_summary["count"] >= min_count
    ].copy()

    def get_step(node_label):
        return int(
            node_label
            .split(":")[0]
            .replace("Step ", "")
        )

    summary["source_step"] = (
        summary["source_node"]
        .apply(get_step)
    )

    summary["target_step"] = (
        summary["target_node"]
        .apply(get_step)
    )

    summary = summary[
        (summary["source_step"] <= max_step) &
        (summary["target_step"] <= max_step)
    ].copy()

    source_nodes = summary["source_node"].tolist()
    target_nodes = summary["target_node"].tolist()

    all_nodes = list(
        dict.fromkeys(source_nodes + target_nodes)
    )

    node_to_index = {
        node: i
        for i, node in enumerate(all_nodes)
    }

    source_indices = [
        node_to_index[node]
        for node in source_nodes
    ]

    target_indices = [
        node_to_index[node]
        for node in target_nodes
    ]

    values = summary["count"].tolist()

    x_positions = []

    for node in all_nodes:
        step = get_step(node)

        if max_step == 0:
            x = 0.0
        else:
            x = step / max_step

        x_positions.append(x)

        node_colors = []

    for node in all_nodes:

        page_type = node.split(": ", 1)[1]

        color_map = {
            "home": "#9ECAE1",
            "category": "#A1D99B",
            "product": "#FDD0A2",
            "sale": "#FDC086",
            "recommendation": "#C7B9E8",
            "search": "#9EDAE5",
            "search_results": "#F6D88A",
            "support": "#F4A6A6",
            "account": "#C7C7C7",
            "cart": "#A6D8D8",
            "checkout_shipping": "#F4B6C2",
            "checkout_payment": "#F4B6C2",
            "checkout_review": "#F4B6C2",
            "confirmation": "#D9B8E8",
            "exit": "#C7C7C7"
        }

        node_colors.append(
            color_map.get(page_type, "#D0D0D0")
        )


    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",

                node=dict(
                    label=all_nodes,
                    color=node_colors,
                    x=x_positions,
                    pad=15,
                    thickness=18,
                    line=dict(
                        color="#888888",
                        width=1
                    )
                ),

                textfont=dict(
                    color="#24324A",
                    size=12
                ),

                link=dict(
                    source=source_indices,
                    target=target_indices,
                    value=values
                )
            )
        ]
    )

    fig.update_layout(
        title_text=(
            f"Summit Outfitters Visitor Journeys "
            f"— Steps 0 to {max_step}"
        ),
        font_size=12,
        width=1400,
        height=800
    )

    return fig

def summarize_journeys(journeys):

    summary = {
        "visitors": len(journeys),

        "conversion_rate": journeys["converted"].mean(),

        "average_steps": journeys["steps"].mean(),

        "median_steps": journeys["steps"].median(),

        "exit_rate": (
            journeys["end_reason"] == "exit"
        ).mean()
    }

    return summary

def add_engagement_steps(journeys, events, site):

    engagement_page_types = [
        "category",
        "search",
        "search_results",
        "product"
    ]

    page_type_map = (
        site.pages
        .set_index("page_id")["page_type"]
        .to_dict()
    )

    engagement_events = events.copy()

    engagement_events["page_type"] = (
        engagement_events["page_id"]
        .map(page_type_map)
    )

    engagement_counts = (
        engagement_events[
            engagement_events["page_type"].isin(
                engagement_page_types
            )
        ]
        .groupby("visitor_id")
        .size()
        .rename("engagement_steps")
    )

    result = journeys.merge(
        engagement_counts,
        on="visitor_id",
        how="left"
    )

    result["engagement_steps"] = (
        result["engagement_steps"]
        .fillna(0)
        .astype(int)
    )

    return result

def calculate_headline_metrics(journeys):

    number_of_visitors = len(journeys)

    number_of_bounces = journeys["bounced"].sum()

    bounce_rate = (
        number_of_bounces / number_of_visitors
    )

    number_of_engaged_visitors = (
        number_of_visitors - number_of_bounces
    )

    number_of_conversions = journeys["converted"].sum()

    engaged_conversion_rate = (
        number_of_conversions / number_of_engaged_visitors
    )

    return {
        "visitors": int(number_of_visitors),
        "bounces": int(number_of_bounces),
        "bounce_rate": round(float(bounce_rate), 3),
        "conversions": int(number_of_conversions),
        "engaged_visitors": int(number_of_engaged_visitors),
        "engaged_conversion_rate": round(float(engaged_conversion_rate), 3)
    }

def display_headline_metrics(headline_metrics):

    fig = go.Figure()

    metrics = [
        {
            "key": "visitors",
            "label": "Visitors",
            "format": ","
        },
        {
            "key": "bounces",
            "label": "Bounces",
            "format": ","
        },
        {
            "key": "bounce_rate",
            "label": "Bounce Rate",
            "format": ".1%"
        },
        {
            "key": "conversions",
            "label": "Conversions",
            "format": ","
        },
        {
            "key": "engaged_visitors",
            "label": "Engaged Visitors",
            "format": ","
        },
        {
            "key": "engaged_conversion_rate",
            "label": "Engaged Conversion Rate",
            "format": ".1%"
        }
    ]

    for i, metric in enumerate(metrics):

        row = i // 3
        col = i % 3

        x_start = col / 3
        x_end = (col + 1) / 3

        if row == 0:
            y_start = 0.5
            y_end = 1.0
        else:
            y_start = 0.0
            y_end = 0.5

        fig.add_shape(
            type="rect",
            xref="paper",
            yref="paper",
            x0=x_start + 0.01,
            x1=x_end - 0.01,
            y0=y_start + 0.03,
            y1=y_end - 0.03,
            line={
                "color": "lightgray",
                "width": 1
            },
            fillcolor="#E8E8E8",
            layer="below"
        )

        fig.add_trace(
            go.Indicator(
                mode="number",
                value=headline_metrics[metric["key"]],
                number={
                    "valueformat": metric["format"],
                        "font": {
                            "size": 40
                        }
                },
                domain={
                    "x": [x_start, x_end],
                    "y": [y_start, y_end - 0.08]
                }
            )
        )

        fig.add_annotation(
            x=(x_start + x_end) / 2,
            y=y_end - 0.08,
            xref="paper",
            yref="paper",
            text=metric["label"],
            showarrow=False,
            font={
                "size": 16
            },
            xanchor="center",
            yanchor="top"
        )

        fig.update_layout(
            height=300,
            margin={
                "l": 20,
                "r": 20,
                "t": 10,
                "b": 10
            }
        )

    fig.show()

def calculate_segment_performance(journeys, segment):

    performance = (
        journeys
        .groupby(segment)
        .agg(
            visitors=("visitor_id", "count"),
            bounces=("bounced", "sum"),
            conversions=("converted", "sum")
        )
    )

    performance["engaged_visitors"] = (
        performance["visitors"]
        - performance["bounces"]
    )

    performance["engaged_conversion_rate"] = (
        performance["conversions"]
        / performance["engaged_visitors"]
    ).round(3)

    performance["bounce_rate"] = (
    performance["bounces"]
    / performance["visitors"]
    ).round(3)

    performance = performance[
    [
        "visitors",
        "bounces",
        "bounce_rate",
        "conversions",
        "engaged_visitors",
        "engaged_conversion_rate"
    ]
    ]

    return performance

def calculate_exit_distribution(journeys, site):

    engaged_nonconverters = journeys[
        (~journeys["bounced"]) &
        (~journeys["converted"])
    ].copy()

    engaged_nonconverters["last_page_before_exit"] = (
        engaged_nonconverters["journey"]
        .apply(lambda x: x[-2])
    )

    page_type_map = (
        site.pages
        .set_index("page_id")["page_type"]
        .to_dict()
    )

    engaged_nonconverters["last_page_type_before_exit"] = (
        engaged_nonconverters["last_page_before_exit"]
        .map(page_type_map)
    )

    exit_distribution = (
        engaged_nonconverters["last_page_type_before_exit"]
        .value_counts()
        .rename_axis("page_type")
        .reset_index(name="exits")
    )

    exit_distribution["percent_of_exits"] = (
        exit_distribution["exits"]
        / exit_distribution["exits"].sum()
    ).round(3)

    return exit_distribution

def calculate_page_type_performance(events, site):

    page_type_map = (
        site.pages
        .set_index("page_id")["page_type"]
        .to_dict()
    )

    page_type_events = events.copy()

    page_type_events["page_type"] = (
        page_type_events["page_id"]
        .map(page_type_map)
    )

    page_type_visitors = (
        page_type_events[
            ["visitor_id", "page_type", "converted"]
        ]
        .drop_duplicates(
            subset=["visitor_id", "page_type"]
        )
    )

    performance = (
        page_type_visitors
        .groupby("page_type")
        .agg(
            visitors=("visitor_id", "count"),
            conversions=("converted", "sum")
        )
    )

    performance["conversion_rate"] = (
        performance["conversions"]
        / performance["visitors"]
    ).round(3)

    return performance.sort_values(
        "conversion_rate",
        ascending=False
    )

def calculate_transition_performance(
    transitions,
    site,
    total_visitors
):

    page_type_map = (
        site.pages
        .set_index("page_id")["page_type"]
        .to_dict()
    )

    transition_performance = transitions.copy()

    transition_performance["source_page_type"] = (
        transition_performance["page_id"]
        .map(page_type_map)
    )

    transition_performance["target_page_type"] = (
        transition_performance["next_page_id"]
        .map(page_type_map)
    )

    transition_visitors = (
        transition_performance[
            [
                "visitor_id",
                "source_page_type",
                "target_page_type",
                "converted"
            ]
        ]
        .drop_duplicates(
            subset=[
                "visitor_id",
                "source_page_type",
                "target_page_type"
            ]
        )
    )

    performance = (
        transition_visitors
        .groupby(
            ["source_page_type", "target_page_type"]
        )
        .agg(
            visitors=("visitor_id", "count"),
            conversions=("converted", "sum")
        )
    )

    performance["conversion_rate"] = (
        performance["conversions"]
        / performance["visitors"]
    ).round(3)

    performance["visitor_share"] = (
        performance["visitors"]
        / total_visitors
    ).round(3)

    return performance.sort_values(
        "conversion_rate",
        ascending=False
    )

def calculate_product_performance(
    events,
    site,
    total_visitors
):

    product_page_ids = site.pages.loc[
        site.pages["page_type"] == "product",
        "page_id"
    ]

    product_events = events[
        events["page_id"].isin(product_page_ids)
    ].copy()

    product_visitors = (
        product_events[
            ["visitor_id", "page_id", "converted"]
        ]
        .drop_duplicates(
            subset=["visitor_id", "page_id"]
        )
    )

    performance = (
        product_visitors
        .groupby("page_id")
        .agg(
            visitors=("visitor_id", "count"),
            conversions=("converted", "sum")
        )
    )

    performance["conversion_rate"] = (
        performance["conversions"]
        / performance["visitors"]
    ).round(3)

    performance["visitor_share"] = (
        performance["visitors"]
        / total_visitors
    ).round(3)

    product_name_map = (
        site.pages
        .set_index("page_id")["page_name"]
        .to_dict()
    )

    performance["product_name"] = (
        performance.index.map(product_name_map)
    )

    performance.loc[
    performance.index.str.contains("product_mens_clothing"),
    "product_name"
    ] = "Men's " + performance.loc[
    performance.index.str.contains("product_mens_clothing"),
    "product_name"
    ]

    performance.loc[
    performance.index.str.contains("product_womens_clothing"),
    "product_name"
    ] = "Women's " + performance.loc[
    performance.index.str.contains("product_womens_clothing"),
    "product_name"
    ]

    return performance.sort_values(
        "conversion_rate",
        ascending=False
    )

def display_segment_performance(
    segment_performance,
    title,
    segment_label
):

    fig = go.Figure()

    fig.add_trace(
        go.Table(
            header={
                "values": [
                    segment_label,
                    "Visitors",
                    "Bounces",
                    "Bounce Rate",
                    "Conversions",
                    "Engaged Visitors",
                    "Engaged Conversion Rate"
                ],
                "fill_color": "#D0D0D0",
                "align": "center",
                "font": {
                    "size": 13
                },
                "height": 28
            },

            cells={
                "values": [
                    segment_performance.index,
                    segment_performance["visitors"],
                    segment_performance["bounces"],
                    segment_performance["bounce_rate"].map(
                        lambda x: f"{x:.1%}"
                    ),
                    segment_performance["conversions"],
                    segment_performance["engaged_visitors"],
                    segment_performance["engaged_conversion_rate"].map(
                        lambda x: f"{x:.1%}"
                    )
                ],
                "fill_color": "#E8E8E8",
                "align": "center",
                "font": {
                    "size": 12
                },
                "height": 25
            }
        )
    )

    fig.update_layout(
        title={
            "text": title,
            "x": 0.01,
            "xanchor": "left"
        },
        height=100 + (len(segment_performance) * 25),
        margin={
            "l": 20,
            "r": 20,
            "t": 55,
            "b": 10
        }
    )

    fig.show()

def display_landing_page_performance(
    landing_page_performance
):
    display_data = (
        landing_page_performance
        .reset_index()
        .copy()
    )

    display_data["landing_page_type"] = (
        display_data["landing_page_type"]
        .str.replace("_", " ")
        .str.title()
    )

    display_data = display_data.sort_values(
        "visitors",
        ascending=False
    )

    display_data["landing_page_label"] = (
        display_data["landing_page_type"]
        + " — "
        + display_data["visitors"].astype(str)
    )

    fig = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=(
        "Bounce Rate",
        "Engaged Conversion Rate"
    ),
    horizontal_spacing=0.12
)

    fig.add_trace(
        go.Bar(
            x=display_data["bounce_rate"],
            y=display_data["landing_page_label"],
            orientation="h",
            text=display_data["bounce_rate"].map(
                lambda x: f"{x:.1%}"
            ),
            textposition="outside"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Bar(
            x=display_data["engaged_conversion_rate"],
            y=display_data["landing_page_label"],
            orientation="h",
            text=display_data["engaged_conversion_rate"].map(
                lambda x: f"{x:.1%}"
            ),
            textposition="outside"
        ),
        row=1,
        col=2
    )

    fig.update_xaxes(
        tickformat=".0%",
        row=1,
        col=1
    )

    fig.update_xaxes(
        tickformat=".0%",
        row=1,
        col=2
    )

    fig.update_yaxes(
        autorange="reversed",
        row=1,
        col=1
    )

    fig.update_yaxes(
        autorange="reversed",
        row=1,
        col=2
    )

    fig.update_layout(
        title="Landing Page Performance",
        height=300,
        showlegend=False,
        margin={
            "l": 120,
            "r": 60,
            "t": 70,
            "b": 30
        }
    )

    fig.show()

def display_exit_distribution(exit_distribution):

    display_data = exit_distribution.copy()

    display_data["page_type"] = (
        display_data["page_type"]
        .str.replace("_", " ")
        .str.title()
    )

    display_data["page_type_label"] = (
        display_data["page_type"]
        + " — "
        + display_data["exits"].astype(str)
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=display_data["percent_of_exits"],
            y=display_data["page_type_label"],
            orientation="h",
            text=display_data["percent_of_exits"].map(
                lambda x: f"{x:.1%}"
            ),
            textposition="outside"
        )
    )

    fig.update_layout(
        title="Last Page Before Exit — Engaged Nonconverters",
        xaxis={
            "tickformat": ".0%",
            "title": "Percent of Exits"
        },
        yaxis={
            "title": "",
            "autorange": "reversed"
        },
        height=400,
        margin={
            "l": 120,
            "r": 60,
            "t": 60,
            "b": 40
        }
    )

    fig.show()

def display_page_type_performance(display_page_types):

    display_data = (
        display_page_types
        .reset_index()
        .copy()
    )

    display_data["page_type"] = (
        display_data["page_type"]
        .str.replace("_", " ")
        .str.title()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Table(
            header={
                "values": [
                    "Page Type",
                    "Visitors",
                    "Conversions",
                    "Conversion Rate"
                ],
                "fill_color": "#D0D0D0",
                "align": "center",
                "font": {
                    "size": 13
                },
                "height": 28
            },
            cells={
                "values": [
                    display_data["page_type"],
                    display_data["visitors"],
                    display_data["conversions"],
                    display_data["conversion_rate"].map(
                        lambda x: f"{x:.1%}"
                    )
                ],
                "fill_color": "#E8E8E8",
                "align": "center",
                "font": {
                    "size": 12
                },
                "height": 25
            }
        )
    )

    fig.update_layout(
        title="Page-Type Performance",
        height=100 + (len(display_data) * 25),
        margin={
            "l": 20,
            "r": 20,
            "t": 55,
            "b": 10
        }
    )

    fig.show()

def display_transition_performance(display_transitions):

    display_data = (
        display_transitions
        .reset_index()
        .copy()
    )

    display_data["transition"] = (
        display_data["source_page_type"]
        .str.replace("_", " ")
        .str.title()
        + " → "
        + display_data["target_page_type"]
        .str.replace("_", " ")
        .str.title()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Table(
            header={
                "values": [
                    "Transition",
                    "Visitors",
                    "Conversions",
                    "Conversion Rate"
                ],
                "fill_color": "#D0D0D0",
                "align": "center",
                "font": {
                    "size": 13
                },
                "height": 28
            },
            cells={
                "values": [
                    display_data["transition"],
                    display_data["visitors"],
                    display_data["conversions"],
                    display_data["conversion_rate"].map(
                        lambda x: f"{x:.1%}"
                    )
                ],
                "fill_color": "#E8E8E8",
                "align": "center",
                "font": {
                    "size": 12
                },
                "height": 25
            }
        )
    )

    fig.update_layout(
        title="Transition Performance",
        height=100 + (len(display_data) * 25),
        margin={
            "l": 20,
            "r": 20,
            "t": 55,
            "b": 10
        }
    )

    fig.show()

def display_product_performance(display_products):

    display_data = (
        display_products
        .reset_index()
        .copy()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Table(
            header={
                "values": [
                    "Product",
                    "Visitors",
                    "Conversions",
                    "Conversion Rate"
                ],
                "fill_color": "#D0D0D0",
                "align": "center",
                "font": {
                    "size": 13
                },
                "height": 28
            },
            cells={
                "values": [
                    display_data["product_name"],
                    display_data["visitors"],
                    display_data["conversions"],
                    display_data["conversion_rate"].map(
                        lambda x: f"{x:.1%}"
                    )
                ],
                "fill_color": "#E8E8E8",
                "align": "center",
                "font": {
                    "size": 12
                },
                "height": 25
            }
        )
    )

    fig.update_layout(
        title="Product Performance",
        height=100 + (len(display_data) * 25),
        margin={
            "l": 20,
            "r": 20,
            "t": 55,
            "b": 10
        }
    )

    fig.show()

def display_product_scatter(display_products):

    display_data = (
        display_products
        .reset_index()
        .copy()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=display_data["visitors"],
            y=display_data["conversion_rate"],
            mode="markers",
            text=display_data["product_name"],
            customdata=display_data[
                ["conversions"]
            ],
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Visitors: %{x}<br>"
                "Conversions: %{customdata[0]}<br>"
                "Conversion Rate: %{y:.1%}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title="Product Exposure and Conversion",
        xaxis={
            "title": "Visitors"
        },
        yaxis={
            "title": "Conversion Rate",
            "tickformat": ".0%"
        },
        height=450,
        margin={
            "l": 70,
            "r": 40,
            "t": 60,
            "b": 60
        }
    )

    fig.show()

def display_journey_report(
    headline_metrics,
    user_type_performance,
    buyer_intent_performance,
    landing_page_performance,
    exit_distribution,
    display_page_types,
    display_transitions,
    display_products,
    step_transition_summary
):
    print("SECTION 1 — VISITOR PERFORMANCE")

    display_headline_metrics(
        headline_metrics
    )

    display_segment_performance(
        user_type_performance,
        "User Type Performance",
        "User Type"
    )

    display_segment_performance(
        buyer_intent_performance,
        "Buyer Intent Performance",
        "Buyer Intent"
    )

    print("SECTION 2 — ENTRY & EXIT")

    display_landing_page_performance(
        landing_page_performance
    )

    display_exit_distribution(
        exit_distribution
    )

    print("SECTION 3 — BEHAVIOR PERFORMANCE")

    display_page_type_performance(
        display_page_types
    )

    display_transition_performance(
        display_transitions
    )

    print("SECTION 4 — PRODUCT PERFORMANCE")

    display_product_scatter(
        display_products
    )

    display_product_performance(
        display_products
    )

    print("SECTION 5 — JOURNEY FLOW")

    fig = build_step_sankey(
        step_transition_summary,
        max_step=5,
        min_count=20
    )

    fig.show()
