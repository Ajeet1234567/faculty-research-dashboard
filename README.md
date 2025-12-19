# CUSB CS Faculty Research Publication Analyzer

A comprehensive Python Streamlit application for statistical analysis of research publications by faculties of the Department of Computer Science at Central University of South Bihar (CUSB), Gaya.

## Features

- **Dashboard**: Overview of key metrics with interactive visualizations
- **Faculty**: Individual faculty profiles, metrics, and rankings
- **Publications**: Publication trends, top papers, and venue analysis
- **Analytics**: Advanced analysis including impact metrics, collaboration networks, and keyword clouds
- **Export**: Download reports in Excel, CSV, and Markdown formats
- **Scholar Details**: Detailed Google Scholar metrics for each faculty member

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Visualization | Plotly, Matplotlib |
| Data Analysis | Pandas, NumPy |
| Data Collection | scholarly (Google Scholar) |
| Network Analysis | NetworkX |
| Word Clouds | wordcloud |
| Excel Export | openpyxl |

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd cusb_research_analyzer
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the Streamlit application:

```bash
python -m streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Project Structure

```
cusb_research_analyzer/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── modules/
│   ├── __init__.py
│   ├── faculty_manager.py    # Faculty CRUD operations
│   ├── scholar_fetcher.py    # Google Scholar data fetcher
│   ├── analytics.py          # Statistical analysis
│   └── visualizer.py         # Plotly visualizations
├── utils/
│   ├── __init__.py
│   └── helpers.py            # Utility functions
├── data/                     # Data files (auto-created)
│   ├── faculty.json
│   ├── publications.json
│   └── cache.json
└── exports/                  # Export directory
```

## Faculty Data

The application includes data for CUSB CS Department faculty:

| Faculty | Designation | Research Areas |
|---------|-------------|----------------|
| Prof. Prabhat Ranjan | Professor & HOD | Software Engineering, Big Data, Data Mining |
| Dr. Jainath Yadav | Associate Professor | Speech Processing, Multi-view Learning, Deep Learning |
| Dr. Piyush Kumar Singh | Assistant Professor | Image Processing, Wavelet Transform, Parallel Computing |
| Dr. Mrityunjay Singh | Assistant Professor | Cryptography, Post-Quantum Security, Algorithms |
| Dr. Prakash Kumar | Assistant Professor | Network Security, Machine Learning, IoT |
| Mr. Nemi Chandra Rathore | Assistant Professor | Cloud Computing, Distributed Systems |

## Data Sources

- **Google Scholar**: Publication data fetched via the `scholarly` library
- **Manual Data**: Faculty information maintained in JSON files

## Key Metrics Analyzed

- Total Publications
- Total Citations
- H-Index
- i10-Index
- Publication Trends (yearly)
- Citation Trends
- Research Area Distribution
- Collaboration Networks
- Top Cited Papers
- Publication Venues

## Export Options

- **Excel**: Multi-sheet workbook with all data
- **CSV**: Individual dataset exports
- **Markdown**: Summary reports

## Configuration

Edit `config.py` to customize:

```python
APP_TITLE = "CUSB CS Faculty Research Analyzer"
INSTITUTION_NAME = "Central University of South Bihar, Gaya"
DEPARTMENT_NAME = "Department of Computer Science"
RATE_LIMIT_DELAY = 2  # Seconds between Google Scholar requests
```

## Fetching Live Data

To fetch live data from Google Scholar:

1. Go to **Settings** page
2. Click **Fetch Live Data**
3. Wait for the data to be fetched (rate limiting is applied)

Note: Google Scholar may block excessive requests. The application uses caching to minimize API calls.

## Requirements

- Python 3.8+
- See `requirements.txt` for package dependencies

## License

This project is for educational and research purposes at CUSB.

---

*Department of Computer Science, Central University of South Bihar, Gaya*
