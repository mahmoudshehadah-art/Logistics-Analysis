# Annual Logistics Performance Analyzer 📊

A robust, fast, and vectorized desktop application designed to analyze year-over-year logistics, delivery performance, and driver earnings. Built with Python, this tool processes multiple Excel datasets efficiently and provides visual insights into operational bottlenecks and fleet efficiency.

**Developed by:** Mahmoud Shehadah

---

## 🚀 Key Features

* **Multi-File Processing:** Upload and concatenate multiple Excel files seamlessly.
* **High-Speed Execution:** Utilizes Pandas vectorization and the `calamine` engine for lightning-fast data reading and processing.
* **Non-Blocking UI:** Heavy data processing runs on background threads to prevent UI freezing.
* **Modern Interface:** Built with `CustomTkinter` for a sleek, responsive dark-mode dashboard.
* **Automated Visualizations:** Generates 5 distinct year-over-year comparative charts:
  1. Monthly Order Volume.
  2. Average Order Cycle Times (Approve, Assign, Arrive, Prep, Shipping).
  3. Active Drivers per Month.
  4. Average Driver Monthly Earnings.
  5. Average Driver Daily Earnings.
* **Excel Export:** One-click export of all calculated metrics into a multi-sheet structured Excel report.

---

## 📋 Prerequisites

Ensure you have Python 3.8 or higher installed. Install the required dependencies using pip:

```bash
pip install customtkinter pandas matplotlib numpy openpyxl