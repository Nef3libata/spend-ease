from datetime import date
from uuid import uuid4
import calendar

from spend_ease.models import Transaction
from spend_ease.storage import save_transaction, load_transactions
from spend_ease.analysis import group_by_month
from spend_ease.models import Budget
from spend_ease.budget_storage import get_budget, save_budget, load_budgets


def add_transaction() -> None:
    try:
        amount_str = input("Amount: ")
        amount = float(amount_str)

        if amount <= 0:
            print("Error: Amount must be greater than 0")
            return

        category = input("Category (e.g., Food, Transport): ").strip().title()
        if not category:
            while not category:
                print("Error: Category cannot be empty")
                category = input("Category (e.g., Food, Transport): ").strip().title()

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

    except ValueError:
        print("Error: Please enter a valid number for amount")
    except Exception as e:
        print(f"An error occurred: {e}")


def display_transactions() -> None:
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


def show_summary() -> None:
    transactions = load_transactions()

    if not transactions:
        print("\nNo transactions yet. Add your first transaction!")
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

    print("\n" + "=" * 90)
    print("SPENDING SUMMARY")
    print("=" * 90)
    print(
        f"{'Category':<15} | {'Spent':>10} | {'Budget':>10} | {'Status':>12} | {'%':>6} | {'Count':>5}"
    )
    print("-" * 90)

    for category, amount, percentage, count in category_data:
        budget = get_budget(category)
        if budget:
            remaining = budget.limit - amount
            if remaining >= 0:
                status = f"€{remaining:.2f} left"
            else:
                status = f"€{abs(remaining):.2f} over"
            budget_str = f"€{budget.limit:>8.2f}"
        else:
            status = "No budget"
            budget_str = "-"

        print(
            f"{category:<15} | €{amount:>9.2f} | {budget_str:>10} | {status:>12} | {percentage:>5.1f}% | {count:>5}"
        )

    print("=" * 90)
    print(
        f"{'TOTAL':<15} | €{total:>9.2f} | {'':<10} | {'':<12} | {'100.0%':>6} | {len(transactions):>5}"
    )
    print("=" * 90)


def show_monthly_breakdown() -> None:
    transactions = load_transactions()

    if not transactions:
        print("\nNo transactions yet. Add your first transaction!")
        return

    monthly_data = group_by_month(transactions)

    sorted_months = sorted(monthly_data.keys(), reverse=True)

    print("\n" + "=" * 70)
    print("MONTHLY SPENDING BREAKDOWN")
    print("=" * 70)
    print(f"{'Month':<20} | {'Amount':>12} | {'Transactions':>12} | {'Avg/Day':>10}")
    print("-" * 70)

    for year, month in sorted_months:
        data = monthly_data[(year, month)]
        month_name = calendar.month_name[month]
        month_year = f"{month_name} {year}"
        days_in_month = calendar.monthrange(year, month)[1]
        avg_per_day = data["amount"] / days_in_month

        print(
            f"{month_year:<20} | €{data['amount']:>10.2f} | "
            f"{data['count']:>12} | €{avg_per_day:>9.2f}"
        )

    print("=" * 70)
    total = sum(d["amount"] for d in monthly_data.values())
    print(f"{'TOTAL':<20} | €{total:>10.2f}")
    print("=" * 70)


def set_budget_command() -> None:

    try:
        category = input("Category: ").strip().title()
        if not category:
            print("Error: Category cannot be empty")
            return

        limit_str = input("Monthly budget limit: ")
        limit = float(limit_str)

        if limit <= 0:
            print("Error: Budget must be greater than 0")
            return

        budget = Budget(category=category, limit=limit, period="monthly")
        save_budget(budget)
        print(f"\nBudget set! {category}: €{limit:.2f}/month")

    except ValueError:
        print("Error: Please enter a valid number for budget")
    except Exception as e:
        print(f"An error occurred: {e}")


def show_budgets() -> None:
    budgets = load_budgets()

    if not budgets:
        print("\nNo budgets set yet. Use 'set-budget' to create one!")
        return

    print("\n" + "=" * 50)
    print("YOUR BUDGETS")
    print("=" * 50)
    print(f"{'Category':<20} | {'Limit':>15}")
    print("-" * 50)

    for budget in budgets:
        print(f"{budget.category:<20} | €{budget.limit:>13.2f}/month")

    print("=" * 50)


def main():
    print("Welcome to SpendEase! 💰")
    print()

    action = (
        input(
            "What would you like to do? (add/list/summary/monthly/set-budget/budgets): "
        )
        .strip()
        .lower()
    )
    if action == "add":
        add_transaction()

    elif action == "list":
        display_transactions()

    elif action == "summary":
        show_summary()

    elif action == "monthly":
        show_monthly_breakdown()

    elif action == "set-budget":
        set_budget_command()

    elif action == "budgets":
        show_budgets()

    else:
        print(
            "Invalid option. Please choose 'add', 'list', 'summary', 'monthly', 'set-budget', or 'budgets'."
        )
