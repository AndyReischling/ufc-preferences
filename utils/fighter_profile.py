"""
Fighter profile display module.
Functions to get fighter data, format lore, and prepare stats for visualization.
"""

import pandas as pd
import numpy as np
import random
import re
import os
from utils import themes

# Load environment variables from .env file if it exists (local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, will use system env vars

# Try to load from Streamlit secrets (for Streamlit Cloud deployment)
try:
    import streamlit as st
    try:
        if hasattr(st, 'secrets') and st.secrets is not None:
            if 'llm_api' in st.secrets:
                USE_API_FOR_BIO = st.secrets['llm_api'].get('use_for_bio', 'true').lower() == 'true'
            else:
                USE_API_FOR_BIO = os.getenv('USE_API_FOR_BIO', 'false').lower() == 'true'
        else:
            USE_API_FOR_BIO = os.getenv('USE_API_FOR_BIO', 'false').lower() == 'true'
    except (FileNotFoundError, AttributeError, KeyError):
        # Secrets not available, use environment variables
        USE_API_FOR_BIO = os.getenv('USE_API_FOR_BIO', 'false').lower() == 'true'
except (ImportError, RuntimeError):
    # Not in Streamlit context, use environment variables
    USE_API_FOR_BIO = os.getenv('USE_API_FOR_BIO', 'false').lower() == 'true'

# Try to import API generation function if available
try:
    from generate_unique_lore import generate_extended_biography_with_api
except ImportError:
    USE_API_FOR_BIO = False
    generate_extended_biography_with_api = None


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
    Generate an extended biography with UNIQUE writing styles for each fighter.
    Uses 12+ distinct narrative structures, tones, and sentence patterns.
    Makes explicit connections between themes, fighting style, and lore.
    No API key needed - uses template-based generation with maximum variety.
    
    Args:
        fighter_profile: Fighter profile dictionary
        fighter_row: Fighter DataFrame row
        fighter_tags: Dictionary with themes, fighting_style, character_archetypes
    
    Returns:
        Extended biography string (5-8 paragraphs) with unique writing style and explicit theme explanations
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
    
    # Get record info
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
    
    # Multiple hashes for maximum variety
    name_hash = hash(fighter_name) % 10000
    style_hash = hash(fighter_name + "style") % 12  # 12 different writing styles
    tone_hash = hash(fighter_name + "tone") % 10000
    struct_hash = hash(fighter_name + "struct") % 10000
    
    # Select writing style (0-11 = 12 unique styles)
    writing_style = style_hash
    
    # Format physical stats
    height_ft = int(height_inches // 12) if height_inches else None
    height_in = int(height_inches % 12) if height_inches else None
    reach_ft = int(reach_inches // 12) if reach_inches else None
    reach_in = int(reach_inches % 12) if reach_inches else None
    reach_advantage = (reach_inches - height_inches) if (height_inches and reach_inches) else 0
    
    # Helper function to add subtle, journalistic theme connections
    def add_theme_explanations(paragraphs, stats, themes_list, fighter_name, total_fights, wins, losses, win_rate, record_str, age):
        """Add paragraphs with subtle, NYT-style connections to themes - show don't tell"""
        # High volume striker - subtle description
        if stats['strikes_per_min'] > 5.5:
            paragraphs.append(f"In the octagon, {fighter_name} operates at a relentless pace, averaging {stats['strikes_per_min']:.1f} significant strikes per minute. Opponents describe fighting {fighter_name} as 'like being caught in a storm'—there's no respite, no moment to reset. The constant pressure forces mistakes, breaks rhythm, and gradually erodes an opponent's will. It's a style built on volume and persistence, where the accumulation of strikes matters more than any single blow.")
        elif stats['strike_accuracy'] > 0.55:
            paragraphs.append(f"What sets {fighter_name} apart is surgical precision. With {stats['strike_accuracy']*100:.0f}% strike accuracy, every shot is measured, every strike purposeful. There's no wasted motion, no wild swings. Instead, {fighter_name} methodically breaks down opponents, finding openings others miss, landing clean shots when they matter most. It's a patient approach that values quality over quantity, where timing and placement trump raw power.")
        
        # Grappling - subtle description
        if stats['takedown_accuracy'] > 0.4:
            paragraphs.append(f"When the fight goes to the ground, {fighter_name} takes control. Their {stats['takedown_accuracy']*100:.0f}% takedown success rate reflects a fighter who can dictate where the fight takes place. They don't simply react to opportunities; they create them, setting up takedowns with striking combinations, controlling positions once they get there. It's a chess match played at full speed, where every move is calculated and every transition planned.")
        
        # Career narrative - subtle and journalistic
        if 'championship_quest' in themes_list or win_rate > 0.7:
            paragraphs.append(f"The numbers tell a story: {wins} victories, a {win_rate*100:.0f}% win rate, a {record_str} record that speaks to consistency at the highest level. Each win has been another step forward, another test passed. There's a sense of momentum building, of a fighter who knows where they're going and has the discipline to get there. The path isn't easy—it never is—but {fighter_name} has shown they can navigate it.")
        
        if 'resilience' in themes_list and losses > 0:
            paragraphs.append(f"The record shows {losses} defeats, but it also shows how {fighter_name} responded to them. After each loss, they returned—sometimes immediately, sometimes after taking time to rebuild. The pattern is consistent: setback, reflection, return, improvement. It's a career marked not by the absence of failure, but by the refusal to let failure define them. The losses taught lessons; the comebacks proved they learned them.")
        
        if 'veteran_wisdom' in themes_list or total_fights > 15:
            paragraphs.append(f"After {total_fights} professional bouts, {fighter_name} has seen nearly everything the sport can offer. The experience shows in the small details: how they read opponents, how they adjust mid-fight, how they stay calm when others panic. There's a depth to their game that only comes with time—not just technical skill, but tactical understanding, the kind of knowledge that can't be taught, only earned.")
        
        if 'rookie_rise' in themes_list or (age and age < 28 and total_fights < 10):
            paragraphs.append(f"At this stage of their career, {fighter_name} represents possibility. The {record_str} record suggests promise, but more than that, it suggests potential. They're still learning, still growing, still discovering what they're capable of. Each fight reveals something new, each victory opens another door. The trajectory is upward, and the ceiling is still unknown.")
    
    bio_paragraphs = []
    
    # STYLE 0: Journalistic/Reportage
    if writing_style == 0:
        bio_paragraphs.append(f"{fighter_name}, {age}, hails from {birthplace} and carries a professional record of {record_str}. The {nationality} fighter has competed in {total_fights} professional bouts, establishing a reputation as a {fighting_style.lower()}.")
        height_reach_str = ""
        if height_inches and reach_inches:
            height_reach_str = f"Standing {height_ft}'{height_in}\" with a {reach_ft}'{reach_in}\" reach, "
        bio_paragraphs.append(f"In the octagon, {fighter_name} averages {stats['strikes_per_min']:.1f} strikes per minute with {stats['strike_accuracy']*100:.0f}% accuracy. {height_reach_str}The fighter employs a {stance.lower()} stance and has demonstrated {'exceptional' if win_rate > 0.7 else 'solid' if win_rate > 0.5 else 'determined'} performance throughout their career.")
        
        # Explain fighting style and its connection to themes
        if stats['strikes_per_min'] > 5.5:
            bio_paragraphs.append(f"Their high-volume striking approach—averaging {stats['strikes_per_min']:.1f} significant strikes per minute—reflects a relentless, pressure-fighting style that overwhelms opponents through constant activity. This aggressive methodology explains why {fighter_name} embodies themes of aggression and pressure fighting, as their fighting philosophy centers on dictating pace and never allowing opponents to find rhythm.")
        elif stats['strike_accuracy'] > 0.55:
            bio_paragraphs.append(f"With a remarkable {stats['strike_accuracy']*100:.0f}% strike accuracy rate, {fighter_name} exemplifies precision striking—every shot calculated, every strike meaningful. This surgical approach to combat demonstrates why themes of precision and technical mastery define their narrative, as they prioritize quality over quantity, methodically breaking down opponents with measured, accurate attacks.")
        
        if stats['takedown_accuracy'] > 0.4:
            bio_paragraphs.append(f"Their grappling prowess is evident in a {stats['takedown_accuracy']*100:.0f}% takedown accuracy rate, showcasing a strategic, controlling approach to combat. This ability to dictate where fights take place—whether standing or on the ground—illustrates why themes of strategy and discipline are central to {fighter_name}'s fighting identity, as they methodically control every aspect of their bouts.")
        
        # Connect themes to lore and career narrative
        if 'veteran_wisdom' in themes_list:
            bio_paragraphs.append(f"With {total_fights} fights under their belt, {fighter_name} brings experience and tactical knowledge to every matchup. This extensive career experience directly connects to themes of veteran wisdom and legacy—each fight has taught valuable lessons, and their ability to adapt and evolve demonstrates the maturity that comes from years of competition at the highest level.")
        
        if 'championship_quest' in themes_list or 'triumph' in themes_list:
            bio_paragraphs.append(f"Their {record_str} record, featuring {wins} victories, reflects a championship-caliber fighter whose career narrative embodies themes of triumph and championship quest. Each win represents another step toward greatness, and their {'dominant' if win_rate > 0.7 else 'consistent'} performance record demonstrates the determination required to compete at the elite level.")
        
        if 'resilience' in themes_list or 'comeback_story' in themes_list:
            bio_paragraphs.append(f"Despite {losses} defeats, {fighter_name} has consistently bounced back, demonstrating remarkable resilience. This ability to overcome adversity connects directly to themes of resilience and comeback stories—their career is defined not by setbacks, but by how they've responded to them, showing the mental fortitude required to succeed in mixed martial arts.")
    
    # STYLE 1: Poetic/Lyrical
    elif writing_style == 1:
        bio_paragraphs.append(f"From the streets of {birthplace} emerges {fighter_name}—a {fighting_style.lower()} whose journey began {'in youth' if age < 30 else 'years ago'} and has led to {total_fights} professional battles.")
        frame_str = f"Their {height_ft}'{height_in}\" frame, " if height_inches else ""
        bio_paragraphs.append(f"Each strike tells a story: {stats['strikes_per_min']:.1f} per minute, {stats['strike_accuracy']*100:.0f}% finding their mark. {frame_str}their {stance.lower()} stance, their {record_str} record—all woven into the fabric of a fighter who {'dominates' if win_rate > 0.7 else 'perseveres' if win_rate > 0.5 else 'fights'} with {'precision' if stats['strike_accuracy'] > 0.5 else 'relentless determination'}.")
        
        # Add subtle, journalistic theme connections
        add_theme_explanations(bio_paragraphs, stats, themes_list, fighter_name, total_fights, wins, losses, win_rate, record_str, age)
    
    # STYLE 2: Technical/Analytical
    elif writing_style == 2:
        bio_paragraphs.append(f"Technical analysis of {fighter_name} ({age}, {nationality}): Born in {birthplace}, currently holding a {record_str} professional record across {total_fights} bouts.")
        physical_str = f"Physical attributes: {height_ft}'{height_in}\" height, {reach_ft}'{reach_in}\" reach. " if height_inches and reach_inches else ""
        takedown_str = f"Takedown accuracy: {stats['takedown_accuracy']*100:.0f}%." if stats['takedown_accuracy'] > 0 else "Striking-focused approach."
        bio_paragraphs.append(f"Performance metrics: {stats['strikes_per_min']:.1f} SLpM (significant strikes landed per minute), {stats['strike_accuracy']*100:.0f}% accuracy rate. {physical_str}Stance: {stance}. {takedown_str}")
        bio_paragraphs.append(f"Win rate analysis: {win_rate*100:.0f}% ({wins}W-{losses}L-{draws}D). {'High-performance fighter' if win_rate > 0.7 else 'Competitive record' if win_rate > 0.5 else 'Developing fighter'} with {'strong finishing ability' if win_rate > 0.7 else 'consistent performance' if win_rate > 0.5 else 'potential for growth'}.")
        
        # Add subtle, journalistic theme connections
        add_theme_explanations(bio_paragraphs, stats, themes_list, fighter_name, total_fights, wins, losses, win_rate, record_str, age)
    
    # STYLE 3: Storytelling/Narrative
    elif writing_style == 3:
        bio_paragraphs.append(f"The story of {fighter_name} begins in {birthplace}, where a {age}-year-old {nationality} athlete discovered their calling in mixed martial arts.")
        height_reach_desc = f"At {height_ft}'{height_in}\" with a {reach_ft}'{reach_in}\" reach, " if height_inches and reach_inches else ""
        bio_paragraphs.append(f"Today, {fighter_name} steps into the octagon as a {fighting_style.lower()}—someone who {'delivers' if stats['strikes_per_min'] > 5 else 'executes'} {stats['strikes_per_min']:.1f} strikes per minute with {'surgical' if stats['strike_accuracy'] > 0.5 else 'devastating'} {stats['strike_accuracy']*100:.0f}% accuracy. {height_reach_desc}Their {stance.lower()} stance has become their signature.")
        bio_paragraphs.append(f"With {wins} victories against {losses} defeats, {fighter_name} {'has proven themselves a force to be reckoned with' if win_rate > 0.7 else 'continues to build their legacy' if win_rate > 0.5 else 'fights with heart and determination'} in every bout.")
        
        # Add subtle theme connections
        add_theme_explanations(bio_paragraphs, stats, themes_list, fighter_name, total_fights, wins, losses, win_rate, record_str, age)
    
    # STYLE 4: Dramatic/Intense
    elif writing_style == 4:
        bio_paragraphs.append(f"{fighter_name}—{age} years old, {nationality}, born in {birthplace}. A {fighting_style.lower()} with {total_fights} fights and a {record_str} record that speaks to {'dominance' if win_rate > 0.7 else 'resilience' if win_rate > 0.5 else 'determination'}.")
        frame_desc = ""
        if height_inches:
            if height_inches > 72:
                frame_desc = f"Their {height_ft}'{height_in}\" frame towers"
            else:
                frame_desc = f"Standing {height_ft}'{height_in}\""
        reach_desc = f" with a {reach_ft}'{reach_in}\" reach" if reach_inches else ""
        bio_paragraphs.append(f"In the cage, {fighter_name} is {'relentless' if stats['strikes_per_min'] > 5 else 'methodical'}—{stats['strikes_per_min']:.1f} strikes per minute, {stats['strike_accuracy']*100:.0f}% accuracy. {frame_desc}{reach_desc}. {stance} stance. {'Every fight is a war' if stats['strikes_per_min'] > 6 else 'Every strike is calculated'}.")
        if 'aggression' in themes_list:
            bio_paragraphs.append(f"{fighter_name} doesn't just fight—they {'overwhelm' if stats['strikes_per_min'] > 6 else 'dominate'}, {'destroy' if win_rate > 0.7 else 'conquer'}, {'annihilate' if stats['strike_accuracy'] > 0.6 else 'devastate'} opponents.")
        
        # Add subtle theme connections
        add_theme_explanations(bio_paragraphs, stats, themes_list, fighter_name, total_fights, wins, losses, win_rate, record_str, age)
    
    # STYLE 5: Conversational/Casual
    elif writing_style == 5:
        bio_paragraphs.append(f"Meet {fighter_name}—{age}, from {birthplace}, {nationality}. They've got a {record_str} record after {total_fights} fights, and they're known as a {fighting_style.lower()}.")
        height_desc = f"They stand {height_ft}'{height_in}\" tall" if height_inches else ""
        reach_desc = f" with a {reach_ft}'{reach_in}\" reach" if reach_inches else ""
        bio_paragraphs.append(f"When {fighter_name} fights, you're looking at {stats['strikes_per_min']:.1f} strikes per minute with {stats['strike_accuracy']*100:.0f}% accuracy. {height_desc}{reach_desc}, fight {stance.lower()}, and have a {'pretty solid' if win_rate > 0.6 else 'decent' if win_rate > 0.5 else 'tough'} record.")
        bio_paragraphs.append(f"With {wins} wins under their belt, {fighter_name} {'is definitely someone to watch' if win_rate > 0.7 else 'keeps improving with every fight' if win_rate > 0.5 else 'never gives up, no matter what'}.")
        
        # Add subtle theme connections
        add_theme_explanations(bio_paragraphs, stats, themes_list, fighter_name, total_fights, wins, losses, win_rate, record_str, age)
    
    # STYLE 6: Biographical/Historical
    elif writing_style == 6:
        bio_paragraphs.append(f"{fighter_name} was born in {birthplace} in {2024 - age if age else 'an unknown year'}. The {nationality} fighter began their professional career and has since compiled a {record_str} record across {total_fights} professional bouts.")
        physical_measurements = f"Physical measurements: {height_ft}'{height_in}\" height, {reach_ft}'{reach_in}\" reach. " if height_inches and reach_inches else ""
        bio_paragraphs.append(f"Throughout their career, {fighter_name} has established themselves as a {fighting_style.lower()} with notable statistics: {stats['strikes_per_min']:.1f} strikes per minute, {stats['strike_accuracy']*100:.0f}% accuracy. {physical_measurements}Stance: {stance}.")
        bio_paragraphs.append(f"Career highlights include {wins} victories, {'demonstrating exceptional skill' if win_rate > 0.7 else 'showing consistent performance' if win_rate > 0.5 else 'displaying remarkable determination'} throughout their time in the sport.")
        
        # Add subtle theme connections
        add_theme_explanations(bio_paragraphs, stats, themes_list, fighter_name, total_fights, wins, losses, win_rate, record_str, age)
    
    # STYLE 7: Action-Packed/Thriller
    elif writing_style == 7:
        bio_paragraphs.append(f"{fighter_name} explodes from {birthplace}—{age} years old, {nationality}, {record_str} record, {total_fights} fights. A {fighting_style.lower()} who {'dominates' if win_rate > 0.7 else 'fights'} with {'brutal' if stats['strikes_per_min'] > 6 else 'surgical'} precision.")
        height_reach_info = f"At {height_ft}'{height_in}\" with {reach_ft}'{reach_in}\" reach, " if height_inches and reach_inches else ""
        bio_paragraphs.append(f"{stats['strikes_per_min']:.1f} strikes per minute. {stats['strike_accuracy']*100:.0f}% accuracy. {height_reach_info}{fighter_name} uses their {stance.lower()} stance to {'devastate' if stats['strike_accuracy'] > 0.5 else 'overwhelm'} opponents.")
        bio_paragraphs.append(f"{wins} wins. {losses} losses. {'Every victory is a statement' if win_rate > 0.7 else 'Every fight is a battle' if win_rate > 0.5 else 'Every round is a war'}.")
        
        # Add subtle theme connections
        add_theme_explanations(bio_paragraphs, stats, themes_list, fighter_name, total_fights, wins, losses, win_rate, record_str, age)
    
    # STYLE 8: Reflective/Philosophical
    elif writing_style == 8:
        bio_paragraphs.append(f"In {birthplace}, {fighter_name} found their path—a journey that has led to {total_fights} professional fights and a {record_str} record at {age} years old.")
        frame_desc = f"Their {height_ft}'{height_in}\" frame, " if height_inches else ""
        reach_desc = f"their {reach_ft}'{reach_in}\" reach, " if reach_inches else ""
        bio_paragraphs.append(f"As a {fighting_style.lower()}, {fighter_name} {'delivers' if stats['strikes_per_min'] > 5 else 'executes'} {stats['strikes_per_min']:.1f} strikes per minute with {stats['strike_accuracy']*100:.0f}% accuracy. {frame_desc}{reach_desc}their {stance.lower()} stance—each element {'contributes to' if win_rate > 0.6 else 'reflects'} their approach to combat.")
        bio_paragraphs.append(f"With {wins} victories, {fighter_name} {'has learned that success comes from' if win_rate > 0.7 else 'understands that' if win_rate > 0.5 else 'knows that'} {'precision beats power' if stats['strike_accuracy'] > 0.5 else 'persistence overcomes all'}.")
        
        # Add subtle theme connections
        add_theme_explanations(bio_paragraphs, stats, themes_list, fighter_name, total_fights, wins, losses, win_rate, record_str, age)
    
    # STYLE 9: Statistical/Fact-Based
    elif writing_style == 9:
        bio_paragraphs.append(f"Fighter: {fighter_name}. Age: {age}. Nationality: {nationality}. Birthplace: {birthplace}. Record: {record_str} ({total_fights} fights). Classification: {fighting_style.lower()}.")
        height_reach_stats = f"Height: {height_ft}'{height_in}\". Reach: {reach_ft}'{reach_in}\". " if height_inches and reach_inches else ""
        bio_paragraphs.append(f"Combat statistics: Strikes landed per minute: {stats['strikes_per_min']:.1f}. Strike accuracy: {stats['strike_accuracy']*100:.0f}%. {height_reach_stats}Stance: {stance}. Win rate: {win_rate*100:.0f}%.")
        bio_paragraphs.append(f"Performance summary: {wins} wins, {losses} losses, {draws} draws. {'Elite-level performance' if win_rate > 0.7 else 'Competitive record' if win_rate > 0.5 else 'Developing fighter'}.")
        
        # Add subtle theme connections
        add_theme_explanations(bio_paragraphs, stats, themes_list, fighter_name, total_fights, wins, losses, win_rate, record_str, age)
    
    # STYLE 10: Inspirational/Motivational
    elif writing_style == 10:
        bio_paragraphs.append(f"{fighter_name} proves that {'champions are made, not born' if win_rate > 0.7 else 'hard work pays off' if win_rate > 0.5 else 'determination conquers all'}. From {birthplace}, this {age}-year-old {nationality} {fighting_style.lower()} has built a {record_str} record through {total_fights} fights.")
        height_reach_desc = f"Standing {height_ft}'{height_in}\" with a {reach_ft}'{reach_in}\" reach, " if height_inches and reach_inches else ""
        bio_paragraphs.append(f"With {stats['strikes_per_min']:.1f} strikes per minute and {stats['strike_accuracy']*100:.0f}% accuracy, {fighter_name} {'demonstrates' if stats['strike_accuracy'] > 0.5 else 'shows'} that {'precision and power' if stats['strikes_per_min'] > 5 else 'skill and strategy'} can coexist. {height_reach_desc}Their {stance.lower()} stance is a testament to {'years of training' if age > 30 else 'dedicated practice'}.")
        bio_paragraphs.append(f"{wins} victories stand as proof that {fighter_name} {'has what it takes' if win_rate > 0.7 else 'never backs down' if win_rate > 0.5 else 'fights with heart'}.")
        
        # Add subtle theme connections
        add_theme_explanations(bio_paragraphs, stats, themes_list, fighter_name, total_fights, wins, losses, win_rate, record_str, age)
    
    # STYLE 11: Minimalist/Concise
    elif writing_style == 11:
        bio_paragraphs.append(f"{fighter_name}. {age}. {birthplace}, {nationality}. {record_str} ({total_fights} fights). {fighting_style.lower()}.")
        height_reach_short = f"H: {height_ft}'{height_in}\" R: {reach_ft}'{reach_in}\". " if height_inches and reach_inches else ""
        bio_paragraphs.append(f"{stats['strikes_per_min']:.1f} SLpM. {stats['strike_accuracy']*100:.0f}% accuracy. {height_reach_short}{stance}.")
        bio_paragraphs.append(f"{wins}W-{losses}L-{draws}D. {'Elite' if win_rate > 0.7 else 'Solid' if win_rate > 0.5 else 'Fighter'}.")
        
        # Add subtle theme connections (minimalist style - brief but journalistic)
        if stats['strikes_per_min'] > 5.5:
            bio_paragraphs.append(f"Relentless pace: {stats['strikes_per_min']:.1f} strikes per minute. Opponents find no respite.")
        elif stats['strike_accuracy'] > 0.55:
            bio_paragraphs.append(f"Surgical precision: {stats['strike_accuracy']*100:.0f}% accuracy. Every shot measured, every strike purposeful.")
        if stats['takedown_accuracy'] > 0.4:
            bio_paragraphs.append(f"Ground control: {stats['takedown_accuracy']*100:.0f}% takedown success. Dictates where fights take place.")
        if win_rate > 0.7:
            bio_paragraphs.append(f"Elite consistency: {win_rate*100:.0f}% win rate. Each victory another step forward.")
        if 'resilience' in themes_list and losses > 0:
            bio_paragraphs.append(f"Resilience: {losses} defeats, but each comeback stronger than the last.")
        if total_fights > 15:
            bio_paragraphs.append(f"Experience: {total_fights} bouts. The knowledge shows in the details.")
    
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
