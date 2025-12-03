"""
Configuration file for Streamlit UFC Fighter Recommendation App
"""

# Data file paths
CONTENT_FEATURES_FILE = 'paramount_content_features.csv'
FIGHTERS_WITH_LORE_FILE = 'fighters_with_lore.csv'
CONTENT_FIGHTER_MAPPING_FILE = 'content_fighter_mapping.csv'
FIGHT_DATA_FILE = 'UFC-DataLab/data/merged_stats_n_scorecards/merged_stats_n_scorecards.csv'

# Default settings
DEFAULT_N_RECOMMENDATIONS = 10
DEFAULT_N_BUNDLES = 3
DEFAULT_N_FIGHTS_PER_BUNDLE = 5

# Theme color mappings for visualization (expanded)
THEME_COLORS = {
    # Action & Combat
    'aggression': '#FF4444',
    'precision': '#4444FF',
    'strategy': '#44FF44',
    'power': '#FF6600',
    'speed': '#00CCFF',
    'endurance': '#66FF66',
    'versatility': '#9966FF',
    
    # Narrative Themes
    'rivalry': '#FF8844',
    'leadership': '#8844FF',
    'triumph': '#FFD700',
    'underdog': '#44DDFF',
    'redemption': '#FF44DD',
    'legacy': '#888888',
    'brotherhood': '#44FF88',
    'struggle': '#FF8888',
    'survival': '#88FF44',
    'rise_to_glory': '#FF99CC',
    
    # Emotional & Psychological
    'determination': '#FF6B9D',
    'resilience': '#4ECDC4',
    'courage': '#FF6B6B',
    'discipline': '#95E1D3',
    'patience': '#AA96DA',
    'instinct': '#FCBAD3',
    'innovation': '#F38181',
    
    # Social & Relationship
    'isolation': '#A8DADC',
    'betrayal': '#E63946',
    
    # Conflict & Resolution
    'conflict': '#D62828',
    'resolution': '#06A77D',
    'transformation': '#F77F00',
    
    # Values & Morality
    'honor': '#264653',
    'justice': '#2A9D8F',
    'sacrifice': '#E76F51',
    
    # Time & Journey
    'journey': '#F4A261',
    'destiny': '#E9C46A',
    'past': '#8B9DC3',
    'future': '#C8B6FF',
    
    # Default
    'exploration': '#4488FF'
}

# Genre colors
GENRE_COLORS = {
    'action': '#FF0000',
    'drama': '#0000FF',
    'comedy': '#FFFF00',
    'thriller': '#800080',
    'sci-fi': '#00FFFF',
    'sports': '#00FF00',
    'horror': '#000000',
    'crime': '#808080',
    'western': '#8B4513',
    'biography': '#FFA500',
    'adventure': '#008000',
    'reality': '#FF69B4',
    'news': '#000080',
    'animation': '#FF1493',
    'family': '#FFB6C1'
}

