import networkx as nx
import random
import pandas as pd
import random


class Website:

    def __init__(self, name):
        self.name = name
        self.pages = pd.DataFrame()
        self.edges = pd.DataFrame()
        self.graph = nx.DiGraph()

    def add_page(self, page_id, page_name, page_type):
        new_page = pd.DataFrame([{
            "page_id": page_id,
            "page_name": page_name,
            "page_type": page_type
        }])

        self.pages = pd.concat(
            [self.pages, new_page],
            ignore_index=True
        )

    def add_category(self, category_id, category_name, products):

        # Create the category page
        category_page_id = f"category_{category_id}"

        self.add_page(
            page_id=category_page_id,
            page_name=category_name,
            page_type="category"
        )

        self.add_edge(
            source="home",
            target=category_page_id,
            link_type="main_navigation"
        )

        # Create the product pages
        for i, product_name in enumerate(products, start=1):
            product_id = f"product_{category_id}_{i:02d}"

            self.add_page(
                page_id=product_id,
                page_name=product_name,
                page_type="product"
            )

            # Connect the category to the product
            self.add_edge(
                source=category_page_id,
                target=product_id,
                link_type="product_link"
            )

    def get_page(self, page_id):
        return self.pages[
            self.pages["page_id"] == page_id
        ]

    def add_edge(self, source, target, link_type):

        if source not in self.pages["page_id"].values:
            raise ValueError(f"Source page '{source}' does not exist.")

        if target not in self.pages["page_id"].values:
            raise ValueError(f"Target page '{target}' does not exist.")

        new_edge = pd.DataFrame([{
            "source": source,
            "target": target,
            "link_type": link_type
        }])

        self.edges = pd.concat(
            [self.edges, new_edge],
            ignore_index=True
        )

    def build_graph(self):

        self.graph = nx.DiGraph()

        for _, row in self.pages.iterrows():
            self.graph.add_node(
                row["page_id"],
                page_name=row["page_name"],
                page_type=row["page_type"]
            )

        for _, row in self.edges.iterrows():
            self.graph.add_edge(
                row["source"],
                row["target"],
                link_type=row["link_type"]
            )

    def connect_products(self, related_products_per_page=2, seed=42):

        rng = random.Random(seed)

        product_pages = self.pages[
            self.pages["page_type"] == "product"
        ]

        for _, row in product_pages.iterrows():

            product_id = row["page_id"]

            # Get the category from the product ID
            # product_footwear_01 -> category_footwear
            parts = product_id.split("_")
            category_id = "_".join(parts[1:-1])
            category_page_id = f"category_{category_id}"

            # Standard product-page links
            self.add_edge(
                product_id,
                category_page_id,
                "breadcrumb"
            )

            self.add_edge(
                product_id,
                "cart",
                "add_to_cart"
            )

            self.add_edge(
                product_id,
                "search",
                "global_navigation"
            )

            self.add_edge(
                product_id,
                "shipping_info",
                "support_link"
            )

            self.add_edge(
                product_id,
                "product_help",
                "support_link"
            )

            self.add_edge(
                product_id,
                "exit",
                "exit"
            )

            same_category_products = product_pages[
                product_pages["page_id"].str.startswith(
                    f"product_{category_id}_"
                )
            ]["page_id"].tolist()

            same_category_products.remove(product_id)

            related_products = rng.sample(
                same_category_products,
                k=related_products_per_page
            )

            for related_product in related_products:
                self.add_edge(
                    product_id,
                    related_product,
                    "related_product"
                )  


    def get_available_pages_by_type(self, current_page, target_page_type):

        outgoing_edges = self.edges[
            self.edges["source"] == current_page
        ]

        target_pages = outgoing_edges["target"].tolist()

        available_pages = self.pages[
            self.pages["page_id"].isin(target_pages) &
            (self.pages["page_type"] == target_page_type)
        ]

        return available_pages    