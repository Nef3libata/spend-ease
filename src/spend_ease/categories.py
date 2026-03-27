# Keyword → Category mapping for auto-categorization of bank transactions
CATEGORY_RULES: dict[str, str] = {
    # University & Mensa
    "studierendenwerk": "Mensa",
    "unibuch": "University",
    "druck und scan": "University",
    "asta tu": "University",
    "technische universitat": "University",
    # Groceries
    "rewe": "Groceries",
    "lidl": "Groceries",
    "aldi": "Groceries",
    "kaufland": "Groceries",
    "erdemli": "Groceries",
    # Drugstore & Health
    "dm drogerie": "Drugstore",
    "apotheke": "Health",
    # Shopping
    "amazon": "Shopping",
    "tedi": "Shopping",
    "new yorker": "Shopping",
    "woolworth": "Shopping",
    "decathlon": "Shopping",
    "action": "Shopping",
    "thalia": "Shopping",
    "barlag": "Shopping",
    # Food & Drinks
    "restaurant": "Eating Out",
    "bäckerei": "Eating Out",
    "backerei": "Eating Out",
    "kiosk": "Eating Out",
    "berliner": "Eating Out",
    "automat": "Vending",
    # Transport
    "nextbike": "Transport",
    "lime": "Transport",
    # Laundry
    "waschmaschinen": "Laundry",
    # Personal care
    "hair": "Personal Care",
    # PayPal (generic)
    "paypal": "PayPal",
}


def categorize_merchant(description: str) -> str:
    description_lower = description.lower()

    for keyword, category in CATEGORY_RULES.items():
        if keyword in description_lower:
            return category

    return "Other"
