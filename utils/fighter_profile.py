"""
Fighter profile display module.
Functions to get fighter data, format lore, and prepare stats for visualization.
"""

import pandas as pd
import numpy as np
import random
import re
from utils import themes


def get_fighter_profile(fighter_name, fighters_df):
    """
    Get complete fighter profile data.
    
    Args:
        fighter_name: Name of the fighter
        fighters_df: Fighters DataFrame
    
    Returns:
        Dictionary with fighter profile data, or None if not found
    """
    fighter_row = fighters_df[fighters_df['fighter'] == fighter_name]
    if len(fighter_row) == 0:
        return None
    
    fighter_row = fighter_row.iloc[0]
    
    # Extract key stats
    stats = {
        'strikes_per_min': fighter_row.get('strikes_landed_per_min_mean', 0) if pd.notna(fighter_row.get('strikes_landed_per_min_mean')) else 0,
        'strike_accuracy': fighter_row.get('strike_accuracy_mean', 0) if pd.notna(fighter_row.get('strike_accuracy_mean')) else 0,
        'head_strike_ratio': fighter_row.get('head_strike_ratio_mean', 0) if pd.notna(fighter_row.get('head_strike_ratio_mean')) else 0,
        'body_strike_ratio': fighter_row.get('body_strike_ratio_mean', 0) if pd.notna(fighter_row.get('body_strike_ratio_mean')) else 0,
        'leg_strike_ratio': fighter_row.get('leg_strike_ratio_mean', 0) if pd.notna(fighter_row.get('leg_strike_ratio_mean')) else 0,
        'takedown_accuracy': fighter_row.get('takedown_accuracy_mean', 0) if pd.notna(fighter_row.get('takedown_accuracy_mean')) else 0,
        'control_time_ratio': fighter_row.get('control_time_ratio_mean', 0) if pd.notna(fighter_row.get('control_time_ratio_mean')) else 0,
        'clinch_time_ratio': fighter_row.get('clinch_time_ratio_mean', 0) if pd.notna(fighter_row.get('clinch_time_ratio_mean')) else 0
    }
    
    # Personal details
    personal = {
        'age': fighter_row.get('age', None),
        'nationality': fighter_row.get('nationality', None),
        'height_inches': fighter_row.get('height_inches', None),
        'reach_inches': fighter_row.get('reach_inches', None),
        'stance': fighter_row.get('stance', None),
        'record': fighter_row.get('record', None),
        'wins': fighter_row.get('wins', None),
        'losses': fighter_row.get('losses', None),
        'draws': fighter_row.get('draws', None),
        'birthplace': fighter_row.get('birthplace', None)
    }
    
    # Other info
    other = {
        'lore': fighter_row.get('lore', ''),
        'fighting_style': fighter_row.get('fighting_style', None),
        'kmeans_cluster': fighter_row.get('kmeans_cluster', None)
    }
    
    return {
        'name': fighter_name,
        'stats': stats,
        'personal': personal,
        'other': other
    }


def generate_realistic_bio_detail(fighter_name, field_name, existing_value=None):
    """
    Generate realistic biographical details when data is missing (NaN).
    Creates varied, believable UFC fighter biographical information.
    
    Args:
        fighter_name: Fighter's name (for consistent generation)
        field_name: Field name (age, nationality, birthplace, etc.)
        existing_value: Existing value if available
    
    Returns:
        Realistic biographical detail
    """
    if existing_value and pd.notna(existing_value) and existing_value != '':
        return existing_value
    
    # Use name hash for consistent generation
    name_hash = hash(fighter_name) % 10000
    
    if field_name == 'nationality':
        # Common UFC fighter nationalities
        nationalities = [
            'United States', 'Brazil', 'Russia', 'Mexico', 'Canada', 'United Kingdom',
            'Ireland', 'Australia', 'Poland', 'Netherlands', 'Sweden', 'Norway',
            'Germany', 'France', 'Spain', 'Italy', 'Japan', 'South Korea',
            'China', 'Thailand', 'Philippines', 'Nigeria', 'South Africa',
            'Argentina', 'Chile', 'Colombia', 'Venezuela', 'Cuba', 'Puerto Rico'
        ]
        return nationalities[name_hash % len(nationalities)]
    
    elif field_name == 'birthplace':
        # Generate believable birthplace based on nationality
        birthplaces = [
            'Las Vegas, Nevada', 'Los Angeles, California', 'New York, New York',
            'Chicago, Illinois', 'Miami, Florida', 'Houston, Texas', 'Phoenix, Arizona',
            'Rio de Janeiro, Brazil', 'São Paulo, Brazil', 'Curitiba, Brazil',
            'Moscow, Russia', 'St. Petersburg, Russia', 'Dagestan, Russia',
            'Mexico City, Mexico', 'Guadalajara, Mexico', 'Tijuana, Mexico',
            'Toronto, Canada', 'Vancouver, Canada', 'Montreal, Canada',
            'London, England', 'Dublin, Ireland', 'Sydney, Australia',
            'Melbourne, Australia', 'Warsaw, Poland', 'Amsterdam, Netherlands',
            'Stockholm, Sweden', 'Oslo, Norway', 'Berlin, Germany',
            'Tokyo, Japan', 'Seoul, South Korea', 'Bangkok, Thailand',
            'Manila, Philippines', 'Lagos, Nigeria', 'Buenos Aires, Argentina'
        ]
        return birthplaces[name_hash % len(birthplaces)]
    
    elif field_name == 'age':
        # Generate realistic age (typically 20-40 for active fighters)
        base_age = 25 + (name_hash % 15)  # 25-39
        return base_age
    
    elif field_name == 'height_inches':
        # Generate realistic height (typically 65-78 inches for UFC fighters)
        base_height = 68 + (name_hash % 10)  # 68-77 inches
        return base_height
    
    elif field_name == 'reach_inches':
        # Generate realistic reach (typically equal to or slightly longer than height)
        if existing_value and pd.notna(existing_value):
            height = existing_value
        else:
            height = 70 + (name_hash % 8)  # 70-77
        
        # Reach is typically height + 0-4 inches
        reach_advantage = (name_hash % 5)  # 0-4 inches
        return height + reach_advantage
    
    elif field_name == 'stance':
        stances = ['Orthodox', 'Southpaw', 'Switch']
        return stances[name_hash % len(stances)]
    
    elif field_name == 'record':
        # Generate realistic record (e.g., "15-8-1")
        wins = 10 + (name_hash % 15)  # 10-24 wins
        losses = 3 + (name_hash % 10)  # 3-12 losses
        draws = name_hash % 2  # 0-1 draws
        return f"{wins}-{losses}-{draws}"
    
    elif field_name == 'wins':
        if existing_value and pd.notna(existing_value):
            return existing_value
        return 10 + (name_hash % 15)
    
    elif field_name == 'losses':
        if existing_value and pd.notna(existing_value):
            return existing_value
        return 3 + (name_hash % 10)
    
    elif field_name == 'draws':
        if existing_value and pd.notna(existing_value):
            return existing_value
        return name_hash % 2
    
    return None


def generate_extended_biography(fighter_profile, fighter_row, fighter_tags):
    """
    Generate an extended biography from thematic tags and fighter data.
    Creates a longer, more detailed narrative biography.
    
    Args:
        fighter_profile: Fighter profile dictionary
        fighter_row: Fighter DataFrame row
        fighter_tags: Dictionary with themes, fighting_style, character_archetypes
    
    Returns:
        Extended biography string (3-5 paragraphs)
    """
    fighter_name = fighter_profile['name']
    personal = fighter_profile['personal']
    stats = fighter_profile['stats']
    themes_list = fighter_tags.get('themes', [])
    archetypes = fighter_tags.get('character_archetypes', [])
    fighting_style = fighter_tags.get('fighting_style', 'Fighter')
    
    # Generate missing personal details
    nationality = generate_realistic_bio_detail(fighter_name, 'nationality', personal.get('nationality'))
    birthplace = generate_realistic_bio_detail(fighter_name, 'birthplace', personal.get('birthplace'))
    age = generate_realistic_bio_detail(fighter_name, 'age', personal.get('age'))
    height_inches = generate_realistic_bio_detail(fighter_name, 'height_inches', personal.get('height_inches'))
    reach_inches = generate_realistic_bio_detail(fighter_name, 'reach_inches', personal.get('reach_inches'))
    stance = generate_realistic_bio_detail(fighter_name, 'stance', personal.get('stance'))
    
    # Get record info - handle NaN properly
    wins_val = personal.get('wins')
    if pd.isna(wins_val) or wins_val is None or wins_val == '':
        wins = generate_realistic_bio_detail(fighter_name, 'wins')
    else:
        try:
            wins = int(float(wins_val))
        except:
            wins = generate_realistic_bio_detail(fighter_name, 'wins')
    
    losses_val = personal.get('losses')
    if pd.isna(losses_val) or losses_val is None or losses_val == '':
        losses = generate_realistic_bio_detail(fighter_name, 'losses')
    else:
        try:
            losses = int(float(losses_val))
        except:
            losses = generate_realistic_bio_detail(fighter_name, 'losses')
    
    draws_val = personal.get('draws')
    if pd.isna(draws_val) or draws_val is None or draws_val == '':
        draws = generate_realistic_bio_detail(fighter_name, 'draws')
    else:
        try:
            draws = int(float(draws_val))
        except:
            draws = generate_realistic_bio_detail(fighter_name, 'draws')
    
    total_fights = wins + losses + draws
    win_rate = wins / total_fights if total_fights > 0 else 0
    record_str = f"{wins}-{losses}-{draws}"
    
    # Use name hash for consistent generation
    name_hash = hash(fighter_name) % 10000
    
    # Build biography paragraphs
    bio_paragraphs = []
    
    # Paragraph 1: Early life and background
    early_life_templates = [
        f"Born in {birthplace}, {fighter_name} discovered combat sports at a young age, {['training in local gyms', 'competing in youth tournaments', 'watching fights with family', 'joining a local martial arts academy'][name_hash % 4]}.",
        f"Hailing from {birthplace}, {fighter_name} grew up {['in a working-class neighborhood', 'in a small town', 'in the city', 'in a rural area'][name_hash % 4]}, where they {['first stepped into a gym', 'discovered their passion for fighting', 'began their martial arts journey', 'found their calling'][name_hash % 4]}.",
        f"Originally from {birthplace}, {fighter_name} {['began training', 'started their journey', 'entered the world of combat sports', 'discovered fighting'][name_hash % 4]} {['as a teenager', 'in their early twenties', 'after high school', 'following a personal challenge'][name_hash % 4]}.",
    ]
    
    # Add nationality context
    if 'immigrant_story' in themes_list:
        early_life_templates.append(
            f"Born in {birthplace}, {fighter_name} moved to pursue their fighting dreams, bringing {['their family traditions', 'their cultural heritage', 'their determination', 'their unique style'][name_hash % 4]} to the octagon."
        )
    
    bio_paragraphs.append(early_life_templates[name_hash % len(early_life_templates)])
    
    # Paragraph 2: Fighting style and approach
    style_paragraphs = []
    
    if 'volume_striker_narrative' in themes_list or 'aggression' in themes_list:
        style_paragraphs.append(
            f"In the octagon, {fighter_name} is known as a {fighting_style.lower()} who {['overwhelms', 'bombards', 'assaults', 'pressures'][name_hash % 4]} opponents with {stats['strikes_per_min']:.1f} strikes per minute, {['creating constant pressure', 'never letting up', 'maintaining relentless output', 'keeping opponents on the defensive'][name_hash % 4]}."
        )
    elif 'precision_striker_narrative' in themes_list or 'precision' in themes_list:
        style_paragraphs.append(
            f"As a {fighting_style.lower()}, {fighter_name} {['excels', 'thrives', 'dominates', 'reigns'][name_hash % 4]} through {['surgical precision', 'methodical accuracy', 'calculated strikes', 'technical mastery'][name_hash % 4]}, landing {stats['strike_accuracy']*100:.0f}% of their strikes with {['devastating', 'deadly', 'remarkable', 'exceptional'][name_hash % 4]} accuracy."
        )
    elif 'grappler_narrative' in themes_list:
        style_paragraphs.append(
            f"{fighter_name} {['excels', 'dominates', 'reigns', 'thrives'][name_hash % 4]} as a {fighting_style.lower()}, {['bringing', 'taking', 'dragging', 'forcing'][name_hash % 4]} fights to the ground with {stats['takedown_accuracy']*100:.0f}% takedown accuracy and {['controlling', 'dominating', 'dictating', 'commanding'][name_hash % 4]} opponents with {stats['control_time_ratio']*100:.0f}% control time."
        )
    else:
        style_paragraphs.append(
            f"{fighter_name} brings a {fighting_style.lower()} approach to every fight, {['combining', 'merging', 'blending', 'uniting'][name_hash % 4]} {['striking and grappling', 'power and technique', 'speed and precision', 'aggression and strategy'][name_hash % 4]} into a {['formidable', 'dangerous', 'threatening', 'complete'][name_hash % 4]} skill set."
        )
    
    # Add physical attributes
    if height_inches and reach_inches:
        height_ft = int(height_inches // 12)
        height_in = int(height_inches % 12)
        reach_ft = int(reach_inches // 12)
        reach_in = int(reach_inches % 12)
        reach_advantage = reach_inches - height_inches
        
        if reach_advantage > 3:
            style_paragraphs[0] += f" Standing {height_ft}'{height_in}\" with an exceptional {reach_ft}'{reach_in}\" reach, they use their physical advantages to {['control distance', 'dictate the pace', 'keep opponents at bay', 'create openings'][name_hash % 4]}."
        elif reach_advantage < -2:
            style_paragraphs[0] += f" At {height_ft}'{height_in}\" with a {reach_ft}'{reach_in}\" reach, they compensate for physical limitations with {['relentless pressure', 'technical precision', 'explosive power', 'tactical brilliance'][name_hash % 4]}."
        else:
            style_paragraphs[0] += f" With a solid {height_ft}'{height_in}\" frame and {reach_ft}'{reach_in}\" reach, they bring {['well-rounded skills', 'balanced attributes', 'versatile tools', 'complete arsenal'][name_hash % 4]} to every bout."
    
    bio_paragraphs.append(style_paragraphs[0])
    
    # Paragraph 3: Career narrative
    career_paragraphs = []
    
    if 'veteran_wisdom' in themes_list or 'legacy' in themes_list:
        career_paragraphs.append(
            f"Now {age} years old with a professional record of {record_str}, {fighter_name} brings {['veteran savvy', 'hard-earned wisdom', 'tested experience', 'championship-level composure'][name_hash % 4]} to every fight. Through {total_fights} professional bouts, they have {['proven their mettle', 'shown consistency', 'demonstrated resilience', 'earned respect'][name_hash % 4]} against elite competition."
        )
    elif 'rookie_rise' in themes_list or 'rise_to_glory' in themes_list:
        career_paragraphs.append(
            f"At just {age} years old, {fighter_name} represents {['the next generation', 'a rising star', 'new blood', 'the future'][name_hash % 4]} of mixed martial arts. With a {record_str} record, they have {['already shown championship potential', 'quickly climbed the rankings', 'turned heads with every performance', 'proven age is just a number'][name_hash % 4]}."
        )
    elif 'comeback_story' in themes_list or 'redemption' in themes_list:
        career_paragraphs.append(
            f"After {['facing setbacks', 'overcoming challenges', 'enduring hardships', 'fighting through adversity'][name_hash % 4]}, {fighter_name} has {['bounced back', 'returned stronger', 'made a comeback', 'proven their resilience'][name_hash % 4]} with a {record_str} record, {['showing', 'demonstrating', 'proving', 'exhibiting'][name_hash % 4]} that {['determination', 'heart', 'will', 'spirit'][name_hash % 4]} can overcome any obstacle."
        )
    elif 'underdog' in themes_list:
        career_paragraphs.append(
            f"Despite a challenging {record_str} record, {fighter_name} continues to {['compete with heart', 'fight with determination', 'show resilience', 'defy expectations'][name_hash % 4]}. They have {['proven', 'shown', 'demonstrated', 'exhibited'][name_hash % 4]} that {['heart', 'determination', 'will', 'spirit'][name_hash % 4]} can overcome {['statistics', 'odds', 'expectations', 'predictions'][name_hash % 4]}."
        )
    else:
        career_paragraphs.append(
            f"With a professional record of {record_str}, {fighter_name} has {['established themselves', 'made their mark', 'proven their worth', 'earned recognition'][name_hash % 4]} in the sport. Through {total_fights} professional fights, they have {['shown consistency', 'demonstrated skill', 'proven their mettle', 'earned respect'][name_hash % 4]} against {['top-level', 'elite', 'world-class', 'championship-caliber'][name_hash % 4]} competition."
        )
    
    bio_paragraphs.append(career_paragraphs[0])
    
    # Paragraph 4: Character and themes
    if archetypes or themes_list:
        character_paragraphs = []
        
        if 'warrior' in archetypes:
            character_paragraphs.append(
                f"{fighter_name} embodies the {['warrior spirit', 'fighter mentality', 'combat ethos', 'fighting spirit'][name_hash % 4]}, {['approaching', 'entering', 'stepping into', 'facing'][name_hash % 4]} every fight with {['unwavering determination', 'relentless drive', 'fierce resolve', 'unbreakable will'][name_hash % 4]}."
            )
        elif 'veteran' in archetypes:
            character_paragraphs.append(
                f"As a {['seasoned veteran', 'experienced fighter', 'battle-tested warrior', 'proven competitor'][name_hash % 4]}, {fighter_name} brings {['wisdom', 'knowledge', 'experience', 'savvy'][name_hash % 4]} that can only be {['earned', 'gained', 'learned', 'acquired'][name_hash % 4]} through {['years', 'countless hours', 'decades', 'a lifetime'][name_hash % 4]} in the sport."
            )
        elif 'prodigy' in archetypes:
            character_paragraphs.append(
                f"{fighter_name} represents {['raw talent', 'natural ability', 'innate skill', 'gifted potential'][name_hash % 4]} combined with {['dedicated training', 'hard work', 'relentless practice', 'unwavering commitment'][name_hash % 4]}, {['creating', 'forming', 'building', 'developing'][name_hash % 4]} a {['formidable', 'dangerous', 'threatening', 'exceptional'][name_hash % 4]} combination."
            )
        
        # Add theme-based character description
        if 'determination' in themes_list:
            character_paragraphs.append(
                f"Their {['unwavering determination', 'relentless drive', 'fierce resolve', 'unbreakable will'][name_hash % 4]} has {['carried', 'guided', 'driven', 'propelled'][name_hash % 4]} them through {['every challenge', 'countless obstacles', 'numerous trials', 'endless adversity'][name_hash % 4]}."
            )
        elif 'resilience' in themes_list:
            character_paragraphs.append(
                f"{fighter_name} has {['demonstrated', 'shown', 'proven', 'exhibited'][name_hash % 4]} {['remarkable resilience', 'incredible toughness', 'exceptional durability', 'unbreakable spirit'][name_hash % 4]}, {['bouncing back', 'returning stronger', 'overcoming setbacks', 'rising again'][name_hash % 4]} from {['every defeat', 'every challenge', 'every obstacle', 'every setback'][name_hash % 4]}."
            )
        
        if character_paragraphs:
            bio_paragraphs.append(character_paragraphs[0])
    
    # Join paragraphs
    biography = " ".join(bio_paragraphs)
    
    # Clean up
    biography = re.sub(r'\s+', ' ', biography)
    biography = re.sub(r'\s+([,.!?])', r'\1', biography)
    biography = biography.strip()
    
    # Ensure proper ending
    if not biography.endswith(('.', '!', '?')):
        biography += "."
    
    # Capitalize first letter
    if biography:
        biography = biography[0].upper() + biography[1:] if len(biography) > 1 else biography.upper()
    
    return biography


def format_fighter_lore(lore):
    """
    Format fighter lore for display.
    
    Args:
        lore: Lore string
    
    Returns:
        Formatted lore string
    """
    if pd.isna(lore) or not lore or lore == '':
        return "No lore available for this fighter."
    
    # Clean up the lore
    lore = str(lore).strip()
    
    # Ensure proper sentence endings
    if not lore.endswith(('.', '!', '?')):
        lore += "."
    
    return lore


def get_fighter_stats_for_chart(fighter_profile):
    """
    Prepare fighter stats for visualization.
    Returns normalized stats for radar/bar charts.
    
    Args:
        fighter_profile: Fighter profile dictionary
    
    Returns:
        Dictionary with stat names and values (normalized 0-1)
    """
    if fighter_profile is None:
        return {}
    
    stats = fighter_profile['stats']
    
    # Normalize stats to 0-1 range for visualization
    # Use reasonable max values based on UFC data
    max_values = {
        'strikes_per_min': 8.0,
        'strike_accuracy': 1.0,
        'head_strike_ratio': 1.0,
        'body_strike_ratio': 1.0,
        'leg_strike_ratio': 1.0,
        'takedown_accuracy': 1.0,
        'control_time_ratio': 1.0,
        'clinch_time_ratio': 1.0
    }
    
    normalized_stats = {}
    for stat_name, value in stats.items():
        max_val = max_values.get(stat_name, 1.0)
        normalized_stats[stat_name] = min(1.0, max(0.0, value / max_val)) if max_val > 0 else 0.0
    
    return normalized_stats


def format_height_reach(height_inches, reach_inches):
    """
    Format height and reach for display.
    
    Args:
        height_inches: Height in inches
        reach_inches: Reach in inches
    
    Returns:
        Formatted string
    """
    if pd.isna(height_inches) or height_inches == 0:
        return "N/A"
    
    height_ft = int(height_inches // 12)
    height_in = int(height_inches % 12)
    
    if pd.isna(reach_inches) or reach_inches == 0:
        return f"{height_ft}'{height_in}\""
    
    reach_ft = int(reach_inches // 12)
    reach_in = int(reach_inches % 12)
    reach_advantage = reach_inches - height_inches
    
    if reach_advantage > 3:
        advantage_str = f" (+{int(reach_advantage)}\" reach)"
    elif reach_advantage < -2:
        advantage_str = f" ({int(reach_advantage)}\" reach)"
    else:
        advantage_str = ""
    
    return f"{height_ft}'{height_in}\" / {reach_ft}'{reach_in}\"{advantage_str}"

