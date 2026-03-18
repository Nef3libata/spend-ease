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


def delete_transaction(transaction_id: str) -> bool:
    transactions = load_transactions()
    original_count = len(transactions)

    transactions = [t for t in transactions if t.id != transaction_id]

    if len(transactions) < original_count:
        DEFAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DEFAULT_PATH, "w") as file:
            json.dump([asdict(t) for t in transactions], file, indent=2, default=str)
        return True
    return False


def update_transaction(transaction_id: str, updated_transaction: Transaction) -> bool:
    transactions = load_transactions()

    for idx, transaction in enumerate(transactions):
        if transaction.id == transaction_id:
            transactions[idx] = updated_transaction

            DEFAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(DEFAULT_PATH, "w") as file:
                json.dump(
                    [asdict(t) for t in transactions], file, indent=2, default=str
                )
            return True
    return False
