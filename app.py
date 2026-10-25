
import streamlit as st

from modules.site_analysis import render_site_analysis
from modules.project_planning import render_project_planning
from modules.ai_assistant import render_ai_assistant
from modules.cost_estimation import render_cost_estimation
from modules.pdf_reports import render_pdf_reports


# Page configuration
st.set_page_config(
    page_title="Construction Intelligence Platform",
    page_icon="🏗️",
    layout="wide"
)


# Header
st.title("🏗️ AI-Powered Construction Intelligence Platform")

st.markdown(
    """
    Manage construction projects with tools for site analysis,
    task scheduling, AI assistance, cost estimation, and PDF reports.
    """
)

st.divider()


# Application tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📷 Site Analysis",
    "📅 Project Planning",
    "🤖 AI Assistant",
    "💰 Cost Estimation",
    "📄 PDF Reports"
])


with tab1:
    render_site_analysis()


with tab2:
    render_project_planning()


with tab3:
    render_ai_assistant()


with tab4:
    render_cost_estimation()


with tab5:
    render_pdf_reports()


# Footer
st.divider()

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    h1 {
        font-weight: 750;
        letter-spacing: -1px;
    }

    div[data-testid="stMetric"] {
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 16px;
        border-radius: 12px;
    }

    div[data-testid="stTabs"] button {
        font-weight: 600;
    }

    div[data-testid="stButton"] button,
    div[data-testid="stDownloadButton"] button {
        border-radius: 8px;
        font-weight: 600;
    }

    div[data-testid="stFileUploader"] {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)
