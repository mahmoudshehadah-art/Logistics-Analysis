import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
from datetime import timedelta
import os
import threading

# --- إعدادات مظهر التطبيق ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PrepTimeOptimizer(ctk.CTk):
    def __init__(self):
        super().__init__()

        # إعدادات النافذة الرئيسية
        self.title("⏱️ Restaurant Prep Time Optimizer")
        self.geometry("750x850") # زيادة الارتفاع قليلاً لاستيعاب التوقيع
        self.resizable(False, False)

        self.df = None
        self.df_last_30 = None
        self.date_col = 'CreatedAtDate'
        self.time_col = 'CreatedAtTime'
        self.city_col = 'CityName'

        # --- عناصر الواجهة الرسومية (UI) ---
        self.header_label = ctk.CTkLabel(self, text="Restaurant Prep Time Optimizer", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.pack(pady=(20, 5))

        self.sub_label = ctk.CTkLabel(self, text="Upload data to analyze and reduce driver wait times.", font=ctk.CTkFont(size=14), text_color="gray")
        self.sub_label.pack(pady=(0, 15))

        self.upload_btn = ctk.CTkButton(self, text="📁 Upload Excel File", command=self.load_file, font=ctk.CTkFont(size=15), height=40)
        self.upload_btn.pack(pady=10)

        self.file_status_label = ctk.CTkLabel(self, text="No file selected", text_color="gray")
        self.file_status_label.pack(pady=(0, 10))

        self.city_label = ctk.CTkLabel(self, text="📌 Select City:", font=ctk.CTkFont(size=14, weight="bold"))
        self.city_label.pack(pady=(5, 5))
        
        self.city_dropdown = ctk.CTkOptionMenu(self, values=["Select a file first..."], state="disabled", width=200)
        self.city_dropdown.pack(pady=5)

        # 1. مربع إدخال الوزن (المتوسط المرجح)
        self.weight_label = ctk.CTkLabel(self, text="⚖️ Weight of Actual Time (0-100%):", font=ctk.CTkFont(size=14, weight="bold"))
        self.weight_label.pack(pady=(10, 5))

        self.weight_entry = ctk.CTkEntry(self, width=200, placeholder_text="e.g., 50")
        self.weight_entry.pack(pady=5)
        self.weight_entry.insert(0, "50")
        
        # 2. مربع إدخال هامش الأمان
        self.buffer_label = ctk.CTkLabel(self, text="🛡️ Safety Buffer (%):", font=ctk.CTkFont(size=14, weight="bold"))
        self.buffer_label.pack(pady=(10, 5))

        self.buffer_entry = ctk.CTkEntry(self, width=200, placeholder_text="e.g., 10")
        self.buffer_entry.pack(pady=5)
        self.buffer_entry.insert(0, "10")

        self.analyze_btn = ctk.CTkButton(self, text="🚀 Analyze & Export Optimization Report", 
                                         command=self.start_analysis_thread, 
                                         font=ctk.CTkFont(size=15, weight="bold"), 
                                         height=45, 
                                         fg_color="#28a745", 
                                         hover_color="#218838",
                                         state="disabled")
        self.analyze_btn.pack(pady=20)
        
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)
        self.progress_bar.pack_forget() 

        self.console = ctk.CTkTextbox(self, width=650, height=160, font=ctk.CTkFont(size=13))
        self.console.pack(pady=10)
        self.console.insert("0.0", "Welcome! Please upload an Excel file to begin.\n")
        self.console.configure(state="disabled")

        # --- توقيع المبرمج ---
        self.signature_label = ctk.CTkLabel(self, text="By Mahmoud Shehadah", font=ctk.CTkFont(size=12, slant="italic"), text_color="#555555")
        self.signature_label.pack(side="bottom", pady=10)

    def log_message(self, message):
        self.console.configure(state="normal")
        self.console.insert("end", message + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if filepath:
            threading.Thread(target=self._load_file_task, args=(filepath,), daemon=True).start()

    def _load_file_task(self, filepath):
        self.upload_btn.configure(state="disabled")
        self.progress_bar.pack(pady=10)
        self.progress_bar.start()
        self.file_status_label.configure(text="Loading large file, please wait...", text_color="#ffc107")
        self.log_message("\n⏳ Reading Excel file... (Vectorized processing)")

        try:
            self.df = pd.read_excel(filepath)
            filename = os.path.basename(filepath)
            
            if self.date_col in self.df.columns and self.city_col in self.df.columns:
                
                # Vectorized Datetime parsing
                if self.time_col in self.df.columns:
                    combined_datetime = self.df[self.date_col].astype(str) + " " + self.df[self.time_col].astype(str)
                    self.df['FullDateTime'] = pd.to_datetime(combined_datetime, errors='coerce')
                else:
                    self.df['FullDateTime'] = pd.to_datetime(self.df[self.date_col], errors='coerce')
                
                valid_dates_df = self.df.dropna(subset=['FullDateTime'])
                
                if valid_dates_df.empty:
                    self.after(0, lambda: messagebox.showerror("Error", "Could not parse dates properly."))
                    return

                # Vectorized Time filtering
                latest_date = valid_dates_df['FullDateTime'].max()
                thirty_days_ago = latest_date - timedelta(days=30)
                self.df_last_30 = valid_dates_df[valid_dates_df['FullDateTime'] >= thirty_days_ago].copy()
                
                self.after(0, self._update_ui_after_load, filename)

            else:
                self.after(0, lambda: messagebox.showerror("Error", f"Columns '{self.date_col}' or '{self.city_col}' not found."))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to load file: {e}"))
        finally:
            self.after(0, self._stop_progress_bar_upload)

    def _update_ui_after_load(self, filename):
        cities = self.df_last_30[self.city_col].dropna().unique().tolist()
        if not cities:
            messagebox.showwarning("Warning", "No data found within the last 30 days.")
            return
            
        self.city_dropdown.configure(state="normal", values=cities)
        self.city_dropdown.set(cities[0]) 
        self.analyze_btn.configure(state="normal")
        self.file_status_label.configure(text=f"Loaded: {filename}", text_color="#28a745")
        self.log_message(f"✅ Data loaded successfully. {len(self.df_last_30)} records found.")

    def _stop_progress_bar_upload(self):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.upload_btn.configure(state="normal")

    def start_analysis_thread(self):
        selected_city = self.city_dropdown.get()
        if not selected_city or self.df_last_30 is None:
            return
            
        try:
            weight_pct = float(self.weight_entry.get().strip())
            if weight_pct < 0 or weight_pct > 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid percentage for Weight (0-100).")
            return
            
        try:
            buffer_pct = float(self.buffer_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for Safety Buffer.")
            return

        alpha = weight_pct / 100.0
        safety_multiplier = 1 + (buffer_pct / 100.0)

        self.analyze_btn.configure(state="disabled")
        self.progress_bar.pack(pady=10)
        self.progress_bar.start()
        self.log_message(f"\n⚙️ Analyzing data for {selected_city} (Weight: {weight_pct}%, Buffer: {buffer_pct}%)...")
        
        threading.Thread(target=self._process_and_export_task, args=(selected_city, alpha, safety_multiplier), daemon=True).start()

    def _process_and_export_task(self, selected_city, alpha, safety_multiplier):
        try:
            df_city = self.df_last_30[self.df_last_30[self.city_col] == selected_city].copy()
            
            if df_city.empty:
                self.after(0, lambda: messagebox.showwarning("Warning", "No data found for the selected city."))
                return

            # Vectorized Data Cleaning (No For Loops)
            cols_to_convert = ['SystemPrepTime', 'ActualPrepTime', 'AtVendorTime (min)']
            existing_cols = [c for c in cols_to_convert if c in df_city.columns]
            df_city[existing_cols] = df_city[existing_cols].apply(pd.to_numeric, errors='coerce')

            # Vectorized Grouping & Aggregation
            summary = df_city.groupby(['VendorId', 'VendorName']).agg(
                Total_Orders=('OrderCode', 'count'),
                Current_Avg_SystemPrep=('SystemPrepTime', 'mean'),
                Avg_ActualPrepTime=('ActualPrepTime', 'mean'),
                Avg_DriverWaitTime=('AtVendorTime (min)', 'mean')
            ).reset_index()

            # Vectorized Math Calculations
            smoothed_time = (summary['Avg_ActualPrepTime'] * alpha) + (summary['Current_Avg_SystemPrep'] * (1 - alpha))
            summary['Suggested_SystemPrepTime'] = (smoothed_time * safety_multiplier).round(0)
            summary['Adjustment_Needed (min)'] = summary['Suggested_SystemPrepTime'] - summary['Current_Avg_SystemPrep']
            
            summary = summary.round(1).sort_values(by='Avg_DriverWaitTime', ascending=False)

            self.after(0, self._ask_save_path, summary, selected_city)
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"An error occurred during analysis: {e}"))
        finally:
             self.after(0, self._stop_progress_bar_after_analysis)

    def _ask_save_path(self, summary, selected_city):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=f"{selected_city}_Optimization_Report.xlsx",
            title="Save Optimization Report As",
            filetypes=[("Excel files", "*.xlsx")]
        )

        if save_path:
            try:
                summary.to_excel(save_path, index=False)
                self.log_message(f"🎉 Success! Report saved to:\n{save_path}")
                
                self.log_message("\n⚠️ Top 3 Vendors Requiring Prep-Time Adjustment:")
                
                # Vectorized String Formatting (No For Loops)
                top_3 = summary.head(3)
                if not top_3.empty:
                    messages = "- " + top_3['VendorName'].astype(str) + ": Avg Wait = " + top_3['Avg_DriverWaitTime'].astype(str) + "m | Needs " + top_3['Adjustment_Needed (min)'].apply(lambda x: f"{x:+g}") + "m adjustment."
                    self.log_message(messages.str.cat(sep='\n'))
                    
                messagebox.showinfo("Success", "Optimization Report Exported Successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def _stop_progress_bar_after_analysis(self):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.analyze_btn.configure(state="normal")

if __name__ == "__main__":
    app = PrepTimeOptimizer()
    app.mainloop()