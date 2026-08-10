import numpy as np
import pandas as pd
import streamlit as st

# إعدادات الصفحة
st.set_page_config(
    page_title="نظام تحديد مسافات التوصيل حسب المناطق", layout="wide"
)

st.title("📍 جدول مسافات التوصيل والتعديلات التشغيلية (معيار 25 دقيقة)")
st.markdown(
    "يقوم النظام بدراسة كل منطقة وساعة، واقتراح تعديل المسافة **فقط** عند وجود تأخير فعلي عن 25 دقيقة، مع الحفاظ على النطاق أو توسيعه في الفترات الهادئة."
)

# 1. رفع ملف البيانات
uploaded_file = st.file_uploader(
    "قم برفع ملف البيانات (CSV أو Excel)", type=["csv", "xlsx"]
)

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.strip()

    required_cols = [
        "CreatedAtTime",
        "CityName",
        "Area",
        "DeliveryDistance",
        "ShippingTime (min)",
        "OrderStatus",
        "Courier",
    ]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"الملف ينقصه الأعمدة التالية: {', '.join(missing_cols)}")
    else:
        # 2. تنظيف وتجهيز البيانات
        df["CreatedAtTime"] = pd.to_datetime(
            df["CreatedAtTime"], errors="coerce"
        )
        df["DeliveryDistance"] = pd.to_numeric(
            df["DeliveryDistance"], errors="coerce"
        )
        df["ShippingTime (min)"] = pd.to_numeric(
            df["ShippingTime (min)"], errors="coerce"
        )
        df["Order_Hour"] = df["CreatedAtTime"].dt.hour

        # الفلاتر والاستثناءات
        order_status_clean = df["OrderStatus"].astype(str).str.lower().str.strip()
        courier_clean = df["Courier"].astype(str).str.lower().str.strip()

        excluded_status_patterns = r"cancel|fail|reject|decline|test"
        is_invalid_status = order_status_clean.str.contains(
            excluded_status_patterns, na=False
        )
        is_pickup = courier_clean.str.contains("pickup", na=False)

        valid_orders = df[
            (df["DeliveryDistance"] > 0)
            & (df["ShippingTime (min)"] > 0)
            & (~is_invalid_status)
            & (~is_pickup)
        ].copy()

        # سرعة التوصيل لكل طلب (كم / ساعة)
        valid_orders["DeliverySpeed_KMH"] = (
            valid_orders["DeliveryDistance"]
            / valid_orders["ShippingTime (min)"]
        ) * 60

        total_valid = len(valid_orders)
        st.success(f"تم تحليل **{total_valid:,}** طلب توصيل فعلي بنجاح.")

        st.markdown("---")

        # 3. الفلاتر
        col1, col2 = st.columns(2)
        cities_list = sorted(valid_orders["CityName"].dropna().unique())

        with col1:
            selected_city = st.selectbox("🏙️ اختر المدينة (CityName):", cities_list)
        with col2:
            selected_hour = st.slider(
                "⏰ اختر ساعة الطلب:",
                min_value=0,
                max_value=23,
                value=14,
                format="%d:00",
            )

        city_data = valid_orders[valid_orders["CityName"] == selected_city]
        city_areas = sorted(city_data["Area"].dropna().unique())

        # 4. بناء منطق التعديل الذكي
        table_rows = []

        for area in city_areas:
            area_orders = city_data[city_data["Area"] == area]
            hour_orders = area_orders[area_orders["Order_Hour"] == selected_hour]

            # إذا كانت البيانات متوفرة للساعة
            target_data = hour_orders if len(hour_orders) >= 3 else area_orders
            is_fallback = len(hour_orders) < 3

            if not target_data.empty:
                # المسافة الحالية المسجلة (الحد الأقصى المعتاد)
                current_max_dist = target_data["DeliveryDistance"].quantile(0.85)

                # نسبة الطلبات التي وصلت في 25 دقيقة أو أقل
                on_time_orders = target_data[target_data["ShippingTime (min)"] <= 25]
                on_time_rate = (len(on_time_orders) / len(target_data)) * 100

                # سرعة القيادة الميدانية (كم/ساعة)
                speed_kmh = target_data["DeliverySpeed_KMH"].median()

                # المسافة القصوى الممكن قطعها نظرياً في 25 دقيقة بناءً على السرعة الحالية
                # المسافة = السرعة × (25 / 60)
                speed_based_max_dist = speed_kmh * (25.0 / 60.0)

                # المنطق الذكي لتحديد التعديل:
                if on_time_rate >= 85:
                    # لا يوجد مشكلة تأخير (أوقات غير ذروة أو أداء ممتاز)
                    rec_distance = max(current_max_dist, speed_based_max_dist)
                    change_action = "✔️ أداء ممتاز (لا حاجة لتقليص النطاق)"
                else:
                    # هناك تأخير حاصل (أوقات ذروة وازدحام)
                    # نقوم بتقليص المسافة للمسافة التي تضمن الوصول بـ 25 دقيقة
                    if not on_time_orders.empty:
                        rec_distance = min(
                            on_time_orders["DeliveryDistance"].quantile(0.80),
                            speed_based_max_dist,
                        )
                    else:
                        rec_distance = speed_based_max_dist

                    diff = current_max_dist - rec_distance
                    if diff > 0.3:
                        change_action = f"🔻 تقليص النطاق بمقدار {diff:.2f} كم لوجود تأخير"
                    else:
                        change_action = "⚠️ مراقبة الأداء (تأخير طفيف)"

                status_note = (
                    "بيانات فعلية للساعة" if not is_fallback else "تقديري (متوسط المنطقة)"
                )
                orders_count = len(target_data)
            else:
                current_max_dist = np.nan
                rec_distance = np.nan
                on_time_rate = np.nan
                speed_kmh = np.nan
                change_action = "لا توجد بيانات كافية"
                status_note = "-"
                orders_count = 0

            table_rows.append(
                {
                    "منطقة المتجر (Area)": area,
                    "المسافة الحالية المعتادة (كم)": (
                        f"{current_max_dist:.2f}" if pd.notnull(current_max_dist) else "-"
                    ),
                    "نسبة الالتزام بالوقت (<=25 دقيقة)": (
                        f"{on_time_rate:.0f}%" if pd.notnull(on_time_rate) else "-"
                    ),
                    "المسافة المقترحة (كم)": (
                        f"{rec_distance:.2f}" if pd.notnull(rec_distance) else "-"
                    ),
                    "التعديل والقرار التشغيلي": change_action,
                    "سرعة السير (كم/س)": (
                        f"{speed_kmh:.1f}" if pd.notnull(speed_kmh) else "-"
                    ),
                    "عدد الطلبات": orders_count,
                    "مصدر الحساب": status_note,
                }
            )

        summary_df = pd.DataFrame(table_rows)

        st.subheader(
            f"📋 تقرير قرارات التوصيل لمدينة: {selected_city} | الساعة {selected_hour:02d}:00"
        )
        st.dataframe(
            summary_df,
            use_container_width=True,
            hide_index=True,
        )

        csv_data = summary_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 تحميل التقرير كملف CSV",
            data=csv_data,
            file_name=f"delivery_strategy_{selected_city}_{selected_hour}h.csv",
            mime="text/csv",
        )
