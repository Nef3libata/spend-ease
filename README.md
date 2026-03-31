# SpendEase

A personal finance tracker for managing expenses, budgets, and financial insights.

## Installation

```bash
git clone https://github.com/Nef3libata/spend-ease.git
cd spend-ease
uv pip install -e .
```

## Running the Application

**CLI (Interactive REPL):**
```bash
uv run -m spend_ease
```

**Web Dashboard:**
```bash
uv run -m spend_ease dashboard
```

## Core Features

### 1. Transaction Management
- Add transactions manually or via CSV import
- Edit and delete existing transactions
- Auto-categorization based on merchant names
- Support for bank CSV format with column mapping

### 2. Budget Tracking
- Set monthly spending limits per category
- Real-time budget status with visual progress bars
- Warnings when approaching or exceeding limits

### 3. Financial Analysis
- Monthly spending trends and breakdowns
- Category-based spending summaries
- Recurring payment detection (subscriptions, rent, etc.)
- Balance forecasting based on income and spending patterns
- Interactive charts (Plotly) and exportable PNG charts (Matplotlib)

### 4. Two User Interfaces
- **CLI**
- **Web Dashboard**

## Usage Examples

### CLI Commands
```bash
>> add 25 food lunch              # Quick add
>> list                           # View all transactions
>> summary                        # Spending breakdown with budgets
>> monthly                        # Monthly trends
>> recurring                      # Detect recurring payments
>> forecast 3                     # 3-month balance forecast
>> budget set food 200            # Set category budget
>> bank-import transactions.csv   # Import from bank CSV
>> export backup.csv              # Export data
>> visualize                      # Generate charts
```

### Web Dashboard
The dashboard (`http://localhost:8501`) provides:
- **Overview**: Summary of spending, category pie chart, monthly bar chart
- **Transactions**: Add, edit, delete with inline table editing
- **Import**: Upload bank CSV with column mapping
- **Budgets**: Set limits and track progress visually

## Technical Implementation

**Requirements:**
- Python 3.10+
- Installable package with `pyproject.toml`
- Entry point via `__main__.py` (supports `uv run -m spend_ease`)

**Key Technologies:**
- **Type hints & dataclasses** for type safety
- **Streamlit** for web dashboard
- **Plotly** for interactive charts
- **Matplotlib** for PNG export
- **JSON** for local data persistence

**Architecture:**
```
src/spend_ease/
├── __main__.py          # Entry point (CLI/dashboard router)
├── cli.py               # CLI interface with all commands
├── dashboard.py         # Streamlit web UI (4 pages)
├── models.py            # Transaction & Budget dataclasses
├── storage.py           # Transaction operations
├── budget_storage.py    # Budget persistence
├── settings.py          # User settings (income, balance)
├── analysis.py          # Monthly aggregation
├── categories.py        # Auto-categorization rules
├── csv_handler.py       # Generic CSV import/export
├── recurring.py         # Recurring payment detection
├── forecast.py          # Balance forecasting algorithm
└── visualize.py         # Chart generation
```

**Data Storage:**
All data stored locally in `~/.spend_ease/` as JSON files (transactions, budgets, settings).

## License

MIT
