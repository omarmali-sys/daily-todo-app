import streamlit as st
import os
import time
import pandas as pd
import plotly.express as px

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

# 3. Session State for Local/Private Tasks
if 'todos' not in st.session_state:
    st.session_state.todos = []

# ==========================================
# 4. UI Navigation & Layout
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
    st.title("✅ Daily To-Do List")
    st.markdown("Stay on top of your daily tasks and priorities.")
with header_col2:
    if os.path.exists("Logo.png"): st.image("Logo.png", use_container_width=True)
st.divider()

# Load tasks from current user's session
todos = st.session_state.todos

if todos:
    completed_count = sum(1 for task in todos if task['completed'])
    pending_count = len(todos) - completed_count
    total_count = len(todos)
    
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
    st.info("Your task list is empty. Add a new task below to get started!")

st.markdown("<br>", unsafe_allow_html=True)

with st.form("add_todo_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    with col1: new_task = st.text_input("➕ Add a new task...", placeholder="e.g., Review weekly BI report")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Add Task", use_container_width=True)
        
    if submitted and new_task.strip():
        st.session_state.todos.append({"task": new_task.strip(), "completed": False, "id": str(time.time())})
        st.rerun()

st.divider()

if todos:
    for index, task in enumerate(todos):
        col_check, col_text, col_del = st.columns([0.5, 4, 0.5])
        with col_check:
            is_checked = st.checkbox("", value=task['completed'], key=f"check_{task['id']}")
            if is_checked != task['completed']:
                st.session_state.todos[index]['completed'] = is_checked
                st.rerun()
        with col_text:
            if task['completed']: 
                st.markdown(f"<p class='completed-task'>{task['task']}</p>", unsafe_allow_html=True)
            else: 
                st.markdown(f"<p>{task['task']}</p>", unsafe_allow_html=True)
        with col_del:
            if st.button("❌", key=f"del_{task['id']}", help="Delete Task"):
                st.session_state.todos.pop(index)
                st.rerun()
                
    if any(task['completed'] for task in todos):
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧹 Clear Completed Tasks"):
            st.session_state.todos = [task for task in todos if not task['completed']]
            st.rerun()
