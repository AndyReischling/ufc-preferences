"""
Data loading module for Streamlit app.
All functions use Streamlit caching for performance.
"""

import pandas as pd
import numpy as np
import ast
from pathlib import Path
import streamlit as st
import config


@st.cache_data
def load_content_catalog():
    """
    Load Paramount+ content catalog with features.
    
    Returns:
        DataFrame with content titles, types, genres, themes, etc.
    """
    try:
        df = pd.read_csv(config.CONTENT_FEATURES_FILE)
        
        # Parse string representations of lists
        if 'themes' in df.columns:
            df['themes'] = df['themes'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        if 'character_archetypes' in df.columns:
            df['character_archetypes'] = df['character_archetypes'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        if 'narrative_patterns' in df.columns:
            df['narrative_patterns'] = df['narrative_patterns'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        if 'genres' in df.columns:
            df['genres'] = df['genres'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        
        return df
    except Exception as e:
        st.error(f"Error loading content catalog: {e}")
        return pd.DataFrame()


@st.cache_data
def load_fighter_data():
    """
    Load fighter data with lore and stats.
    
    Returns:
        DataFrame with fighter profiles, stats, lore, etc.
    """
    try:
        df = pd.read_csv(config.FIGHTERS_WITH_LORE_FILE)
        return df
    except Exception as e:
        st.error(f"Error loading fighter data: {e}")
        return pd.DataFrame()


@st.cache_data
def load_content_fighter_mapping():
    """
    Load content-fighter similarity mapping.
    
    Returns:
        DataFrame with content_title, fighter_name, similarity_score, etc.
    """
    try:
        df = pd.read_csv(config.CONTENT_FIGHTER_MAPPING_FILE)
        return df
    except Exception as e:
        st.error(f"Error loading content-fighter mapping: {e}")
        return pd.DataFrame()


@st.cache_data
def load_fight_data():
    """
    Load UFC fight data for finding fights involving fighters.
    
    Returns:
        DataFrame with fight records
    """
    try:
        fight_file = Path(config.FIGHT_DATA_FILE)
        if not fight_file.exists():
            # Silently return empty DataFrame - fight data is optional
            return pd.DataFrame()
        
        df = pd.read_csv(fight_file)
        return df
    except Exception as e:
        # Silently return empty DataFrame - fight data is optional
        return pd.DataFrame()


@st.cache_data
def load_all_data():
    """
    Load all data files and return as dictionary.
    Convenience function for initializing app.
    
    Returns:
        Dictionary with keys: 'content', 'fighters', 'mapping', 'fights'
    """
    return {
        'content': load_content_catalog(),
        'fighters': load_fighter_data(),
        'mapping': load_content_fighter_mapping(),
        'fights': load_fight_data()
    }

