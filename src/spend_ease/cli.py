from datetime import date
from uuid import uuid4

from spend_ease.models import Transaction
from spend_ease.storage import save_transaction, load_transactions


def main():
    print("Welcome to SpendEase! 💰")
    print()

    action = input("What would you like to do? (add/list/summary): ").strip().lower()
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

    elif action == "summary":
        transactions = load_transactions()

        if not transactions:
            print("\n No transactions yet. Add your first transaction!")
            return

        category_totals = {}
        for transaction in transactions:
            category = transaction.category
            if category in category_totals:
                category_totals[category] += transaction.amount
            else:
                category_totals[category] = transaction.amount

        total = sum(category_totals.values())

        category_data = []
        for category, amount in category_totals.items():
            count = sum(1 for t in transactions if t.category == category)
            percentage = (amount / total) * 100
            category_data.append((category, amount, percentage, count))

        category_data.sort(key=lambda x: x[1], reverse=True)

        print("\n" + "=" * 70)
        print("SPENDING SUMMARY")
        print("=" * 70)
        print(f"{'Category':<15} | {'Amount':>10} | {'Percentage':>10} | {'Count':>5}")
        print("-" * 70)

        for category, amount, percentage, count in category_data:
            print(
                f"{category:<15} | €{amount:>9.2f} | {percentage:>9.1f}% | {count:>5}"
            )

        print("=" * 70)
        print(
            f"{'TOTAL':<15} | €{total:>9.2f} | {'100.0%':>10} | {len(transactions):>5}"
        )
        print("=" * 70)

    else:
        print("Invalid option. Please choose 'add', 'list', or 'summary'.")
