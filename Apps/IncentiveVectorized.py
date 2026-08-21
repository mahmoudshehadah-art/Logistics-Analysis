import customtkinter as ctk
import pandas as pd
import numpy as np
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Setup Modern Appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class IncentiveAnalyzer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Retrospective Incentive Impact Analyzer")
        self.geometry("1150x850") 
        
        self.orders_df = None
        self.incentives_df = None
        
        self.build_ui()
        
    def build_ui(self):
        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        self.lbl_title = ctk.CTkLabel(self.sidebar, text="Data Management", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_title.pack(pady=30)
        
        self.btn_load_orders = ctk.CTkButton(self.sidebar, text="Load Orders Data", command=self.load_orders, fg_color="#2b7b5c", hover_color="#1e5c44")
        self.btn_load_orders.pack(pady=15, padx=20)
        self.lbl_orders_status = ctk.CTkLabel(self.sidebar, text="Not Loaded", text_color="gray")
        self.lbl_orders_status.pack(pady=(0, 10))
        
        self.btn_load_inc = ctk.CTkButton(self.sidebar, text="Load Incentives Data", command=self.load_incentives, fg_color="#2b7b5c", hover_color="#1e5c44")
        self.btn_load_inc.pack(pady=15, padx=20)
        self.lbl_inc_status = ctk.CTkLabel(self.sidebar, text="Not Loaded", text_color="gray")
        self.lbl_inc_status.pack(pady=(0, 10))
        
        # --- Signature ---
        self.lbl_signature = ctk.CTkLabel(self.sidebar, text="By Mahmoud Shehadah", font=ctk.CTkFont(size=12, slant="italic"), text_color="#7f8c8d")
        self.lbl_signature.pack(side="bottom", pady=20)

        # --- Main Frame ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        self.lbl_main = ctk.CTkLabel(self.main_frame, text="Incentive Operational Impact Dashboard", font=ctk.CTkFont(size=22, weight="bold"))
        self.lbl_main.pack(pady=10)
        
        # --- Controls Panel ---
        self.controls_frame = ctk.CTkFrame(self.main_frame)
        self.controls_frame.pack(fill="x", padx=10, pady=10)
        
        # City Filter
        self.lbl_city = ctk.CTkLabel(self.controls_frame, text="City:", font=ctk.CTkFont(weight="bold"))
        self.lbl_city.grid(row=0, column=0, padx=10, pady=15, sticky="w")
        
        self.combo_city = ctk.CTkComboBox(self.controls_frame, values=["Please Load Data First"])
        self.combo_city.grid(row=0, column=1, padx=10, pady=15, sticky="we")
        
        # Date Filter
        self.lbl_date = ctk.CTkLabel(self.controls_frame, text="Incentive Date (YYYY-MM-DD):", font=ctk.CTkFont(weight="bold"))
        self.lbl_date.grid(row=0, column=2, padx=10, pady=15, sticky="e")
        
        self.entry_date = ctk.CTkEntry(self.controls_frame, placeholder_text="e.g., 2026-08-18", justify="center", width=130)
        self.entry_date.grid(row=0, column=3, padx=10, pady=15, sticky="we")
        
        # Run Button
        self.btn_analyze = ctk.CTkButton(self.controls_frame, text="Run Analysis", command=self.run_analysis)
        self.btn_analyze.grid(row=0, column=4, padx=10, pady=15)
        
        self.controls_frame.grid_columnconfigure((1, 3), weight=1)

        # --- Tabview for Results & Charts ---
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_report = self.tabview.add("Summary Report")
        self.tab_visuals = self.tabview.add("Visualizations")
        
        # Report Label
        self.lbl_res_text = ctk.CTkLabel(self.tab_report, text="Load files and enter date to begin...", justify="left", font=ctk.CTkFont(size=14))
        self.lbl_res_text.pack(pady=20, padx=20, anchor="w")
        
    def load_orders(self):
        file_path = filedialog.askopenfilename(title="Select Orders File", filetypes=[("Excel/CSV Files", "*.xlsx *.xls *.csv")])
        if file_path:
            try:
                self.orders_df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
                self.orders_df.columns = self.orders_df.columns.str.strip()
                
                if 'CityName' in self.orders_df.columns:
                    cities = ["All"] + sorted([str(x) for x in self.orders_df['CityName'].dropna().unique()])
                    self.combo_city.configure(values=cities)
                    self.combo_city.set("All")
                    
                self.lbl_orders_status.configure(text="Loaded Successfully", text_color="#2ecc71")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading Orders: {e}")

    def load_incentives(self):
        file_path = filedialog.askopenfilename(title="Select Incentives File", filetypes=[("Excel/CSV Files", "*.xlsx *.xls *.csv")])
        if file_path:
            try:
                self.incentives_df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
                self.incentives_df.columns = self.incentives_df.columns.str.strip()
                self.lbl_inc_status.configure(text="Loaded Successfully", text_color="#2ecc71")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading Incentives: {e}")

    def run_analysis(self):
        if self.orders_df is None or self.incentives_df is None:
            messagebox.showwarning("Missing Data", "Please load both Orders and Incentives files first.")
            return
            
        target_date_str = self.entry_date.get().strip()
        try:
            target_date_pd = pd.to_datetime(target_date_str)
            target_date = target_date_pd.date()
            day_name = target_date_pd.strftime('%A') 
            thirty_days_ago = (target_date_pd - pd.Timedelta(days=30)).date()
        except Exception:
            messagebox.showerror("Invalid Date", "Invalid date format. Use YYYY-MM-DD.")
            return

        try:
            # 1. Vectorized Incentive Calculation
            inc_col = [col for col in self.incentives_df.columns if 'Incentive Amount' in col or 'Incentive' in col]
            if inc_col:
                driver_col = [col for col in self.incentives_df.columns if 'Driver Id' in col or 'Driver' in col]
                if driver_col:
                    # Vectorized string mask
                    mask_valid = ~self.incentives_df[driver_col[0]].astype(str).str.contains('total|مجموع', case=False, na=False)
                    valid_incs = self.incentives_df.loc[mask_valid, inc_col[0]]
                    total_incentive_paid = pd.to_numeric(valid_incs, errors='coerce').fillna(0).sum()
                else:
                    total_incentive_paid = pd.to_numeric(self.incentives_df[inc_col[0]], errors='coerce').fillna(0).sum()
            else:
                total_incentive_paid = 0
            
            # 2. Fully Vectorized Orders Filtering
            df = self.orders_df.copy()
            df['CreatedAtDate'] = pd.to_datetime(df['CreatedAtDate']).dt.date
            
            selected_city = self.combo_city.get()
            if selected_city != "All" and selected_city != "Please Load Data First":
                if 'CityName' in df.columns:
                    df = df[df['CityName'].astype(str) == selected_city]
            
            valid_statuses = ['Completed', 'Cancelled With Pay To Driver', 'Cancelled With Pay To Driver And Vendor']
            
            # Boolean indexing for statuses
            status_mask = df['OrderStatus'].astype(str).str.strip().isin(valid_statuses)
            df = df[status_mask]
            
            # 3. Vectorized Date Splitting (Target vs Baseline)
            target_mask = df['CreatedAtDate'] == target_date
            
            target_weekday = target_date.weekday()
            # Vectorized multi-condition mask for baseline
            baseline_mask = (
                (df['CreatedAtDate'] < target_date) & 
                (df['CreatedAtDate'] >= thirty_days_ago) & 
                (pd.to_datetime(df['CreatedAtDate']).dt.weekday == target_weekday)
            )
            
            target_df = df[target_mask]
            baseline_df = df[baseline_mask]
            
            target_completed = len(target_df)
            if target_completed == 0:
                msg = f"No valid orders found on {target_date} ({day_name})"
                msg += f" in {selected_city}." if selected_city != "All" else "."
                self.lbl_res_text.configure(text=msg)
                return

            unique_past_dates = baseline_df['CreatedAtDate'].nunique()
            baseline_completed_avg = len(baseline_df) / unique_past_dates if unique_past_dates > 0 else 0

            # 4. Vectorized Driver Analysis using Numpy
            target_active_drivers = 0
            baseline_active_drivers_avg = 0
            drivers_only_today = 0
            drivers_absent_today = 0
            target_orders_per_driver = 0
            baseline_orders_per_driver = 0
            
            if 'DriverId' in df.columns:
                # Numpy unique arrays
                target_drivers = target_df['DriverId'].dropna().unique()
                baseline_drivers = baseline_df['DriverId'].dropna().unique()
                
                target_active_drivers = target_drivers.size
                
                if not baseline_df.empty:
                    baseline_active_drivers_avg = baseline_df.groupby('CreatedAtDate')['DriverId'].nunique().mean()
                
                # Numpy set operations for vectorization
                drivers_only_today = np.setdiff1d(target_drivers, baseline_drivers).size
                drivers_absent_today = np.setdiff1d(baseline_drivers, target_drivers).size
                
                if target_active_drivers > 0:
                    target_orders_per_driver = target_completed / target_active_drivers
                if baseline_active_drivers_avg > 0:
                    baseline_orders_per_driver = baseline_completed_avg / baseline_active_drivers_avg

            # 5. Operational ROI Calculations
            driver_turnout_roi = 0.0
            if baseline_active_drivers_avg > 0:
                driver_turnout_roi = ((target_active_drivers - baseline_active_drivers_avg) / baseline_active_drivers_avg) * 100

            productivity_roi = 0.0
            if baseline_orders_per_driver > 0:
                productivity_roi = ((target_orders_per_driver - baseline_orders_per_driver) / baseline_orders_per_driver) * 100

            # 6. Formatting Report Text
            extra_completed = target_completed - baseline_completed_avg
            turnout_emoji = "🟢" if driver_turnout_roi > 0 else "🔴"
            prod_emoji = "🟢" if productivity_roi > 0 else "🔴"
            city_label = selected_city if selected_city != "All" else "All Cities"
            
            res = f"""📅 Operational Performance Analysis for {target_date} ({day_name})
Geographic Scope: {city_label}
Baseline Context: Compared to previous {day_name}s over the past 30 days.

📊 Orders Fulfillment (Completed & Paid):
Historical Avg Orders: {baseline_completed_avg:.0f}
Incentive Day Orders: {target_completed}
Variance: {extra_completed:+.0f} orders
--------------------------------------------------
🛵 Driver Engagement Metrics:
Historical Avg Active Drivers: {baseline_active_drivers_avg:.0f} drivers
Incentive Day Active Drivers: {target_active_drivers} drivers
New Drivers (Worked due to incentive): {drivers_only_today}
Absent Drivers (Worked baseline, absent today): {drivers_absent_today}
--------------------------------------------------
📈 Operational ROI (Return on Incentive):
Total Incentive Investment: {total_incentive_paid:,.2f} JOD

{turnout_emoji} Driver Turnout ROI: {driver_turnout_roi:+.1f}% 
(Measures the increase/decrease in the number of active drivers compared to the baseline)

{prod_emoji} Driver Productivity ROI: {productivity_roi:+.1f}% 
(Historical: {baseline_orders_per_driver:.1f} orders/driver ➔ Incentive Day: {target_orders_per_driver:.1f} orders/driver)
"""
            self.lbl_res_text.configure(text=res)
            
            # --- Draw Charts ---
            self.draw_charts(baseline_completed_avg, target_completed, 
                             baseline_active_drivers_avg, target_active_drivers, 
                             baseline_orders_per_driver, target_orders_per_driver)
            
            self.tabview.set("Summary Report")

        except Exception as e:
            messagebox.showerror("Analysis Error", f"Details: {str(e)}")

    def draw_charts(self, base_orders, target_orders, base_drivers, target_drivers, base_prod, target_prod):
        for widget in self.tab_visuals.winfo_children():
            widget.destroy()
            
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(10, 4), dpi=100)
        fig.patch.set_facecolor('#2b2b2b') 
        
        text_color = 'white'
        
        # 1. Orders Chart
        ax1.bar(['Historical Avg', 'Incentive Day'], [base_orders, target_orders], color=['#7f8c8d', '#2ecc71'])
        ax1.set_title('Orders Fulfillment', color=text_color)
        ax1.tick_params(colors=text_color)
        ax1.set_facecolor('#2b2b2b')
        for spine in ax1.spines.values(): spine.set_color('gray')
        
        # 2. Drivers Chart
        ax2.bar(['Historical Avg', 'Incentive Day'], [base_drivers, target_drivers], color=['#7f8c8d', '#3498db'])
        ax2.set_title('Active Drivers Turnout', color=text_color)
        ax2.tick_params(colors=text_color)
        ax2.set_facecolor('#2b2b2b')
        for spine in ax2.spines.values(): spine.set_color('gray')
        
        # 3. Productivity Chart
        ax3.bar(['Historical Avg', 'Incentive Day'], [base_prod, target_prod], color=['#7f8c8d', '#9b59b6'])
        ax3.set_title('Productivity (Orders/Driver)', color=text_color)
        ax3.tick_params(colors=text_color)
        ax3.set_facecolor('#2b2b2b')
        for spine in ax3.spines.values(): spine.set_color('gray')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.tab_visuals)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

if __name__ == "__main__":
    app = IncentiveAnalyzer()
    app.mainloop()