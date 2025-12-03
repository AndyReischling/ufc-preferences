"""
Fight finder module.
Queries UFC fight data to find fights involving selected fighters.
"""

import pandas as pd
import numpy as np
from datetime import datetime


def find_fights_for_fighters(fighter_names, fight_data, limit=10):
    """
    Find fights involving one or more fighters.
    
    Args:
        fighter_names: List of fighter names or single fighter name string
        fight_data: UFC fight DataFrame
        limit: Maximum number of fights to return
    
    Returns:
        DataFrame with fight records
    """
    if fight_data is None or len(fight_data) == 0:
        return pd.DataFrame()
    
    if isinstance(fighter_names, str):
        fighter_names = [fighter_names]
    
    if len(fighter_names) == 0:
        return pd.DataFrame()
    
    # Normalize fighter names (uppercase for matching)
    fighter_names_upper = [name.upper() for name in fighter_names]
    
    # Find fights where any of the fighters participated (red or blue corner)
    mask = (
        fight_data['red_fighter_name'].str.upper().isin(fighter_names_upper) |
        fight_data['blue_fighter_name'].str.upper().isin(fighter_names_upper)
    )
    
    fighter_fights = fight_data[mask].copy()
    
    if len(fighter_fights) == 0:
        return pd.DataFrame()
    
    # Sort by date (most recent first) if date column exists
    if 'event_date' in fighter_fights.columns:
        try:
            # Try to parse dates
            fighter_fights['date_parsed'] = pd.to_datetime(
                fighter_fights['event_date'], 
                errors='coerce',
                format='%d/%m/%Y'
            )
            fighter_fights = fighter_fights.sort_values('date_parsed', ascending=False, na_position='last')
            fighter_fights = fighter_fights.drop('date_parsed', axis=1)
        except:
            # If date parsing fails, keep original order
            pass
    
    # Limit results
    fighter_fights = fighter_fights.head(limit)
    
    # Format fight information
    formatted_fights = []
    for idx, fight in fighter_fights.iterrows():
        red_fighter = fight.get('red_fighter_name', 'Unknown')
        blue_fighter = fight.get('blue_fighter_name', 'Unknown')
        red_result = fight.get('red_fighter_result', '')
        blue_result = fight.get('blue_fighter_result', '')
        method = fight.get('method', '')
        round_num = fight.get('round', '')
        event_name = fight.get('event_name', 'Unknown Event')
        event_date = fight.get('event_date', '')
        
        # Determine which fighter won
        winner = None
        if red_result == 'W':
            winner = red_fighter
        elif blue_result == 'W':
            winner = blue_fighter
        
        formatted_fights.append({
            'event_name': event_name,
            'event_date': event_date,
            'fighter_1': red_fighter,
            'fighter_2': blue_fighter,
            'winner': winner,
            'method': method,
            'round': round_num,
            'red_result': red_result,
            'blue_result': blue_result
        })
    
    return pd.DataFrame(formatted_fights)


def get_recent_fights(fighter_name, fight_data, n=5):
    """
    Get most recent fights for a fighter.
    
    Args:
        fighter_name: Name of the fighter
        fight_data: UFC fight DataFrame
        n: Number of recent fights to return
    
    Returns:
        DataFrame with recent fights
    """
    return find_fights_for_fighters(fighter_name, fight_data, limit=n)


def get_title_fights(fighter_name, fight_data):
    """
    Get title fights for a fighter.
    
    Args:
        fighter_name: Name of the fighter
        fight_data: UFC fight DataFrame
    
    Returns:
        DataFrame with title fights
    """
    if fight_data is None or len(fight_data) == 0:
        return pd.DataFrame()
    
    fighter_name_upper = fighter_name.upper()
    
    # Find fights involving this fighter
    mask = (
        (fight_data['red_fighter_name'].str.upper() == fighter_name_upper) |
        (fight_data['blue_fighter_name'].str.upper() == fighter_name_upper)
    )
    
    fighter_fights = fight_data[mask].copy()
    
    # Filter for title fights
    if 'bout_type' in fighter_fights.columns:
        title_mask = fighter_fights['bout_type'].str.contains('Title', case=False, na=False)
        title_fights = fighter_fights[title_mask]
        return title_fights
    
    return pd.DataFrame()

