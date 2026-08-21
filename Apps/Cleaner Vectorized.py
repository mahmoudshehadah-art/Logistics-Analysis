import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import pandas as pd

# إعداد مظهر واجهة CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def process_data(file_path, output_path, status_label, progress_bar, root):
    try:
        # 1. قراءة الملف
        status_label.configure(text="Reading file...")
        progress_bar.set(0.2)
        root.update_idletasks()

        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        progress_bar.set(0.4)
        status_label.configure(text="Processing hours and rounding distances...")
        root.update_idletasks()

        # 2. استخراج خانة الساعات
        if "CreatedAtTime" in df.columns:
            time_series = pd.to_datetime(df["CreatedAtTime"].astype(str), errors="coerce")
            df["CreatedHour"] = time_series.dt.hour
        else:
            df["CreatedHour"] = None

        # 3. تصنيف الساعات بسرعة فائقة باستخدام pd.cut (Vectorization)
        if "CreatedHour" in df.columns:
            bins = [-1, 3, 7, 11, 15, 19, 23]
            labels = [
                "12 AM - 3 AM",
                "4 AM - 7 AM",
                "8 AM - 11 AM",
                "12 PM - 3 PM",
                "4 PM - 7 PM",
                "8 PM - 11 PM"
            ]
            df["TimeBucket"] = pd.cut(df["CreatedHour"], bins=bins, labels=labels)
        else:
            df["TimeBucket"] = None

        # 4. تقريب قيم عمود DeliveryDistance
        if "DeliveryDistance" in df.columns:
            df["DeliveryDistance_Rounded"] = pd.to_numeric(df["DeliveryDistance"], errors="coerce").round()
        else:
            df["DeliveryDistance_Rounded"] = None

        # 5. قائمة الأعمدة المطلوبة
        target_columns = [
            "OrderCode", "OrderStatus", "TotalShipping", "CallingDistance",
            "DeliveryDistance", "DeliveryDistance_Rounded",
            "TimeToApprove (min)", "TimeToAssign (min)", "TimeToArrive (min)",
            "AtVendorTime (min)", "ShippingTime (min)", "DeliveryTimeInMinutes",
            "CreatedAtDate", "CreatedAtTime", "CreatedHour", "TimeBucket",
            "CompletedAt", "VendorId", "VendorName", "SystemPrepTime",
            "ActualPrepTime", "Area", "CityName", "DriverId", "DriverName",
            "DrivingCompanyName", "AssignedBy", "Courier", "Domain", "Month",
        ]

        # فلترة الأعمدة المتوفرة فقط
        available_columns = [col for col in target_columns if col in df.columns]
        df_cleaned = df[available_columns]

        progress_bar.set(0.8)
        status_label.configure(text="Saving cleaned file...")
        root.update_idletasks()

        # 6. حفظ الملف الجديد
        if output_path.endswith(".csv"):
            df_cleaned.to_csv(output_path, index=False)
        else:
            df_cleaned.to_excel(output_path, index=False)

        progress_bar.set(1.0)
        status_label.configure(text="Processing completed successfully! ✅")
        messagebox.showinfo("Success", f"Data cleaned and saved successfully at:\n{output_path}")

    except Exception as e:
        status_label.configure(text="An error occurred ❌")
        messagebox.showerror("Error", f"Error processing file:\n{str(e)}")
    finally:
        progress_bar.set(0)

def start_processing():
    input_file = input_entry.get().strip()
    if not input_file:
        messagebox.showwarning("Warning", "Please select a data file first.")
        return

    default_out_name = f"Cleaned_{os.path.basename(input_file)}"
    default_dir = os.path.dirname(input_file)

    file_types = [("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")]
    if input_file.endswith(".csv"):
        file_types = [("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")]

    output_file = filedialog.asksaveasfilename(
        title="Save Cleaned File As",
        initialdir=default_dir,
        initialfile=default_out_name,
        filetypes=file_types,
        defaultextension=".xlsx" if not input_file.endswith(".csv") else ".csv",
    )

    if not output_file:
        return

    threading.Thread(
        target=process_data,
        args=(input_file, output_file, status_label, progress_bar, root),
        daemon=True,
    ).start()

def browse_file():
    file_path = filedialog.askopenfilename(
        title="Select Data File",
        filetypes=[
            ("Data Files", "*.xlsx *.xls *.csv"),
            ("Excel Files", "*.xlsx *.xls"),
            ("CSV Files", "*.csv"),
        ],
    )
    if file_path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, file_path)
        status_label.configure(text="File selected. Click 'Clean & Process'")

# ================== تصميم الواجهة العصرية ==================
root = ctk.CTk()
root.title("Logistics Data Cleaner")
root.geometry("640x390")
root.resizable(False, False)

# العنوان الرئيسي
title_label = ctk.CTkLabel(
    root,
    text="📊 Logistics Data Cleaner & Processor",
    font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
)
title_label.pack(pady=(25, 5))

desc_label = ctk.CTkLabel(
    root,
    text="Filter columns, extract hours, time buckets, and round delivery distances",
    font=ctk.CTkFont(family="Segoe UI", size=12),
    text_color="gray",
)
desc_label.pack(pady=(0, 20))

# إطار اختيار الملف
frame_file = ctk.CTkFrame(root, fg_color="transparent")
frame_file.pack(fill="x", padx=35, pady=5)

input_entry = ctk.CTkEntry(
    frame_file,
    placeholder_text="Select your data file (.xlsx, .csv)...",
    font=ctk.CTkFont(family="Segoe UI", size=12),
    height=38,
)
input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

browse_btn = ctk.CTkButton(
    frame_file,
    text="Browse...",
    command=browse_file,
    font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
    width=100,
    height=38,
)
browse_btn.pack(side="right")

# زر المعالجة الرئيسي
process_btn = ctk.CTkButton(
    root,
    text="⚡ Clean & Process File",
    command=start_processing,
    font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
    fg_color="#27ae60",
    hover_color="#219653",
    height=42,
)
process_btn.pack(fill="x", padx=35, pady=(20, 10))

# شريط التقدم
progress_bar = ctk.CTkProgressBar(root, orientation="horizontal", width=570)
progress_bar.pack(pady=(5, 5))
progress_bar.set(0)

# حالة التنفيذ
status_label = ctk.CTkLabel(
    root,
    text="Ready to select file",
    font=ctk.CTkFont(family="Segoe UI", size=11, slant="italic"),
    text_color="gray",
)
status_label.pack(pady=(0, 5))

# التوقيع
signature_label = ctk.CTkLabel(
    root,
    text="Mahmoud Shehadah",
    font=ctk.CTkFont(family="Segoe UI", size=10),
    text_color="gray",
)
signature_label.pack(side="bottom", pady=(0, 10))

if __name__ == "__main__":
    root.mainloop()