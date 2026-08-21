import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

# Modern Appearance Settings
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class DeliveryOptimizationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Comprehensive Field Delivery Optimization System")
        self.geometry("1100x850")
        
        self.valid_orders_global = pd.DataFrame()
        self.current_analysis_df = pd.DataFrame()
        self.table_data_global = []

        self.setup_ui()

    def setup_ui(self):
        # ==========================================
        # Make the entire UI Scrollable
        # ==========================================
        self.main_scroll_frame = ctk.CTkScrollableFrame(self)
        self.main_scroll_frame.pack(fill="both", expand=True)

        # Main Title
        self.title_label = ctk.CTkLabel(self.main_scroll_frame, text="📍 Comprehensive Field Delivery Optimization (30 Days)", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        # ----------------------------------------
        # Frame 1: File Loading
        # ----------------------------------------
        self.file_frame = ctk.CTkFrame(self.main_scroll_frame)
        self.file_frame.pack(pady=5, padx=20, fill="x")

        self.file_label = ctk.CTkLabel(self.file_frame, text="File Path:", font=ctk.CTkFont(size=14))
        self.file_label.pack(side="left", padx=10, pady=10)

        self.file_entry = ctk.CTkEntry(self.file_frame, width=400, justify="left")
        self.file_entry.pack(side="left", padx=10, pady=10)

        self.browse_btn = ctk.CTkButton(self.file_frame, text="Browse", width=80, command=self.browse_file)
        self.browse_btn.pack(side="left", padx=5, pady=10)

        self.load_btn = ctk.CTkButton(self.file_frame, text="Load & Filter Data", fg_color="#17a2b8", hover_color="#138496", text_color="white", command=self.load_data)
        self.load_btn.pack(side="right", padx=20, pady=10)

        # ----------------------------------------
        # Frame 2: Filters and Analysis Buttons
        # ----------------------------------------
        self.controls_frame = ctk.CTkFrame(self.main_scroll_frame)
        self.controls_frame.pack(pady=10, padx=20, fill="x")

        self.filter_subframe = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.filter_subframe.pack(pady=10)

        ctk.CTkLabel(self.filter_subframe, text="Select City:", font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        self.city_combo = ctk.CTkComboBox(self.filter_subframe, values=[], state="readonly", width=150, justify="left")
        self.city_combo.pack(side="left", padx=10)

        ctk.CTkLabel(self.filter_subframe, text="Select Hour:", font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        self.hour_combo = ctk.CTkComboBox(self.filter_subframe, values=[], state="readonly", width=100, justify="left")
        self.hour_combo.pack(side="left", padx=30)

        self.btns_subframe = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.btns_subframe.pack(pady=10)

        self.btn_alldays = ctk.CTkButton(self.btns_subframe, text="Analyze: All Days", fg_color="#28a745", hover_color="#218838", text_color="white", state="disabled", command=lambda: self.analyze_data([0, 1, 2, 3, 4, 5, 6], "All Days"))
        self.btn_alldays.pack(side="left", padx=10)
        
        self.btn_weekend = ctk.CTkButton(self.btns_subframe, text="Analyze: Fri + Sat", fg_color="#d9534f", hover_color="#c9302c", text_color="white", state="disabled", command=lambda: self.analyze_data([4, 5], "Friday + Saturday"))
        self.btn_weekend.pack(side="left", padx=10)

        self.btn_thu = ctk.CTkButton(self.btns_subframe, text="Analyze: Thursday", fg_color="#f0ad4e", hover_color="#ec971f", text_color="white", state="disabled", command=lambda: self.analyze_data([3], "Thursday"))
        self.btn_thu.pack(side="left", padx=10)

        self.btn_weekdays = ctk.CTkButton(self.btns_subframe, text="Analyze: Sun to Wed", fg_color="#5bc0de", hover_color="#31b0d5", text_color="white", state="disabled", command=lambda: self.analyze_data([6, 0, 1, 2], "Sunday to Wednesday"))
        self.btn_weekdays.pack(side="left", padx=10)

        self.status_label = ctk.CTkLabel(self.controls_frame, text="", font=ctk.CTkFont(size=14, weight="bold"), text_color="#007bff", justify="left")
        self.status_label.pack(pady=5)

        # ----------------------------------------
        # Frame 3: Table and Export
        # ----------------------------------------
        self.table_frame = ctk.CTkFrame(self.main_scroll_frame)
        self.table_frame.pack(pady=5, padx=20, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=30, font=('Arial', 11), background="#2b2b2b" if ctk.get_appearance_mode()=="Dark" else "white", foreground="white" if ctk.get_appearance_mode()=="Dark" else "black", fieldbackground="#2b2b2b" if ctk.get_appearance_mode()=="Dark" else "white")
        style.configure("Treeview.Heading", font=('Arial', 12, 'bold'), background="#565b5e", foreground="white")
        style.map('Treeview', background=[('selected', '#1f538d')])
        
        columns = ('Area', 'CurrentDist', 'AdjustedDist', 'Decision', 'Orders')
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show='headings', height=6)
        
        self.tree.heading('Area', text='Area')
        self.tree.heading('CurrentDist', text='Current Max Dist (km)')
        self.tree.heading('AdjustedDist', text='Adjusted Dist')
        self.tree.heading('Decision', text='Operational Decision')
        self.tree.heading('Orders', text='Orders Count')
        
        self.tree.column('Area', width=150, anchor='w')
        self.tree.column('CurrentDist', width=150, anchor='center')
        self.tree.column('AdjustedDist', width=120, anchor='center')
        self.tree.column('Decision', width=200, anchor='w')
        self.tree.column('Orders', width=100, anchor='center')

        scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        self.export_btn = ctk.CTkButton(self.main_scroll_frame, text="Export to Excel", fg_color="#ffc107", hover_color="#e0a800", text_color="white", state="disabled", command=self.export_excel)
        self.export_btn.pack(pady=10)

        # ----------------------------------------
        # Frame 4: Plot and Insights
        # ----------------------------------------
        self.plot_controls_frame = ctk.CTkFrame(self.main_scroll_frame, fg_color="transparent")
        self.plot_controls_frame.pack(pady=5)

        ctk.CTkLabel(self.plot_controls_frame, text="Select Area for Plotting:", font=ctk.CTkFont(size=14)).pack(side="left", padx=5)
        self.area_combo = ctk.CTkComboBox(self.plot_controls_frame, values=[], state="readonly", width=150, justify="left")
        self.area_combo.pack(side="left", padx=10)

        self.plot_btn = ctk.CTkButton(self.plot_controls_frame, text="Plot Relationship (Deep Dive)", text_color="white", state="disabled", command=self.plot_graph)
        self.plot_btn.pack(side="left", padx=10)

        self.canvas_frame = ctk.CTkFrame(self.main_scroll_frame)
        self.canvas_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.insights_box = ctk.CTkTextbox(self.main_scroll_frame, height=200, font=ctk.CTkFont(family="Arial", size=14), wrap="word")
        self.insights_box.tag_config("ltr", justify="left")
        self.insights_box.pack(pady=10, padx=20, fill="x")
        self.insights_box.insert("1.0", "A detailed analytical explanation will appear here after clicking 'Plot Relationship'...", "ltr")
        self.insights_box.configure(state="disabled")

        # ----------------------------------------
        # Signature
        # ----------------------------------------
        self.signature_label = ctk.CTkLabel(self.main_scroll_frame, text="Developed by Mahmoud Shehadah", font=ctk.CTkFont(family="Helvetica", size=12, slant="italic"), text_color="gray")
        self.signature_label.pack(side="bottom", pady=20)

    # ==========================================
    # Vectorized Operational Methods
    # ==========================================
    def browse_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Excel/CSV Files", "*.csv;*.xlsx")])
        if filepath:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filepath)

    def load_data(self):
        filepath = self.file_entry.get()
        if not filepath:
            messagebox.showerror("Error", "Please select a file first.")
            return
            
        try:
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)
                
            df.columns = df.columns.str.strip()
            
            required_cols = ["CreatedAtDate", "CreatedHour", "CityName", "Area", "DeliveryDistance", "ShippingTime (min)", "OrderStatus", "Courier"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                messagebox.showerror("Error", f"The file is missing the following columns:\n{', '.join(missing_cols)}")
                return

            # Vectorized datetime parsing (removed 'mixed' format for speed optimization)
            df["CreatedAtDate"] = pd.to_datetime(df["CreatedAtDate"], errors="coerce")
            today = pd.Timestamp.now().normalize()
            thirty_days_ago = today - pd.Timedelta(days=30)
            df = df[df["CreatedAtDate"] >= thirty_days_ago].copy()
            
            if df.empty:
                messagebox.showerror("Error", "No orders found in the last 30 days.")
                return
                
            df["DayOfWeek"] = df["CreatedAtDate"].dt.dayofweek
            
            # Vectorized string operations
            df["CityName"] = df["CityName"].fillna("Unknown").astype(str).str.strip().str.title()
            df["OrderStatus"] = df["OrderStatus"].fillna("").astype(str).str.strip().str.lower()
            df["Courier"] = df["Courier"].fillna("").astype(str).str.strip().str.lower()
            df["Area"] = df["Area"].fillna("").astype(str).str.strip()

            allowed_statuses = ["completed", "cancelled with pay to driver and vendor", "cancelled with pay to driver", "cancelled with pay to vendor"]
            df = df[(df["Courier"].str.contains("delivery", na=False)) & (df["OrderStatus"].isin(allowed_statuses))].copy()
            
            # Vectorized regex replacements
            df["FixedHour"] = pd.to_numeric(df["CreatedHour"], errors="coerce")
            df["DeliveryDistance"] = pd.to_numeric(df["DeliveryDistance"].astype(str).str.replace(r'[^\d.]', '', regex=True), errors="coerce")
            df["ShippingTime (min)"] = pd.to_numeric(df["ShippingTime (min)"].astype(str).str.replace(r'[^\d.]', '', regex=True), errors="coerce")
            
            self.valid_orders_global = df[(df["DeliveryDistance"] > 0) & (df["ShippingTime (min)"] > 0) & (df["FixedHour"].notnull())].copy()
            self.valid_orders_global["FixedHour"] = self.valid_orders_global["FixedHour"].astype(int)
            
            if self.valid_orders_global.empty:
                messagebox.showerror("Error", "No valid data remains after filtering out zero distances or zero times.")
                return
                
            cities = sorted(self.valid_orders_global["CityName"].unique())
            self.city_combo.configure(values=cities)
            if cities: self.city_combo.set(cities[0])
            
            hours = [str(h) for h in sorted(self.valid_orders_global["FixedHour"].unique())]
            self.hour_combo.configure(values=hours)
            if hours: self.hour_combo.set("14" if "14" in hours else hours[0])
            
            self.btn_alldays.configure(state="normal")
            self.btn_weekend.configure(state="normal")
            self.btn_thu.configure(state="normal")
            self.btn_weekdays.configure(state="normal")
            
            messagebox.showinfo("Success", f"Successfully loaded and filtered {len(self.valid_orders_global)} orders (over 30 days)!\nNow select a City and Hour, then click an analysis button.")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading the file:\n{str(e)}")

    def analyze_data(self, target_days, lbl):
        selected_city = self.city_combo.get()
        if not selected_city:
            messagebox.showerror("Error", "Please select a City first.")
            return
            
        selected_hour = int(self.hour_combo.get())
        self.status_label.configure(text=f"📊 {selected_city} | Analysis ({lbl}) - Hour {selected_hour:02d}:00")
        
        # Apply initial filters
        self.current_analysis_df = self.valid_orders_global[
            (self.valid_orders_global["CityName"] == selected_city) &
            (self.valid_orders_global["FixedHour"] == selected_hour) & 
            (self.valid_orders_global["DayOfWeek"].isin(target_days))
        ].copy()

        self.table_data_global = []
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        active_areas = []

        # =========================================================================================
        # HIGH-PERFORMANCE VECTORIZATION
        # Replaced slow boolean masking with Pandas GroupBy and pure Numpy array calculations
        # =========================================================================================
        grouped_data = self.current_analysis_df.groupby("Area")

        for area, group in grouped_data:
            # Extract underlying numpy arrays for ultra-fast vectorized calculations
            x = group["DeliveryDistance"].values
            y = group["ShippingTime (min)"].values
            orders_count = len(x)
            
            if orders_count > 0:
                # Numpy vectorization instead of pandas series methods
                current_max_dist = np.quantile(x, 0.85) if orders_count >= 3 else np.max(x)
                avg_trip_time = np.mean(y)
                on_time_rate = (np.sum(y <= 25) / orders_count) * 100
                
                if orders_count >= 3:
                    m, c = np.polyfit(x, y, 1)
                    dist_20min = max(0, (20 - c) / m) if m > 0 else np.max(x[y <= 20]) if np.any(y <= 20) else current_max_dist
                    dist_25min = max(0, (25 - c) / m) if m > 0 else np.max(x[y <= 25]) if np.any(y <= 25) else current_max_dist
                else:
                    m, c = 0, 0
                    dist_20min = np.max(x[y <= 20]) if np.any(y <= 20) else current_max_dist
                    dist_25min = np.max(x[y <= 25]) if np.any(y <= 25) else current_max_dist
                
                # Sanitize NaNs
                dist_20min = dist_20min if not np.isnan(dist_20min) else current_max_dist
                dist_25min = dist_25min if not np.isnan(dist_25min) else current_max_dist
                    
                if on_time_rate >= 90 and avg_trip_time < 20:
                    rec_distance = max(current_max_dist, min(dist_20min, current_max_dist * 1.5) if (orders_count >= 3 and m > 0) else current_max_dist * 1.2)
                    action = "Expand Range" if (rec_distance - current_max_dist) > 0.25 else "Optimal Range"
                elif on_time_rate < 85:
                    rec_distance = min(dist_25min, current_max_dist)
                    if rec_distance == 0 or (orders_count >= 3 and m > 0 and c >= 25):
                        action = "Field Difficulties"
                        rec_distance = 1.0
                    elif (current_max_dist - rec_distance) > 0.25:
                        action = "Contract Range"
                    else:
                        action = "Monitor Performance"
                else:
                    rec_distance = current_max_dist
                    action = "Appropriate Range"
                    
                rounded_rec_dist = int(round(rec_distance))
                rounded_curr_dist = int(round(current_max_dist))
                
                row = (area, f"{rounded_curr_dist}", f"{rounded_rec_dist}", action, orders_count)
                self.table_data_global.append(row)
                self.tree.insert('', tk.END, values=row)
                active_areas.append(area)
                
        self.export_btn.configure(state="normal")
        
        if active_areas:
            self.area_combo.configure(values=active_areas)
            self.area_combo.set(active_areas[0])
            self.plot_btn.configure(state="normal")
        else:
            self.area_combo.configure(values=[])
            self.area_combo.set('')
            self.plot_btn.configure(state="disabled")

    def export_excel(self):
        if not self.table_data_global: return
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if save_path:
            columns_names = ['Area', 'Current Max Distance (km)', 'Rounded Adjusted Distance', 'Operational Decision', 'Analyzed Orders Count']
            pd.DataFrame(self.table_data_global, columns=columns_names).to_excel(save_path, index=False)
            messagebox.showinfo("Success", "File exported successfully!")

    def plot_graph(self):
        selected_area = self.area_combo.get()
        if not selected_area: return

        target_chart_data = self.current_analysis_df[self.current_analysis_df["Area"] == selected_area]
        x = target_chart_data["DeliveryDistance"].values
        y = target_chart_data["ShippingTime (min)"].values
        orders_count = len(x)
        
        if orders_count >= 3:
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()

            fig, ax = plt.subplots(figsize=(10, 5))
            m, c = np.polyfit(x, y, 1)
            
            ax.scatter(x, y, color='blue', alpha=0.6)
            if m > 0:
                x_line = np.linspace(np.min(x), np.max(x), 100)
                ax.plot(x_line, (m * x_line) + c, color='red', linewidth=2)
                
            ax.axhline(y=25, color='orange', linestyle='--', label='25 Min SLA')
            ax.axhline(y=20, color='green', linestyle=':', label='20 Min Target')
            
            selected_city = self.city_combo.get()
            ax.set_title(f"Time vs. Distance: {selected_area} ({selected_city})")
            ax.set_xlabel("Distance (km)")
            ax.set_ylabel("Time (min)")
            ax.legend()
            
            # Info Box within the plot
            on_time_rate = (np.sum(y <= 25) / orders_count) * 100
            avg_trip_time = np.mean(y)
            
            stats_text = (
                f"Total Orders: {orders_count}\n"
                f"On-Time (<25m): {on_time_rate:.1f}%\n"
                f"Avg Time: {avg_trip_time:.1f} min\n"
                f"Fixed Overhead: {c:.1f} min\n"
                f"Slope: {m:.1f} min/km"
            )
            
            props = dict(boxstyle='round', facecolor='#f8f9fa', alpha=0.8, edgecolor='#ced4da')
            ax.text(0.02, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
                    verticalalignment='top', bbox=props, color='#343a40', fontweight='bold')
            
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Generate Insights
            current_max_dist = np.quantile(x, 0.85)
            dist_20min = max(0, (20 - c) / m) if m > 0 else current_max_dist
            dist_25min = max(0, (25 - c) / m) if m > 0 else current_max_dist
            rounded_curr_dist = int(round(current_max_dist))

            if on_time_rate >= 90 and avg_trip_time < 20:
                rec_distance = max(current_max_dist, min(dist_20min, current_max_dist * 1.5) if m > 0 else current_max_dist * 1.2)
                rounded_rec = int(round(rec_distance))
                if (rec_distance - current_max_dist) > 0.25:
                    decision = "Expand Range"
                    logic_explanation = f"Performance is Excellent. The on-time completion rate is {on_time_rate:.1f}% with an average trip time of {avg_trip_time:.1f} mins. The regression indicates couriers can reach {dist_20min:.1f} km within 20 mins. Recommendation: Increase distance from {rounded_curr_dist} km to {rounded_rec} km."
                else:
                    decision = "Optimal Range"
                    logic_explanation = f"Performance is Optimal. Despite a high completion rate ({on_time_rate:.1f}%), expanding further may risk breaching the 25-minute SLA based on the regression slope. The current range of {rounded_curr_dist} km is stable."
            
            elif on_time_rate < 85:
                rec_distance = min(dist_25min, current_max_dist)
                rounded_rec = int(round(rec_distance))
                if rec_distance == 0 or (m > 0 and c >= 25):
                    decision = "Field Difficulties"
                    logic_explanation = f"Critical Warning! The fixed overhead time (y-intercept) is {c:.1f} mins. This indicates couriers are spending excessive time at the vendor or customer location before driving. Distance is minimized until operational bottlenecks are resolved."
                elif (current_max_dist - rec_distance) > 0.25:
                    decision = "Contract Range"
                    logic_explanation = f"Performance is Substandard. The completion rate is only {on_time_rate:.1f}%. Based on the slope, to ensure delivery within 25 minutes, the distance must not exceed {dist_25min:.1f} km. Recommendation: Contract distance from {rounded_curr_dist} km to {rounded_rec} km."
                else:
                    decision = "Monitor Performance"
                    logic_explanation = f"Performance is slightly declining ({on_time_rate:.1f}%), but the calculated target distance is very close to the current distance ({rounded_curr_dist} km). Advise monitoring courier and vendor performance without immediate range reduction."
            
            else:
                decision = "Appropriate Range"
                logic_explanation = f"Performance is Stable ({on_time_rate:.1f}% completion rate). The analytical model shows no urgent need for expansion or contraction. Maintaining current distance at {rounded_curr_dist} km."

            # Update text box
            insight_text = (
                f"🔍 Performance Analysis for ({selected_area}) based on the scatter plot:\n\n"
                f"• Total Analyzed Orders: {orders_count}\n"
                f"• Successful SLA Completion (<25 min): {on_time_rate:.1f}%\n"
                f"• Actual Average Trip Time: {avg_trip_time:.1f} min\n"
                f"• Estimated Fixed Overhead Time: {c:.1f} min\n"
                f"• Additional Time Required per 1 km (Slope): {m:.1f} min/km\n\n"
                f"💡 Operational Decision: [{decision}]\n"
                f"{logic_explanation}"
            )
            
            self.insights_box.configure(state="normal")
            self.insights_box.delete("1.0", "end")
            self.insights_box.insert("1.0", insight_text, "ltr")
            self.insights_box.configure(state="disabled")

            self.main_scroll_frame._parent_canvas.yview_moveto(1.0)
            
        else:
            messagebox.showwarning("Warning", "Not enough data points to plot (minimum 3 trips required).")

if __name__ == "__main__":
    app = DeliveryOptimizationApp()
    app.mainloop()