import streamlit as st
import os
import json
import datetime
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
    margin-bottom: 5px;
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
div[role="radiogroup"] {
    justify-content: center;
    background-color: rgba(255,255,255,0.05);
    padding: 10px;
    border-radius: 10px;
}
/* تنسيق رؤوس الجدول */
.table-header {
    font-weight: bold;
    color: #94a3b8 !important;
    font-size: 0.95rem;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 15px;
}

/* محاذاة دقيقة وموحدة (Flexbox Alignment) */
div[data-testid="stCheckbox"] {
    display: flex;
    align-items: center;
    height: 40px;
}
/* توحيد ارتفاع الأزرار وصناديق النصوص لتتساوى مع النصوص */
div[data-testid="stTextInput"] > div, div[data-testid="stButton"] button {
    height: 40px !important;
    min-height: 40px !important;
}

/* 🆕 تعديل خلفية حقول النصوص (الملاحظات) لتكون شفافة وأنيقة وتلغي اللون الرمادي */
div[data-baseweb="input"] {
    background-color: rgba(0, 0, 0, 0.2) !important; /* لون أسود شفاف يندمج مع الخلفية */
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 6px !important;
}
div[data-baseweb="input"]:hover {
    border-color: rgba(255, 255, 255, 0.3) !important;
}
div[data-baseweb="input"]:focus-within {
    border-color: #38bdf8 !important; /* إضاءة زرقاء عند الكتابة */
}
input::placeholder {
    color: #64748b !important; /* لون هادئ للنص الإرشادي */
}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 3. Robust Cookies Manager Setup
cookies = EncryptedCookieManager(prefix="todo/", password="secure_todo_app_password_2026")

if not cookies.ready():
    st.info("جاري مزامنة المهام مع المتصفح... 🔄")
    st.stop()

# تهيئة الذاكرة السريعة
if "todos" not in st.session_state:
    st.session_state.todos = []
    st.session_state.needs_save = False
    
    saved_todos = cookies.get("local_todos")
    if saved_todos:
        try:
            st.session_state.todos = json.loads(saved_todos)
        except:
            st.session_state.todos = []
            
        for t in st.session_state.todos:
            if 'progress' not in t: t['progress'] = 100 if t.get('completed') else 0
            if 'notes' not in t: t['notes'] = ""
            if 'date' not in t: t['date'] = datetime.date.today().isoformat()
            
        try:
            st.session_state.todos.sort(key=lambda x: x.get('date', ''))
        except:
            pass

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

def get_task_index(task_id):
    return next((i for i, t in enumerate(st.session_state.todos) if t['id'] == task_id), -1)

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

# نموذج إضافة مهمة جديدة
with st.form("add_todo_form", clear_on_submit=True):
    col1, col2, col3 = st.columns([3, 1.2, 0.8])
    with col1: 
        new_task = st.text_input("➕ Add a new task...", placeholder="Add your Task")
    with col2:
        task_date = st.date_input("📅 Due Date", datetime.date.today())
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
            "date": task_date.isoformat(),
            "id": str(time.time())
        })
        try:
            st.session_state.todos.sort(key=lambda x: x.get('date', ''))
        except:
            pass
        st.session_state.celebrated = False 
        st.session_state.needs_save = True
        st.rerun()

st.divider()

# --- قسم الإحصائيات والشارت ---
if st.session_state.todos:
    total_count = len(st.session_state.todos)
    total_possible_progress = total_count * 100 

    completed_val = sum(task.get('progress', 0) for task in st.session_state.todos)
    pending_val = total_possible_progress - completed_val
    
    overall_progress = completed_val / total_possible_progress if total_possible_progress > 0 else 0

    today_str = datetime.date.today().isoformat()
    yesterday_str = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    
    if overall_progress == 1.0 and total_count > 0:
        last_date = st.session_state.streak_data.get("last_date", "")
        streak = st.session_state.streak_data.get("streak", 0)
        
        if last_date != today_str:
            if last_date == yesterday_str:
                streak += 1
            else:
                streak = 1
                
            st.session_state.streak_data["streak"] = streak
            st.session_state.streak_data["last_date"] = today_str
            st.session_state.needs_save = True
            
        if not st.session_state.celebrated:
            st.balloons()
            st.session_state.celebrated = True
    elif overall_progress < 1.0:
        st.session_state.celebrated = False

    df_pie = pd.DataFrame({
        "Status": ["Completed ✅", "Pending ⏳"],
        "Value": [completed_val, pending_val]
    })

    color_map = {
        "Completed ✅": "#10b981",
        "Pending ⏳": "#475569"
    }

    fig = px.pie(
        df_pie, values='Value', names='Status', hole=0.5,
        color='Status', color_discrete_map=color_map
    )
    
    fig.update_traces(hovertemplate='<b>%{label}</b><br>Ratio: %{percent}<extra></extra>')
    
    fig.update_layout(
        margin=dict(t=10, b=10, l=0, r=0), height=220,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc", size=14), showlegend=True
    )

    chart_col, progress_col = st.columns([1, 2])
    with chart_col: st.plotly_chart(fig, use_container_width=True)
    with progress_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.progress(overall_progress, text=f"Overall Total Progress: {int(overall_progress * 100)}%")
        
else:
    st.info("Your task list is empty. Add a new task above to get started!")

st.markdown("<br>", unsafe_allow_html=True)

# --- قسم الفلترة وقائمة المهام المنظمة ذات الـ 6 أعمدة ---
if st.session_state.todos:
    filter_option = st.radio(
        "🔍 Filter Tasks by Date:", 
        ["All Tasks 📋", "Today 📅", "Overdue ⚠️", "Upcoming ⏭️", "Custom Date 📆"], 
        horizontal=True
    )
    
    custom_filter_date_str = None
    if filter_option == "Custom Date 📆":
        f_col1, f_col2 = st.columns([1.5, 4])
        with f_col1:
            custom_filter_date = st.date_input("🗓️ Select Date:", datetime.date.today())
            custom_filter_date_str = custom_filter_date.isoformat()
            
    filtered_todos = []
    current_date_str = datetime.date.today().isoformat()
    
    for task in st.session_state.todos:
        t_date = task.get('date', '')
        if filter_option == "All Tasks 📋":
            filtered_todos.append(task)
        elif filter_option == "Today 📅" and t_date == current_date_str:
            filtered_todos.append(task)
        elif filter_option == "Overdue ⚠️" and t_date < current_date_str and not task.get('completed'):
            filtered_todos.append(task)
        elif filter_option == "Upcoming ⏭️" and t_date > current_date_str:
            filtered_todos.append(task)
        elif filter_option == "Custom Date 📆" and t_date == custom_filter_date_str:
            filtered_todos.append(task)

    st.markdown("<br>", unsafe_allow_html=True)

    if not filtered_todos:
        st.info(f"No tasks found for: {filter_option}")
    else:
        # عناوين الجدول
        st.markdown("<div class='table-header'>", unsafe_allow_html=True)
        h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns([0.4, 2.5, 2.5, 1.3, 1.5, 0.5])
        with h_col1: st.markdown("Status")
        with h_col2: st.markdown("Task Name")
        with h_col3: st.markdown("Notes")
        with h_col4: st.markdown("Due Date")
        with h_col5: st.markdown("Details")
        with h_col6: st.markdown("Action")
        st.markdown("</div>", unsafe_allow_html=True)

        for task in filtered_todos: 
            t_id = task['id']
            idx = get_task_index(t_id)
            
            chk_key = f"chk_{t_id}_{task.get('progress', 0)}"
            prog_key = f"prog_{t_id}_{task.get('completed', False)}"
            
            # توزيع الأعمدة بشكل أنيق
            col_check, col_text, col_notes, col_date, col_exp, col_del = st.columns([0.4, 2.5, 2.5, 1.3, 1.5, 0.5])
            
            with col_check:
                chk_val = st.checkbox("", value=task['completed'], key=chk_key)
                if chk_val != task['completed']:
                    st.session_state.todos[idx]['completed'] = chk_val
                    st.session_state.todos[idx]['progress'] = 100 if chk_val else 0
                    st.session_state.needs_save = True
                    st.rerun()
                    
            with col_text:
                text_style = "text-decoration: line-through; color: #94a3b8;" if task['completed'] else ""
                text_html = f"<div style='display: flex; align-items: center; height: 40px;'><span style='{text_style}'><b>{task['task']}</b></span></div>"
                st.markdown(text_html, unsafe_allow_html=True)
                
            with col_notes:
                notes_val = st.text_input(
                    "Notes", 
                    value=task.get('notes', ''), 
                    placeholder="📝 Add notes...", 
                    key=f"note_{t_id}", 
                    label_visibility="collapsed"
                )
                if notes_val != task.get('notes', ''):
                    st.session_state.todos[idx]['notes'] = notes_val
                    st.session_state.needs_save = True
                    st.rerun()
                
            with col_date:
                t_date = task.get('date', '')
                if t_date < current_date_str and not task['completed']:
                    date_html = f"<span style='color: #ef4444; font-size: 0.9rem;'>⚠️ {t_date}</span>"
                elif t_date == current_date_str:
                    date_html = f"<span style='color: #fbbf24; font-size: 0.9rem;'>📅 Today</span>"
                else:
                    date_html = f"<span style='color: #94a3b8; font-size: 0.9rem;'>📅 {t_date}</span>"
                st.markdown(f"<div style='display: flex; align-items: center; height: 40px;'>{date_html}</div>", unsafe_allow_html=True)
            
            with col_exp:
                with st.expander(f"📊 {task.get('progress', 0)}% | ✏️ Edit"):
                    title_val = st.text_input("Name:", value=task['task'], key=f"edit_{t_id}")
                    if title_val != task['task']:
                        st.session_state.todos[idx]['task'] = title_val
                        st.session_state.needs_save = True
                        st.rerun()
                    
                    parsed_date = datetime.date.fromisoformat(task.get('date', current_date_str))
                    new_date_val = st.date_input("Due Date:", value=parsed_date, key=f"edit_date_{t_id}")
                    if new_date_val.isoformat() != task.get('date', ''):
                        st.session_state.todos[idx]['date'] = new_date_val.isoformat()
                        try:
                            st.session_state.todos.sort(key=lambda x: x.get('date', ''))
                        except:
                            pass
                        st.session_state.needs_save = True
                        st.rerun()
                    
                    sl_val = st.slider("Progress %", 0, 100, value=task.get('progress', 0), step=10, key=prog_key)
                    if sl_val != task.get('progress', 0):
                        st.session_state.todos[idx]['progress'] = sl_val
                        if sl_val == 100:
                            st.session_state.todos[idx]['completed'] = True
                        elif sl_val < 100 and st.session_state.todos[idx]['completed']:
                            st.session_state.todos[idx]['completed'] = False
                        st.session_state.needs_save = True
                        st.rerun()

            with col_del:
                if st.button("❌", key=f"del_{t_id}"):
                    st.session_state.todos.pop(idx)
                    st.session_state.needs_save = True
                    st.rerun()

    if any(task['completed'] for task in st.session_state.todos):
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧹 Clear All Completed Tasks"):
            st.session_state.todos = [t for t in st.session_state.todos if not t['completed']]
            st.session_state.needs_save = True
            st.rerun()

# ==========================================
# 6. التنفيذ النهائي للحفظ
# ==========================================
if st.session_state.get("needs_save", False):
    cookies["local_todos"] = json.dumps(st.session_state.todos)
    cookies["todo_streaks"] = json.dumps(st.session_state.streak_data)
    cookies.save()
    st.session_state.needs_save = False
