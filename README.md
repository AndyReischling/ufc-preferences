# UFC Fighter Recommendation App

An interactive Streamlit web application that connects Paramount+ content preferences to UFC fighter recommendations through thematic analysis.

## Features

- **Content Selection**: Browse and filter Paramount+ content by genre, theme, and type
- **Fighter Recommendations**: Get personalized fighter recommendations based on content themes
- **Fighter Profiles**: Explore detailed fighter profiles with:
  - Biographical lore and stories
  - Personal details (age, nationality, height, reach, stance)
  - Fighting statistics and visualizations
  - Thematic metadata tags
- **Thematic Bundles**: Discover curated bundles combining:
  - Content titles
  - Recommended fighters
  - Related UFC fights
  - Thematic connection explanations

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure all required data files are present:
- `paramount_content_features.csv` - Content catalog with themes
- `fighters_with_lore.csv` - Fighter profiles with lore
- `content_fighter_mapping.csv` - Content-fighter similarity mappings
- `UFC-DataLab/data/merged_stats_n_scorecards/merged_stats_n_scorecards.csv` - Fight data (optional)

## Running the App

```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`

## Usage

1. **Select Content**: Use the sidebar filters or browse the content catalog to select Paramount+ titles you like
2. **View Recommendations**: Fighter recommendations appear automatically based on your selections
3. **Explore Profiles**: Click on any fighter to see their detailed profile, stats, and lore
4. **Discover Bundles**: Scroll down to see thematic bundles combining content, fighters, and fights

## Project Structure

```
Paramount-streaming/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── utils/
│   ├── data_loader.py        # Data loading with caching
│   ├── recommendations.py    # Recommendation engine
│   ├── bundles.py            # Bundle generation
│   ├── fighter_profile.py    # Fighter profile utilities
│   ├── themes.py             # Thematic metadata extraction
│   ├── visualizations.py     # Plotly chart creation
│   └── fight_finder.py       # Fight data queries
└── README.md                 # This file
```

## Data Sources

- UFC fight data from [UFC-DataLab](https://github.com/komaksym/UFC-DataLab.git)
- Paramount+ content catalog (simulated)
- Fighter lore generated from UFC statistics and personal details

## Notes

- The app uses Streamlit's caching for optimal performance
- All visualizations are interactive Plotly charts
- Fighter recommendations are based on thematic similarity (themes 50%, genres 30%, narratives 20%)

