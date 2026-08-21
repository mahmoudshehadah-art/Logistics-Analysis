# Comprehensive Field Delivery Optimization System

## 1. Overview
The **Comprehensive Field Delivery Optimization System** is a sophisticated, data-driven desktop application designed for logistics and delivery operations managers. Built with Python and a modern GUI framework (`customtkinter`), it analyzes historical delivery data to determine the optimal delivery radius (distance) for any given city, area, and specific time of day.

The core purpose of the system is to balance operational efficiency (On-Time Delivery SLA) with business expansion (maximizing delivery range) by mathematically modeling courier behavior using **Linear Regression**.

## 2. Key Features
* **Modern Desktop Interface:** Sleek, responsive, dark/light mode compatible UI built with `CustomTkinter`.
* **Dynamic Time Filtering (30-Day Rolling):** Automatically filters out stale data, ensuring analysis is strictly based on the last 30 days of actual performance.
* **Granular Sub-Filtering:** Analyze operations by:
  * **City:** Dynamically populates based on available data.
  * **Hour of Day:** Crucial for separating rush hour traffic from off-peak times.
  * **Day Clusters:** Analyze 'All Days', 'Weekends (Fri+Sat)', 'Thursdays', or 'Weekdays (Sun-Wed)'.
* **High-Performance Vectorization:** Uses pure `numpy` arrays and `pandas` groupby operations, bypassing slow Python loops to handle hundreds of thousands of orders in milliseconds.
* **Mathematical Modeling (Linear Regression):** Calculates the *Fixed Overhead Time* and the *Per-Kilometer Travel Time* for every single area independently.
* **Automated Decision Engine:** Outputs actionable operational decisions (e.g., "Expand Range", "Contract Range", "Field Difficulties").
* **Deep Dive Visualization:** Generates a Matplotlib scatter plot with the regression line, SLA thresholds, and a floating statistical summary box directly on the UI.
* **Smart Insights Box:** Provides a plain-text, logical explanation of *why* the mathematical engine made a specific decision.
* **Excel Export:** Exports a clean, standardized action plan ready for the dispatch or operations team.

---

## 3. How the Mathematical Engine Works

The system represents every delivery trip using the linear equation:
`y = (m * x) + c`

* **`y` (Shipping Time):** Total time taken to deliver the order.
* **`x` (Delivery Distance):** The distance from the vendor to the customer.
* **`m` (Slope - Variable Time):** The additional minutes required to drive 1 kilometer in this specific area at this specific hour.
* **`c` (Y-intercept - Fixed Overhead Time):** The time lost regardless of distance (e.g., waiting at the restaurant, parking, walking up to the customer's apartment).

### The Decision Matrix
Based on the regression results, the system calculates an *Adjusted Target Distance* and assigns one of five decisions:

1. **🟢 Expand Range:** 
   * **Condition:** On-Time rate $\ge 90\%$ AND Average time $< 20$ mins AND calculated safe distance is $> 0.25$ km larger than current.
   * **Meaning:** Couriers are extremely fast here. You can safely increase the delivery radius to capture more orders without breaching the 25-minute SLA.
2. **✔️ Optimal / Appropriate Range:** 
   * **Condition:** Performance is stable (85%-90%), or performance is excellent but the regression slope warns that further expansion will breach the SLA.
   * **Meaning:** Keep the delivery radius exactly as it is.
3. **🔻 Contract Range:** 
   * **Condition:** On-Time rate $< 85\%$ AND calculated safe distance is $> 0.25$ km smaller than current.
   * **Meaning:** Couriers are taking too long. The radius must be reduced to the calculated safe distance to restore SLA compliance.
4. **⚠️ Monitor Performance:** 
   * **Condition:** On-Time rate $< 85\%$ BUT the calculated safe distance is almost identical to the current distance.
   * **Meaning:** The distance is mathematically correct, but performance is dropping. The issue is likely a shortage of available couriers, not the distance itself.
5. **🔴 Field Difficulties (Critical Warning):**
   * **Condition:** On-Time rate $< 85\%$ AND the Fixed Overhead (`c`) is $\ge 25$ minutes.
   * **Meaning:** Couriers are wasting 25+ minutes just waiting at the restaurant or trying to park, even if the distance is 0 km. Contracting the radius will not solve this. The system forcefully drops the radius to 1.0 km as an emergency measure and flags the area for physical operations intervention (e.g., restaurant delay management).

---

## 4. Required Data Format
For the system to function, the uploaded `.csv` or `.xlsx` file must contain the following columns (names must match exactly):

| Column Name | Description |
| :--- | :--- |
| `CreatedAtDate` | The date the order was created (used for the 30-day filter). |
| `CreatedHour` | The numeric hour the order was created (0-23). |
| `CityName` | The city where the order took place. |
| `Area` | The specific neighborhood or zone within the city. |
| `Courier` | Delivery type (Must contain the word 'Delivery'). |
| `OrderStatus` | Status of the order (Must be 'completed', or cancelled with pay). |
| `DeliveryDistance` | The actual distance traveled in kilometers (numeric). |
| `ShippingTime (min)`| The total time taken to deliver in minutes (numeric). |

---

## 5. Deployment & Execution
To run the application or compile it into a standalone Windows executable (`.exe`):

### Prerequisites
Ensure Python is installed, then install the required libraries:
```bash
pip install customtkinter pandas numpy matplotlib openpyxl pyinstaller
```

### Running from Source
Execute the script directly via Python:
```bash
python app_en.py
```

### Compiling to `.exe`
To package the app into a single, distributable `.exe` file without the background console window:
```bash
python -m PyInstaller --onefile --noconsole app_en.py
```
*The compiled executable will be located in the `dist/` folder.*

---
*Developed by Mahmoud Shehadah*
