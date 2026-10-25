
import streamlit as st
import pandas as pd
from modules.database import get_connection, initialize_database


def render_cost_estimation():
    initialize_database()

    st.subheader("💰 Construction Cost Estimator")
    st.write("Estimate and permanently save construction expenses.")

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT id, item_name, material_cost, labour_cost,
                   equipment_cost, contingency, total_cost
            FROM cost_items
            ORDER BY id
        """).fetchall()

    with st.form("cost_estimation_form", clear_on_submit=True):
        item_name = st.text_input("Task or Item Name")

        col1, col2 = st.columns(2)
        with col1:
            material = st.number_input(
                "Material Cost (₹)", min_value=0.0, step=1000.0
            )
            labour = st.number_input(
                "Labour Cost (₹)", min_value=0.0, step=500.0
            )
        with col2:
            equipment = st.number_input(
                "Equipment Cost (₹)", min_value=0.0, step=500.0
            )
            contingency_percent = st.number_input(
                "Contingency (%)", min_value=0.0,
                max_value=100.0, value=10.0
            )

        submitted = st.form_submit_button("Save Cost Item")

    if submitted:
        if not item_name.strip():
            st.error("Please enter an item name.")
        else:
            base_cost = material + labour + equipment
            contingency = base_cost * contingency_percent / 100
            total = base_cost + contingency

            with get_connection() as conn:
                conn.execute("""
                    INSERT INTO cost_items
                    (item_name, material_cost, labour_cost,
                     equipment_cost, contingency, total_cost)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    item_name.strip(), material, labour,
                    equipment, contingency, total
                ))

            st.success("Cost item saved permanently!")
            st.rerun()

    st.divider()
    st.subheader("📊 Saved Cost Items")

    if not rows:
        st.info("Add a cost item to get started.")
        return

    df = pd.DataFrame(rows, columns=[
        "ID", "Item", "Materials (₹)", "Labour (₹)",
        "Equipment (₹)", "Contingency (₹)", "Total (₹)"
    ])

    st.dataframe(df.drop(columns=["ID"]), use_container_width=True)

    st.metric("Estimated Total Project Cost", f"₹{df['Total (₹)'].sum():,.2f}")

    chart = pd.DataFrame({
        "Category": ["Materials", "Labour", "Equipment", "Contingency"],
        "Cost": [
            df["Materials (₹)"].sum(),
            df["Labour (₹)"].sum(),
            df["Equipment (₹)"].sum(),
            df["Contingency (₹)"].sum()
        ]
    })

    st.subheader("Cost Distribution")
    st.bar_chart(chart.set_index("Category"))

    item_to_delete = st.selectbox(
        "Select item to delete",
        options=df["ID"].tolist(),
        format_func=lambda item_id: df.loc[
            df["ID"] == item_id, "Item"
        ].iloc[0]
    )

    if st.button("Delete Selected Item"):
        with get_connection() as conn:
            conn.execute(
                "DELETE FROM cost_items WHERE id = ?",
                (item_to_delete,)
            )
        st.rerun()
