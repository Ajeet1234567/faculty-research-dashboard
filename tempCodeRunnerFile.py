"""
CUSB CS Faculty Research Publication Analyzer
Main Streamlit Application
"""
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from io import BytesIO

# Import local modules
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    APP_TITLE, APP_ICON, INSTITUTION_NAME, DEPARTMENT_NAME,
    FACULTY_FILE, PUBLICATIONS_FILE, CACHE_FILE, EXPORTS_DIR,
    DATA_DIR
)
from modules.faculty_manager import FacultyManager
from modules.scholar_fetcher import ScholarFetcher, create_demo_data, SCHOLARLY_AVAILABLE
from modules.analytics import Analytics
from modules.visualizer import Visualizer

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Hide Streamlit deploy button only, keep sidebar toggle visible */
    .stDeployButton {
        display: none !important;
    }
    #MainMenu {
        visibility: hidden;
    }
    footer {
        visibility: hidden;
    }
    .stAppDeployButton {
        display: none !important;
    }
    /* Hide only the deploy button in toolbar, not the entire toolbar */
    [data-testid="stToolbar"] button[kind="header"] {
        display: none !important;
    }
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 5px;
    }
    .faculty-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: #f9f9f9;
    }
    .highlight-box {
        background: #e7f3ff;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 5px 5px 0;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    if 'faculty_manager' not in st.session_state:
        st.session_state.faculty_manager = FacultyManager(FACULTY_FILE)
    
    if 'scholar_fetcher' not in st.session_state:
        st.session_state.scholar_fetcher = ScholarFetcher(CACHE_FILE)
    
    if 'scholar_data' not in st.session_state:
        # Load cached data or use demo data
        if os.path.exists(PUBLICATIONS_FILE):
            try:
                with open(PUBLICATIONS_FILE, 'r', encoding='utf-8') as f:
                    st.session_state.scholar_data = json.load(f)
            except:
                st.session_state.scholar_data = create_demo_data()
        else:
            st.session_state.scholar_data = create_demo_data()
    
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = True


def save_scholar_data():
    """Save scholar data to file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PUBLICATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(st.session_state.scholar_data, f, indent=2, ensure_ascii=False)


def get_analytics():
    """Get analytics instance with current data."""
    return Analytics(
        st.session_state.scholar_data,
        st.session_state.faculty_manager.get_all_faculty()
    )


def get_visualizer():
    """Get visualizer instance."""
    return Visualizer(get_analytics())


# ==================== Page Components ====================

def render_header():
    """Render the main header."""
    st.markdown(f'<h1 class="main-header">{APP_ICON} {APP_TITLE}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{DEPARTMENT_NAME} | {INSTITUTION_NAME}</p>', unsafe_allow_html=True)


def render_metrics_row():
    """Render the key metrics row."""
    analytics = get_analytics()
    summary = analytics.get_department_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Faculty",
            value=summary["total_faculty"]
        )
    
    with col2:
        st.metric(
            label="Total Publications",
            value=f"{summary['total_publications']:,}"
        )
    
    with col3:
        st.metric(
            label="Total Citations",
            value=f"{summary['total_citations']:,}"
        )
    
    with col4:
        st.metric(
            label="Avg H-Index",
            value=summary["avg_h_index"]
        )


def render_dashboard():
    """Render the main dashboard."""
    st.header("Dashboard Overview")
    
    render_metrics_row()
    
    st.divider()
    
    analytics = get_analytics()
    viz = get_visualizer()
    
    # Two column layout for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Publications by Faculty")
        fig = viz.publications_by_faculty_chart()
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Publication Trend")
        fig = viz.publications_trend_chart()
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Citations by Faculty")
        fig = viz.citations_by_faculty_chart()
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Citation Trend")
        fig = viz.citations_trend_chart()
        st.plotly_chart(fig, use_container_width=True)
    
    # Full width charts
    st.subheader("Research Areas Distribution")
    col1, col2 = st.columns(2)
    with col1:
        fig = viz.research_area_pie_chart()
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = viz.h_index_comparison_chart()
        st.plotly_chart(fig, use_container_width=True)


def render_faculty_page():
    """Render the faculty management page."""
    st.header("Faculty Members")
    
    faculty_list = st.session_state.faculty_manager.get_all_faculty()
    analytics = get_analytics()
    ranking = analytics.get_faculty_ranking()
    
    # Faculty cards
    for faculty in faculty_list:
        faculty_id = faculty["id"]
        scholar_data = st.session_state.scholar_data.get(faculty_id, {})
        
        with st.expander(f"**{faculty['name']}** - {faculty['designation']}", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**Research Areas:** {', '.join(faculty.get('research_areas', []))}")
                st.write(f"**Google Scholar ID:** {faculty.get('scholar_id', 'Not set')}")
                if faculty.get('joined_year'):
                    st.write(f"**Joined:** {faculty['joined_year']}")
            
            with col2:
                st.metric("Publications", scholar_data.get("publications", []).__len__() or 0)
                st.metric("H-Index", scholar_data.get("hindex", 0))
            
            with col3:
                st.metric("Citations", f"{scholar_data.get('citedby', 0):,}")
                st.metric("i10-Index", scholar_data.get("i10index", 0))
            
            # Publications list
            pubs = scholar_data.get("publications", [])
            if pubs:
                st.write("**Recent Publications:**")
                for pub in pubs[:5]:
                    st.write(f"- {pub.get('title', 'Unknown')} ({pub.get('year', 'N/A')}) - {pub.get('citations', 0)} citations")
    
    st.divider()
    
    # Faculty ranking table
    st.subheader("Faculty Ranking")
    
    ranking_metric = st.selectbox(
        "Rank by:",
        ["citations", "publications", "h_index", "i10_index"],
        format_func=lambda x: x.replace("_", " ").title()
    )
    
    ranking = analytics.get_faculty_ranking(by=ranking_metric)
    st.dataframe(ranking, use_container_width=True, hide_index=True)


def render_publications_page():
    """Render the publications analysis page."""
    st.header("Publications Analysis")
    
    analytics = get_analytics()
    viz = get_visualizer()
    
    # Summary metrics
    summary = analytics.get_department_summary()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Publications", summary["total_publications"])
    with col2:
        st.metric("Avg per Faculty", summary["avg_publications_per_faculty"])
    with col3:
        st.metric("Avg Citations/Paper", summary["avg_citations_per_paper"])
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Trends", "Top Papers", "Venues"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Combined Trend")
            fig = viz.combined_trend_chart()
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            growth = analytics.get_yearly_growth()
            st.subheader("Growth Analysis")
            st.metric("Average Yearly Growth", f"{growth['avg_growth']}%")
            
            if growth['growth_rates']:
                growth_df = pd.DataFrame(growth['growth_rates'])
                st.dataframe(growth_df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("Top Cited Papers")
        n_papers = st.slider("Number of papers:", 5, 20, 10)
        top_papers = analytics.get_top_cited_papers(n_papers)
        st.dataframe(top_papers, use_container_width=True, hide_index=True)
        
        st.subheader("Citation Distribution")
        fig = viz.citation_distribution_scatter()
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Publication Venues")
        venues = analytics.get_venue_distribution()
        if not venues.empty:
            st.dataframe(venues, use_container_width=True, hide_index=True)
        else:
            st.info("No venue data available")


def render_analytics_page():
    """Render the advanced analytics page."""
    st.header("Advanced Analytics")
    
    analytics = get_analytics()
    viz = get_visualizer()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Impact Analysis", "Collaboration", "Keywords"])
    
    with tab1:
        st.subheader("Impact Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = viz.impact_scatter()
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Citation Impact Ratio**")
            impact_df = analytics.get_citation_impact_ratio()
            st.dataframe(impact_df, use_container_width=True, hide_index=True)
        
        st.subheader("Citation Distribution")
        fig = viz.citations_box_plot()
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Collaboration Analysis")
        
        coauthor_stats = analytics.get_coauthor_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg Authors/Paper", coauthor_stats["avg_authors_per_paper"])
        with col2:
            st.metric("Solo Papers", coauthor_stats["solo_papers"])
        with col3:
            st.metric("Collaborative Papers", coauthor_stats["collaborative_papers"])
        
        st.subheader("Collaboration Matrix")
        fig = viz.collaboration_heatmap()
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Collaboration Network")
        network_fig = viz.coauthor_network()
        if network_fig:
            st.plotly_chart(network_fig, use_container_width=True)
        else:
            st.info("Network visualization requires networkx library")
    
    with tab3:
        st.subheader("Research Keywords")
        
        keywords = analytics.get_research_keywords()
        
        if keywords:
            # Display as bar chart
            kw_df = pd.DataFrame(list(keywords.items())[:20], columns=["Keyword", "Count"])
            
            import plotly.express as px
            fig = px.bar(kw_df, x="Keyword", y="Count", title="Top Research Keywords")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Word cloud
            st.subheader("Word Cloud")
            wordcloud_buf = viz.generate_wordcloud()
            if wordcloud_buf:
                st.image(wordcloud_buf, use_container_width=True)
            else:
                st.info("Word cloud requires wordcloud library")
        else:
            st.info("No keyword data available")


def render_export_page():
    """Render the export page."""
    st.header("Export Reports")
    
    analytics = get_analytics()
    
    st.write("Download comprehensive reports in various formats.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Excel Report")
        st.write("Complete data export with multiple sheets including faculty, publications, and analytics.")
        
        if st.button("Generate Excel Report", key="excel"):
            with st.spinner("Generating Excel report..."):
                try:
                    # Create Excel file
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        # Faculty sheet
                        analytics.get_all_faculty().to_excel(writer, sheet_name='Faculty', index=False)
                        
                        # Publications sheet
                        analytics.get_all_publications().to_excel(writer, sheet_name='Publications', index=False)
                        
                        # Ranking sheet
                        analytics.get_faculty_ranking().to_excel(writer, sheet_name='Rankings', index=False)
                        
                        # Top papers sheet
                        analytics.get_top_cited_papers(20).to_excel(writer, sheet_name='Top Papers', index=False)
                        
                        # Yearly trends
                        analytics.get_publications_by_year().to_excel(writer, sheet_name='Yearly Pubs', index=False)
                        analytics.get_citations_by_year().to_excel(writer, sheet_name='Yearly Citations', index=False)
                        
                        # Venues
                        analytics.get_venue_distribution().to_excel(writer, sheet_name='Venues', index=False)
                    
                    buffer.seek(0)
                    
                    st.download_button(
                        label="Download Excel",
                        data=buffer,
                        file_name=f"cusb_research_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    st.success("Excel report generated!")
                except Exception as e:
                    st.error(f"Error generating Excel: {e}")
    
    with col2:
        st.subheader("CSV Export")
        st.write("Export individual datasets as CSV files.")
        
        export_options = {
            "Faculty Data": analytics.get_all_faculty(),
            "All Publications": analytics.get_all_publications(),
            "Faculty Rankings": analytics.get_faculty_ranking(),
            "Top Cited Papers": analytics.get_top_cited_papers(50),
            "Publication Trends": analytics.get_publications_by_year()
        }
        
        selected_export = st.selectbox("Select dataset:", list(export_options.keys()))
        
        if st.button("Export CSV", key="csv"):
            df = export_options[selected_export]
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{selected_export.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    st.divider()
    
    st.subheader("Summary Report")
    
    summary = analytics.get_department_summary()
    
    report_text = f"""
# CUSB Computer Science Department - Research Publication Analysis Report

**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

## Department Overview

| Metric | Value |
|--------|-------|
| Total Faculty | {summary['total_faculty']} |
| Total Publications | {summary['total_publications']} |
| Total Citations | {summary['total_citations']:,} |
| Average H-Index | {summary['avg_h_index']} |
| Avg Publications per Faculty | {summary['avg_publications_per_faculty']} |
| Avg Citations per Paper | {summary['avg_citations_per_paper']} |

## Faculty Rankings (by Citations)

"""
    
    ranking = analytics.get_faculty_ranking()
    for _, row in ranking.iterrows():
        report_text += f"- **{row['name']}**: {row['total_citations']:,} citations, {row['total_publications']} publications, H-Index: {row['h_index']}\n"
    
    st.text_area("Report Preview:", report_text, height=400)
    
    st.download_button(
        label="Download Report (Markdown)",
        data=report_text,
        file_name=f"cusb_research_summary_{datetime.now().strftime('%Y%m%d')}.md",
        mime="text/markdown"
    )


def render_settings_page():
    """Render the settings page."""
    st.header("Settings")
    
    tab1, tab2, tab3 = st.tabs(["Data Management", "Scholar Details", "About"])
    
    with tab1:
        st.subheader("Data Management")
        
        # Data status
        st.write("**Current Data Status:**")
        
        # Check if data has Google Scholar source
        has_scholar_source = any(d.get("source") == "Google Scholar Profile" for d in st.session_state.scholar_data.values())
        
        if has_scholar_source:
            st.success("Using Google Scholar sourced publication data")
        else:
            st.warning("Data source not verified. Consider refreshing from Google Scholar.")
        
        cache_stats = st.session_state.scholar_fetcher.get_cache_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Faculty", len(st.session_state.scholar_data))
        with col2:
            total_pubs = sum(len(d.get("publications", [])) for d in st.session_state.scholar_data.values())
            st.metric("Total Publications", total_pubs)
        with col3:
            total_citations = sum(d.get("citedby", 0) for d in st.session_state.scholar_data.values())
            st.metric("Total Citations", f"{total_citations:,}")
        
        st.divider()
        
        # Fetch data button
        st.subheader("Fetch Data from Google Scholar")
        
        if not SCHOLARLY_AVAILABLE:
            st.error("The `scholarly` library is not installed. Install it with: `pip install scholarly`")
        else:
            st.info("This will fetch live publication data from Google Scholar. Rate limiting is applied to avoid blocks.")
        
        if st.button("Fetch Live Data", disabled=not SCHOLARLY_AVAILABLE):
            with st.spinner("Fetching data from Google Scholar... This may take a few minutes."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def progress_callback(current, total, name):
                    progress_bar.progress(current / total)
                    status_text.text(f"Fetching: {name} ({current}/{total})")
                
                faculty_list = st.session_state.faculty_manager.get_all_faculty()
                
                results = st.session_state.scholar_fetcher.fetch_faculty_data(
                    faculty_list,
                    progress_callback=progress_callback
                )
                
                st.session_state.scholar_data = results
                save_scholar_data()
                
                progress_bar.progress(1.0)
                status_text.text("Complete!")
                st.success("Data fetched successfully!")
                st.rerun()
        
        st.divider()
        
        # Reset data
        st.subheader("Reset Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Reset to Cached Data"):
                st.session_state.scholar_data = create_demo_data()
                save_scholar_data()
                st.success("Reset to cached Google Scholar data")
                st.rerun()
        
        with col2:
            if st.button("Clear Cache"):
                st.session_state.scholar_fetcher.clear_cache()
                st.success("Cache cleared")
    
    with tab2:
        st.subheader("Google Scholar Details Analysis")
        
        st.markdown("""
        This section provides detailed Google Scholar metrics for each faculty member in the 
        **Department of Computer Science, CUSB Gaya**.
        """)
        
        for faculty_id, data in st.session_state.scholar_data.items():
            with st.expander(f"**{data.get('name', 'Unknown')}** - {data.get('affiliation', 'CUSB')}", expanded=False):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown("### Metrics")
                    st.metric("Total Citations", f"{data.get('citedby', 0):,}")
                    st.metric("H-Index", data.get('hindex', 0))
                    st.metric("i10-Index", data.get('i10index', 0))
                    st.metric("Publications", len(data.get('publications', [])))
                
                with col2:
                    st.markdown("### Research Interests")
                    interests = data.get('interests', [])
                    if interests:
                        st.write(", ".join(interests))
                    else:
                        st.write("Not specified")
                    
                    st.markdown("### Academic Email")
                    st.write(f"Verified: **@{data.get('email_domain', 'cusb.ac.in')}**")
                    
                    st.markdown("### Data Source")
                    st.write(f"Source: {data.get('source', 'Google Scholar Profile')}")
                
                st.divider()
                
                st.markdown("### Top Publications")
                pubs = sorted(data.get('publications', []), key=lambda x: x.get('citations', 0), reverse=True)[:5]
                
                for i, pub in enumerate(pubs, 1):
                    st.markdown(f"""
                    **{i}. {pub.get('title', 'Unknown Title')}**  
                    Year: {pub.get('year', 'N/A')} | Citations: {pub.get('citations', 0)} | Venue: {pub.get('venue', 'N/A')}
                    """)
        
        # Summary table
        st.divider()
        st.subheader("Faculty Scholar Metrics Summary")
        
        summary_data = []
        for fid, data in st.session_state.scholar_data.items():
            summary_data.append({
                "Name": data.get('name', 'Unknown'),
                "Citations": data.get('citedby', 0),
                "H-Index": data.get('hindex', 0),
                "i10-Index": data.get('i10index', 0),
                "Publications": len(data.get('publications', [])),
                "Top Interest": data.get('interests', ['N/A'])[0] if data.get('interests') else 'N/A'
            })
        
        import pandas as pd
        summary_df = pd.DataFrame(summary_data)
        summary_df = summary_df.sort_values('Citations', ascending=False)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    with tab3:
        st.subheader("About This Application")
        
        st.markdown("""
        ### CUSB CS Faculty Research Publication Analyzer
        
        This application provides statistical analysis of research publications by faculty members 
        of the **Department of Computer Science** at the **Central University of South Bihar, Gaya**.
        
        #### Features:
        - **Dashboard**: Overview of key metrics and visualizations
        - **Faculty**: Individual faculty profiles and rankings
        - **Publications**: Publication trends and top papers
        - **Analytics**: Advanced analysis including collaboration networks
        - **Export**: Download reports in Excel, CSV, and Markdown formats
        
        #### Data Sources:
        - Google Scholar (via scholarly library)
        - Manual faculty information
        
        #### Technology Stack:
        - **Streamlit** - Web interface
        - **Plotly** - Interactive visualizations
        - **Pandas** - Data analysis
        - **scholarly** - Google Scholar data
        
        ---
        
        *Built for CUSB*
        """)


# ==================== Main Application ====================

def main():
    """Main application entry point."""
    init_session_state()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        
        page = st.radio(
            "Go to:",
            ["Dashboard", "Faculty", "Publications", "Analytics", "Export", "Settings"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Quick stats in sidebar
        analytics = get_analytics()
        summary = analytics.get_department_summary()
        
        st.caption("Quick Stats")
        st.write(f"{summary['total_publications']} publications")
        st.write(f"{summary['total_citations']:,} citations")
        st.write(f"{summary['total_faculty']} faculty")
        
        st.divider()
        
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Render header
    render_header()
    
    # Render selected page
    if page == "Dashboard":
        render_dashboard()
    elif page == "Faculty":
        render_faculty_page()
    elif page == "Publications":
        render_publications_page()
    elif page == "Analytics":
        render_analytics_page()
    elif page == "Export":
        render_export_page()
    elif page == "Settings":
        render_settings_page()


if __name__ == "__main__":
    main()
