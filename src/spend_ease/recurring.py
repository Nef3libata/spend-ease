from collections import defaultdict
from statistics import mean, stdev

from spend_ease.models import Transaction

AMOUNT_TOLERANCE = 0.05
INTERVAL_TOLERANCE = 3

PERIODS = {
    "weekly": 7,
    "monthly": 30,
    "quarterly": 90,
}


def group_by_category(transactions: list[Transaction]) -> dict[str, list[Transaction]]:
    groups = defaultdict(list)

    for transaction in transactions:
        groups[transaction.category].append(transaction)

    return dict(groups)


def group_by_similar_amount(
    transactions: list[Transaction], tolerance: float = AMOUNT_TOLERANCE
) -> list[list[Transaction]]:
    if not transactions:
        return []

    sorted_transactions = sorted(transactions, key=lambda t: t.amount)
    groups = []
    current_group = [sorted_transactions[0]]

    for transaction in sorted_transactions[1:]:
        base = current_group[0].amount
        if base * (1 - tolerance) <= transaction.amount <= base * (1 + tolerance):
            current_group.append(transaction)
        else:
            groups.append(current_group)
            current_group = [transaction]

    groups.append(current_group)
    return groups


def calculate_intervals(transactions: list[Transaction]) -> list[int]:
    if len(transactions) < 2:
        return []

    sorted_transactions = sorted(transactions, key=lambda t: t.date)
    return [
        (sorted_transactions[i].date - sorted_transactions[i - 1].date).days
        for i in range(1, len(sorted_transactions))
    ]


def detect_period(intervals: list[int]) -> str | None:
    if not intervals:
        return None

    avg = mean(intervals)
    spread = stdev(intervals) if len(intervals) > 1 else 0

    if spread > INTERVAL_TOLERANCE:
        return None

    for period_name, target in PERIODS.items():
        if abs(avg - target) <= INTERVAL_TOLERANCE:
            return period_name

    return None


def detect_recurring_payments(transactions: list[Transaction]) -> list[dict]:
    recurring_patterns = []
    by_category = group_by_category(transactions)

    for category, category_transactions in by_category.items():
        for group in group_by_similar_amount(category_transactions):
            intervals = calculate_intervals(group)
            period = detect_period(intervals)

            if period:
                recurring_patterns.append({
                    "category": category,
                    "amount": mean(transaction.amount for transaction in group),
                    "period": period,
                    "interval_days": mean(intervals),
                    "last_date": max(group, key=lambda t: t.date).date,
                    "count": len(group),
                })

    return sorted(recurring_patterns, key=lambda x: x["amount"], reverse=True)
