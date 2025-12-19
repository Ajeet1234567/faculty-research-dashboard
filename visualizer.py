"""
Visualization Module
Creates interactive charts and graphs for research publication data
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from io import BytesIO

try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False


class Visualizer:
    """Creates visualizations for research publication data."""
    
    # Color schemes
    COLORS = {
        "primary": "#1f77b4",
        "secondary": "#ff7f0e",
        "success": "#2ca02c",
        "danger": "#d62728",
        "warning": "#ff9800",
        "info": "#17a2b8",
        "palette": px.colors.qualitative.Set2,
        "sequential": px.colors.sequential.Blues
    }
    
    def __init__(self, analytics):
        """
        Initialize visualizer with analytics instance.
        
        Args:
            analytics: Analytics instance with data
        """
        self.analytics = analytics
    
    # ==================== Bar Charts ====================
    
    def publications_by_faculty_chart(self) -> go.Figure:
        """Create bar chart of publications per faculty."""
        df = self.analytics.get_publications_by_faculty()
        
        fig = px.bar(
            df, 
            x="name", 
            y="total_publications",
            title="Publications by Faculty",
            labels={"name": "Faculty", "total_publications": "Number of Publications"},
            color="total_publications",
            color_continuous_scale="Blues"
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            showlegend=False,
            coloraxis_showscale=False
        )
        
        return fig
    
    def citations_by_faculty_chart(self) -> go.Figure:
        """Create bar chart of citations per faculty."""
        df = self.analytics.get_citations_by_faculty()
        
        fig = px.bar(
            df,
            x="name",
            y="total_citations",
            title="Total Citations by Faculty",
            labels={"name": "Faculty", "total_citations": "Total Citations"},
            color="total_citations",
            color_continuous_scale="Oranges"
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            showlegend=False,
            coloraxis_showscale=False
        )
        
        return fig
    
    def h_index_comparison_chart(self) -> go.Figure:
        """Create h-index comparison chart."""
        df = self.analytics.get_all_faculty()
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='H-Index',
            x=df["name"],
            y=df["h_index"],
            marker_color=self.COLORS["primary"]
        ))
        
        fig.add_trace(go.Bar(
            name='i10-Index',
            x=df["name"],
            y=df["i10_index"],
            marker_color=self.COLORS["secondary"]
        ))
        
        fig.update_layout(
            title="H-Index and i10-Index Comparison",
            xaxis_title="Faculty",
            yaxis_title="Index Value",
            xaxis_tickangle=-45,
            barmode='group'
        )
        
        return fig
    
    # ==================== Line Charts ====================
    
    def publications_trend_chart(self) -> go.Figure:
        """Create publications over time trend chart."""
        df = self.analytics.get_publications_by_year()
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(text="No publication data available", 
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        fig = px.line(
            df,
            x="year",
            y="count",
            title="Publication Trend Over Years",
            labels={"year": "Year", "count": "Number of Publications"},
            markers=True
        )
        
        fig.update_traces(line_color=self.COLORS["primary"], marker_size=10)
        fig.update_layout(xaxis=dict(tickmode='linear'))
        
        return fig
    
    def citations_trend_chart(self) -> go.Figure:
        """Create citations over time trend chart."""
        df = self.analytics.get_citations_by_year()
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(text="No citation data available",
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        fig = px.area(
            df,
            x="year",
            y="citations",
            title="Citation Trend Over Years",
            labels={"year": "Year", "citations": "Total Citations"}
        )
        
        fig.update_traces(
            fill='tozeroy',
            line_color=self.COLORS["secondary"],
            fillcolor='rgba(255, 127, 14, 0.3)'
        )
        
        return fig
    
    def combined_trend_chart(self) -> go.Figure:
        """Create combined publications and citations trend."""
        pubs_df = self.analytics.get_publications_by_year()
        cites_df = self.analytics.get_citations_by_year()
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        if not pubs_df.empty:
            fig.add_trace(
                go.Scatter(
                    x=pubs_df["year"],
                    y=pubs_df["count"],
                    name="Publications",
                    mode="lines+markers",
                    line=dict(color=self.COLORS["primary"])
                ),
                secondary_y=False
            )
        
        if not cites_df.empty:
            fig.add_trace(
                go.Scatter(
                    x=cites_df["year"],
                    y=cites_df["citations"],
                    name="Citations",
                    mode="lines+markers",
                    line=dict(color=self.COLORS["secondary"])
                ),
                secondary_y=True
            )
        
        fig.update_layout(title="Publications and Citations Trend")
        fig.update_xaxes(title_text="Year")
        fig.update_yaxes(title_text="Publications", secondary_y=False)
        fig.update_yaxes(title_text="Citations", secondary_y=True)
        
        return fig
    
    # ==================== Pie Charts ====================
    
    def research_area_pie_chart(self) -> go.Figure:
        """Create pie chart of research area distribution."""
        areas = self.analytics.get_research_area_distribution()
        
        if not areas:
            fig = go.Figure()
            fig.add_annotation(text="No research area data available",
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        fig = px.pie(
            names=list(areas.keys()),
            values=list(areas.values()),
            title="Research Area Distribution",
            color_discrete_sequence=self.COLORS["palette"]
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return fig
    
    def faculty_contribution_pie(self) -> go.Figure:
        """Create pie chart of faculty publication contributions."""
        df = self.analytics.get_publications_by_faculty()
        
        fig = px.pie(
            df,
            names="name",
            values="total_publications",
            title="Faculty Publication Contribution",
            color_discrete_sequence=self.COLORS["palette"]
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return fig
    
    # ==================== Heatmaps ====================
    
    def collaboration_heatmap(self) -> go.Figure:
        """Create collaboration heatmap between faculty."""
        matrix = self.analytics.get_faculty_collaboration_matrix()
        
        fig = px.imshow(
            matrix,
            title="Faculty Collaboration Matrix",
            labels=dict(color="Collaborations"),
            color_continuous_scale="Blues"
        )
        
        fig.update_layout(
            xaxis_tickangle=-45
        )
        
        return fig
    
    # ==================== Scatter Plots ====================
    
    def impact_scatter(self) -> go.Figure:
        """Create scatter plot of publications vs citations."""
        df = self.analytics.get_all_faculty()
        
        fig = px.scatter(
            df,
            x="total_publications",
            y="total_citations",
            size="h_index",
            color="name",
            hover_name="name",
            title="Publications vs Citations (bubble size = H-Index)",
            labels={
                "total_publications": "Total Publications",
                "total_citations": "Total Citations"
            }
        )
        
        fig.update_traces(marker=dict(sizemin=10))
        
        return fig
    
    def citation_distribution_scatter(self) -> go.Figure:
        """Create scatter plot of citation distribution."""
        df = self.analytics.get_all_publications()
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(text="No publication data available",
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        fig = px.scatter(
            df,
            x="year",
            y="citations",
            color="faculty_name",
            hover_data=["title"],
            title="Citation Distribution by Year",
            labels={"year": "Year", "citations": "Citations"}
        )
        
        return fig
    
    # ==================== Box Plots ====================
    
    def citations_box_plot(self) -> go.Figure:
        """Create box plot of citations by faculty."""
        df = self.analytics.get_all_publications()
        
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(text="No publication data available",
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        fig = px.box(
            df,
            x="faculty_name",
            y="citations",
            title="Citation Distribution by Faculty",
            labels={"faculty_name": "Faculty", "citations": "Citations per Paper"}
        )
        
        fig.update_layout(xaxis_tickangle=-45)
        
        return fig
    
    # ==================== Gauge Charts ====================
    
    def department_metrics_gauge(self, metric: str, value: float, max_val: float) -> go.Figure:
        """Create gauge chart for a department metric."""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': metric},
            gauge={
                'axis': {'range': [0, max_val]},
                'bar': {'color': self.COLORS["primary"]},
                'steps': [
                    {'range': [0, max_val * 0.33], 'color': "lightgray"},
                    {'range': [max_val * 0.33, max_val * 0.66], 'color': "gray"},
                    {'range': [max_val * 0.66, max_val], 'color': "darkgray"}
                ]
            }
        ))
        
        fig.update_layout(height=250)
        
        return fig
    
    # ==================== Word Cloud ====================
    
    def generate_wordcloud(self, width: int = 800, height: int = 400) -> Optional[BytesIO]:
        """Generate word cloud from research keywords."""
        if not WORDCLOUD_AVAILABLE:
            return None
        
        keywords = self.analytics.get_research_keywords()
        
        if not keywords:
            return None
        
        wordcloud = WordCloud(
            width=width,
            height=height,
            background_color='white',
            colormap='Blues',
            max_words=100
        ).generate_from_frequencies(keywords)
        
        # Create figure and save to BytesIO
        fig, ax = plt.subplots(figsize=(width/100, height/100))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        plt.close(fig)
        
        return buf
    
    # ==================== Network Graph ====================
    
    def coauthor_network(self) -> Optional[go.Figure]:
        """Create co-author network visualization."""
        if not NETWORKX_AVAILABLE:
            return None
        
        matrix = self.analytics.get_faculty_collaboration_matrix()
        
        # Create network graph
        G = nx.Graph()
        faculty_names = matrix.index.tolist()
        
        # Add nodes
        for name in faculty_names:
            G.add_node(name)
        
        # Add edges
        for i, name1 in enumerate(faculty_names):
            for j, name2 in enumerate(faculty_names):
                if i < j and matrix.iloc[i, j] > 0:
                    G.add_edge(name1, name2, weight=matrix.iloc[i, j])
        
        if len(G.edges()) == 0:
            fig = go.Figure()
            fig.add_annotation(text="No collaboration data available",
                             xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            return fig
        
        # Get positions
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Create edges trace
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edges_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Create nodes trace
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        
        df = self.analytics.get_all_faculty()
        node_sizes = []
        for node in G.nodes():
            pubs = df[df["name"] == node]["total_publications"].values
            node_sizes.append(max(20, (pubs[0] if len(pubs) > 0 else 1) * 5))
        
        nodes_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=list(G.nodes()),
            textposition="top center",
            marker=dict(
                size=node_sizes,
                color=self.COLORS["primary"],
                line=dict(width=2, color='white')
            )
        )
        
        fig = go.Figure(data=[edges_trace, nodes_trace])
        fig.update_layout(
            title="Faculty Collaboration Network",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
        
        return fig
    
    # ==================== Summary Dashboard ====================
    
    def create_dashboard_summary(self) -> go.Figure:
        """Create a summary dashboard with key metrics."""
        summary = self.analytics.get_department_summary()
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Publications by Faculty", "Citation Trend", 
                          "H-Index Comparison", "Research Areas"),
            specs=[[{"type": "bar"}, {"type": "scatter"}],
                   [{"type": "bar"}, {"type": "pie"}]]
        )
        
        # Publications by faculty
        pubs_df = self.analytics.get_publications_by_faculty()
        fig.add_trace(
            go.Bar(x=pubs_df["name"], y=pubs_df["total_publications"], 
                   marker_color=self.COLORS["primary"], showlegend=False),
            row=1, col=1
        )
        
        # Citations trend
        cites_df = self.analytics.get_citations_by_year()
        if not cites_df.empty:
            fig.add_trace(
                go.Scatter(x=cites_df["year"], y=cites_df["citations"],
                          mode="lines+markers", line=dict(color=self.COLORS["secondary"]),
                          showlegend=False),
                row=1, col=2
            )
        
        # H-index comparison
        faculty_df = self.analytics.get_all_faculty()
        fig.add_trace(
            go.Bar(x=faculty_df["name"], y=faculty_df["h_index"],
                   marker_color=self.COLORS["success"], showlegend=False),
            row=2, col=1
        )
        
        # Research areas pie
        areas = self.analytics.get_research_area_distribution()
        if areas:
            fig.add_trace(
                go.Pie(labels=list(areas.keys())[:8], values=list(areas.values())[:8],
                       showlegend=False),
                row=2, col=2
            )
        
        fig.update_layout(
            height=800,
            title_text=f"Department Overview - {summary['total_publications']} Publications, {summary['total_citations']} Citations"
        )
        
        return fig
