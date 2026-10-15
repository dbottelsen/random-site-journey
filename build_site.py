from website import Website

footwear_products = [
    "Trail Running Shoe",
    "Hiking Boot",
    "Approach Shoe",
    "Road Running Shoe",
    "Hiking Sandal",
    "Winter Boot",
    "Camp Shoe",
    "Water Shoe"
]

mens_clothing_products = [
    "Hiking Shirt",
    "Trail Pants",
    "Fleece Jacket",
    "Rain Jacket",
    "Down Jacket",
    "Base Layer",
    "Hiking Shorts",
    "Insulated Vest"
]

womens_clothing_products = [
    "Hiking Shirt",
    "Trail Pants",
    "Fleece Jacket",
    "Rain Jacket",
    "Down Jacket",
    "Base Layer",
    "Hiking Shorts",
    "Insulated Vest"
]

camping_products = [
    "Two Person Tent",
    "Four Person Tent",
    "Sleeping Bag",
    "Sleeping Pad",
    "Camp Stove",
    "Camp Chair",
    "Lantern",
    "Cooler"
]

hiking_products = [
    "Daypack",
    "Trekking Poles",
    "Hydration Pack",
    "Headlamp",
    "Compass",
    "Water Filter",
    "First Aid Kit",
    "Hiking Gaiters"
]

accessories_products = [
    "Hiking Socks",
    "Sun Hat",
    "Winter Hat",
    "Gloves",
    "Sunglasses",
    "Water Bottle",
    "Dry Bag",
    "Multi Tool"
]

sale_products = [
    "product_footwear_01",
    "product_mens_clothing_01",
    "product_womens_clothing_01",
    "product_camping_01",
    "product_hiking_01",
    "product_accessories_01"
]

search_products = [
    "product_footwear_01",
    "product_mens_clothing_01",
    "product_womens_clothing_01",
    "product_camping_01",
    "product_hiking_01",
    "product_accessories_01"
]

def build_summit_outfitters():

    site = Website("Summit Outfitters")

    site.add_page(
        page_id="home",
        page_name="home",
        page_type="home"
    )

    site.add_category(
        category_id="footwear",
        category_name="Footwear",
        products = footwear_products
    )

    site.add_category(
        category_id="mens_clothing",
        category_name="Men's Clothing",
        products=mens_clothing_products
    )

    site.add_category(
        category_id="womens_clothing",
        category_name="Women's Clothing",
        products=womens_clothing_products
    )

    site.add_category(
        category_id="camping",
        category_name="Camping",
        products=camping_products
    )

    site.add_category(
        category_id="hiking",
        category_name="Hiking",
        products=hiking_products
    )

    site.add_category(
        category_id="accessories",
        category_name="Accessories",
        products=accessories_products
    )

    site.add_page("search", "Search", "search")
    site.add_page("search_results", "Search Results", "search_results")

    site.add_page("sale", "Sale", "sale")
    site.add_page("recommendations", "Recommendations", "recommendation")

    site.add_page("cart", "Cart", "cart")

    site.add_page("checkout_shipping", "Checkout - Shipping", "checkout")
    site.add_page("checkout_payment", "Checkout - Payment", "checkout")
    site.add_page("checkout_review", "Checkout - Review", "checkout")
    site.add_page("confirmation", "Order Confirmation", "confirmation")

    site.add_page("login", "Login", "account")
    site.add_page("account", "My Account", "account")
    site.add_page("order_history", "Order History", "account")
    site.add_page("registration", "Create Account", "account")

    site.add_page("faq", "FAQ", "support")
    site.add_page("shipping_info", "Shipping Information", "support")
    site.add_page("returns", "Returns", "support")
    site.add_page("contact", "Contact Us", "support")
    site.add_page("product_help", "Product Help", "support")

    site.add_page("about", "About Us", "corporate")
    site.add_page("store_locator", "Store Locator", "corporate")

    site.add_page("exit", "Exit", "exit")

    site.add_edge("home", "search", "global_navigation")
    site.add_edge("home", "sale", "main_navigation")
    site.add_edge("home", "recommendations", "main_navigation")
    site.add_edge("home", "login", "global_navigation")
    site.add_edge("home", "faq", "footer_navigation")
    site.add_edge("home", "about", "footer_navigation")
    site.add_edge("home", "store_locator", "footer_navigation")
    site.add_edge("home", "exit", "exit")
    site.add_edge("cart", "checkout_shipping", "checkout")
    site.add_edge("checkout_shipping", "checkout_payment", "checkout")
    site.add_edge("checkout_payment", "checkout_review", "checkout")
    site.add_edge("checkout_review", "confirmation", "purchase")
    site.add_edge("login", "account", "account_navigation")
    site.add_edge("login", "registration", "account_navigation")
    site.add_edge("account", "order_history", "account_navigation")
    site.add_edge("faq", "shipping_info", "support_navigation")
    site.add_edge("faq", "returns", "support_navigation")
    site.add_edge("faq", "contact", "support_navigation")
    site.add_edge("sale", "home", "main_navigation")
    site.add_edge("sale", "exit", "exit") 
    site.add_edge("search", "search_results", "search")
    site.add_edge("search", "home", "global_navigation")
    site.add_edge("search", "exit", "exit")
    site.add_edge("search_results", "search", "search")
    site.add_edge("search_results", "home", "global_navigation")
    site.add_edge("search_results", "exit", "exit")

    for product_id in sale_products:
        site.add_edge(
            "sale",
            product_id,
            "sale_product"
        )

    for product_id in search_products:
        site.add_edge(
            "search_results",
            product_id,
            "search_result"
        )

    # Recommendation connections
    site.add_edge("recommendations", "home", "main_navigation")
    site.add_edge("recommendations", "exit", "exit")

    for product_id in search_products:
        site.add_edge(
        "recommendations",
        product_id,
        "recommended_product"
        )


    # Support connections
    for support_page in ["shipping_info", "product_help"]:
        site.add_edge(support_page, "home", "global_navigation")
        site.add_edge(support_page, "cart", "cart_navigation")
        site.add_edge(support_page, "exit", "exit")

        for product_id in search_products:
            site.add_edge(
                support_page,
                product_id,
                "product_link"
            )


    # Login connections
    site.add_edge("login", "home", "global_navigation")
    site.add_edge("login", "exit", "exit")


    # Corporate connections
    for corporate_page in ["about", "store_locator"]:
        site.add_edge(corporate_page, "home", "global_navigation")
        site.add_edge(corporate_page, "exit", "exit")

        site.add_edge(
            corporate_page,
            "category_footwear",
            "category_link"
        )

        category_pages = [
        "category_footwear",
        "category_mens_clothing",
        "category_womens_clothing",
        "category_camping",
        "category_hiking",
        "category_accessories"
    ]

    for category_page_id in category_pages:
        site.add_edge(category_page_id, "home", "global_navigation")
        site.add_edge(category_page_id, "search", "global_navigation")
        site.add_edge(category_page_id, "sale", "global_navigation")
        site.add_edge(category_page_id, "exit", "exit")

    site.connect_products()

    return site



