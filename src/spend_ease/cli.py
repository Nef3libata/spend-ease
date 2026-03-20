import calendar
from collections import defaultdict
from datetime import date
from uuid import uuid4

from spend_ease.models import Transaction, Budget
from spend_ease.storage import (
    save_transaction,
    load_transactions,
    delete_transaction,
    update_transaction,
)
from spend_ease.budget_storage import get_budget, save_budget, load_budgets
from spend_ease.analysis import group_by_month
from spend_ease.csv_handler import export_to_csv, import_from_csv
from spend_ease.visualize import create_all_charts


def cmd_add(
    amount: float,
    category: str,
    description: str = "",
    transaction_date: date | None = None,
) -> None:
    if amount <= 0:
        print("Error: Amount must be greater than 0")
        return

    category = category.strip().title()
    if not category:
        print("Error: Category cannot be empty")
        return

    transaction = Transaction(
        id=str(uuid4()),
        amount=amount,
        category=category,
        date=transaction_date or date.today(),
        description=description,
    )
    save_transaction(transaction)
    print(f"Saved! €{amount:.2f} for {category}")


def cmd_list() -> None:
    transactions = load_transactions()

    if not transactions:
        print("No transactions yet. Add your first with: add 25 food lunch")
        return

    print("\n" + "=" * 65)
    print("YOUR TRANSACTIONS")
    print("=" * 65)
    for idx, t in enumerate(transactions, 1):
        print(
            f"{idx:>3}. {t.date} | {t.category:<12} | €{t.amount:>8.2f} | {t.description}"
        )
    print("=" * 65)
    total = sum(t.amount for t in transactions)
    print(f"     TOTAL: €{total:.2f}  ({len(transactions)} transactions)")
    print("=" * 65)


def cmd_summary() -> None:
    transactions = load_transactions()

    if not transactions:
        print("No transactions yet.")
        return

    categories = defaultdict(lambda: {"amount": 0.0, "count": 0})

    for t in transactions:
        categories[t.category]["amount"] += t.amount
        categories[t.category]["count"] += 1

    total = sum(cat["amount"] for cat in categories.values())

    category_data = [
        (cat, data["amount"], data["amount"] / total * 100, data["count"])
        for cat, data in categories.items()
    ]
    category_data.sort(key=lambda x: x[1], reverse=True)

    print("\n" + "=" * 90)
    print("SPENDING SUMMARY")
    print("=" * 90)
    print(
        f"{'Category':<15} | {'Spent':>10} | {'Budget':>10} | {'Status':<15} | {'%':>6} | {'Count':>5}"
    )
    print("-" * 90)

    for category, amount, percentage, count in category_data:
        budget = get_budget(category)
        if budget:
            remaining = budget.limit - amount
            status = (
                f"€{remaining:.2f} left"
                if remaining >= 0
                else f"€{abs(remaining):.2f} over"
            )
            budget_str = f"€{budget.limit:.2f}"
        else:
            status = "no budget"
            budget_str = "-"

        print(
            f"{category:<15} | €{amount:>9.2f} | {budget_str:>10} | {status:<15} | {percentage:>5.1f}% | {count:>5}"
        )

    print("=" * 90)
    print(f"{'TOTAL':<15} | €{total:>9.2f}")
    print("=" * 90)


def cmd_monthly() -> None:
    transactions = load_transactions()

    if not transactions:
        print("No transactions yet.")
        return

    monthly_data = group_by_month(transactions)

    print("\n" + "=" * 70)
    print("MONTHLY SPENDING BREAKDOWN")
    print("=" * 70)
    print(f"{'Month':<20} | {'Amount':>12} | {'Transactions':>12} | {'Avg/Day':>10}")
    print("-" * 70)

    for year, month in sorted(monthly_data.keys(), reverse=True):
        data = monthly_data[(year, month)]
        month_year = f"{calendar.month_name[month]} {year}"
        avg_per_day = data["amount"] / calendar.monthrange(year, month)[1]
        print(
            f"{month_year:<20} | €{data['amount']:>10.2f} | {data['count']:>12} | €{avg_per_day:>9.2f}"
        )

    print("=" * 70)
    total = sum(d["amount"] for d in monthly_data.values())
    print(f"{'TOTAL':<20} | €{total:>10.2f}")
    print("=" * 70)


def cmd_budget_set(category: str, limit: float) -> None:
    category = category.strip().title()
    if not category:
        print("Error: Category cannot be empty")
        return
    if limit <= 0:
        print("Error: Budget must be greater than 0")
        return
    save_budget(Budget(category=category, limit=limit, period="monthly"))
    print(f"Budget set: {category} → €{limit:.2f}/month")


def cmd_budget_list() -> None:
    budgets = load_budgets()

    if not budgets:
        print("No budgets set. Try: budget set food 200")
        return

    print("\n" + "=" * 45)
    print("YOUR BUDGETS")
    print("=" * 45)
    for b in budgets:
        print(f"  {b.category:<20} €{b.limit:.2f}/month")
    print("=" * 45)


def cmd_delete_interactive() -> None:
    transactions = load_transactions()

    if not transactions:
        print("No transactions to delete.")
        return

    cmd_list()
    try:
        choice = input("\nEnter transaction # to delete (or cancel): ").strip()
        if choice.lower() == "cancel":
            return
        idx = int(choice)
        if idx < 1 or idx > len(transactions):
            print(f"Error: Enter a number between 1 and {len(transactions)}")
            return
        t = transactions[idx - 1]
        confirm = (
            input(
                f"Delete €{t.amount:.2f} - {t.category} - {t.description}? (yes/no): "
            )
            .strip()
            .lower()
        )
        if confirm == "yes":
            if delete_transaction(t.id):
                print("Deleted!")
        else:
            print("Cancelled.")
    except ValueError:
        print("Error: Enter a valid number")


def cmd_edit_interactive() -> None:
    transactions = load_transactions()

    if not transactions:
        print("No transactions to edit.")
        return

    cmd_list()
    try:
        choice = input("\nEnter transaction # to edit (or cancel): ").strip()
        if choice.lower() == "cancel":
            return
        idx = int(choice)
        if idx < 1 or idx > len(transactions):
            print(f"Error: Enter a number between 1 and {len(transactions)}")
            return
        t = transactions[idx - 1]
        print(f"\nEditing: €{t.amount:.2f} - {t.category} - {t.description}")
        print("(Press Enter to keep current value)\n")

        amount_in = input(f"Amount [{t.amount}]: ").strip()
        new_amount = float(amount_in) if amount_in else t.amount

        category_in = input(f"Category [{t.category}]: ").strip().title()
        new_category = category_in if category_in else t.category

        desc_in = input(f"Description [{t.description}]: ").strip()
        new_description = desc_in if desc_in else t.description

        date_in = input(f"Date [{t.date}] (YYYY-MM-DD or Enter): ").strip()
        if date_in:
            new_date = date.fromisoformat(date_in)
        else:
            new_date = t.date

        if new_amount <= 0:
            print("Error: Amount must be greater than 0")
            return

        updated = Transaction(
            id=t.id,
            amount=new_amount,
            category=new_category,
            date=new_date,
            description=new_description,
        )
        if update_transaction(t.id, updated):
            print("Updated!")
        else:
            print("Error: Transaction not found.")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_export(filepath: str = "transactions.csv") -> None:
    if not filepath.endswith(".csv"):
        filepath += ".csv"
    if export_to_csv(filepath):
        print(f"Exported to {filepath}")
    else:
        print("Export failed. No transactions to export.")


def cmd_import(filepath: str) -> None:
    imported, errors = import_from_csv(filepath)
    if imported > 0:
        print(f"Imported {imported} transaction(s)")
    if errors > 0:
        print(f"Skipped {errors} (duplicates or errors)")
    if imported == 0 and errors == 0:
        print("Import failed. File not found or empty.")


def cmd_visualize(output_dir: str = ".") -> None:
    print("Generating charts...")
    pie_ok, bar_ok = create_all_charts(output_dir)
    if pie_ok:
        print(f"  Pie chart  → {output_dir}/spending_by_category.png")
    if bar_ok:
        print(f"  Bar chart  → {output_dir}/monthly_spending.png")
    if not pie_ok and not bar_ok:
        print("No transactions to chart.")


REPL_HELP = """
Commands:
  add <amount> <category> [description]   Add a transaction  (e.g. add 25 food lunch)
  add                                     Add interactively with prompts
  list                                    Show all transactions
  summary                                 Spending summary with budget warnings
  monthly                                 Monthly spending breakdown
  edit                                    Edit a transaction
  delete                                  Delete a transaction
  budget set <category> <limit>           Set monthly budget  (e.g. budget set food 200)
  budget list                             Show all budgets
  export [filename]                       Export to CSV
  import <filename>                       Import from CSV
  visualize [directory]                   Generate spending charts
  help                                    Show this help
  quit                                    Exit
"""


def _repl_add(parts: list[str]) -> None:
    """Handle 'add [amount] [category] [description...]' in REPL."""
    try:
        if parts:
            amount = float(parts[0])
            category = parts[1] if len(parts) > 1 else input("Category: ").strip()
            description = " ".join(parts[2:]) if len(parts) > 2 else ""
        else:
            amount = float(input("Amount: ").strip())
            category = input("Category: ").strip()
            description = input("Description (optional): ").strip()
        cmd_add(amount, category, description)
    except ValueError:
        print("Error: Invalid amount. Usage: add 25 food lunch")


def _repl_budget(parts: list[str]) -> None:
    """Handle 'budget set/list ...' in REPL."""
    if not parts:
        cmd_budget_list()
        return

    sub = parts[0].lower()

    if sub == "list":
        cmd_budget_list()

    elif sub == "set":
        try:
            if len(parts) >= 3:
                cmd_budget_set(parts[1], float(parts[2]))
            elif len(parts) == 2:
                limit = float(input("Monthly limit: ").strip())
                cmd_budget_set(parts[1], limit)
            else:
                category = input("Category: ").strip()
                limit = float(input("Monthly limit: ").strip())
                cmd_budget_set(category, limit)
        except ValueError:
            print("Error: Invalid limit. Usage: budget set food 200")
    else:
        print("Usage: budget set <category> <limit>  |  budget list")


def run_repl() -> None:
    """Start the interactive REPL session."""
    print("SpendEase 💰  Type 'help' for commands, 'quit' to exit.\n")

    while True:
        try:
            line = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHappy saving!")
            break

        if not line:
            continue

        parts = line.split()
        command = parts[0].lower()
        rest = parts[1:]

        if command in ("quit", "exit", "q"):
            print("Happy saving!")
            break
        elif command == "help":
            print(REPL_HELP)
        elif command == "add":
            _repl_add(rest)
        elif command == "list":
            cmd_list()
        elif command == "summary":
            cmd_summary()
        elif command == "monthly":
            cmd_monthly()
        elif command == "edit":
            cmd_edit_interactive()
        elif command == "delete":
            cmd_delete_interactive()
        elif command == "budget":
            _repl_budget(rest)
        elif command == "export":
            cmd_export(rest[0] if rest else "transactions.csv")
        elif command == "import":
            if rest:
                cmd_import(rest[0])
            else:
                print("Usage: import <filename.csv>")
        elif command == "visualize":
            cmd_visualize(rest[0] if rest else ".")
        else:
            print(f"Unknown command '{command}'. Type 'help' for available commands.")


def main() -> None:
    """Entry point - starts the interactive REPL."""
    run_repl()


if __name__ == "__main__":
    main()
