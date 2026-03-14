from datetime import date
from uuid import uuid4

from spend_ease.models import Transaction
from spend_ease.storage import save_transaction, load_transactions


def main():
    print("Welcome to SpendEase! 💰")
    print()

    action = input("What would you like to do? (add/list): ").strip().lower()
    if action == "add":
        amount = float(input("Amount: "))
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

    elif action == "list":
        transactions = load_transactions()

        if not transactions:
            print("\nNo transactions yet. Add your first transaction!")
            return

        print("\n" + "=" * 60)
        print("YOUR TRANSACTIONS")
        print("=" * 60)

        total = 0
        for transaction in transactions:
            print(
                f"{transaction.date} | {transaction.category:12} | €{transaction.amount:6.2f} | {transaction.description}"
            )
            total += transaction.amount

        print("=" * 60)
        print(f"TOTAL: €{total:.2f}")
        print("=" * 60)

    else:
        print("Invalid option. Please choose 'add' or 'list'.")
