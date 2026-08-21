import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import pandas as pd
import numpy as np

# Matplotlib for Charts
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

try:
    import arabic_reshaper
    from bidi.algorithm import get_display

    def ar_text(text):
        if not isinstance(text, str): return str(text)
        return get_display(arabic_reshaper.reshape(text))
except ImportError:
    def ar_text(text): return str(text)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class OrderLifecycleAnalyzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Order Lifecycle & Bottleneck Analyzer (Vectorized & Fast)")
        self.geometry("1180x850")
        self.minsize(1050, 750)

        self.file_path = None
        self.raw_df = None
        self.processed_df = None
        self.driver_summary = None

        self._build_ui()

    def _build_ui(self):
        # Footer
        self.signature_label = ctk.CTkLabel(
            self, text="Developed by Mahmoud Shehadah", 
            font=ctk.CTkFont(size=11, slant="italic"), text_color="gray"
        )
        self.signature_label.pack(side="bottom", pady=(0, 5))

        # 1. Top Frame
        top_frame = ctk.CTkFrame(self, corner_radius=8)
        top_frame.pack(fill="x", padx=15, pady=8)

        self.btn_select = ctk.CTkButton(top_frame, text="📁 1. Select Operations File", command=self.browse_file, width=180)
        self.btn_select.pack(side="left", padx=10, pady=8)

        self.lbl_file_status = ctk.CTkLabel(top_frame, text="No file selected", text_color="gray")
        self.lbl_file_status.pack(side="left", padx=10)

        # 2. Filter Frame
        filter_frame = ctk.CTkFrame(self, corner_radius=8, fg_color="#2b3038")
        filter_frame.pack(fill="x", padx=15, pady=(0, 8))

        ctk.CTkLabel(filter_frame, text="City:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(15, 5), pady=10)
        self.combo_city = ctk.CTkComboBox(filter_frame, values=["All"], state="disabled", width=140)
        self.combo_city.pack(side="left", padx=(0, 20), pady=10)

        ctk.CTkLabel(filter_frame, text="From (YYYY-MM-DD):", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(10, 5), pady=10)
        self.entry_start_date = ctk.CTkEntry(filter_frame, width=110, state="disabled")
        self.entry_start_date.pack(side="left", padx=(0, 20), pady=10)

        ctk.CTkLabel(filter_frame, text="To:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(10, 5), pady=10)
        self.entry_end_date = ctk.CTkEntry(filter_frame, width=110, state="disabled")
        self.entry_end_date.pack(side="left", padx=(0, 20), pady=10)

        self.btn_run = ctk.CTkButton(
            filter_frame, text="⚡ 2. Apply & Analyze Data", command=self.start_processing_thread,
            state="disabled", fg_color="#27ae60", hover_color="#219150"
        )
        self.btn_run.pack(side="right", padx=15, pady=10)

        # 3. Dynamic SLA Configuration Frame
        sla_frame = ctk.CTkFrame(self, corner_radius=8)
        sla_frame.pack(fill="x", padx=15, pady=(0, 8))
        
        ctk.CTkLabel(sla_frame, text="Dynamic Rules Configuration:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=6, sticky="w", padx=10, pady=(5,0))

        info_text = "Vendor Prep: Fixed 10m  |  Transit to Vendor: Fixed 15m  |  Assign Time: Auto 50% of SystemPrepTime  |  Total SLA: Auto-Calculated"
        ctk.CTkLabel(sla_frame, text=info_text, text_color="#f1c40f", font=ctk.CTkFont(size=11, slant="italic")).grid(row=1, column=0, columnspan=6, sticky="w", padx=10, pady=5)

        self.sla_inputs = {}
        
        ctk.CTkLabel(sla_frame, text="Vendor Approval SLA (m):").grid(row=2, column=0, padx=10, pady=8, sticky="e")
        ent_app = ctk.CTkEntry(sla_frame, width=50, justify="center")
        ent_app.insert(0, "3")
        ent_app.grid(row=2, column=1, padx=5, pady=8, sticky="w")
        self.sla_inputs['approve'] = ent_app

        ctk.CTkLabel(sla_frame, text="Mins per KM (For Shipping):").grid(row=2, column=2, padx=10, pady=8, sticky="e")
        ent_km = ctk.CTkEntry(sla_frame, width=50, justify="center")
        ent_km.insert(0, "4")
        ent_km.grid(row=2, column=3, padx=5, pady=8, sticky="w")
        self.sla_inputs['mins_per_km'] = ent_km

        ctk.CTkLabel(sla_frame, text="Base Drop-off Time (m):").grid(row=2, column=4, padx=10, pady=8, sticky="e")
        ent_base = ctk.CTkEntry(sla_frame, width=50, justify="center")
        ent_base.insert(0, "5")
        ent_base.grid(row=2, column=5, padx=5, pady=8, sticky="w")
        self.sla_inputs['base_dropoff'] = ent_base

        # 4. Main Tabs
        self.tabview = ctk.CTkTabview(self, corner_radius=8)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        self.tab_summary = self.tabview.add("📋 Summary & Insights")
        self.tab_bottlenecks = self.tabview.add("📊 Bottlenecks Analysis")
        self.tab_vendors = self.tabview.add("🏬 Vendor Performance")
        self.tab_drivers = self.tabview.add("🚚 Driver Performance")

        self.txt_summary = ctk.CTkTextbox(self.tab_summary, font=ctk.CTkFont(family="Consolas", size=14))
        self.txt_summary.pack(fill="both", expand=True, padx=10, pady=10)

        self.frame_bottlenecks_chart = ctk.CTkFrame(self.tab_bottlenecks, fg_color="transparent")
        self.frame_bottlenecks_chart.pack(fill="both", expand=True)

        self.frame_vendors_chart = ctk.CTkFrame(self.tab_vendors, fg_color="transparent")
        self.frame_vendors_chart.pack(fill="both", expand=True)

        self.frame_drivers_chart = ctk.CTkFrame(self.tab_drivers, fg_color="transparent")
        self.frame_drivers_chart.pack(fill="both", expand=True)

    def browse_file(self):
        filetypes = (("Excel / CSV files", "*.xlsx *.xls *.csv"), ("All files", "*.*"))
        path = filedialog.askopenfilename(title="Select Data File", filetypes=filetypes)
        if path:
            self.file_path = path
            self.lbl_file_status.configure(text="Reading file...", text_color="orange")
            self.update()
            threading.Thread(target=self.load_initial_data, args=(path,), daemon=True).start()

    def load_initial_data(self, path):
        try:
            df = pd.read_csv(path) if path.endswith('.csv') else pd.read_excel(path)
            df.columns = df.columns.str.strip()
            
            if 'CreatedAtDate' in df.columns:
                df['CreatedAtDate'] = pd.to_datetime(df['CreatedAtDate'], errors='coerce')

            self.raw_df = df
            
            cities = ["All"]
            if 'CityName' in df.columns:
                cities.extend(sorted(df['CityName'].dropna().astype(str).unique().tolist()))
            
            min_date, max_date = "", ""
            if 'CreatedAtDate' in df.columns:
                valid_dates = df['CreatedAtDate'].dropna()
                if not valid_dates.empty:
                    min_date = valid_dates.min().strftime('%Y-%m-%d')
                    max_date = valid_dates.max().strftime('%Y-%m-%d')

            self.after(0, self.update_filter_ui, os.path.basename(path), cities, min_date, max_date)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to read file:\n{str(e)}"))

    def update_filter_ui(self, filename, cities, min_date, max_date):
        self.lbl_file_status.configure(text=filename, text_color="#4CAF50")
        self.combo_city.configure(values=cities, state="normal")
        self.combo_city.set("All")
        self.entry_start_date.configure(state="normal")
        self.entry_start_date.delete(0, 'end')
        self.entry_start_date.insert(0, min_date)
        self.entry_end_date.configure(state="normal")
        self.entry_end_date.delete(0, 'end')
        self.entry_end_date.insert(0, max_date)
        self.btn_run.configure(state="normal")

    def log(self, text):
        self.txt_summary.insert("end", text + "\n")
        self.txt_summary.see("end")

    def get_analytical_insights(self, bottleneck_counts, total_breached):
        if total_breached == 0 or bottleneck_counts.empty:
            return "\n✅ Excellent! No orders exceeded their dynamic SLAs."
        
        top_bottleneck = bottleneck_counts.index[0]
        pct = (bottleneck_counts.iloc[0] / total_breached) * 100
        
        insights = "\n" + "="*50 + "\n💡 Dynamic Insights & Recommendations:\n"
        insights += f"Primary delay stage is [{top_bottleneck}], causing {pct:.1f}% of all delayed orders.\n\n"
        
        if top_bottleneck == "Vendor Prep":
            insights += "📌 Diagnosis: Vendors frequently exceed the strict 10-minute prep SLA.\n"
        elif top_bottleneck == "Dispatch/Assign":
            insights += "📌 Diagnosis: Dispatching takes longer than 50% of the Vendor's SystemPrepTime. Supply shortage detected.\n"
        elif top_bottleneck == "Transit to Vendor":
            insights += "📌 Diagnosis: Couriers repeatedly take longer than the 15-minute SLA to reach the vendor.\n"
        elif top_bottleneck == "Shipping Transit":
            insights += "📌 Diagnosis: Last-mile delivery is taking longer than the dynamically calculated distance time.\n"
        elif top_bottleneck == "Vendor Approval":
            insights += "📌 Diagnosis: Vendors are ignoring incoming order prompts.\n"
        else:
            insights += "📌 Diagnosis: Minor delays across multiple stages compounded to breach the dynamic total SLA.\n"
            
        return insights

    def start_processing_thread(self):
        self.btn_run.configure(state="disabled")
        self.txt_summary.delete("1.0", "end")
        threading.Thread(target=self.process_data, daemon=True).start()

    def process_data(self):
        try:
            self.log("[+] Applying filters and running fully vectorized analysis...")
            df = self.raw_df.copy()
            
            # --- 1. FILTER: Exclude Pickup Orders ---
            if 'Courier' in df.columns:
                pickup_mask = df['Courier'].astype(str).str.lower().str.contains('pickup|pick up|استلام', na=False)
                pickup_count = pickup_mask.sum()
                df = df[~pickup_mask]
                if pickup_count > 0:
                    self.log(f"🧹 Filtered out {pickup_count} Pickup orders from the analysis.")
            
            # --- 2. FILTER: City & Date ---
            selected_city = self.combo_city.get()
            if selected_city != "All" and 'CityName' in df.columns:
                df = df[df['CityName'] == selected_city]
                
            start_date_str = self.entry_start_date.get()
            end_date_str = self.entry_end_date.get()
            if 'CreatedAtDate' in df.columns:
                if start_date_str: df = df[df['CreatedAtDate'] >= pd.to_datetime(start_date_str)]
                if end_date_str: df = df[df['CreatedAtDate'] <= pd.to_datetime(end_date_str)]

            if len(df) == 0: raise ValueError("No data matches the selected filters (or all were pickup orders).")

            # Data prep
            num_cols = ['TimeToApprove (min)', 'TimeToAssign (min)', 'TimeToArrive (min)', 
                        'AtVendorTime (min)', 'ShippingTime (min)', 'DeliveryTimeInMinutes',
                        'SystemPrepTime', 'DeliveryDistance']
            
            if 'SystemPrepTime' not in df.columns:
                df['SystemPrepTime'] = 20
                self.log("⚠️ Column 'SystemPrepTime' missing. Assumed 20 mins default.")
            if 'DeliveryDistance' not in df.columns:
                df['DeliveryDistance'] = 3.0
                self.log("⚠️ Column 'DeliveryDistance' missing. Assumed 3.0 KM default.")

            for col in num_cols:
                if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            # --- DYNAMIC SLA CALCULATION ---
            sla_approve = float(self.sla_inputs['approve'].get())
            mins_per_km = float(self.sla_inputs['mins_per_km'].get())
            base_dropoff = float(self.sla_inputs['base_dropoff'].get())
            
            df['SLA_Approve'] = sla_approve
            df['SLA_Assign'] = df['SystemPrepTime'] * 0.5
            df['SLA_Arrive'] = 15.0 
            df['SLA_Vendor'] = 10.0  
            df['SLA_Shipping'] = (df['DeliveryDistance'] * mins_per_km) + base_dropoff
            
            df['SLA_Total_Dynamic'] = df['SLA_Approve'] + df['SLA_Assign'] + df['SLA_Arrive'] + df['SLA_Vendor'] + df['SLA_Shipping']

            if 'OrderStatus' in df.columns:
                completed_mask = df['OrderStatus'].astype(str).str.strip().str.lower().isin(['completed', 'completeddeclined'])
            else:
                completed_mask = pd.Series([True] * len(df))

            df['Breach_Total'] = (df['DeliveryTimeInMinutes'] > df['SLA_Total_Dynamic']) & completed_mask

            # --- VECTORIZED BOTTLENECK ENGINE ---
            diff_df = pd.DataFrame({
                "Vendor Approval": df['TimeToApprove (min)'] - df['SLA_Approve'],
                "Dispatch/Assign": df['TimeToAssign (min)'] - df['SLA_Assign'],
                "Transit to Vendor": df['TimeToArrive (min)'] - df['SLA_Arrive'],
                "Vendor Prep": df['AtVendorTime (min)'] - df['SLA_Vendor'],
                "Shipping Transit": df['ShippingTime (min)'] - df['SLA_Shipping']
            })

            max_diffs = diff_df.max(axis=1)
            max_stages = diff_df.idxmax(axis=1)

            df['Primary_Bottleneck'] = np.where(
                ~df['Breach_Total'], 
                "On Time",
                np.where(max_diffs > 0, max_stages, "Multiple Minor Delays")
            )

            # Vendor Performance
            vendor_col = 'VendorName' if 'VendorName' in df.columns else df.columns[0]
            vendor_summary = df[completed_mask].groupby(vendor_col).agg(
                Total_Orders=('DeliveryTimeInMinutes', 'count'),
                Avg_Prep_Min=('AtVendorTime (min)', 'mean')
            ).reset_index().rename(columns={vendor_col: 'VendorName'})
            self.vendor_summary = vendor_summary[vendor_summary['Total_Orders'] >= 3]

            # Driver Performance (Vectorized Aggregation with Delay Rate %)
            if 'DriverId' in df.columns:
                driver_fault_mask = df['Primary_Bottleneck'].isin(['Transit to Vendor', 'Shipping Transit'])
                driver_totals = df[completed_mask].groupby('DriverId').agg(Total_Orders=('DeliveryTimeInMinutes', 'count')).reset_index()
                driver_delays = df[completed_mask & driver_fault_mask].groupby('DriverId').agg(Driver_Caused_Delays=('Primary_Bottleneck', 'count')).reset_index()
                
                d_summary = pd.merge(driver_totals, driver_delays, on='DriverId', how='left').fillna(0)
                d_summary['Delay_Rate_%'] = (d_summary['Driver_Caused_Delays'] / d_summary['Total_Orders'] * 100).round(1)
                
                # فرز السائقين بناءً على (نسبة التأخير) بدلاً من عدد الطلبات، مع شرط 3 طلبات كحد أدنى لتفادي القيم الشاذة
                self.driver_summary = d_summary[d_summary['Total_Orders'] >= 3].sort_values(by='Delay_Rate_%', ascending=False)
            else:
                self.driver_summary = pd.DataFrame()

            self.processed_df = df

            # Print Summary
            total_orders = len(df)
            total_completed = completed_mask.sum()
            total_breached = df['Breach_Total'].sum()
            breach_pct = (total_breached / total_completed * 100) if total_completed > 0 else 0

            self.log("="*50)
            self.log(f"City: {selected_city} | Period: {start_date_str} to {end_date_str}")
            self.log(f"Completed Delivery Orders: {total_completed:,} out of {total_orders:,} total orders")
            self.log(f"Dynamic SLA Breaches: {total_breached:,} orders ({breach_pct:.1f}%)")
            self.log("="*50 + "\n")
            
            delayed_df = df[df['Breach_Total']]
            bottleneck_counts = delayed_df['Primary_Bottleneck'].value_counts() if not delayed_df.empty else pd.Series()
            
            if not bottleneck_counts.empty:
                self.log("Root Cause Bottleneck Breakdown:")
                for b_name, b_count in bottleneck_counts.items():
                    self.log(f" • {b_name}: {b_count:,} orders ({(b_count/total_breached*100):.1f}%)")

            insights = self.get_analytical_insights(bottleneck_counts, total_breached)
            self.log(insights)

            # Export to Excel
            safe_city = selected_city.replace("/", "").replace("\\", "")
            out_name = f"Analysis_{safe_city}.xlsx" if selected_city != "All" else "Analysis_AllCities.xlsx"
            output_file = os.path.join(os.path.dirname(self.file_path), out_name)
            
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Filtered_Orders', index=False)
                self.vendor_summary.sort_values(by='Avg_Prep_Min', ascending=False).to_excel(writer, sheet_name='Vendors_Performance', index=False)
                if not self.driver_summary.empty:
                    self.driver_summary.to_excel(writer, sheet_name='Drivers_Performance', index=False)
            
            self.log(f"\n[✓] Analysis exported to:\n{output_file}")
            
            # Render Charts
            self.after(0, self.render_charts, df, self.vendor_summary)

        except Exception as e:
            self.log(f"\n[!] Error occurred: {str(e)}")
            messagebox.showerror("Error", str(e))
        finally:
            self.btn_run.configure(state="normal")

    def render_charts(self, df, vendor_summary):
        # 1. Bottleneck Donut Chart
        for widget in self.frame_bottlenecks_chart.winfo_children(): widget.destroy()
        delayed_df = df[df['Breach_Total']]
        if not delayed_df.empty:
            counts = delayed_df['Primary_Bottleneck'].value_counts()
            fig1 = Figure(figsize=(7, 4.5), dpi=100, facecolor='#2b3038')
            ax1 = fig1.add_subplot(111)
            ax1.pie(counts.values, labels=[ar_text(x) for x in counts.index], autopct='%1.1f%%', 
                    startangle=140, textprops=dict(color="white"), wedgeprops=dict(width=0.45, edgecolor='#2b3038'))
            ax1.set_title(ar_text("Primary Bottleneck (Dynamic SLA Breach)"), color="white", fontsize=12)
            canvas1 = FigureCanvasTkAgg(fig1, self.frame_bottlenecks_chart)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill="both", expand=True)
            NavigationToolbar2Tk(canvas1, self.frame_bottlenecks_chart).update()

        # 2. Top 10 Vendors Bar Chart
        for widget in self.frame_vendors_chart.winfo_children(): widget.destroy()
        if not vendor_summary.empty:
            top_vendors = vendor_summary.sort_values(by='Avg_Prep_Min', ascending=True).tail(10)
            fig2 = Figure(figsize=(7, 4.5), dpi=100, facecolor='#2b3038')
            ax2 = fig2.add_subplot(111)
            ax2.set_facecolor('#2b3038')
            bars = ax2.barh([ar_text(str(x)) for x in top_vendors['VendorName']], top_vendors['Avg_Prep_Min'].values, color='#e74c3c', height=0.6)
            ax2.tick_params(colors='white', labelsize=10)
            for spine in ['top','right']: ax2.spines[spine].set_visible(False)
            for spine in ['bottom','left']: ax2.spines[spine].set_color('white')
            
            for bar in bars:
                w = bar.get_width()
                ax2.text(w + 0.3, bar.get_y() + bar.get_height()/2, f"{w:.1f}m", va='center', color='white', fontsize=9)
            
            ax2.set_title(ar_text("Top 10 Vendors by Prep & Wait Time"), color="white", fontsize=12)
            fig2.tight_layout()
            canvas2 = FigureCanvasTkAgg(fig2, self.frame_vendors_chart)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill="both", expand=True)
            NavigationToolbar2Tk(canvas2, self.frame_vendors_chart).update()

        # 3. Top 10 Delayed Drivers Bar Chart (Now by Percentage)
        for widget in self.frame_drivers_chart.winfo_children(): widget.destroy()
        if hasattr(self, 'driver_summary') and not self.driver_summary.empty:
            delayed_drivers = self.driver_summary[self.driver_summary['Driver_Caused_Delays'] > 0]
            if not delayed_drivers.empty:
                # الفرز التصاعدي هنا لكي يظهر صاحب النسبة الأعلى في قمة الرسم البياني
                top_drivers = delayed_drivers.sort_values(by='Delay_Rate_%', ascending=True).tail(10)
                fig3 = Figure(figsize=(7, 4.5), dpi=100, facecolor='#2b3038')
                ax3 = fig3.add_subplot(111)
                ax3.set_facecolor('#2b3038')
                
                driver_ids = [str(int(x)) if isinstance(x, float) else str(x) for x in top_drivers['DriverId']]
                delays_pct = top_drivers['Delay_Rate_%'].values
                
                bars = ax3.barh(driver_ids, delays_pct, color='#f39c12', height=0.6)
                ax3.tick_params(colors='white', labelsize=10)
                for spine in ['top','right']: ax3.spines[spine].set_visible(False)
                for spine in ['bottom','left']: ax3.spines[spine].set_color('white')
                
                for bar in bars:
                    w = bar.get_width()
                    # إضافة علامة النسبة المئوية %
                    ax3.text(w + 0.3, bar.get_y() + bar.get_height()/2, f"{w:.1f}%", va='center', color='white', fontsize=9)
                
                ax3.set_title(ar_text("Top 10 Drivers by Delay Rate (%)"), color="white", fontsize=12)
                ax3.set_xlabel("Delay Rate (%)", color="white")
                ax3.set_ylabel("Driver ID", color="white")
                fig3.tight_layout()
                canvas3 = FigureCanvasTkAgg(fig3, self.frame_drivers_chart)
                canvas3.draw()
                canvas3.get_tk_widget().pack(fill="both", expand=True)
                NavigationToolbar2Tk(canvas3, self.frame_drivers_chart).update()

if __name__ == "__main__":
    app = OrderLifecycleAnalyzerApp()
    app.mainloop()