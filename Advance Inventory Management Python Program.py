"""
INVENTORY MANAGEMENT SYSTEM
Libraries used: pandas, matplotlib, csv  (nothing else)

Features
 a) Owner enters stock: item name, quantity, cost price, selling price
 b) Bill is generated on every sale
 c) Stock decreases automatically on a sale
 d) Reordering of low stock
 e) CSV reports
 f) 4 charts (bar, histogram, pie, profit/loss bar)
 g) Profit and loss analysis
"""

import csv
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# DATA STORAGE (kept in memory while the program runs)
# ---------------------------------------------------------------
COLUMNS = ["Item", "Quantity", "Cost Price", "Selling Price",
           "Reorder Level", "Units Sold"]
NUMERIC = ["Quantity", "Cost Price", "Selling Price",
           "Reorder Level", "Units Sold"]

inventory = pd.DataFrame(columns=COLUMNS)
sales_log = []       # one dict per item sold
purchase_log = []    # one dict per reorder
bill_counter = 1


# ---------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------
def get_number(prompt, number_type=float, minimum=0):
    """Keeps asking until the user types a valid number >= minimum."""
    while True:
        try:
            value = number_type(input(prompt))
            if value < minimum:
                print("   Value must be at least", minimum)
            else:
                return value
        except ValueError:
            print("   Invalid input. Please enter a number.")


def clean_numbers():
    """Makes sure numeric columns really are numbers."""
    global inventory
    inventory[NUMERIC] = inventory[NUMERIC].apply(pd.to_numeric)


def find_item(name):
    """Returns the row index of an item (case-insensitive) or None."""
    if inventory.empty:
        return None
    match = inventory[inventory["Item"].str.lower() == name.strip().lower()]
    if match.empty:
        return None
    return match.index[0]


def now():
    return pd.Timestamp.now().strftime("%d-%m-%Y %H:%M:%S")


# ---------------------------------------------------------------
# a) ASK THE OWNER FOR STOCK DETAILS
# ---------------------------------------------------------------
def add_stock():
    global inventory
    print("\n--- ADD STOCK (type 'done' as the item name to finish) ---")
    while True:
        name = input("Item name: ").strip()
        if name.lower() == "done":
            break
        if name == "":
            print("   Name cannot be empty.")
            continue

        idx = find_item(name)
        if idx is not None:
            print("   '" + name + "' already exists. Adding to its quantity.")
            extra = get_number("   Quantity to add: ", int, 1)
            inventory.at[idx, "Quantity"] += extra
            continue

        qty = get_number("Quantity in stock: ", int, 0)
        cost = get_number("Cost price (what you paid) per unit: ", float, 0)
        sell = get_number("Selling price per unit: ", float, 0)
        level = get_number("Reorder level (reorder when stock is at or below): ", int, 0)

        inventory.loc[len(inventory)] = [name, qty, cost, sell, level, 0]
        if sell < cost:
            print("   WARNING: selling price is below cost price (loss on every sale).")
        print("   Added", name)
    clean_numbers()


def view_stock():
    print("\n--- CURRENT STOCK ---")
    if inventory.empty:
        print("No stock yet. Please add stock first.")
    else:
        print(inventory.to_string(index=False))


# ---------------------------------------------------------------
# b) + c) SALE -> BILL -> STOCK DECREASES
# ---------------------------------------------------------------
def make_sale():
    global bill_counter
    if inventory.empty:
        print("\nNo stock available. Add stock first.")
        return

    print("\n--- NEW SALE ---")
    customer = input("Customer name: ").strip()
    if customer == "":
        customer = "Walk-in customer"

    cart = []
    while True:
        view_stock()
        name = input("\nItem to buy (or 'done' to finish): ").strip()
        if name.lower() == "done":
            break

        idx = find_item(name)
        if idx is None:
            print("   Item not found.")
            continue

        available = int(inventory.at[idx, "Quantity"])
        if available == 0:
            print("   Out of stock! Please reorder this item.")
            continue

        qty = get_number("Quantity (available " + str(available) + "): ", int, 1)
        if qty > available:
            print("   Not enough stock. Only", available, "left.")
            continue

        # c) stock decreases on buying
        inventory.at[idx, "Quantity"] -= qty
        inventory.at[idx, "Units Sold"] += qty

        item_name = inventory.at[idx, "Item"]
        sell = float(inventory.at[idx, "Selling Price"])
        cost = float(inventory.at[idx, "Cost Price"])
        cart.append({"Item": item_name, "Qty": qty, "Price": sell,
                     "Cost": cost, "Total": qty * sell})
        print("   Added to bill:", qty, "x", item_name)

    if len(cart) == 0:
        print("Nothing was bought. No bill created.")
        return

    # ----- b) print the bill -----
    time_now = now()
    grand_total = 0
    lines = []
    lines.append("=" * 52)
    lines.append("                    SALES BILL")
    lines.append("=" * 52)
    lines.append("Bill No : " + str(bill_counter))
    lines.append("Date    : " + time_now)
    lines.append("Customer: " + customer)
    lines.append("-" * 52)
    lines.append("{:<18}{:>6}{:>12}{:>14}".format("Item", "Qty", "Price", "Amount"))
    lines.append("-" * 52)
    for row in cart:
        lines.append("{:<18}{:>6}{:>12.2f}{:>14.2f}".format(
            row["Item"], row["Qty"], row["Price"], row["Total"]))
        grand_total += row["Total"]

        sales_log.append({
            "Bill No": bill_counter, "Date": time_now, "Customer": customer,
            "Item": row["Item"], "Quantity": row["Qty"],
            "Selling Price": row["Price"], "Cost Price": row["Cost"],
            "Revenue": row["Total"], "Cost": row["Qty"] * row["Cost"],
            "Profit": row["Total"] - row["Qty"] * row["Cost"]
        })
    lines.append("-" * 52)
    lines.append("{:<36}{:>16.2f}".format("GRAND TOTAL", grand_total))
    lines.append("=" * 52)
    lines.append("        Thank you! Visit again.")
    lines.append("=" * 52)

    bill_text = "\n".join(lines)
    print("\n" + bill_text)

    # keep a copy of every bill in a text file
    with open("bills.txt", "a") as f:
        f.write(bill_text + "\n\n")
    print("(Bill saved in bills.txt)")

    bill_counter += 1
    clean_numbers()

    # warn the owner if something is running low
    low = inventory[inventory["Quantity"] <= inventory["Reorder Level"]]
    if not low.empty:
        print("\n*** LOW STOCK ALERT: " + ", ".join(low["Item"]) +
              " -> please use the Reorder option ***")


# ---------------------------------------------------------------
# d) REORDERING OF STOCK
# ---------------------------------------------------------------
def reorder_stock():
    print("\n--- REORDER STOCK ---")
    if inventory.empty:
        print("No stock yet.")
        return

    low = inventory[inventory["Quantity"] <= inventory["Reorder Level"]]
    if low.empty:
        print("All items are above their reorder level. Nothing to reorder.")
        return

    print("Items that need reordering:")
    print(low[["Item", "Quantity", "Reorder Level", "Cost Price"]].to_string(index=False))

    for idx in low.index:
        name = inventory.at[idx, "Item"]
        choice = input("\nReorder '" + name + "'? (y/n): ").strip().lower()
        if choice == "y":
            qty = get_number("   Quantity to order: ", int, 1)
            cost = float(inventory.at[idx, "Cost Price"])
            inventory.at[idx, "Quantity"] += qty
            purchase_log.append({
                "Date": now(), "Item": name, "Quantity Ordered": qty,
                "Cost Price": cost, "Total Cost": qty * cost
            })
            print("   Ordered", qty, "of", name, "| cost =", round(qty * cost, 2))
        else:
            print("   Skipped.")
    clean_numbers()


# ---------------------------------------------------------------
# e) CSV REPORTS
# ---------------------------------------------------------------
def save_csv_reports():
    print("\n--- SAVING CSV REPORTS ---")
    if inventory.empty:
        print("Nothing to report yet.")
        return

    report = inventory.copy()
    report["Stock Value (Cost)"] = report["Quantity"] * report["Cost Price"]
    report["Profit Per Unit"] = report["Selling Price"] - report["Cost Price"]

    status = []
    for q, lvl in zip(report["Quantity"], report["Reorder Level"]):
        if q == 0:
            status.append("OUT OF STOCK")
        elif q <= lvl:
            status.append("REORDER NEEDED")
        else:
            status.append("OK")
    report["Status"] = status

    report.to_csv("inventory_report.csv", index=False)
    print("Saved: inventory_report.csv")

    if len(sales_log) > 0:
        pd.DataFrame(sales_log).to_csv("sales_report.csv", index=False)
        print("Saved: sales_report.csv")
    else:
        print("No sales yet, so sales_report.csv was not created.")

    if len(purchase_log) > 0:
        pd.DataFrame(purchase_log).to_csv("purchase_report.csv", index=False)
        print("Saved: purchase_report.csv")

    # summary file written with the csv module
    total_revenue = sum(r["Revenue"] for r in sales_log)
    total_cost = sum(r["Cost"] for r in sales_log)
    profit = total_revenue - total_cost
    with open("summary_report.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Items in Inventory", len(inventory)])
        writer.writerow(["Total Units in Stock", int(inventory["Quantity"].sum())])
        writer.writerow(["Stock Value (Cost)", round(float(report["Stock Value (Cost)"].sum()), 2)])
        writer.writerow(["Total Revenue", round(total_revenue, 2)])
        writer.writerow(["Cost of Goods Sold", round(total_cost, 2)])
        writer.writerow(["Profit / Loss", round(profit, 2)])
    print("Saved: summary_report.csv")


# ---------------------------------------------------------------
# f) CHARTS (bar, histogram, pie, profit/loss bar)
# ---------------------------------------------------------------
def show_charts():
    if inventory.empty:
        print("\nNo data to plot. Add stock first.")
        return

    data = inventory.copy()
    for col in NUMERIC:
        data[col] = pd.to_numeric(data[col])

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Inventory Dashboard", fontsize=16, fontweight="bold")

    # 1) BAR CHART - stock quantity of each item
    ax1 = axes[0][0]
    ax1.bar(data["Item"], data["Quantity"], color="steelblue")
    ax1.set_title("Stock Quantity per Item (Bar Chart)")
    ax1.set_xlabel("Item")
    ax1.set_ylabel("Quantity")
    ax1.tick_params(axis="x", rotation=45)

    # 2) HISTOGRAM - distribution of selling prices
    ax2 = axes[0][1]
    ax2.hist(data["Selling Price"], bins=5, color="orange", edgecolor="black")
    ax2.set_title("Selling Price Distribution (Histogram)")
    ax2.set_xlabel("Selling Price")
    ax2.set_ylabel("Number of Items")

    # 3) PIE CHART - revenue share (or stock value if nothing sold yet)
    ax3 = axes[1][0]
    if len(sales_log) > 0:
        sales_df = pd.DataFrame(sales_log)
        share = sales_df.groupby("Item")["Revenue"].sum()
        ax3.pie(share, labels=share.index, autopct="%1.1f%%", startangle=90)
        ax3.set_title("Revenue Share by Item (Pie Chart)")
    else:
        value = data["Quantity"] * data["Cost Price"]
        if value.sum() > 0:
            ax3.pie(value, labels=data["Item"], autopct="%1.1f%%", startangle=90)
        ax3.set_title("Stock Value Share (Pie Chart - no sales yet)")

    # 4) BAR CHART - profit / loss per item
    ax4 = axes[1][1]
    if len(sales_log) > 0:
        sales_df = pd.DataFrame(sales_log)
        pl = sales_df.groupby("Item")["Profit"].sum()
        colors = []
        for p in pl:
            if p >= 0:
                colors.append("green")
            else:
                colors.append("red")
        ax4.bar(pl.index, pl.values, color=colors)
        ax4.axhline(0, color="black", linewidth=0.8)
        ax4.set_title("Profit / Loss per Item (Bar Chart)")
        ax4.set_xlabel("Item")
        ax4.set_ylabel("Profit (green) / Loss (red)")
        ax4.tick_params(axis="x", rotation=45)
    else:
        ax4.text(0.5, 0.5, "No sales yet", ha="center", va="center", fontsize=14)
        ax4.set_title("Profit / Loss per Item")
        ax4.axis("off")

    plt.tight_layout()
    plt.savefig("inventory_charts.png", dpi=150)
    print("\nCharts saved as inventory_charts.png")
    plt.show()


# ---------------------------------------------------------------
# g) PROFIT AND LOSS ANALYSIS
# ---------------------------------------------------------------
def profit_loss_analysis():
    print("\n--- PROFIT & LOSS ANALYSIS ---")
    if len(sales_log) == 0:
        print("No sales made yet.")
        return

    sales_df = pd.DataFrame(sales_log)
    summary = sales_df.groupby("Item")[["Quantity", "Revenue", "Cost", "Profit"]].sum()

    status = []
    for p in summary["Profit"]:
        if p > 0:
            status.append("PROFIT")
        elif p < 0:
            status.append("LOSS")
        else:
            status.append("BREAK-EVEN")
    summary["Result"] = status

    print(summary.round(2).to_string())

    total_revenue = summary["Revenue"].sum()
    total_cost = summary["Cost"].sum()
    total_profit = total_revenue - total_cost
    total_reorder_spend = sum(p["Total Cost"] for p in purchase_log)

    print("\nTotal Revenue (sales)        :", round(total_revenue, 2))
    print("Cost of Goods Sold           :", round(total_cost, 2))
    print("Gross Profit / Loss          :", round(total_profit, 2))
    if total_revenue > 0:
        print("Profit Margin                :", round(total_profit / total_revenue * 100, 2), "%")
    print("Money spent on reordering    :", round(total_reorder_spend, 2))

    if total_profit > 0:
        print("\nOVERALL RESULT: PROFIT of", round(total_profit, 2))
    elif total_profit < 0:
        print("\nOVERALL RESULT: LOSS of", round(abs(total_profit), 2))
    else:
        print("\nOVERALL RESULT: BREAK-EVEN")

    best = summary["Profit"].idxmax()
    worst = summary["Profit"].idxmin()
    print("Most profitable item         :", best, "(", round(summary.at[best, "Profit"], 2), ")")
    print("Least profitable item        :", worst, "(", round(summary.at[worst, "Profit"], 2), ")")


# ---------------------------------------------------------------
# MAIN MENU
# ---------------------------------------------------------------
def main():
    print("=" * 50)
    print("        INVENTORY MANAGEMENT SYSTEM")
    print("=" * 50)

    while True:
        print("\n1. Add / enter stock")
        print("2. View stock")
        print("3. Make a sale (generate bill)")
        print("4. Reorder stock")
        print("5. Save CSV reports")
        print("6. Show charts")
        print("7. Profit & loss analysis")
        print("8. Exit")

        choice = input("Choose an option (1-8): ").strip()

        if choice == "1":
            add_stock()
        elif choice == "2":
            view_stock()
        elif choice == "3":
            make_sale()
        elif choice == "4":
            reorder_stock()
        elif choice == "5":
            save_csv_reports()
        elif choice == "6":
            show_charts()
        elif choice == "7":
            profit_loss_analysis()
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 8.")


main()
