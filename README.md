# SpendEase

A smart financial tracker for international residents in Germany. Helping you understand your spending, optimize grocery costs, and save for what matters.

## Features

### Transaction Management

- **Quick Add** - `add 25 food lunch` (3 seconds, no flags!)
- **Edit & Delete** - Fix mistakes or remove transactions
- **CSV Import/Export** - Backup and bulk import your data

### Analysis & Insights

- **Spending Summary** - Category breakdown with budget warnings
- **Monthly Trends** - Track spending patterns over time
- **Visual Charts** - Generate pie and bar charts (PNG)

### Budget Tracking

- **Set Budgets** - Monthly limits per category
- **Real-time Warnings** - See how much budget remains
- **Smart Alerts** - Know when you're over budget

## Quick Start

### Installation

```bash
git clone https://github.com/Nef3libata/spend-ease.git
cd spend-ease
uv pip install -e .
```

### Run SpendEase

```bash
spend-ease
```

Or with uv:

```bash
uv run spend-ease
```

## 📖 Usage

SpendEase uses an **interactive REPL** (Read-Eval-Print Loop) for fast, daily use:

```
SpendEase 💰  Type 'help' for commands, 'quit' to exit.

>> help
Commands:
  add <amount> <category> [description]   Add a transaction
  add                                     Add interactively
  list                                    Show all transactions
  summary                                 Spending summary with budgets
  monthly                                 Monthly breakdown
  edit                                    Edit a transaction
  delete                                  Delete a transaction
  budget set <category> <limit>           Set monthly budget
  budget list                             Show all budgets
  export [filename]                       Export to CSV
  import <filename>                       Import from CSV
  visualize [directory]                   Generate charts
  quit                                    Exit
```

### Examples

**Quick expense tracking:**

```
>> add 25 food lunch
Saved! €25.00 for Food

>> add 2.90 transport bus
Saved! €2.90 for Transport

>> add 89 rent monthly payment
Saved! €89.00 for Rent
```

**Interactive add (with prompts):**

```
>> add
Amount: 12.50
Category: Food
Description (optional): Groceries
Saved! €12.50 for Food
```

**View spending:**

```
>> list
=================================================================
YOUR TRANSACTIONS
=================================================================
  1. 2026-03-20 | Food         | €   25.00 | lunch
  2. 2026-03-20 | Transport    | €    2.90 | bus
  3. 2026-03-20 | Rent         | €   89.00 | monthly payment
=================================================================
     TOTAL: €116.90  (3 transactions)
=================================================================
```

**Check budget status:**

```
>> summary
==========================================================================================
SPENDING SUMMARY
==========================================================================================
Category        |      Spent |     Budget | Status          |      % | Count
------------------------------------------------------------------------------------------
Rent            | €    89.00 |          - | no budget       |  76.1% |     1
Food            | €    25.00 |    €100.00 | €75.00 left     |  21.4% |     1
Transport       | €     2.90 |     €50.00 | €47.10 left     |   2.5% |     1
==========================================================================================
TOTAL           | €   116.90
==========================================================================================
```

**Set budgets:**

```
>> budget set food 200
Budget set: Food → €200.00/month

>> budget set transport 50
Budget set: Transport → €50.00/month

>> budget list
=============================================
YOUR BUDGETS
=============================================
  Food                 €200.00/month
  Transport            €50.00/month
=============================================
```

**Generate visual reports:**

```
>> visualize
Generating charts...
  Pie chart  → ./spending_by_category.png
  Bar chart  → ./monthly_spending.png
```

**Backup your data:**

```
>> export backup.csv
Exported to backup.csv

>> import backup.csv
Imported 15 transaction(s)
```

## 📁 Data Storage

All data is stored locally in `~/.spend_ease/`:

- `storage.json` - Your transactions
- `budgets.json` - Your budget settings

Data is stored in human-readable JSON format for easy backup and portability.

## 🛠️ Technical Details

**Built with:**

- Python 3.13+ with type hints and dataclasses
- Matplotlib for data visualization

## 📄 License

MIT
