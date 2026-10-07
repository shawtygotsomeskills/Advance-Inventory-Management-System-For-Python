# 📦 Inventory Management System (Python)

A simple, menu-driven **command-line inventory management system** for small shops, built with only **`pandas`**, **`matplotlib`** and **`csv`**. It lets a shop owner manage stock, generate bills, reorder low-stock items, export CSV reports, view charts and analyse profit and loss.

Built using plain Python logic (`if / elif / else`, loops and functions), so it is easy to read and a good fit for beginners and college or school projects.

---

## ✨ Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Stock entry** | The owner enters item name, quantity, cost price, selling price and reorder level. |
| 2 | **Billing** | Every sale generates a formatted bill (printed on screen and saved to `bills.txt`). |
| 3 | **Automatic stock update** | Stock decreases as soon as a sale is made. Out-of-stock items can't be sold. |
| 4 | **Reordering** | Items at or below their reorder level are listed, and the owner can reorder them. |
| 5 | **CSV reports** | Inventory, sales, purchase and summary reports are exported to CSV. |
| 6 | **Charts** | Four charts: bar chart, histogram, pie chart and a profit/loss bar chart. |
| 7 | **Profit & loss analysis** | Per-item and overall profit or loss, profit margin, and the best and worst items. |

---

## 🛠️ Requirements

- Python 3.7 or higher
- [pandas](https://pandas.pydata.org/)
- [matplotlib](https://matplotlib.org/)

(`csv` is part of Python's standard library.)

Install the dependencies:

```bash
pip install pandas matplotlib
```

---

## 🚀 How to Run

```bash
git clone https://github.com/<shawtygotsomeskills>/<Advanced-Inventory-Management-System-For-Python>.git
cd <Advanced-Inventory-Management-System-For-Python>
python inventory_management.py
```

---

## 📋 Menu

```
1. Add / enter stock
2. View stock
3. Make a sale (generate bill)
4. Reorder stock
5. Save CSV reports
6. Show charts
7. Profit & loss analysis
8. Exit
```

### Typical workflow

1. **Add stock** (option 1): enter each item's details. Type `done` as the item name to finish.
2. **Make a sale** (option 3): enter the customer name, pick items and quantities, and type `done` to print the bill.
3. **Reorder** (option 4): restock any item that has fallen to or below its reorder level.
4. **Analyse**: use options 5, 6 and 7 to export reports, view charts and check profit or loss.

---

## 🧾 Sample Bill

```
====================================================
                    SALES BILL
====================================================
Bill No : 1
Date    : 07-10-2026 14:32:10
Customer: Ravi
----------------------------------------------------
Item                 Qty       Price        Amount
----------------------------------------------------
Pen                   10        5.00         50.00
Notebook               2       40.00         80.00
----------------------------------------------------
GRAND TOTAL                                 130.00
====================================================
        Thank you! Visit again.
====================================================
```

---

## 📊 Charts

All four charts are shown in one window and saved as `inventory_charts.png`:

1. **Bar chart**: stock quantity per item
2. **Histogram**: distribution of selling prices
3. **Pie chart**: revenue share per item (stock value share if nothing has been sold yet)
4. **Bar chart**: profit (green) or loss (red) per item

---

## 📁 Files Generated

| File | Created by | Contents |
|------|-----------|----------|
| `bills.txt` | Making a sale | Copy of every bill generated |
| `inventory_report.csv` | Option 5 | Stock, stock value, profit per unit, status (OK / REORDER NEEDED / OUT OF STOCK) |
| `sales_report.csv` | Option 5 | Every item sold with revenue, cost and profit |
| `purchase_report.csv` | Option 5 | All reorders and their cost |
| `summary_report.csv` | Option 5 | Total stock, stock value, revenue, cost of goods sold, profit or loss |
| `inventory_charts.png` | Option 6 | Image of the four charts |

---

## 💰 How Profit & Loss Is Calculated

```
Revenue       = Selling price × Quantity sold
Cost of goods = Cost price × Quantity sold
Profit / Loss = Revenue − Cost of goods
Profit margin = (Profit / Revenue) × 100
```

Money spent on reordering is shown separately in the analysis.

---

## ⚠️ Limitations

- Data is stored **in memory only**. Stock and sales are lost when the program exits, so save the CSV reports before quitting.
- Item names are matched case-insensitively (`pen` and `Pen` are the same item).
- It is a single-user, command-line program with no login system.

---

## 🔮 Future Improvements

- Load stock from `inventory_report.csv` on startup so data persists between runs
- Discounts and GST/tax on bills
- Date-wise sales reports
- Remove or edit items
- A GUI version

---

## 🤝 Contributing

Suggestions and pull requests are welcome. Feel free to fork the repo and improve it.

## 📄 License

This project is open source.

