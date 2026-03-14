import json
from pathlib import Path
from dataclasses import asdict
from datetime import date

from spend_ease.models import Transaction

DEFAULT_PATH = Path.home() / ".spend_ease" / "storage.json"


def save_transaction(transaction: Transaction) -> None:
    if DEFAULT_PATH.exists():
        with open(DEFAULT_PATH, "r") as file:
            transactions = json.load(file)
    else:
        transactions = []

    transaction_dict = asdict(transaction)
    transaction_dict["date"] = str(transaction.date)
    transactions.append(transaction_dict)

    DEFAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DEFAULT_PATH, "w") as file:
        json.dump(transactions, file, indent=2)


def load_transactions() -> list[Transaction]:
    if not DEFAULT_PATH.exists():
        return []
    with open(DEFAULT_PATH, "r") as file:
        data = json.load(file)

    transactions = [
        Transaction(
            id=item["id"],
            amount=item["amount"],
            category=item["category"],
            date=date.fromisoformat(item["date"]),
            description=item["description"],
        )
        for item in data
    ]
    return transactions
