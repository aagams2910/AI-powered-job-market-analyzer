# AI-Powered Job Market Analyzer

An intelligent application that forecasts demand for specific skills and roles using data from job boards and labor statistics.

## Features

- **Data Collection:** Scrapes job postings from LinkedIn, Indeed, and Glassdoor
- **Market Analysis:** Identifies trends in job skills and requirements
- **Forecasting:** Predicts future demand for specific skills and roles
- **Interactive Dashboard:** Visualizes job market trends and opportunities
- **Personalized Insights:** Offers career recommendations based on user skills

## Installation

1. Clone this repository
```bash
git clone https://github.com/aagams2910/AI-powered-job-market-analyzer.git
cd AI-powered-job-market-analyzer
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Download required NLTK and spaCy models
```bash
python -m nltk.downloader punkt stopwords wordnet
python -m spacy download en_core_web_sm
```

4. Set up environment variables (create a .env file with required API keys)

## Usage

Run the Streamlit app:
```bash
streamlit run app/main.py
```

## Project Structure

```
AI-powered-job-market-analyzer/
│
├── app/                    # Application code
│   ├── components/         # UI components
│   ├── utils/              # Utility functions
│   ├── models/             # Forecasting and ML models
│   ├── data/               # Data processing modules
│   ├── api/                # API connectors
│   ├── viz/                # Visualization modules
│   └── main.py             # Main Streamlit app
│
├── data/                   # Data storage
│   ├── raw/                # Raw data from various sources
│   ├── processed/          # Processed datasets
│   └── models/             # Trained models
│
├── tests/                  # Test files
│
├── requirements.txt        # Project dependencies
├── .env.example            # Example environment variables
└── README.md               # Project documentation
```
