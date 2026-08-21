# 📊 Logistics Data Cleaner & Processor

## 📝 Description
A fast and modern desktop application built with Python to clean, process, and organize logistics and delivery data. It features a sleek user interface using `CustomTkinter` and utilizes `Pandas` for high-speed data manipulation (Vectorization).

## ✨ Features
- **Modern UI:** Clean, responsive interface that automatically adapts to the system's Dark/Light mode.
- **High-Speed Processing:** Uses `pd.cut` for lightning-fast time bucketing, capable of processing large datasets in milliseconds.
- **Time Extraction & Bucketing:** Automatically extracts the hour from `CreatedAtTime` and groups orders into specific time periods (e.g., *12 AM - 3 AM*, *4 AM - 7 AM*, etc.).
- **Distance Rounding:** Automatically rounds the `DeliveryDistance` values to the nearest integer.
- **Smart Filtering:** Drops unnecessary data and keeps only the essential 30 columns needed for operational analysis.
- **Export Options:** Seamlessly save the cleaned dataset as `.xlsx` or `.csv`.

## 🛠️ Prerequisites
If you are running the script directly from the source code, ensure you have Python installed along with the following libraries:

```bash
pip install pandas openpyxl customtkinter