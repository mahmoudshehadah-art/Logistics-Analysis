import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
from datetime import timedelta

# إعداد المظهر العام للتطبيق
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ShiftPlannerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Smart Courier Shift Planner - Optimized")
        self.geometry("600x750")
        self.df = None

        # خطوط التنسيق
        self.font_title = ctk.CTkFont(family="Arial", size=14, weight="bold")
        self.font_normal = ctk.CTkFont(family="Arial", size=13)
        self.font_signature = ctk.CTkFont(family="Arial", size=11, slant="italic")

        # --- Main Container ---
        self.main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 1. Load File Section
        self.btn_load = ctk.CTkButton(self.main_frame, text="Upload Orders Data (Excel)", 
                                      font=self.font_title, fg_color="#28a745", hover_color="#218838",
                                      command=self.load_file)
        self.btn_load.pack(fill="x", pady=(0, 5))

        self.lbl_file_status = ctk.CTkLabel(self.main_frame, text="No file uploaded yet", text_color="#dc3545", font=self.font_normal)
        self.lbl_file_status.pack(pady=(0, 20))

        # 2. Days Pattern Selection
        ctk.CTkLabel(self.main_frame, text="Select Days Pattern (From Last 30 Days):", font=self.font_title).pack(anchor="w", pady=(0, 10))
        
        self.day_group_var = ctk.StringVar(value="all")
        self.days_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.days_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkRadioButton(self.days_frame, text="All Days", variable=self.day_group_var, value="all", font=self.font_normal).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkRadioButton(self.days_frame, text="Thursday", variable=self.day_group_var, value="thu", font=self.font_normal).grid(row=0, column=1, padx=10, pady=10, sticky="w")
        ctk.CTkRadioButton(self.days_frame, text="Sunday", variable=self.day_group_var, value="sun", font=self.font_normal).grid(row=0, column=2, padx=10, pady=10, sticky="w")
        ctk.CTkRadioButton(self.days_frame, text="Fri + Sat", variable=self.day_group_var, value="fri_sat", font=self.font_normal).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkRadioButton(self.days_frame, text="Mon + Tue + Wed", variable=self.day_group_var, value="mon_tue_wed", font=self.font_normal).grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="w")

        # 3. City Selection
        ctk.CTkLabel(self.main_frame, text="Select City:", font=self.font_title).pack(anchor="w")
        self.city_combo = ctk.CTkComboBox(self.main_frame, values=[], font=self.font_normal, state="readonly")
        self.city_combo.pack(fill="x", pady=(5, 20))

        # 4. Total Expected Orders
        ctk.CTkLabel(self.main_frame, text="Expected Total Orders for the Entire Country:", font=self.font_title).pack(anchor="w")
        self.orders_entry = ctk.CTkEntry(self.main_frame, font=self.font_normal, justify="center", placeholder_text="e.g., 5000")
        self.orders_entry.pack(fill="x", pady=(5, 20))

        # 5. UTR
        ctk.CTkLabel(self.main_frame, text="UTR (Orders per Courier per Hour):", font=self.font_title).pack(anchor="w")
        self.utr_entry = ctk.CTkEntry(self.main_frame, font=self.font_normal, justify="center", placeholder_text="e.g., 2.5")
        self.utr_entry.pack(fill="x", pady=(5, 20))

        # 6. Buffer Percentage
        ctk.CTkLabel(self.main_frame, text="Buffer Percentage (%):", font=self.font_title).pack(anchor="w")
        self.buffer_entry = ctk.CTkEntry(self.main_frame, font=self.font_normal, justify="center")
        self.buffer_entry.insert(0, "0")
        self.buffer_entry.pack(fill="x", pady=(5, 30))

        # 7. Generate Button
        self.btn_generate = ctk.CTkButton(self.main_frame, text="Calculate Shifts & Export Excel", 
                                          font=self.font_title, height=45,
                                          command=self.generate_shifts)
        self.btn_generate.pack(fill="x", pady=(0, 20))

        # 8. Signature
        self.lbl_signature = ctk.CTkLabel(self, text="Mahmoud shehadah", font=self.font_signature, text_color="gray")
        self.lbl_signature.pack(side="bottom", pady=10)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not file_path:
            return

        required_cols = ['OrderCode', 'CityName', 'CreatedHour', 'CreatedAtDate']

        try:
            # قراءة صف العناوين فقط للتحقق من وجود الأعمدة (Memory Optimization)
            header_df = pd.read_excel(file_path, nrows=0)
            missing_cols = [col for col in required_cols if col not in header_df.columns]
            
            if missing_cols:
                messagebox.showerror("Data Error", f"The file is missing the following columns:\n{', '.join(missing_cols)}")
                return

            # قراءة الأعمدة المطلوبة فقط لتقليل الضغط على الذاكرة
            self.df = pd.read_excel(file_path, usecols=required_cols)
            
            # تحويل عمود التاريخ فور التحميل (متوافق مع أحدث إصدارات Pandas)
            self.df['CreatedAtDate'] = pd.to_datetime(self.df['CreatedAtDate'], errors='coerce')
            
            # إزالة أي أسطر تحتوي على تواريخ غير صالحة إن وجدت
            self.df.dropna(subset=['CreatedAtDate'], inplace=True)

            cities = self.df['CityName'].dropna().unique().tolist()
            if cities:
                self.city_combo.configure(values=cities)
                self.city_combo.set(cities[0])

            self.lbl_file_status.configure(text=f"File uploaded successfully! ({len(self.df)} Total Orders)", text_color="#28a745")
            messagebox.showinfo("Success", "Data loaded and optimized successfully. You can now set your parameters.")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while reading the file:\n{str(e)}")

    def generate_shifts(self):
        if self.df is None:
            messagebox.showwarning("Warning", "Please upload the data file first.")
            return

        city = self.city_combo.get()
        day_group = self.day_group_var.get()
        
        try:
            expected_orders_country = float(self.orders_entry.get())
            utr = float(self.utr_entry.get())
            buffer_pct = float(self.buffer_entry.get())
            
            if expected_orders_country <= 0 or utr <= 0 or buffer_pct < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid positive numbers in all fields.")
            return

        try:
            max_date = self.df['CreatedAtDate'].max()
            thirty_days_ago = max_date - timedelta(days=30)
            
            recent_df_country = self.df[self.df['CreatedAtDate'] >= thirty_days_ago].copy()

            # Vectorized Filtering 
            if day_group == "thu":
                recent_df_country = recent_df_country[recent_df_country['CreatedAtDate'].dt.dayofweek == 3]
            elif day_group == "sun":
                recent_df_country = recent_df_country[recent_df_country['CreatedAtDate'].dt.dayofweek == 6]
            elif day_group == "fri_sat":
                recent_df_country = recent_df_country[recent_df_country['CreatedAtDate'].dt.dayofweek.isin([4, 5])]
            elif day_group == "mon_tue_wed":
                recent_df_country = recent_df_country[recent_df_country['CreatedAtDate'].dt.dayofweek.isin([0, 1, 2])]

            total_orders_country_filtered = len(recent_df_country)

            if total_orders_country_filtered == 0:
                messagebox.showwarning("Warning", "No data available for the selected days in the last 30 days.")
                return

            recent_df_city = recent_df_country[recent_df_country['CityName'] == city].copy()
            total_orders_city_filtered = len(recent_df_city)

            if total_orders_city_filtered == 0:
                messagebox.showwarning("Warning", f"No data available for {city} in the selected days.")
                return

            city_ratio = total_orders_city_filtered / total_orders_country_filtered
            expected_orders_city = expected_orders_country * city_ratio

            hourly_stats = recent_df_city.groupby('CreatedHour')['OrderCode'].count().reset_index()
            hourly_stats.rename(columns={'OrderCode': 'HistoricalCount'}, inplace=True)
            
            # Vectorized Math Operations
            hourly_stats['HourRatio'] = hourly_stats['HistoricalCount'] / total_orders_city_filtered
            hourly_stats['ExpectedOrders'] = hourly_stats['HourRatio'] * expected_orders_city
            hourly_stats['CouriersNeeded'] = hourly_stats['ExpectedOrders'] / utr
            hourly_stats['BaseShifts'] = hourly_stats['CouriersNeeded'] / 4
            hourly_stats['ShiftsWithBuffer'] = hourly_stats['BaseShifts'] * (1 + (buffer_pct / 100))
            
            # Numpy Vectorized Ceil
            hourly_stats['FinalShifts'] = np.ceil(hourly_stats['ShiftsWithBuffer']).astype(int)

            output_df = pd.DataFrame({
                'Hour': hourly_stats['CreatedHour'],
                'Hour Ratio (City)': hourly_stats['HourRatio'].apply(lambda x: f"{x:.2%}"),
                'Expected Orders': hourly_stats['ExpectedOrders'].round(1),
                'Required Shifts (Final)': hourly_stats['FinalShifts']
            })

            group_names = {
                "all": "All_Days",
                "thu": "Thursday",
                "sun": "Sunday",
                "fri_sat": "Fri_Sat",
                "mon_tue_wed": "Mon_Tue_Wed"
            }
            file_suffix = group_names.get(day_group, "")

            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Save Shift Plan",
                initialfile=f"Shift_Plan_{city}_{file_suffix}.xlsx"
            )

            if save_path:
                output_df.to_excel(save_path, index=False)
                
                success_msg = (
                    f"File successfully generated!\n\n"
                    f"Calculation Details:\n"
                    f"- Days Pattern: {file_suffix.replace('_', ' ')}\n"
                    f"- {city} Share from Country: {city_ratio:.2%}\n"
                    f"- Expected Orders for {city}: {expected_orders_city:.0f} orders"
                )
                messagebox.showinfo("Success", success_msg)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while processing data:\n{str(e)}")

if __name__ == "__main__":
    app = ShiftPlannerApp()
    app.mainloop()