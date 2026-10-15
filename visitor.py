import random

class Visitor:

    def __init__(self, visitor_id, user_type, buyer_intent):
        self.visitor_id = visitor_id
        self.user_type = user_type
        self.buyer_intent = buyer_intent

    def get_rules(self, rules, current_page_type):

        return rules[
            (rules["user_type"] == self.user_type) &
            (rules["buyer_intent"] == self.buyer_intent) &
            (rules["current_page_type"] == current_page_type)
        ]

    def choose_next_page_type(self, rules, current_page_type, rng):

        visitor_rules = self.get_rules(
            rules,
            current_page_type
        )

        choices = rng.choices(
            population=visitor_rules["next_page_type"].tolist(),
            weights=visitor_rules["probability"].tolist(),
            k=1
        )

        return choices[0]

    def choose_next_page(self, site, rules, current_page, rng):

        # What type of page are we currently on?
        current_page_type = site.pages.loc[
            site.pages["page_id"] == current_page,
            "page_type"
        ].iloc[0]

        # Get this visitor's behavioral rules
        visitor_rules = self.get_rules(
            rules,
            current_page_type
        ).copy()

        # Find all actual pages reachable from the current page
        outgoing_edges = site.edges[
            site.edges["source"] == current_page
        ]

        target_page_ids = outgoing_edges["target"].tolist()

        available_pages = site.pages[
            site.pages["page_id"].isin(target_page_ids)
        ]

        # Find which page TYPES are actually available
        available_page_types = (
            available_pages["page_type"]
            .unique()
            .tolist()
        )

        # Keep only behavioral choices that the website allows
        valid_rules = visitor_rules[
            visitor_rules["next_page_type"].isin(
                available_page_types
            )
        ].copy()

        # Nothing valid is available
        if valid_rules.empty:
            return None

        # Renormalize probabilities among the valid choices
        valid_rules["probability"] = (
            valid_rules["probability"]
            / valid_rules["probability"].sum()
        )

        # Choose the destination TYPE
        target_page_type = rng.choices(
            population=valid_rules["next_page_type"].tolist(),
            weights=valid_rules["probability"].tolist(),
            k=1
        )[0]

        # Find actual connected pages of that type
        possible_pages = available_pages[
            available_pages["page_type"] == target_page_type
        ]

        # Choose the actual page
        return rng.choice(
            possible_pages["page_id"].tolist()
        )

    def create_journey(
        self,
        site,
        rules,
        start_page="home",
        max_steps=30,
        seed=42
    ):

        rng = random.Random(seed)

        journey = [start_page]
        current_page = start_page
        end_reason = None

        for _ in range(max_steps):

            if current_page == "confirmation":
                end_reason = "confirmation"
                break

            if current_page == "exit":
                end_reason = "exit"
                break

            next_page = self.choose_next_page(
                site=site,
                rules=rules,
                current_page=current_page,
                rng=rng
            )

            if next_page is None:
                end_reason = "no_available_transition"
                break

            journey.append(next_page)
            current_page = next_page

        if end_reason is None:
            end_reason = "max_steps"

        return journey, end_reason