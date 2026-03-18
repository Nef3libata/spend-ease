import csv
from pathlib import Path
from datetime import date

from spend_ease.models import Transaction
from spend_ease.storage import load_transactions, save_transaction


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
                writer.writerow({
                    "id": transaction.id,
                    "date": transaction.date.isoformat(),
                    "category": transaction.category,
                    "amount": transaction.amount,
                    "description": transaction.description
                })
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
                        description=row["description"]
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
