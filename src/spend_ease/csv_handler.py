import csv
import uuid
from pathlib import Path
from datetime import date, datetime

from spend_ease.models import Transaction
from spend_ease.storage import load_transactions, save_transaction
from spend_ease.categories import categorize_merchant


def export_to_csv(filepath: str) -> bool:
    transactions = load_transactions()

    if not transactions:
        return False

    try:
        with open(filepath, "w", newline="") as csvfile:
            fieldnames = ["id", "date", "category", "amount", "description"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for transaction in transactions:
                writer.writerow(
                    {
                        "id": transaction.id,
                        "date": transaction.date.isoformat(),
                        "category": transaction.category,
                        "amount": transaction.amount,
                        "description": transaction.description,
                    }
                )
        return True
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False


def import_from_csv(filepath: str) -> tuple[int, int]:
    if not Path(filepath).exists():
        return (0, 0)

    imported_count = 0
    error_count = 0
    existing_ids = {t.id for t in load_transactions()}

    try:
        with open(filepath, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                try:
                    if row["id"] in existing_ids:
                        error_count += 1
                        continue

                    transaction = Transaction(
                        id=row["id"],
                        amount=float(row["amount"]),
                        category=row["category"].strip().title(),
                        date=date.fromisoformat(row["date"]),
                        description=row["description"],
                    )

                    save_transaction(transaction)
                    imported_count += 1
                    existing_ids.add(transaction.id)

                except (ValueError, KeyError) as e:
                    error_count += 1
                    continue

        return (imported_count, error_count)
    except Exception as e:
        print(f"Error importing from CSV: {e}")
        return (0, error_count)


DATE_FORMATS = [
    "%Y-%m-%d %H:%M:%S",  # 2025-12-08 11:17:14
    "%Y-%m-%d",  # 2025-12-08
    "%d.%m.%Y",  # 08.12.2025
    "%d/%m/%Y",  # 08/12/2025
    "%m/%d/%Y",  # 12/08/2025
    "%d-%m-%Y",  # 08-12-2025
]


def parse_date_flexible(date_string: str) -> date:
    """Try multiple date formats and return the first that works."""
    date_string = date_string.strip()

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"Could not parse date: '{date_string}'")


def read_csv_headers(filepath: str) -> list[str]:
    """Read and return the column headers from a CSV file."""
    with open(filepath, "r", newline="") as csvfile:
        reader = csv.reader(csvfile)
        return next(reader)


def import_bank_csv(
    filepath: str,
    date_column: str,
    amount_column: str,
    description_column: str,
    status_column: str | None = None,
    skip_status: str | None = None,
) -> tuple[int, int, int]:
    if not Path(filepath).exists():
        return (0, 0, 0)

    imported_count = 0
    skipped_count = 0
    error_count = 0

    try:
        with open(filepath, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                try:
                    amount = float(row[amount_column].replace(",", "."))

                    if amount >= 0:
                        skipped_count += 1
                        continue

                    if status_column and skip_status:
                        status = row.get(status_column, "").strip()
                        if status == skip_status:
                            skipped_count += 1
                            continue

                    description = row[description_column].strip()
                    transaction_date = parse_date_flexible(row[date_column])

                    transaction = Transaction(
                        id=str(uuid.uuid4()),
                        amount=abs(amount),
                        category=categorize_merchant(description),
                        date=transaction_date,
                        description=description,
                    )

                    save_transaction(transaction)
                    imported_count += 1

                except (ValueError, KeyError):
                    error_count += 1
                    continue

        return (imported_count, skipped_count, error_count)
    except Exception as e:
        print(f"Error importing bank CSV: {e}")
        return (0, skipped_count, error_count)
