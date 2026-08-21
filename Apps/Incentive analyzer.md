# Retrospective Incentive Impact Analyzer 🚀

**By Mahmoud Shehadah**

## 📌 عن البرنامج (About the Application)
أداة تحليل لوجستية متقدمة مبنية بلغة Python تستخدم تقنيات **Vectorization** عبر `Pandas` و `Numpy` لمعالجة مئات الآلاف من صفوف البيانات في أجزاء من الثانية. 
تهدف الأداة إلى قياس الأثر التشغيلي الفعلي (Operational Impact) لحملات الحوافز المالية المدفوعة لسائقي التوصيل، بعيداً عن التحليل المالي السطحي. تقيس الأداة العائد على الاستثمار (ROI) من منظور **تفاعل السائقين (Driver Turnout)** و**الإنتاجية (Productivity)**.

---

## ✨ المميزات الرئيسية (Features)
- **أداء فائق السرعة (Vectorized):** استخدام تقنيات الفلترة المتقدمة (Boolean Indexing) والعمليات الرياضية على المصفوفات (Numpy Arrays) لتجاوز بطء الحلقات التكرارية (Loops).
- **تنظيف ذكي للبيانات (Smart Data Cleaning):** يتجاهل البرنامج تلقائياً صفوف "المجاميع" (Totals) والخلايا الفارغة في ملفات الحوافز لمنع تضخم الأرقام.
- **عزل الأثر الجغرافي (Dynamic City Filtering):** القدرة على تصفية البيانات تلقائياً بناءً على المدن (CityName) المتوفرة في قاعدة البيانات.
- **خط أساس ديناميكي (Dynamic Baseline 30-Days):** يقارن أداء يوم المسابقة بمتوسط أداء *نفس اليوم من الأسبوع* خلال الـ 30 يوماً الماضية لضمان دقة الاستنتاج.
- **مؤشرات أداء مئوية (Percentage ROI):** قياس مدى نجاح الحافز في استقطاب سائقين جدد، أو زيادة أوردرات السائقين الحاليين.
- **لوحات تحكم بصرية (Data Visualizations):** رسوم بيانية مدمجة باستخدام `Matplotlib` داخل واجهة داكنة وحديثة عبر `CustomTkinter`.

---

## 📂 متطلبات البيانات (Data Requirements)

يعمل البرنامج باستقبال ملفين (Excel أو CSV). يجب أن تحتوى الملفات على الأعمدة التالية (تتجاهل الأداة المسافات الزائدة تلقائياً):

### 1. ملف الطلبات (Orders Data)
* `CreatedAtDate`: تاريخ إنشاء الطلب.
* `OrderStatus`: حالة الطلب (يقوم البرنامج تلقائياً بفلترة الحالات: Completed, Cancelled With Pay To Driver, Cancelled With Pay To Driver And Vendor).
* `DriverId`: المعرف الفريد للسائق.
* `CityName`: مدينة التوصيل (للفلترة الجغرافية).

### 2. ملف الحوافز (Incentives Data)
* `Driver Id` أو `Driver`: المعرف الفريد للسائق.
* `Incentive Amount ( JD )` أو `Incentive`: المبلغ المدفوع للسائق.

---

## 🛠️ التثبيت والتشغيل (Installation & Setup)

### 1. تثبيت المكتبات المطلوبة (Dependencies)
تأكد من تثبيت بيئة بايثون لديك، ثم قم بتشغيل الأمر التالي في موجه الأوامر (CMD):
```bash
pip install customtkinter pandas numpy matplotlib openpyxl