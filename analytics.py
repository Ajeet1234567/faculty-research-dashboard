"""
Analytics Module
Statistical analysis of research publications data
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import Counter
from datetime import datetime


class Analytics:
    """Performs statistical analysis on publication data."""
    
    def __init__(self, scholar_data: Dict[str, Dict], faculty_data: List[Dict]):
        """
        Initialize analytics with scholar and faculty data.
        
        Args:
            scholar_data: Dictionary mapping faculty IDs to their scholar data
            faculty_data: List of faculty information dictionaries
        """
        self.scholar_data = scholar_data
        self.faculty_data = {f["id"]: f for f in faculty_data}
        self._build_dataframes()
    
    def _build_dataframes(self):
        """Build pandas DataFrames from the data."""
        # Faculty DataFrame
        faculty_rows = []
        for fid, data in self.scholar_data.items():
            faculty_info = self.faculty_data.get(fid, {})
            faculty_rows.append({
                "id": fid,
                "name": data.get("name", faculty_info.get("name", "")),
                "designation": faculty_info.get("designation", ""),
                "total_citations": data.get("citedby", 0),
                "h_index": data.get("hindex", 0),
                "i10_index": data.get("i10index", 0),
                "total_publications": len(data.get("publications", [])),
                "research_areas": data.get("interests", faculty_info.get("research_areas", []))
            })
        self.faculty_df = pd.DataFrame(faculty_rows)
        
        # Publications DataFrame
        pub_rows = []
        for fid, data in self.scholar_data.items():
            faculty_name = data.get("name", self.faculty_data.get(fid, {}).get("name", ""))
            for pub in data.get("publications", []):
                year = pub.get("year")
                if year:
                    try:
                        year = int(str(year)[:4])
                    except (ValueError, TypeError):
                        year = None
                
                pub_rows.append({
                    "faculty_id": fid,
                    "faculty_name": faculty_name,
                    "title": pub.get("title", ""),
                    "year": year,
                    "citations": pub.get("citations", 0),
                    "authors": pub.get("authors", ""),
                    "venue": pub.get("venue", ""),
                })
        self.publications_df = pd.DataFrame(pub_rows)
    
    # ==================== Department Statistics ====================
    
    def get_department_summary(self) -> Dict:
        """Get overall department statistics."""
        if self.faculty_df.empty:
            return {
                "total_faculty": 0,
                "total_publications": 0,
                "total_citations": 0,
                "avg_h_index": 0,
                "avg_publications_per_faculty": 0,
                "avg_citations_per_faculty": 0,
                "avg_citations_per_paper": 0
            }
        
        total_pubs = self.faculty_df["total_publications"].sum()
        total_citations = self.faculty_df["total_citations"].sum()
        
        return {
            "total_faculty": len(self.faculty_df),
            "total_publications": int(total_pubs),
            "total_citations": int(total_citations),
            "avg_h_index": round(self.faculty_df["h_index"].mean(), 2),
            "avg_publications_per_faculty": round(total_pubs / len(self.faculty_df), 2),
            "avg_citations_per_faculty": round(total_citations / len(self.faculty_df), 2),
            "avg_citations_per_paper": round(total_citations / total_pubs, 2) if total_pubs > 0 else 0
        }
    
    def get_faculty_ranking(self, by: str = "citations") -> pd.DataFrame:
        """
        Rank faculty by specified metric.
        
        Args:
            by: Ranking metric - 'citations', 'publications', 'h_index', 'i10_index'
        """
        column_map = {
            "citations": "total_citations",
            "publications": "total_publications",
            "h_index": "h_index",
            "i10_index": "i10_index"
        }
        
        sort_col = column_map.get(by, "total_citations")
        ranked = self.faculty_df.sort_values(sort_col, ascending=False).reset_index(drop=True)
        ranked["rank"] = range(1, len(ranked) + 1)
        return ranked[["rank", "name", "designation", "total_publications", "total_citations", "h_index", "i10_index"]]
    
    # ==================== Publication Analysis ====================
    
    def get_publications_by_year(self) -> pd.DataFrame:
        """Get publication count by year."""
        if self.publications_df.empty:
            return pd.DataFrame(columns=["year", "count"])
        
        yearly = self.publications_df[self.publications_df["year"].notna()].groupby("year").size()
        return yearly.reset_index(name="count").sort_values("year")
    
    def get_citations_by_year(self) -> pd.DataFrame:
        """Get citation count by year."""
        if self.publications_df.empty:
            return pd.DataFrame(columns=["year", "citations"])
        
        yearly = self.publications_df[self.publications_df["year"].notna()].groupby("year")["citations"].sum()
        return yearly.reset_index().sort_values("year")
    
    def get_publications_by_faculty(self) -> pd.DataFrame:
        """Get publication count per faculty."""
        return self.faculty_df[["name", "total_publications"]].sort_values("total_publications", ascending=False)
    
    def get_citations_by_faculty(self) -> pd.DataFrame:
        """Get citation count per faculty."""
        return self.faculty_df[["name", "total_citations"]].sort_values("total_citations", ascending=False)
    
    def get_top_cited_papers(self, n: int = 10) -> pd.DataFrame:
        """Get top N most cited papers."""
        if self.publications_df.empty:
            return pd.DataFrame()
        return self.publications_df.nlargest(n, "citations")[["title", "faculty_name", "year", "citations", "venue"]]
    
    def get_recent_publications(self, n: int = 10) -> pd.DataFrame:
        """Get N most recent publications."""
        if self.publications_df.empty:
            return pd.DataFrame()
        df = self.publications_df[self.publications_df["year"].notna()]
        return df.nlargest(n, "year")[["title", "faculty_name", "year", "citations", "venue"]]
    
    # ==================== Research Area Analysis ====================
    
    def get_research_area_distribution(self) -> Dict[str, int]:
        """Get research area distribution across faculty."""
        areas = []
        for _, row in self.faculty_df.iterrows():
            if isinstance(row["research_areas"], list):
                areas.extend(row["research_areas"])
        return dict(Counter(areas).most_common(20))
    
    def get_research_keywords(self) -> Dict[str, int]:
        """Extract and count keywords from publication titles."""
        if self.publications_df.empty:
            return {}
        
        # Common words to exclude
        stopwords = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought',
            'used', 'using', 'based', 'new', 'novel', 'approach', 'method', 'study',
            'analysis', 'model', 'system', 'systems', 'application', 'applications'
        }
        
        words = []
        for title in self.publications_df["title"].dropna():
            title_words = title.lower().split()
            # Clean and filter words
            for word in title_words:
                word = ''.join(c for c in word if c.isalnum())
                if len(word) > 3 and word not in stopwords:
                    words.append(word)
        
        return dict(Counter(words).most_common(50))
    
    # ==================== Venue Analysis ====================
    
    def get_venue_distribution(self) -> pd.DataFrame:
        """Get publication count by venue."""
        if self.publications_df.empty:
            return pd.DataFrame(columns=["venue", "count"])
        
        venues = self.publications_df[self.publications_df["venue"] != ""].groupby("venue").size()
        return venues.reset_index(name="count").sort_values("count", ascending=False).head(20)
    
    # ==================== Collaboration Analysis ====================
    
    def get_coauthor_stats(self) -> Dict:
        """Analyze co-authorship patterns."""
        if self.publications_df.empty:
            return {
                "avg_authors_per_paper": 0,
                "solo_papers": 0,
                "collaborative_papers": 0
            }
        
        author_counts = []
        solo = 0
        collaborative = 0
        
        for authors in self.publications_df["authors"].dropna():
            count = len([a.strip() for a in str(authors).replace(" and ", ",").split(",") if a.strip()])
            author_counts.append(count)
            if count == 1:
                solo += 1
            else:
                collaborative += 1
        
        return {
            "avg_authors_per_paper": round(np.mean(author_counts), 2) if author_counts else 0,
            "solo_papers": solo,
            "collaborative_papers": collaborative
        }
    
    def get_faculty_collaboration_matrix(self) -> pd.DataFrame:
        """
        Create a collaboration matrix between faculty members.
        This shows papers where multiple department faculty are co-authors.
        """
        faculty_names = self.faculty_df["name"].tolist()
        n = len(faculty_names)
        matrix = np.zeros((n, n))
        
        for _, pub in self.publications_df.iterrows():
            authors = str(pub.get("authors", "")).lower()
            collaborating = []
            
            for i, name in enumerate(faculty_names):
                # Check if faculty name appears in authors
                name_parts = name.lower().split()
                if any(part in authors for part in name_parts if len(part) > 2):
                    collaborating.append(i)
            
            # Mark collaborations
            for i in collaborating:
                for j in collaborating:
                    if i != j:
                        matrix[i][j] += 1
        
        return pd.DataFrame(matrix, index=faculty_names, columns=faculty_names)
    
    # ==================== Trend Analysis ====================
    
    def get_yearly_growth(self) -> Dict:
        """Calculate yearly publication growth rate."""
        yearly = self.get_publications_by_year()
        if yearly.empty or len(yearly) < 2:
            return {"growth_rates": [], "avg_growth": 0}
        
        growth_rates = []
        years = yearly["year"].tolist()
        counts = yearly["count"].tolist()
        
        for i in range(1, len(counts)):
            if counts[i-1] > 0:
                rate = ((counts[i] - counts[i-1]) / counts[i-1]) * 100
                growth_rates.append({"year": years[i], "growth_rate": round(rate, 2)})
        
        avg_growth = np.mean([g["growth_rate"] for g in growth_rates]) if growth_rates else 0
        
        return {
            "growth_rates": growth_rates,
            "avg_growth": round(avg_growth, 2)
        }
    
    def get_citation_impact_ratio(self) -> pd.DataFrame:
        """Calculate citation per publication ratio for each faculty."""
        df = self.faculty_df.copy()
        df["impact_ratio"] = df.apply(
            lambda x: round(x["total_citations"] / x["total_publications"], 2) 
            if x["total_publications"] > 0 else 0,
            axis=1
        )
        return df[["name", "total_publications", "total_citations", "impact_ratio"]].sort_values("impact_ratio", ascending=False)
    
    # ==================== Comparative Analysis ====================
    
    def get_faculty_comparison(self) -> pd.DataFrame:
        """Get comprehensive faculty comparison data."""
        df = self.faculty_df.copy()
        
        # Calculate percentile ranks
        for col in ["total_publications", "total_citations", "h_index"]:
            df[f"{col}_percentile"] = df[col].rank(pct=True).round(2) * 100
        
        return df
    
    def get_productivity_by_designation(self) -> pd.DataFrame:
        """Group productivity metrics by designation."""
        if self.faculty_df.empty:
            return pd.DataFrame()
        
        grouped = self.faculty_df.groupby("designation").agg({
            "total_publications": ["sum", "mean"],
            "total_citations": ["sum", "mean"],
            "h_index": "mean"
        }).round(2)
        
        grouped.columns = ["total_pubs", "avg_pubs", "total_citations", "avg_citations", "avg_h_index"]
        return grouped.reset_index()
    
    # ==================== Export Methods ====================
    
    def export_to_dict(self) -> Dict:
        """Export all analytics to a dictionary."""
        return {
            "department_summary": self.get_department_summary(),
            "faculty_ranking": self.get_faculty_ranking().to_dict("records"),
            "publications_by_year": self.get_publications_by_year().to_dict("records"),
            "citations_by_year": self.get_citations_by_year().to_dict("records"),
            "top_cited_papers": self.get_top_cited_papers().to_dict("records"),
            "research_areas": self.get_research_area_distribution(),
            "venue_distribution": self.get_venue_distribution().to_dict("records"),
            "coauthor_stats": self.get_coauthor_stats(),
            "yearly_growth": self.get_yearly_growth()
        }
    
    def get_all_publications(self) -> pd.DataFrame:
        """Get all publications DataFrame."""
        return self.publications_df
    
    def get_all_faculty(self) -> pd.DataFrame:
        """Get all faculty DataFrame."""
        return self.faculty_df
