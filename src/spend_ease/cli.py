from datetime import date
from uuid import uuid4

from spend_ease.models import Transaction
from spend_ease.storage import save_transaction


def main():
    print("Welcome to SpendEase! 💰")
    print()

    amount = float(input("Amount:"))
    category = input("Category (e.g., Food, Transport): ")
    description = input("Description: ")

    transaction = Transaction(
        id=str(uuid4()),
        amount=amount,
        category=category,
        date=date.today(),
        description=description,
    )

    save_transaction(transaction)
    print(f"\n✅ Transaction saved! €{amount} for {category}")
