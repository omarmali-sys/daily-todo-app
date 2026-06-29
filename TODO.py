import streamlit as st
import os
import time
import json
import datetime
import pandas as pd
import plotly.express as px
import extra_streamlit_components as stx

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
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# 3. Smart Cookies & Session State Setup
cookie_manager = stx.CookieManager()

# تهيئة الذاكرة السريعة
if "todos" not in st.session_state:
    st.session_state.todos = []
    st.session_state.data_loaded = False

# تحميل البيانات من المتصفح مرة واحدة فقط عند بداية الجلسة
if not st.session_state.data_loaded:
    saved_todos = cookie_manager.get(cookie="local_todos")
    if saved_todos is not None:
        if isinstance(saved_todos, str):
            try:
                st.session_state.todos = json.loads(saved_todos)
            except:
                st.session_state.todos = []
        else:
            st.session_state.todos = saved_todos
        st.session_state.data_loaded = True
    elif cookie_manager.get_all() is not None:
        st.session_state.data_loaded = True

# دالة الحفظ الصامتة (تحفظ في المتصفح في الخلفية)
def save_tasks():
    expire_date = datetime.datetime.now() + datetime.timedelta(days=3650)
    cookie_manager.set("local_todos", json.dumps(st.session_state.todos), expires_at=expire_date)

# ==========================================
# 4. Main Page Content
# ==========================================

header_col1, header_col2 = st.columns([5, 1])
with header_col1:
    st.title("✅ Daily To-Do List")
    st.markdown("Stay on top of your daily tasks and priorities.")
with header_col2:
    if os.path.exists("Logo.png"): st.image("Logo.png", use_container_width=True)
st.divider()

# --- نموذج إضافة مهمة ---
with st.form("add_todo_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    with col1: new_task = st.text_input("➕ Add a new task...", placeholder="e.g., Review weekly BI report")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Add Task", use_container_width=True)
        
    if submitted and new_task.strip():
        # إضافة المهمة للذاكرة السريعة أولاً
        st.session_state.todos.append({"task": new_task.strip(), "completed": False, "id": str(time.time())})
        # ثم إرسال نسخة للمتصفح للحفظ
        save_tasks()

st.divider()

# --- قسم الإحصائيات ---
if st.session_state.todos:
    completed_count = sum(1 for task in st.session_state.todos if task['completed'])
    pending_count = len(st.session_state.todos) - completed_count
    total_count = len(st.session_state.todos)
    
    progress = completed_count / total_count if total_count > 0 else 0

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

# --- قسم قائمة المهام ---
if st.session_state.todos:
    for index, task in enumerate(list(st.session_state.todos)): 
        col_check, col_text, col_del = st.columns([0.5, 4, 0.5])
        with col_check:
            is_checked = st.checkbox("", value=task['completed'], key=f"check_{task['id']}")
            if is_checked != task['completed']:
                st.session_state.todos[index]['completed'] = is_checked
                save_tasks()
                time.sleep(0.2)
                st.rerun()
        with col_text:
            if task['completed']: 
                st.markdown(f"<p class='completed-task'>{task['task']}</p>", unsafe_allow_html=True)
            else: 
                st.markdown(f"<p>{task['task']}</p>", unsafe_allow_html=True)
        with col_del:
            if st.button("❌", key=f"del_{task['id']}", help="Delete Task"):
                st.session_state.todos.pop(index)
                save_tasks()
                time.sleep(0.2)
                st.rerun()
                
    if any(task['completed'] for task in st.session_state.todos):
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧹 Clear Completed Tasks"):
            st.session_state.todos = [task for task in st.session_state.todos if not task['completed']]
            save_tasks()
            time.sleep(0.2)
            st.rerun()
