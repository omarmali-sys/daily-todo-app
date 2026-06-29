import streamlit as st
import os
import json
import datetime # 🆕 تم التأكد من استدعاء مكتبة التواريخ بالكامل
import pandas as pd
import plotly.express as px
from streamlit_cookies_manager import EncryptedCookieManager

# 1. Page Configuration
st.set_page_config(page_title="Daily To-Do", page_icon="✅", layout="wide")

# 2. Custom CSS
css = """
<style>
.stApp {
    background: linear-gradient(-45deg, #0f172a, #1e293b, #0f172a, #334155);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}
@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
h1, h2, h3, p, span { color: #f8fafc !important; }
div[data-testid="stMetricValue"] { color: #38bdf8 !important; }
[data-testid="stSidebar"] {
    background-color: rgba(15, 23, 42, 0.8) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
}
.completed-task {
    text-decoration: line-through;
    color: #94a3b8 !important;
}
div[data-testid="stExpander"] {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: 10px;
}
.streak-badge {
    background-color: rgba(255, 165, 0, 0.2);
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 1.2rem;
    color: #fbbf24;
    border: 1px solid #fbbf24;
    display: inline-block;
    margin-left: 15px;
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 3. Robust Cookies Manager Setup
cookies = EncryptedCookieManager(prefix="todo/", password="secure_todo_app_password_2026")

if not cookies.ready():
    st.info("جاري مزامنة المهام مع المتصفح... 🔄")
    st.stop()

# تهيئة الذاكرة السريعة (Session State)
if "todos" not in st.session_state:
    st.session_state.todos = []
    st.session_state.needs_save = False
    
    # استرجاع المهام
    saved_todos = cookies.get("local_todos")
    if saved_todos:
        try:
            st.session_state.todos = json.loads(saved_todos)
        except:
            st.session_state.todos = []
            
        for t in st.session_state.todos:
            if 'progress' not in t: t['progress'] = 100 if t.get('completed') else 0
            if 'notes' not in t: t['notes'] = ""
            if 'date' not in t: t['date'] = datetime.date.today().isoformat() # 🆕 للمهام القديمة التي لا تحتوي على تاريخ
            
        # فرز القائمة تلقائياً عند أول تحميل للتطبيق بناءً على التاريخ 🆕
        try:
            st.session_state.todos.sort(key=lambda x: x.get('date', ''))
        except:
            pass

# تهيئة نظام الشعلة (Streaks) والاحتفال
if "streak_data" not in st.session_state:
    saved_streaks = cookies.get("todo_streaks")
    if saved_streaks:
        try:
            st.session_state.streak_data = json.loads(saved_streaks)
        except:
            st.session_state.streak_data = {"streak": 0, "last_date": ""}
    else:
        st.session_state.streak_data = {"streak": 0, "last_date": ""}

if "celebrated" not in st.session_state:
    st.session_state.celebrated = False

# دالة الحفظ الذكية
def flag_for_save():
    cookies["local_todos"] = json.dumps(st.session_state.todos)
    cookies["todo_streaks"] = json.dumps(st.session_state.streak_data)
    st.session_state.needs_save = True

# --- دوال التحكم (Callbacks) ---
def toggle_task(index, key):
    is_checked = st.session_state[key]
    st.session_state.todos[index]['completed'] = is_checked
    if is_checked:
        st.session_state.todos[index]['progress'] = 100
    elif st.session_state.todos[index]['progress'] == 100:
        st.session_state.todos[index]['progress'] = 0
    flag_for_save()

def update_progress(index, key):
    new_prog = st.session_state[key]
    st.session_state.todos[index]['progress'] = new_prog
    if new_prog == 100:
        st.session_state.todos[index]['completed'] = True
    elif new_prog < 100 and st.session_state.todos[index]['completed']:
        st.session_state.todos[index]['completed'] = False
    flag_for_save()

def update_notes(index, key):
    st.session_state.todos[index]['notes'] = st.session_state[key]
    flag_for_save()

def delete_task(task_id):
    st.session_state.todos = [t for t in st.session_state.todos if t['id'] != task_id]
    flag_for_save()

def clear_completed():
    st.session_state.todos = [t for t in st.session_state.todos if not t['completed']]
    flag_for_save()

# ==========================================
# 4. UI Sidebar Layout
# ==========================================

with st.sidebar:
    if os.path.exists("Logo.png"):
        st.image("Logo.png", use_container_width=True)
        st.markdown("---")
        
    st.title("📌 Main Menu")
    st.info("Daily To-Do List is active. ✅")
    st.markdown("---")
    st.caption("© 2026 Pro Dashboard")

# ==========================================
# 5. Main Page Content
# ==========================================

header_col1, header_col2 = st.columns([5, 1])
with header_col1:
    current_streak = st.session_state.streak_data.get("streak", 0)
    streak_html = f"<span class='streak-badge'>🔥 {current_streak} Days Streak</span>" if current_streak > 0 else ""
    st.markdown(f"<h1>✅ Daily To-Do List {streak_html}</h1>", unsafe_allow_html=True)
    st.markdown("Stay on top of your daily tasks, progress, and notes.")
with header_col2:
    if os.path.exists("Logo.png"): st.image("Logo.png", use_container_width=True)
st.divider()

# نموذج إضافة مهمة جديدة مع التاريخ المحدث 🆕
with st.form("add_todo_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([3, 1.2, 0.8]) # تم تقسيم السطر لثلاثة أعمدة ليتسع التاريخ
    with col1: 
        new_task = st.text_input("➕ Add a new task...", placeholder="Add your Task")
    with col2:
        task_date = st.date_input("📅 Due Date", datetime.date.today()) # خانة اختيار التاريخ 🆕
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Add Task", use_container_width=True)
        
    if submitted and new_task.strip():
        import time
        st.session_state.todos.append({
            "task": new_task.strip(), 
            "completed": False, 
            "progress": 0, 
            "notes": "", 
            "date": task_date.isoformat(), # حفظ التاريخ بصيغة نصية YYYY-MM-DD 🆕
            "id": str(time.time())
        })
        
        # فرز القائمة مباشرة بعد الإضافة لضمان الترتيب الصحيح ومنع التداخل 🆕
        try:
            st.session_state.todos.sort(key=lambda x: x.get('date', ''))
        except:
            pass
            
        st.session_state.celebrated = False 
        flag_for_save()
        st.rerun()

st.divider()

# --- قسم الإحصائيات ونظام الشعلة ---
if st.session_state.todos:
    completed_count = sum(1 for task in st.session_state.todos if task['completed'])
    pending_count = len(st.session_state.todos) - completed_count
    total_count = len(st.session_state.todos)
    
    progress = completed_count / total_count if total_count > 0 else 0

    today_str = datetime.date.today().isoformat()
    yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    
    if progress == 1.0 and total_count > 0:
        last_date = st.session_state.streak_data.get("last_date", "")
        streak = st.session_state.streak_data.get("streak", 0)
        
        if last_date != today_str:
            if last_date == yesterday_str:
                streak += 1
            else:
                streak = 1
                
            st.session_state.streak_data["streak"] = streak
            st.session_state.streak_data["last_date"] = today_str
            flag_for_save()
            
        if not st.session_state.celebrated:
            st.balloons()
            st.session_state.celebrated = True
    elif progress < 1.0:
        st.session_state.celebrated = False

    df_pie = pd.DataFrame({
        "Status": ["Completed ✅", "Pending ⏳"],
        "Tasks": [completed_count, pending_count]
    })

    fig = px.pie(
        df_pie, values='Tasks', names='Status', hole=0.5,
        color='Status', color_discrete_map={"Completed ✅": "#10b981", "Pending ⏳": "#475569"}
    )
    
    fig.update_layout(
        margin=dict(t=10, b=10, l=0, r=0), height=220,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc", size=14), showlegend=True
    )

    chart_col, progress_col = st.columns([1, 2])
    with chart_col: st.plotly_chart(fig, use_container_width=True)
    with progress_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.progress(progress, text=f"Task Completion: {completed_count}/{total_count} ({int(progress * 100)}%)")
        
else:
    st.info("Your task list is empty. Add a new task above to get started!")

st.markdown("<br>", unsafe_allow_html=True)

# --- قسم قائمة المهام المنظم حسب التاريخ ---
if st.session_state.todos:
    for index, task in enumerate(st.session_state.todos): 
        col_check, col_text, col_del = st.columns([0.5, 4, 0.5])
        
        with col_check:
            st.checkbox(
                "", 
                value=task['completed'], 
                key=f"check_{task['id']}", 
                on_change=toggle_task, 
                args=(index, f"check_{task['id']}")
            )
                
        with col_text:
            if task['completed']: 
                st.markdown(f"<p class='completed-task'><b>{task['task']}</b></p>", unsafe_allow_html=True)
            else: 
                st.markdown(f"<p><b>{task['task']}</b></p>", unsafe_allow_html=True)
            # عرض تاريخ الاستحقاق بشكل واضح وأنيق أسفل المهمة 🆕
            st.caption(f"📅 Due Date: {task.get('date', '')}")
                
        with col_del:
            st.button(
                "❌", 
                key=f"del_{task['id']}", 
                help="Delete Task", 
                on_click=delete_task, 
                args=(task['id'],)
            )
        
        # القائمة المنسدلة للنسبة والملاحظات لكل مهمة
        with st.expander(f"📊 Progress: {task.get('progress', 0)}% | 📝 Notes"):
            col_prog, col_notes = st.columns([1, 1.5])
            
            with col_prog:
                st.slider(
                    "Completion %", 
                    0, 100, 
                    task.get('progress', 0), 
                    step=10, 
                    key=f"prog_{task['id']}",
                    on_change=update_progress,
                    args=(index, f"prog_{task['id']}")
                )
            
            with col_notes:
                st.text_area(
                    "Task Notes", 
                    task.get('notes', ''), 
                    height=68, 
                    placeholder="Add your notes here...", 
                    key=f"note_{task['id']}",
                    on_change=update_notes,
                    args=(index, f"note_{task['id']}")
                )

    if any(task['completed'] for task in st.session_state.todos):
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("🧹 Clear Completed Tasks", on_click=clear_completed)

# ==========================================
# 6. التنفيذ النهائي للحفظ
# ==========================================
if st.session_state.get("needs_save", False):
    cookies.save()
    st.session_state.needs_save = False
