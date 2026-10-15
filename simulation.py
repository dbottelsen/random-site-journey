import random
import pandas as pd

from visitor import Visitor


def simulate_visitors(
    site,
    rules,
    number_of_visitors=1000,
    user_type_distribution=None,
    buyer_intent_distribution=None,
    seed=42
):

    rng = random.Random(seed)

    landing_page_distribution = {
        "home": 0.35,
        "product": 0.25,
        "category": 0.20,
        "sale": 0.10,
        "search_results": 0.10
    }

    if user_type_distribution is None:
        user_type_distribution = {
            "browser": 0.35,
            "researcher": 0.30,
            "deal_seeker": 0.20,
            "direct_shopper": 0.15
    }

    if buyer_intent_distribution is None:
        buyer_intent_distribution = {
            "low": 0.30,
            "medium": 0.40,
            "high": 0.30
    }

    results = []

    for i in range(1, number_of_visitors + 1):

        # -------------------------
        # Choose visitor type
        # -------------------------

        user_type = rng.choices(
            population=list(user_type_distribution.keys()),
            weights=list(user_type_distribution.values()),
            k=1
        )[0]

        buyer_intent = rng.choices(
            population=list(buyer_intent_distribution.keys()),
            weights=list(buyer_intent_distribution.values()),
            k=1
        )[0]

        # -------------------------
        # Choose landing page type
        # -------------------------

        landing_page_type = rng.choices(
            population=list(landing_page_distribution.keys()),
            weights=list(landing_page_distribution.values()),
            k=1
        )[0]

        # Find actual pages of that type
        available_pages = site.pages.loc[
            site.pages["page_type"] == landing_page_type,
            "page_id"
        ].tolist()

        # Pick one actual landing page
        landing_page = rng.choice(available_pages)

        # -------------------------
        # Create visitor
        # -------------------------

        visitor_id = f"V{i:06d}"

        visitor = Visitor(
            visitor_id=visitor_id,
            user_type=user_type,
            buyer_intent=buyer_intent
        )

        journey_seed = rng.randint(
            0,
            1_000_000_000
        )

        # -------------------------
        # Create journey
        # -------------------------

        journey, end_reason = visitor.create_journey(
            site=site,
            rules=rules,
            start_page=landing_page,
            max_steps=30,
            seed=journey_seed
        )

        # -------------------------
        # Store results
        # -------------------------

        results.append({
            "visitor_id": visitor_id,
            "user_type": user_type,
            "buyer_intent": buyer_intent,
            "landing_page_type": landing_page_type,
            "landing_page": landing_page,
            "journey": journey,
            "steps": len(journey) - 1,
            "end_reason": end_reason,
            "converted": end_reason == "confirmation"
        })

    return pd.DataFrame(results)