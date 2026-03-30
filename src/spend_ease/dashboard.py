import csv
import io
import tempfile
import uuid
from collections import defaultdict
from datetime import date
from pathlib import Path

import plotly.express as px
import streamlit as st

from spend_ease.analysis import group_by_month
from spend_ease.budget_storage import get_budget, load_budgets, save_budget
from spend_ease.csv_handler import import_bank_csv
from spend_ease.models import Budget, Transaction
from spend_ease.storage import (
    delete_transaction,
    load_transactions,
    save_transaction,
    update_transaction,
)


# Page config

st.set_page_config(page_title="SpendEase", page_icon="💰", layout="wide")


# Sidebar

st.sidebar.title("💰 SpendEase")
page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Transactions", "Import", "Budgets"],
)


# Helper functions


def get_category_totals(transactions):
    """Group transactions by category and return sorted totals."""
    categories = defaultdict(lambda: {"amount": 0.0, "count": 0})

    for transaction in transactions:
        categories[transaction.category]["amount"] += transaction.amount
        categories[transaction.category]["count"] += 1

    return dict(sorted(categories.items(), key=lambda x: x[1]["amount"], reverse=True))


# Overview page


def page_overview():
    st.title("Overview")

    transactions = load_transactions()

    if not transactions:
        st.info("No transactions yet. Go to **Import** to load your bank CSV or add transactions.")
        return

    total_spent = sum(t.amount for t in transactions)
    categories = get_category_totals(transactions)
    monthly = group_by_month(transactions)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Spent", f"€{total_spent:,.2f}")
    col2.metric("Transactions", len(transactions))
    col3.metric("Categories", len(categories))

    if monthly:
        sorted_months = sorted(monthly.keys())
        last_month_key = sorted_months[-1]
        col4.metric(
            f"This Month ({last_month_key[1]}/{last_month_key[0]})",
            f"€{monthly[last_month_key]['amount']:,.2f}",
        )

    st.divider()

    chart_left, chart_right = st.columns(2)

    with chart_left:
        st.subheader("Spending by Category")
        cat_names = list(categories.keys())
        cat_amounts = [data["amount"] for data in categories.values()]

        fig_pie = px.pie(
            names=cat_names,
            values=cat_amounts,
            hole=0.4,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_pie, width="stretch")

    with chart_right:
        st.subheader("Monthly Spending")
        sorted_months = sorted(monthly.keys())
        month_labels = [f"{m[1]:02d}/{m[0]}" for m in sorted_months]
        month_amounts = [monthly[m]["amount"] for m in sorted_months]

        fig_bar = px.bar(
            x=month_labels,
            y=month_amounts,
            labels={"x": "Month", "y": "Amount (€)"},
        )
        fig_bar.update_layout(margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_bar, width="stretch")

    # Top spending categories table
    st.subheader("Category Breakdown")
    table_data = []
    for category, data in categories.items():
        budget = get_budget(category)
        budget_str = f"€{budget.limit:,.2f}" if budget else "—"
        table_data.append(
            {
                "Category": category,
                "Spent": f"€{data['amount']:,.2f}",
                "Count": data["count"],
                "% of Total": f"{data['amount'] / total_spent * 100:.1f}%",
                "Budget": budget_str,
            }
        )
    st.table(table_data)


# Transactions page


def page_transactions():
    st.title("Transactions")

    transactions = load_transactions()
    existing_categories = (
        sorted(set(t.category for t in transactions)) if transactions else []
    )

    with st.expander("Add New Transaction", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            amount = st.number_input(
                "Amount (€)",
                min_value=0.01,
                step=0.01,
                format="%.2f",
            )

            if existing_categories:
                category_mode = st.radio(
                    "Category",
                    ["Select existing", "Create new"],
                    horizontal=True,
                )

                if category_mode == "Select existing":
                    category = st.selectbox("Choose category", existing_categories)
                else:
                    category = st.text_input("New category name")
            else:
                category = st.text_input("Category")

        with col2:
            transaction_date = st.date_input(
                "Date",
                value=date.today(),
                max_value=date.today(),
            )

            description = st.text_input("Description (optional)")

        if st.button("Add Transaction", type="primary", use_container_width=True):
            if not category or not category.strip():
                st.error("Please enter a category")
            elif amount <= 0:
                st.error("Amount must be greater than 0")
            else:
                transaction = Transaction(
                    id=str(uuid.uuid4()),
                    amount=amount,
                    category=category.strip().title(),
                    date=transaction_date,
                    description=description.strip(),
                )

                save_transaction(transaction)
                st.success(f"Added €{amount:.2f} for {category.strip().title()}")
                st.rerun()

    st.divider()

    if not transactions:
        st.info("No transactions yet. Add one above to get started.")
        return

    # Filters
    all_categories = sorted(set(t.category for t in transactions))
    col_filter, col_sort = st.columns(2)

    with col_filter:
        selected_categories = st.multiselect(
            "Filter by category",
            all_categories,
            default=all_categories,
        )

    with col_sort:
        sort_by = st.selectbox(
            "Sort by",
            ["Date (newest)", "Date (oldest)", "Amount (high)", "Amount (low)"],
        )

    filtered = [t for t in transactions if t.category in selected_categories]

    if sort_by == "Date (newest)":
        filtered.sort(key=lambda t: t.date, reverse=True)
    elif sort_by == "Date (oldest)":
        filtered.sort(key=lambda t: t.date)
    elif sort_by == "Amount (high)":
        filtered.sort(key=lambda t: t.amount, reverse=True)
    elif sort_by == "Amount (low)":
        filtered.sort(key=lambda t: t.amount)

    st.caption(f"Showing {len(filtered)} of {len(transactions)} transactions")

    # Editable transaction table
    table_data = [
        {
            "Date": str(t.date),
            "Category": t.category,
            "Amount": t.amount,
            "Description": t.description,
            "Delete": False,
        }
        for t in filtered
    ]

    edited = st.data_editor(
        table_data,
        column_config={
            "Amount": st.column_config.NumberColumn("Amount (€)", format="€%.2f"),
            "Delete": st.column_config.CheckboxColumn("Delete?"),
        },
        disabled=["Date"],
        hide_index=True,
        use_container_width=True,
    )

    if st.button("Apply Changes", type="primary"):
        changes = 0
        deletions = 0

        for i, row in enumerate(edited):
            original = filtered[i]

            if row["Delete"]:
                delete_transaction(original.id)
                deletions += 1
                continue

            if (
                row["Category"] != original.category
                or row["Amount"] != original.amount
                or row["Description"] != original.description
            ):
                updated = Transaction(
                    id=original.id,
                    amount=row["Amount"],
                    category=row["Category"].strip().title(),
                    date=original.date,
                    description=row["Description"].strip(),
                )
                update_transaction(original.id, updated)
                changes += 1

        if changes > 0 or deletions > 0:
            parts = []
            if changes > 0:
                parts.append(f"{changes} edited")
            if deletions > 0:
                parts.append(f"{deletions} deleted")
            st.success(", ".join(parts))
            st.rerun()


# Import page


def page_import():
    st.title("Import Bank CSV")
    st.caption("Upload a CSV from any bank. You pick which columns to use.")

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is None:
        return

    # Read headers from uploaded file
    content = uploaded_file.getvalue().decode("utf-8")
    lines = content.splitlines()
    if not lines:
        st.error("File is empty.")
        return

    reader = csv.reader(io.StringIO(lines[0]))
    headers = next(reader)

    st.success(f"Found {len(lines) - 1} rows with columns: **{', '.join(headers)}**")

    # Column mapping
    st.subheader("Map Columns")
    col1, col2 = st.columns(2)

    with col1:
        date_col = st.selectbox("Date column", headers)
        amount_col = st.selectbox("Amount column", headers)

    with col2:
        desc_col = st.selectbox("Description column", headers)
        use_status = st.checkbox("Filter by status column?")

    status_col = None
    skip_status = None
    if use_status:
        status_col = st.selectbox("Status column", headers)
        skip_status = st.text_input("Skip transactions with status", "REVERTED")

    # Preview first 5 rows
    st.subheader("Preview")
    preview_reader = csv.DictReader(io.StringIO(content))
    preview_rows = []
    for i, row in enumerate(preview_reader):
        if i >= 5:
            break
        preview_rows.append(
            {
                "Date": row.get(date_col, ""),
                "Amount": row.get(amount_col, ""),
                "Description": row.get(desc_col, ""),
            }
        )
    st.table(preview_rows)

    # Import button
    if st.button("Import Transactions", type="primary"):
        # Save uploaded file to temp path for import_bank_csv
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            imported, skipped, errors = import_bank_csv(
                tmp_path,
                date_column=date_col,
                amount_column=amount_col,
                description_column=desc_col,
                status_column=status_col,
                skip_status=skip_status,
            )

            if imported > 0:
                st.success(f"Imported **{imported}** transactions!")
            if skipped > 0:
                st.info(f"Skipped {skipped} (income or filtered)")
            if errors > 0:
                st.warning(f"{errors} rows had errors")
            if imported == 0 and skipped == 0 and errors == 0:
                st.error("No transactions found to import.")
        finally:
            Path(tmp_path).unlink(missing_ok=True)


# Budgets page


def page_budgets():
    st.title("Budgets")

    transactions = load_transactions()
    categories = get_category_totals(transactions)
    budgets = load_budgets()

    # Current budgets
    if budgets:
        st.subheader("Current Budgets")
        for budget in budgets:
            spent = categories.get(budget.category, {}).get("amount", 0.0)
            remaining = budget.limit - spent
            progress = min(spent / budget.limit, 1.0) if budget.limit > 0 else 0

            col_name, col_bar, col_status = st.columns([2, 4, 2])
            col_name.write(f"**{budget.category}**")
            col_bar.progress(progress)

            if remaining >= 0:
                col_status.write(f"€{remaining:,.2f} left")
            else:
                col_status.write(f" €{abs(remaining):,.2f} over!")

    st.divider()

    # Set new budget
    st.subheader("Set Budget")
    all_categories = (
        sorted(set(t.category for t in transactions)) if transactions else []
    )

    if not all_categories:
        st.info("Import transactions first to set budgets by category.")
        return

    col_cat, col_limit, col_btn = st.columns([3, 2, 1])

    with col_cat:
        budget_category = st.selectbox("Category", all_categories)
    with col_limit:
        budget_limit = st.number_input("Monthly limit (€)", min_value=0.0, step=10.0)
    with col_btn:
        st.write("")
        if st.button("Set Budget"):
            if budget_limit > 0:
                save_budget(
                    Budget(
                        category=budget_category,
                        limit=budget_limit,
                        period="monthly",
                    )
                )
                st.success(
                    f"Budget set: {budget_category} → €{budget_limit:,.2f}/month"
                )
                st.rerun()
            else:
                st.warning("Please enter a budget amount greater than 0.")


# Page router

if page == "Overview":
    page_overview()
elif page == "Transactions":
    page_transactions()
elif page == "Import":
    page_import()
elif page == "Budgets":
    page_budgets()
