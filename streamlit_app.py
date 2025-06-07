import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from ec2_sql_sizing import EC2DatabaseSizingCalculator

st.set_page_config(page_title="AWS EC2 SQL Sizing", layout="wide")
st.title("AWS EC2 SQL Server Sizing Calculator")

# Sidebar Inputs
st.sidebar.header("Input Parameters")

inputs = {
    "on_prem_cores": st.sidebar.number_input("On-Prem CPU Cores", min_value=1, value=16),
    "peak_cpu_percent": st.sidebar.slider("Peak CPU Utilization (%)", 0, 100, 65),
    "on_prem_ram_gb": st.sidebar.number_input("On-Prem RAM (GB)", min_value=1, value=64),
    "peak_ram_percent": st.sidebar.slider("Peak RAM Utilization (%)", 0, 100, 75),
    "storage_current_gb": st.sidebar.number_input("Current DB Storage (GB)", min_value=1, value=500),
    "storage_growth_rate": st.sidebar.number_input("Annual Storage Growth Rate (e.g., 0.15)", min_value=0.0, max_value=1.0, value=0.15),
    "peak_iops": st.sidebar.number_input("Peak IOPS", min_value=1, value=8000),
    "peak_throughput_mbps": st.sidebar.number_input("Peak Throughput (MB/s)", min_value=1, value=400),
    "years": st.sidebar.slider("Growth Projection (Years)", 1, 10, 3),
    "workload_profile": st.sidebar.selectbox("Workload Profile", ["general", "memory", "compute"]),
    "prefer_amd": st.sidebar.checkbox("Prefer AMD Instances (Cost Optimized)", value=True)
}

calculator = EC2DatabaseSizingCalculator()
calculator.inputs.update(inputs)

# Main app
if st.button("Generate Recommendations"):
    results = calculator.generate_all_recommendations()
    df = pd.DataFrame.from_dict(results, orient='index')

    st.success("EC2 Recommendations:")
    st.dataframe(df, use_container_width=True)

    # CSV export
    csv = df.to_csv(index=True).encode('utf-8')
    st.download_button("Download CSV", csv, "ec2_sizing.csv", "text/csv")

    # DOCX export
    doc = Document()
    doc.add_heading('EC2 Sizing Recommendations', 0)
    for env, rec in results.items():
        doc.add_heading(f'{env} Environment', level=1)
        for key, val in rec.items():
            doc.add_paragraph(f"{key}: {val}")
    doc_io = BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    st.download_button("Download DOCX", doc_io, "ec2_sizing.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    # Optimization Tip
    if any("AMD" in r['processor'] for r in results.values()):
        st.info("💡 Tip: AMD-based instances (m6a, r6a, c6a) are selected for cost savings (typically 10–20% cheaper than Intel equivalents).")
