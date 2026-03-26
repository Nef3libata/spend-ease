from datetime import date

from spend_ease.models import Transaction
from spend_ease.recurring import detect_recurring_payments


def calculate_monthly_fixed_costs(transactions: list[Transaction]) -> float:
    recurring = detect_recurring_payments(transactions)

    monthly_total = 0.0
    for pattern in recurring:
        monthly_amount = pattern["amount"] * (30 / pattern["interval_days"])
        monthly_total += monthly_amount

    return monthly_total


def calculate_monthly_variable_spending(
    transactions: list[Transaction], months_to_analyze: int = 3
) -> float:
    if not transactions:
        return 0.0

    recurring = detect_recurring_payments(transactions)
    recurring_ids = set()

    for pattern in recurring:
        for transaction in transactions:
            if (
                transaction.category == pattern["category"]
                and abs(transaction.amount - pattern["amount"])
                <= pattern["amount"] * 0.05
            ):
                recurring_ids.add(transaction.id)

    variable_txns = [t for t in transactions if t.id not in recurring_ids]

    if not variable_txns:
        return 0.0

    sorted_txns = sorted(variable_txns, key=lambda t: t.date)
    recent_date = sorted_txns[-1].date

    cutoff_date = date(
        (
            recent_date.year
            if recent_date.month > months_to_analyze
            else recent_date.year - 1
        ),
        (
            recent_date.month - months_to_analyze
            if recent_date.month > months_to_analyze
            else 12 - (months_to_analyze - recent_date.month)
        ),
        1,
    )

    recent_variable = [t for t in variable_txns if t.date >= cutoff_date]

    if not recent_variable:
        return 0.0

    total_variable = sum(t.amount for t in recent_variable)

    months_span = (
        (recent_date.year - cutoff_date.year) * 12
        + (recent_date.month - cutoff_date.month)
        + 1
    )

    return total_variable / max(months_span, 1)


def forecast_balance(
    current_balance: float,
    monthly_income: float,
    transactions: list[Transaction],
    months_ahead: int = 3,
) -> list[dict]:
    fixed_costs = calculate_monthly_fixed_costs(transactions)
    variable_costs = calculate_monthly_variable_spending(transactions)

    forecast = []
    balance = current_balance
    today = date.today()

    for i in range(1, months_ahead + 1):
        month = today.month + i
        year = today.year

        while month > 12:
            month -= 12
            year += 1

        balance += monthly_income - fixed_costs - variable_costs

        forecast.append(
            {
                "month": month,
                "year": year,
                "fixed_costs": fixed_costs,
                "variable_costs": variable_costs,
                "projected_balance": balance,
            }
        )

    return forecast
