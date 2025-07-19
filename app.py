import streamlit as st
import pandas as pd
from datetime import datetime
import time
import json
import os
from io import BytesIO
import pytz

# إعداد الصفحة
st.set_page_config(
    page_title="نظام البصمة",
    page_icon="🔐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# إعداد CSS مخصص
st.markdown("""
<style>
    /* تنسيق الخط العربي */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap');
    
    .rtl {
        direction: rtl;
        text-align: right;
        font-family: 'Tajawal', sans-serif;
    }
    
    /* تنسيق العنوان الرئيسي */
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        color: #667eea;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* تنسيق البطاقة الرئيسية */
    .fingerprint-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        color: white;
        text-align: center;
    }
    
    /* تنسيق دائرة البصمة */
    .fingerprint-circle {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: linear-gradient(45deg, #4facfe, #00f2fe);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 20px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(79, 172, 254, 0.4);
    }
    
    .fingerprint-circle:hover {
        transform: scale(1.1);
        box-shadow: 0 15px 40px rgba(79, 172, 254, 0.6);
    }
    
    .fingerprint-icon {
        font-size: 4rem;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* تنسيق أزرار الأشخاص */
    .user-buttons {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 15px;
        margin-bottom: 30px;
    }
    
    /* تنسيق حالة النجاح */
    .success-message {
        background: linear-gradient(45deg, #56ab2f, #a8e6cf);
        color: #2d5016;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 20px 0;
    }
    
    /* تنسيق حالة الخطأ */
    .error-message {
        background: linear-gradient(45deg, #ff416c, #ff4b2b);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 20px 0;
    }
    
    /* تنسيق سجل الحضور */
    .attendance-log {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .log-entry {
        padding: 12px;
        margin-bottom: 10px;
        background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white;
        border-radius: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 3px 10px rgba(240, 147, 251, 0.3);
    }
    
    /* إخفاء عناصر Streamlit غير المرغوبة */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    
    /* تنسيق الأزرار */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        border: none;
        padding: 15px;
        font-size: 1.1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    /* تنسيق الجدول */
    .dataframe {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# ملف حفظ البيانات
DATA_FILE = "attendance_data.json"

# تحميل البيانات المحفوظة
def load_attendance_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

# حفظ البيانات
def save_attendance_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# إنشاء ملف Excel
def create_excel_file(data):
    if not data:
        return None
    
    df = pd.DataFrame(data)
    # ترتيب الأعمدة
    df = df[['name', 'date', 'time', 'timestamp']]
    df.columns = ['الاسم', 'التاريخ', 'الوقت', 'الطابع الزمني']
    
    # إنشاء ملف Excel في الذاكرة
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='سجل الحضور', index=False)
        
        # تنسيق الجدول
        workbook = writer.book
        worksheet = writer.sheets['سجل الحضور']
        
        # تنسيق الهيدر
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#667eea',
            'font_color': 'white',
            'border': 1
        })
        
        # تطبيق التنسيق على الهيدر
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # ضبط عرض الأعمدة
        worksheet.set_column('A:A', 15)  # الاسم
        worksheet.set_column('B:B', 15)  # التاريخ
        worksheet.set_column('C:C', 15)  # الوقت
        worksheet.set_column('D:D', 20)  # الطابع الزمني
    
    output.seek(0)
    return output

# إعداد التوقيت المحلي للإسكندرية
ALEXANDRIA_TZ = pytz.timezone('Africa/Cairo')

def get_local_time():
    """الحصول على التوقيت المحلي للإسكندرية"""
    # الحصول على التوقيت العالمي ثم تحويله للتوقيت المحلي
    utc_time = datetime.utcnow()
    utc_time = pytz.utc.localize(utc_time)
    local_time = utc_time.astimezone(ALEXANDRIA_TZ)
    return local_time

# تهيئة البيانات في الجلسة
if 'attendance_log' not in st.session_state:
    st.session_state.attendance_log = load_attendance_data()

if 'selected_user' not in st.session_state:
    st.session_state.selected_user = None

if 'scanning' not in st.session_state:
    st.session_state.scanning = False

# العنوان الرئيسي
st.markdown('<div class="rtl main-title">🔐 نظام البصمة</div>', unsafe_allow_html=True)

# قائمة الأشخاص
users = ["Amr", "Rana", "Farida", "Hadel", "Fatma","Asmaa"]

# اختيار الشخص
st.markdown('<div class="rtl"><h3>اختر الشخص:</h3></div>', unsafe_allow_html=True)
cols = st.columns(len(users))

for i, user in enumerate(users):
    with cols[i]:
        if st.button(user, key=f"user_{user}"):
            st.session_state.selected_user = user
            st.success(f"تم اختيار: {user}")
            st.rerun()

# عرض الشخص المختار
if st.session_state.selected_user:
    st.markdown(f'<div class="rtl success-message">الشخص المختار: {st.session_state.selected_user}</div>', 
                unsafe_allow_html=True)

# قسم البصمة
st.markdown('<div class="rtl"><h3>📱 مسح البصمة:</h3></div>', unsafe_allow_html=True)

# زر البصمة
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("👆 مسح البصمة", key="fingerprint_scan"):
        if not st.session_state.selected_user:
            st.error("⚠️ من فضلك اختر الشخص أولاً")
        else:
            # بدء المسح
            st.session_state.scanning = True
            with st.spinner("🔍 جاري مسح البصمة..."):
                time.sleep(2)  # محاكاة وقت المسح
            
            # تسجيل الحضور
            now = get_local_time()
            entry = {
                'name': st.session_state.selected_user,
                'time': now.strftime("%I:%M:%S %p"),
                'time_24': now.strftime("%H:%M:%S"),
                'date': now.strftime("%Y-%m-%d"),
                'date_arabic': now.strftime("%d/%m/%Y"),
                'timestamp': now.timestamp()
            }
            
            st.session_state.attendance_log.insert(0, entry)
            save_attendance_data(st.session_state.attendance_log)
            
            st.success(f"✅ تم تسجيل حضور: {st.session_state.selected_user}")
            st.session_state.selected_user = None
            st.session_state.scanning = False
            st.rerun()

# سجل الحضور
st.markdown('<div class="rtl"><h3>📋 سجل الحضور:</h3></div>', unsafe_allow_html=True)

if st.session_state.attendance_log:
    # عرض آخر 10 سجلات
    recent_logs = st.session_state.attendance_log[:10]
    
    for entry in recent_logs:
        date_display = entry.get('date_arabic', entry['date'])
        time_display = entry.get('time', entry.get('time_24', 'غير محدد'))
        st.markdown(f"""
        <div class="rtl log-entry">
            <div style="font-weight: bold; font-size: 1.1rem;">{entry['name']}</div>
            <div style="opacity: 0.9;">{date_display} - {time_display}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # إحصائيات سريعة
    st.markdown("### 📊 الإحصائيات:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("إجمالي السجلات", len(st.session_state.attendance_log))
    
    with col2:
        today = get_local_time().strftime("%Y-%m-%d")
        today_count = len([entry for entry in st.session_state.attendance_log if entry['date'] == today])
        st.metric("سجلات اليوم", today_count)
    
    with col3:
        # عدد الأشخاص الفريدين
        unique_users = len(set(entry['name'] for entry in st.session_state.attendance_log))
        st.metric("الأشخاص", unique_users)
    
    # أزرار الإدارة
    col1, col2 = st.columns(2)
    
    with col1:
        # تحميل Excel
        if st.button("📥 تحميل Excel"):
            excel_file = create_excel_file(st.session_state.attendance_log)
            if excel_file:
                st.download_button(
                    label="تحميل ملف Excel",
                    data=excel_file,
                    file_name=f"attendance_log_{get_local_time().strftime('%Y-%m-%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("لا توجد بيانات للتحميل")
    
    with col2:
        # مسح السجل
        if st.button("🗑️ مسح السجل"):
            if st.session_state.attendance_log:
                st.session_state.attendance_log = []
                save_attendance_data([])
                st.success("🗑️ تم مسح السجل بنجاح")
                st.rerun()
            else:
                st.error("📝 السجل فارغ بالفعل")

    # عرض الجدول التفصيلي
    if st.checkbox("عرض الجدول التفصيلي"):
        df = pd.DataFrame(st.session_state.attendance_log)
        # اختيار الأعمدة المناسبة
        if 'date_arabic' in df.columns:
            df_display = df[['name', 'date_arabic', 'time']].copy()
        else:
            df_display = df[['name', 'date', 'time']].copy()
        
        df_display.columns = ['الاسم', 'التاريخ', 'الوقت']
        st.dataframe(df_display, use_container_width=True)

else:
    st.info("📝 لا توجد سجلات حضور بعد")

# معلومات إضافية في الشريط الجانبي
with st.sidebar:
    st.markdown("### ℹ️ معلومات النظام")
    st.info("""
    **نظام البصمة الذكي**
    
    ✅ تسجيل الحضور بسهولة
    
    ✅ حفظ البيانات تلقائياً
    
    ✅ تصدير إلى Excel
    
    ✅ إحصائيات فورية
    
    ✅ واجهة عربية
    
    🕐 التوقيت: الإسكندرية
    """)
    
    # عرض التوقيت الحالي
    current_time = get_local_time()
    st.markdown(f"**التوقيت الحالي (الإسكندرية):**")
    st.markdown(f"📅 {current_time.strftime('%d/%m/%Y')}")
    st.markdown(f"🕐 {current_time.strftime('%I:%M:%S %p')}")
    st.markdown(f"🌍 المنطقة الزمنية: {current_time.tzinfo}")
    
    # إضافة زر تحديث الوقت
    if st.button("🔄 تحديث الوقت"):
        st.rerun()

# رسالة ترحيب للمستخدمين الجدد
if not st.session_state.attendance_log and 'welcome_shown' not in st.session_state:
    st.balloons()
    st.success("🎉 مرحباً بك في نظام البصمة!")
    st.session_state.welcome_shown = True
