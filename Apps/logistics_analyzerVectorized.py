import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import warnings

# Suppress pandas warnings for cleaner terminal output
warnings.filterwarnings('ignore')

# Modern UI Settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class LogisticsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Annual Logistics Performance Analyzer (Vectorized)")
        self.geometry("1100x800")
        
        self.master_df = None
        self.create_widgets()

    def create_widgets(self):
        # Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Dashboard", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.pack(padx=20, pady=(20, 10))
        
        self.upload_btn = ctk.CTkButton(self.sidebar_frame, text="Upload Excel Files", command=self.upload_files)
        self.upload_btn.pack(padx=20, pady=20)
        
        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="No files uploaded", text_color="gray")
        self.status_label.pack(padx=20, pady=5)
        
        # Main Frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        self.info_label = ctk.CTkLabel(self.main_frame, text="Please upload data files to start analysis", font=ctk.CTkFont(size=18))
        self.info_label.pack(pady=20)
        
        # Charts Frame
        self.charts_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.charts_frame.pack(fill="both", expand=True)

    def upload_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Excel Files",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        
        if file_paths:
            try:
                self.status_label.configure(text="Processing...", text_color="yellow")
                self.update()
                
                # Load and concatenate all selected files
                dfs = [pd.read_excel(file) for file in file_paths]
                self.master_df = pd.concat(dfs, ignore_index=True)
                
                # Vectorized Datetime extraction
                if 'CreatedAtDate' in self.master_df.columns:
                    self.master_df['CreatedAtDate'] = pd.to_datetime(self.master_df['CreatedAtDate'], errors='coerce')
                    self.master_df['Year'] = self.master_df['CreatedAtDate'].dt.year
                    self.master_df['MonthNum'] = self.master_df['CreatedAtDate'].dt.month
                
                # Clean and convert time columns to numeric using Vectorized apply
                time_columns = ['TimeToApprove (min)', 'TimeToAssign (min)', 'TimeToArrive (min)', 
                                'AtVendorTime (min)', 'ShippingTime (min)', 'DeliveryTimeInMinutes']
                
                existing_cols = [col for col in time_columns if col in self.master_df.columns]
                
                if existing_cols:
                    self.master_df[existing_cols] = self.master_df[existing_cols].apply(pd.to_numeric, errors='coerce')
                
                self.status_label.configure(text=f"Loaded: {len(self.master_df)} orders", text_color="green")
                self.info_label.configure(text="Year-over-Year Performance Analysis")
                
                self.generate_charts(time_columns)
                
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while reading files:\n{str(e)}")
                self.status_label.configure(text="Error occurred", text_color="red")

    def generate_charts(self, time_columns):
        # Clear previous charts
        for widget in self.charts_frame.winfo_children():
            widget.destroy()

        fig = plt.Figure(figsize=(10, 8), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')

        # Verify we have Year data to compare
        if 'Year' not in self.master_df.columns or self.master_df['Year'].dropna().empty:
            ax = fig.add_subplot(111)
            ax.set_facecolor('#2b2b2b')
            ax.text(0.5, 0.5, 'Error: Could not extract dates from "CreatedAtDate" column.', 
                    color='white', ha='center', va='center', fontsize=14)
        else:
            # Determine the two most recent years in the dataset
            years = sorted(self.master_df['Year'].dropna().unique())
            if len(years) >= 2:
                y_prev, y_curr = years[-2], years[-1]
            else:
                y_prev, y_curr = years[0], years[0]

            # ---------------------------------------------------------
            # Chart 1: Monthly Order Volume (Year over Year Comparison)
            # ---------------------------------------------------------
            ax1 = fig.add_subplot(211)
            ax1.set_facecolor('#2b2b2b')
            
            # Vectorized GroupBy for Monthly Orders
            monthly_orders = self.master_df.groupby(['Year', 'MonthNum']).size().unstack(fill_value=0)
            months = np.arange(1, 13)
            width = 0.35
            
            # Vectorized array extraction using pandas reindex (no loops)
            orders_prev_vals = monthly_orders.loc[y_prev].reindex(months, fill_value=0).values if y_prev in monthly_orders.index else np.zeros(12)
            orders_curr_vals = monthly_orders.loc[y_curr].reindex(months, fill_value=0).values if y_curr in monthly_orders.index else np.zeros(12)
            
            # Plot arrays directly
            ax1.bar(months - width/2, orders_prev_vals, width, label=f'{int(y_prev)}', color='#8e44ad')
            ax1.bar(months + width/2, orders_curr_vals, width, label=f'{int(y_curr)}', color='#2980b9')
            
            ax1.set_title(f"Monthly Order Volume ({int(y_prev)} vs {int(y_curr)})", color='white', fontsize=14, pad=15)
            ax1.set_xticks(months)
            ax1.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
            ax1.tick_params(colors='white')
            
            # Add grid for readability
            ax1.grid(axis='y', linestyle='--', alpha=0.3, color='gray')
            ax1.legend()

            # ---------------------------------------------------------
            # Chart 2: Order Cycle Times Improvement (Year over Year)
            # ---------------------------------------------------------
            ax2 = fig.add_subplot(212)
            ax2.set_facecolor('#2b2b2b')
            
            available_time_cols = [col for col in time_columns if col in self.master_df.columns]
            
            # Single pass Vectorized GroupBy for all cycle times
            yearly_means = self.master_df.groupby('Year')[available_time_cols].mean()
            
            # Extract Numpy arrays for plotting directly
            times_prev_vals = yearly_means.loc[y_prev].values if y_prev in yearly_means.index else np.zeros(len(available_time_cols))
            times_curr_vals = yearly_means.loc[y_curr].values if y_curr in yearly_means.index else np.zeros(len(available_time_cols))
            
            x = np.arange(len(available_time_cols))
            
            # Plot bars using numpy arrays
            ax2.bar(x - width/2, times_prev_vals, width, label=f'{int(y_prev)}', color='#e74c3c')
            ax2.bar(x + width/2, times_curr_vals, width, label=f'{int(y_curr)}', color='#27ae60')
            
            ax2.set_title(f"Average Order Cycle Times ({int(y_prev)} vs {int(y_curr)}) - Minutes", color='white', fontsize=14, pad=15)
            ax2.set_xticks(x)
            
            # Format labels (List comprehension here is fine as it's just for 6 static string labels, not data processing)
            short_labels = [c.replace(' (min)', '').replace('InMinutes', '').replace('TimeTo', '') for c in available_time_cols]
            ax2.set_xticklabels(short_labels, rotation=15)
            
            ax2.tick_params(colors='white')
            ax2.grid(axis='y', linestyle='--', alpha=0.3, color='gray')
            ax2.legend()
            
        fig.tight_layout(pad=3.0)

        # Embed into CustomTkinter
        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    app = LogisticsApp()
    app.mainloop()
