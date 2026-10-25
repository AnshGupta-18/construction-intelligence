
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from modules.database import get_connection, initialize_database


def load_tasks():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, name, duration, priority, start_date, status,
                   predecessor
            FROM tasks
            ORDER BY id
        """).fetchall()

    return [
        {
            "ID": row[0],
            "Task": row[1],
            "Duration (days)": row[2],
            "Priority": row[3],
            "Start Date": date.fromisoformat(row[4]),
            "Status": row[5],
            "Depends on": row[6]
        }
        for row in rows
    ]


def save_task(task):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO tasks
            (name, duration, priority, start_date, status, predecessor)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            task["Task"],
            task["Duration (days)"],
            task["Priority"],
            task["Start Date"].isoformat(),
            task["Status"],
            task["Depends on"]
        ))


def render_project_planning():
    initialize_database()

    st.subheader("📅 Construction Project Planning")
    st.write(
        "Plan construction tasks, manage dependencies, "
        "track progress, and visualize the project timeline."
    )

    tasks = load_tasks()
    task_names = [task["Task"] for task in tasks]

    st.subheader("Add Construction Task")

    with st.form("add_construction_task"):
        task_name = st.text_input(
            "Task Name", placeholder="e.g., Foundation Work"
        )

        col1, col2 = st.columns(2)

        with col1:
            duration = st.number_input(
                "Duration (days)", min_value=1,
                max_value=365, value=7
            )

        with col2:
            priority = st.selectbox(
                "Priority", ["High", "Medium", "Low"]
            )

        start_date = st.date_input(
            "Project Start Date", value=date.today()
        )

        predecessor = st.selectbox(
            "Depends on", ["None"] + task_names
        )

        submitted = st.form_submit_button("Add Task")

    if submitted:
        name = task_name.strip()

        if not name:
            st.error("Please enter a task name.")
        elif name in task_names:
            st.error("A task with this name already exists.")
        else:
            save_task({
                "Task": name,
                "Duration (days)": int(duration),
                "Priority": priority,
                "Start Date": start_date,
                "Status": "Not Started",
                "Depends on": (
                    None if predecessor == "None" else predecessor
                )
            })
            st.success("Task saved to database!")
            st.rerun()

    if not tasks:
        st.info("Add your first construction task to begin.")
        return

    task_map = {task["Task"]: task for task in tasks}
    calculated = {}
    visiting = set()

    def calculate_schedule(name):
        if name in calculated:
            return calculated[name]

        if name in visiting:
            raise ValueError("Circular dependency detected.")

        visiting.add(name)
        task = task_map[name]
        predecessor_name = task["Depends on"]

        if predecessor_name:
            if predecessor_name not in task_map:
                raise ValueError(
                    f"Predecessor '{predecessor_name}' was not found."
                )
            previous = calculate_schedule(predecessor_name)
            task_start = previous["End Date"] + timedelta(days=1)
        else:
            task_start = task["Start Date"]

        task_end = task_start + timedelta(
            days=task["Duration (days)"] - 1
        )

        visiting.remove(name)
        calculated[name] = {
            "Start Date": task_start,
            "End Date": task_end
        }
        return calculated[name]

    try:
        for task in tasks:
            schedule = calculate_schedule(task["Task"])
            task.update(schedule)
    except ValueError as error:
        st.error(str(error))
        return

    st.divider()
    st.subheader("Update Task Status")

    selected_task = st.selectbox(
        "Select task", task_names, key="status_task_select"
    )
    selected = task_map[selected_task]

    statuses = ["Not Started", "In Progress", "Completed"]
    new_status = st.selectbox(
        "New status",
        statuses,
        index=statuses.index(selected["Status"]),
        key="status_value"
    )

    if st.button("Update Status"):
        predecessor_name = selected["Depends on"]
        predecessor_task = task_map.get(predecessor_name)

        if (
            new_status == "Completed"
            and predecessor_task
            and predecessor_task["Status"] != "Completed"
        ):
            st.error(
                f"Complete '{predecessor_name}' first."
            )
        else:
            with get_connection() as conn:
                conn.execute(
                    "UPDATE tasks SET status = ? WHERE id = ?",
                    (new_status, selected["ID"])
                )
            st.success("Task status saved.")
            st.rerun()

    st.divider()
    st.subheader("📋 Construction Schedule")

    df = pd.DataFrame(tasks)
    st.dataframe(
        df.drop(columns=["ID"]),
        use_container_width=True,
        hide_index=True
    )

    total_tasks = len(tasks)
    completed = sum(t["Status"] == "Completed" for t in tasks)
    in_progress = sum(t["Status"] == "In Progress" for t in tasks)
    total_days = sum(t["Duration (days)"] for t in tasks)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Tasks", total_tasks)
    col2.metric("Completed", completed)
    col3.metric("In Progress", in_progress)
    col4.metric("Total Task-Days", total_days)

    progress = completed / total_tasks
    st.subheader("Overall Project Progress")
    st.progress(progress)
    st.write(f"{progress * 100:.1f}% of tasks completed.")

    latest_finish = max(t["End Date"] for t in tasks)
    st.metric(
        "Estimated Project Finish",
        latest_finish.strftime("%d %b %Y")
    )

    st.divider()
    st.subheader("📊 Project Gantt Chart")

    chart_df = pd.DataFrame([
        {
            "Task": t["Task"],
            "Start": t["Start Date"],
            "Finish": t["End Date"] + timedelta(days=1),
            "Status": t["Status"],
            "Priority": t["Priority"],
            "Depends on": t["Depends on"] or "None"
        }
        for t in tasks
    ])

    fig = px.timeline(
        chart_df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Status",
        hover_data=["Priority", "Depends on"],
        title="Construction Task Timeline"
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Manage Tasks")

    task_to_remove = st.selectbox(
        "Select task to remove",
        task_names,
        key="remove_task_select"
    )

    if st.button("Remove Selected Task"):
        task_id = task_map[task_to_remove]["ID"]

        with get_connection() as conn:
            conn.execute(
                "DELETE FROM tasks WHERE id = ?", (task_id,)
            )
            conn.execute(
                "UPDATE tasks SET predecessor = NULL "
                "WHERE predecessor = ?",
                (task_to_remove,)
            )

        st.success("Task deleted.")
        st.rerun()
