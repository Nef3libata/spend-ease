import json
from pathlib import Path
from dataclasses import asdict

from spend_ease.models import Budget

DEFAULT_PATH = Path.home() / ".spend_ease" / "budget_storage.json"


def save_budget(budget: Budget) -> None:
    if DEFAULT_PATH.exists():
        with open(DEFAULT_PATH, "r") as file:
            budgets = json.load(file)
    else:
        budgets = []

    budgets = [b for b in budgets if b["category"] != budget.category]

    budget_dict = asdict(budget)
    budgets.append(budget_dict)

    DEFAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DEFAULT_PATH, "w") as file:
        json.dump(budgets, file, indent=2)


def load_budgets() -> list[Budget]:
    if not DEFAULT_PATH.exists():
        return []
    with open(DEFAULT_PATH, "r") as file:
        data = json.load(file)

    budgets = [
        Budget(category=item["category"], limit=item["limit"], period=item["period"])
        for item in data
    ]
    return budgets


def get_budget(category: str) -> Budget | None:
    budgets = load_budgets()

    for budget in budgets:
        if budget.category == category:
            return budget
    return None

