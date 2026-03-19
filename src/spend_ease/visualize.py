import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict
import calendar

from spend_ease.storage import load_transactions
from spend_ease.analysis import group_by_month


def create_category_pie_chart(output_path: str = "spending_by_category.png") -> bool:
    transactions = load_transactions()
    
    if not transactions:
        return False
    
    category_totals = defaultdict(float)
    for transaction in transactions:
        category_totals[transaction.category] += transaction.amount
    
    categories = list(category_totals.keys())
    amounts = list(category_totals.values())
    
    plt.figure(figsize=(10, 8))
    colors = plt.cm.Set3(range(len(categories)))
    
    wedges, texts, autotexts = plt.pie(
        amounts,
        labels=categories,
        autopct='%1.1f%%',
        colors=colors,
        startangle=90
    )
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)
        autotext.set_weight('bold')
    
    plt.title('Spending by Category', fontsize=16, fontweight='bold', pad=20)
    plt.axis('equal')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return True


def create_monthly_bar_chart(output_path: str = "monthly_spending.png") -> bool:
    transactions = load_transactions()
    
    if not transactions:
        return False
    
    monthly_data = group_by_month(transactions)
    
    if not monthly_data:
        return False
    
    sorted_months = sorted(monthly_data.keys())
    
    month_labels = []
    amounts = []
    
    for year, month in sorted_months:
        month_name = calendar.month_abbr[month]
        month_labels.append(f"{month_name} {year}")
        amounts.append(monthly_data[(year, month)]["amount"])
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(range(len(month_labels)), amounts, color='steelblue', alpha=0.8)
    
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.,
            height,
            f'€{height:.2f}',
            ha='center',
            va='bottom',
            fontsize=9
        )
    
    plt.xlabel('Month', fontsize=12, fontweight='bold')
    plt.ylabel('Amount (€)', fontsize=12, fontweight='bold')
    plt.title('Monthly Spending Trend', fontsize=16, fontweight='bold', pad=20)
    plt.xticks(range(len(month_labels)), month_labels, rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return True


def create_all_charts(output_dir: str = ".") -> tuple[bool, bool]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    pie_success = create_category_pie_chart(str(output_path / "spending_by_category.png"))
    bar_success = create_monthly_bar_chart(str(output_path / "monthly_spending.png"))
    
    return (pie_success, bar_success)
