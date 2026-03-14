import json
from pathlib import Path
from dataclasses import asdict

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
