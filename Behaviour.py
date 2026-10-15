import pandas as pd

user_types = [
    "browser",
    "researcher",
    "deal_seeker",
    "direct_shopper"
]

buyer_intents = [
    "low",
    "medium",
    "high"
]

base_behavior = pd.DataFrame([
    # HOME
    ["home", "category", 0.45],
    ["home", "search", 0.15],
    ["home", "sale", 0.10],
    ["home", "recommendation", 0.10],
    ["home", "account", 0.05],
    ["home", "corporate", 0.05],
    ["home", "exit", 0.10],

    # CATEGORY
    ["category", "product", 0.65],
    ["category", "home", 0.10],
    ["category", "search", 0.10],
    ["category", "sale", 0.05],
    ["category", "exit", 0.10],

    # PRODUCT
    ["product", "product", 0.25],
    ["product", "category", 0.15],
    ["product", "cart", 0.20],
    ["product", "search", 0.10],
    ["product", "support", 0.10],
    ["product", "exit", 0.20],

    # CART
    ["cart", "checkout", 0.55],
    ["cart", "product", 0.15],
    ["cart", "home", 0.05],
    ["cart", "exit", 0.25],

    # SUPPORT
    ["support", "product", 0.45],
    ["support", "cart", 0.20],
    ["support", "home", 0.10],
    ["support", "exit", 0.25],

    # SEARCH
    ["search", "search_results", 0.80],
    ["search", "home", 0.10],
    ["search", "exit", 0.10],

    # SEARCH RESULTS
    ["search_results", "product", 0.65],
    ["search_results", "search", 0.15],
    ["search_results", "home", 0.05],
    ["search_results", "exit", 0.15],

    # SALE
    ["sale", "product", 0.70],
    ["sale", "home", 0.10],
    ["sale", "exit", 0.20],

    # RECOMMENDATION
    ["recommendation", "product", 0.75],
    ["recommendation", "home", 0.10],
    ["recommendation", "exit", 0.15],

    # ACCOUNT
    ["account", "home", 0.60],
    ["account", "category", 0.20],
    ["account", "exit", 0.20],

    # CORPORATE
    ["corporate", "home", 0.50],
    ["corporate", "category", 0.15],
    ["corporate", "exit", 0.35],

    # CHECKOUT
    ["checkout", "checkout", 0.65],
    ["checkout", "confirmation", 0.25],
    ["checkout", "exit", 0.10],
],
columns=[
    "current_page_type",
    "next_page_type",
    "base_probability"
])

user_type_modifiers = {
    "browser": {
        "product": 1.30,
        "category": 1.20,
        "search": 1.10,
        "cart": 0.70,
        "checkout": 0.70,
        "exit": 1.15
    },

    "researcher": {
        "product": 1.25,
        "search": 1.40,
        "support": 1.50,
        "cart": 0.85,
        "checkout": 0.90,
        "exit": 0.90
    },

    "deal_seeker": {
        "sale": 1.75,
        "product": 1.20,
        "search": 1.10,
        "cart": 1.05,
        "checkout": 1.00,
        "exit": 1.00
    },

    "direct_shopper": {
        "product": 1.10,
        "cart": 1.60,
        "checkout": 1.50,
        "search": 0.60,
        "support": 0.70,
        "category": 0.80,
        "exit": 0.70
    }
}

buyer_intent_modifiers = {
    "low": {
        "product": 1.10,
        "category": 1.10,
        "search": 1.10,
        "support": 1.00,
        "cart": 0.60,
        "checkout": 0.50,
        "confirmation": 0.50,
        "exit": 1.40
    },

    "medium": {
        "product": 1.00,
        "category": 1.00,
        "search": 1.00,
        "support": 1.00,
        "cart": 1.00,
        "checkout": 1.00,
        "confirmation": 1.00,
        "exit": 1.00
    },

    "high": {
        "product": 1.05,
        "category": 0.80,
        "search": 0.80,
        "support": 1.10,
        "cart": 1.50,
        "checkout": 1.60,
        "confirmation": 1.50,
        "exit": 0.50
    }
}

product_rules = pd.DataFrame([
    {
        "user_type": "researcher",
        "buyer_intent": "high",
        "current_page_type": "product",
        "next_page_type": "product",
        "probability": 0.25
    },
    {
        "user_type": "researcher",
        "buyer_intent": "high",
        "current_page_type": "product",
        "next_page_type": "cart",
        "probability": 0.35
    },
    {
        "user_type": "researcher",
        "buyer_intent": "high",
        "current_page_type": "product",
        "next_page_type": "support",
        "probability": 0.15
    },
    {
        "user_type": "researcher",
        "buyer_intent": "high",
        "current_page_type": "product",
        "next_page_type": "search",
        "probability": 0.10
    },
    {
        "user_type": "researcher",
        "buyer_intent": "high",
        "current_page_type": "product",
        "next_page_type": "category",
        "probability": 0.05
    },
    {
        "user_type": "researcher",
        "buyer_intent": "high",
        "current_page_type": "product",
        "next_page_type": "exit",
        "probability": 0.10
    }
])

def build_behavior_rules(
    base_behavior,
    user_type,
    buyer_intent,
    user_type_modifiers,
    buyer_intent_modifiers
):

    rules = base_behavior.copy()

    # Apply user-type modifier
    rules["user_modifier"] = rules["next_page_type"].map(
        user_type_modifiers[user_type]
    ).fillna(1.0)

    # Apply buyer-intent modifier
    rules["intent_modifier"] = rules["next_page_type"].map(
        buyer_intent_modifiers[buyer_intent]
    ).fillna(1.0)

    # Create an unnormalized probability
    rules["adjusted_probability"] = (
        rules["base_probability"]
        * rules["user_modifier"]
        * rules["intent_modifier"]
    )

    # Normalize within each current page type
    rules["probability"] = (
        rules["adjusted_probability"]
        / rules.groupby("current_page_type")[
            "adjusted_probability"
        ].transform("sum")
    )

    # Add the visitor characteristics
    rules["user_type"] = user_type
    rules["buyer_intent"] = buyer_intent

    return rules

researcher_high_rules = build_behavior_rules(
    base_behavior=base_behavior,
    user_type="researcher",
    buyer_intent="high",
    user_type_modifiers=user_type_modifiers,
    buyer_intent_modifiers=buyer_intent_modifiers
)

browser_low_rules = build_behavior_rules(
    base_behavior=base_behavior,
    user_type="browser",
    buyer_intent="low",
    user_type_modifiers=user_type_modifiers,
    buyer_intent_modifiers=buyer_intent_modifiers
)

direct_high_rules = build_behavior_rules(
    base_behavior=base_behavior,
    user_type="direct_shopper",
    buyer_intent="high",
    user_type_modifiers=user_type_modifiers,
    buyer_intent_modifiers=buyer_intent_modifiers
)

all_behavior_rules = []

for user_type in user_types:
    for buyer_intent in buyer_intents:

        profile_rules = build_behavior_rules(
            base_behavior=base_behavior,
            user_type=user_type,
            buyer_intent=buyer_intent,
            user_type_modifiers=user_type_modifiers,
            buyer_intent_modifiers=buyer_intent_modifiers
        )

        all_behavior_rules.append(profile_rules)

all_behavior_rules = pd.concat(
    all_behavior_rules,
    ignore_index=True
)