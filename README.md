# 📦 Logistics & Delivery Optimization Suite

## 🚀 Overview
This repository contains a portfolio of high-performance desktop applications built to solve complex operational challenges in the food delivery and logistics sector. Developed entirely in Python, these tools replace manual analysis with automated, data-driven decision engines to improve delivery SLAs, optimize courier efficiency, and reduce operational bottlenecks.

All tools are built with a focus on speed, utilizing vectorized data processing to handle hundreds of thousands of records in milliseconds without freezing the user interface.

## 🛠️ Core Technologies
* **Data Processing Engine:** `Pandas` and `Numpy` for high-speed, vectorized manipulation of massive datasets.
* **User Interface:** `CustomTkinter` for modern, responsive, dark-mode compatible dashboards.
* **Visualizations:** `Matplotlib` for generating integrated scatter plots and performance charts.
* **Packaging:** `PyInstaller` for compiling standalone Windows executables.

---

## 📂 The Applications

### 1. Annual Logistics Performance Analyzer
Evaluates year-over-year operational metrics, order volumes, and driver earnings. Features automated multi-sheet Excel exporting and generates 5 distinct comparative charts to identify operational bottlenecks and fleet efficiency.

### 2. Logistics Data Cleaner & Processor
A fast utility that standardizes delivery distances, extracts time buckets, and drops unnecessary columns. Prepares raw operational data for downstream analysis with lightning-fast execution.

### 3. Field Delivery Optimization System
Utilizes Linear Regression modeling to mathematically balance on-time delivery SLAs with delivery radius expansion. Calculates the *Fixed Overhead Time* and *Per-Kilometer Travel Time* to output automated, actionable operational decisions (e.g., "Expand Range", "Contract Range").

### 4. Retrospective Incentive Impact Analyzer
Measures the true operational ROI of financial campaigns on driver turnout and productivity. Compares campaign performance against a dynamic 30-day baseline to isolate the geographic and temporal impact of driver incentives.

### 5. Order Lifecycle & Bottleneck Analyzer
Pinpoints the exact root cause of delayed orders by calculating dynamic SLAs based on distance and standard prep times. Evaluates vendor and driver performance fairly by isolating delay responsibilities.

### 6. Restaurant Prep Time Optimizer
Analyzes historical wait times to automatically adjust system prep times. Eliminates driver dead time at vendors by suggesting optimized times using weighted averages and safety buffers.

### 7. Smart Courier Shift Planner
Allocates driver shifts and determines city-specific ratios based on historical order volume patterns. Features day-pattern filtering to accurately predict and assign headcounts for peak and off-peak hours.

---

## 📋 Prerequisites & Installation

To run these applications from the source code, ensure you have Python 3.8+ installed, then install the required dependencies:

```bash
pip install pandas numpy customtkinter matplotlib openpyxl xlsxwriter arabic-reshaper python-bidi
