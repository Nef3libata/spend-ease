# SpendEase

A smart financial tracker for international residents in Germany. Helping you understand your spending, optimize grocery costs, and save for what matters.

## Features

- **Track Transactions** - Record expenses with amount, category, and description
- **View Transaction History** - See all your spending in one place with totals
- **Category Analysis** - Breakdown spending by category with percentages and counts

## Installation

```bash
git clone https://github.com/Nef3libata/spend-ease.git
cd spend-ease
uv pip install -e .
```

## Usage

Run the application:

```bash
uv run -m spend_ease
```

### Add a Transaction

```
What would you like to do? (add/list/summary): add
Amount: 3.50
Category (e.g., Food, Transport): Food
Description: Coffee

✅ Transaction saved! €3.50 for Food
```

### View All Transactions

```
What would you like to do? (add/list/summary): list

============================================================
YOUR TRANSACTIONS
============================================================
2026-03-15 | Food         | €  3.50 | Coffee
2026-03-15 | Transport    | €  2.90 | Bus ticket
2026-03-14 | Food         | € 12.50 | Groceries
============================================================
TOTAL: €18.90
============================================================
```

### View Spending Summary

```
What would you like to do? (add/list/summary): summary

======================================================================
SPENDING SUMMARY
======================================================================
Category        |     Amount | Percentage | Count
----------------------------------------------------------------------
Food            | €    16.00 |      84.7% |     2
Transport       | €     2.90 |      15.3% |     1
======================================================================
TOTAL           | €    18.90 |     100.0% |     3
======================================================================
```

## Data Storage

Transactions are stored in `~/.spend_ease/storage.json` in a human-readable JSON format.

## Requirements

- Python >= 3.13
- uv (for package management)

## License

MIT
