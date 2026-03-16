from datetime import date
from collections import defaultdict
from spend_ease.models import Transaction


def group_by_month(transactions: list[Transaction]) -> dict:
    """Group transactions by month and calculate totals.

    Returns:
        dict: {(year, month): {'amount': float, 'count': int, 'transactions': list}}
    """

    monthly_data = defaultdict(lambda: {"amount": 0.0, "count": 0, "transactions": []})

    for transaction in transactions:
        month_key = (transaction.date.year, transaction.date.month)
        monthly_data[month_key]["amount"] += transaction.amount
        monthly_data[month_key]["count"] += 1
        monthly_data[month_key]["transactions"].append(transaction)

    return dict(monthly_data)
