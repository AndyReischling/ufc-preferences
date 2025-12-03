"""
Regenerate fighter lore with accurate UFC data and wildly different styles based on fighting type.
"""

import pandas as pd
import numpy as np
import re
import json
from pathlib import Path


def determine_fighting_style_from_stats(fighter_row):
    """
    Determine fighting style from actual UFC statistics.
    Returns a detailed style description.
    """
    strikes_per_min = fighter_row.get('strikes_landed_per_min_mean', 0) if pd.notna(fighter_row.get('strikes_landed_per_min_mean')) else 0
    strike_accuracy = fighter_row.get('strike_accuracy_mean', 0) if pd.notna(fighter_row.get('strike_accuracy_mean')) else 0
    takedown_accuracy = fighter_row.get('takedown_accuracy_mean', 0) if pd.notna(fighter_row.get('takedown_accuracy_mean')) else 0
    control_time_ratio = fighter_row.get('control_time_ratio_mean', 0) if pd.notna(fighter_row.get('control_time_ratio_mean')) else 0
    head_strike_ratio = fighter_row.get('head_strike_ratio_mean', 0) if pd.notna(fighter_row.get('head_strike_ratio_mean')) else 0
    body_strike_ratio = fighter_row.get('body_strike_ratio_mean', 0) if pd.notna(fighter_row.get('body_strike_ratio_mean')) else 0
    leg_strike_ratio = fighter_row.get('leg_strike_ratio_mean', 0) if pd.notna(fighter_row.get('leg_strike_ratio_mean')) else 0
    clinch_time_ratio = fighter_row.get('clinch_time_ratio_mean', 0) if pd.notna(fighter_row.get('clinch_time_ratio_mean')) else 0
    
    # Determine primary style characteristics
    is_extreme_volume = strikes_per_min > 6.0
    is_high_volume = strikes_per_min > 4.0
    is_precise = strike_accuracy > 0.55
    is_very_precise = strike_accuracy > 0.65
    is_grappler = takedown_accuracy > 0.5 or control_time_ratio > 0.4
    is_dominant_grappler = control_time_ratio > 0.5
    is_head_hunter = head_strike_ratio > 0.65
    is_body_attacker = body_strike_ratio > 0.4
    is_leg_kicker = leg_strike_ratio > 0.3
    is_clinch_fighter = clinch_time_ratio > 0.3
    is_balanced = strikes_per_min > 2.0 and takedown_accuracy > 0.3
    
    # Create detailed style description
    style_parts = []
    
    if is_extreme_volume and is_precise:
        style_parts.append("Elite Volume Striker")
    elif is_high_volume and is_very_precise:
        style_parts.append("Precision Volume Striker")
    elif is_high_volume:
        style_parts.append("High-Volume Striker")
    elif is_very_precise and strikes_per_min < 3.0:
        style_parts.append("Surgical Counter-Striker")
    elif is_precise:
        style_parts.append("Precision Striker")
    
    if is_dominant_grappler:
        style_parts.append("Ground Dominator")
    elif is_grappler:
        style_parts.append("Grappling Specialist")
    
    if is_head_hunter:
        style_parts.append("Head Hunter")
    if is_body_attacker:
        style_parts.append("Body Destroyer")
    if is_leg_kicker:
        style_parts.append("Leg Kick Specialist")
    if is_clinch_fighter:
        style_parts.append("Clinch Fighter")
    
    if is_balanced and not style_parts:
        style_parts.append("Well-Rounded Fighter")
    
    if not style_parts:
        style_parts.append("Versatile Fighter")
    
    return " / ".join(style_parts)


def generate_accurate_fighter_lore(fighter_name, fighter_row, cluster_styles_dict=None):
    """
    Generate accurate, diverse lore based on real UFC data and fighting style.
    """
    name_hash = hash(fighter_name) % 10000
    
    # Extract REAL UFC statistics
    strikes_per_min = fighter_row.get('strikes_landed_per_min_mean', 0) if pd.notna(fighter_row.get('strikes_landed_per_min_mean')) else 0
    strike_accuracy = fighter_row.get('strike_accuracy_mean', 0) if pd.notna(fighter_row.get('strike_accuracy_mean')) else 0
    head_strike_ratio = fighter_row.get('head_strike_ratio_mean', 0) if pd.notna(fighter_row.get('head_strike_ratio_mean')) else 0
    body_strike_ratio = fighter_row.get('body_strike_ratio_mean', 0) if pd.notna(fighter_row.get('body_strike_ratio_mean')) else 0
    leg_strike_ratio = fighter_row.get('leg_strike_ratio_mean', 0) if pd.notna(fighter_row.get('leg_strike_ratio_mean')) else 0
    takedown_accuracy = fighter_row.get('takedown_accuracy_mean', 0) if pd.notna(fighter_row.get('takedown_accuracy_mean')) else 0
    control_time_ratio = fighter_row.get('control_time_ratio_mean', 0) if pd.notna(fighter_row.get('control_time_ratio_mean')) else 0
    clinch_time_ratio = fighter_row.get('clinch_time_ratio_mean', 0) if pd.notna(fighter_row.get('clinch_time_ratio_mean')) else 0
    
    # Get cluster and determine style
    cluster_id = fighter_row.get('kmeans_cluster', None)
    fighting_style = determine_fighting_style_from_stats(fighter_row)
    
    # Personal details (clean them up)
    nationality = None
    if 'nationality' in fighter_row:
        nat = str(fighter_row.get('nationality', '')).strip()
        # Filter out HTML/CSS junk
        if nat and len(nat) < 50 and not nat.startswith('.') and not nat.startswith('@'):
            nationality = nat
    
    age = None
    if 'age' in fighter_row:
        try:
            age_val = fighter_row.get('age')
            if pd.notna(age_val) and age_val > 0:
                age = int(age_val)
        except:
            pass
    
    height_inches = fighter_row.get('height_inches') if pd.notna(fighter_row.get('height_inches')) and fighter_row.get('height_inches') > 0 else None
    reach_inches = fighter_row.get('reach_inches') if pd.notna(fighter_row.get('reach_inches')) and fighter_row.get('reach_inches') > 0 else None
    
    stance = None
    if 'stance' in fighter_row:
        st = str(fighter_row.get('stance', '')).strip()
        # Filter out junk
        if st and len(st) < 20 and st.lower() in ['orthodox', 'southpaw', 'switch']:
            stance = st.lower()
    
    record = None
    wins = 0
    losses = 0
    if 'record' in fighter_row:
        rec = str(fighter_row.get('record', '')).strip()
        if rec and len(rec) < 20 and '-' in rec:
            record = rec
            try:
                parts = rec.split('-')
                wins = int(parts[0]) if len(parts) > 0 else 0
                losses = int(parts[1]) if len(parts) > 1 else 0
            except:
                pass
    
    # Determine fighter archetype from stats
    is_extreme_volume = strikes_per_min > 6.0
    is_high_volume = strikes_per_min > 4.0
    is_precise = strike_accuracy > 0.55
    is_grappler = takedown_accuracy > 0.5 or control_time_ratio > 0.4
    is_dominant_grappler = control_time_ratio > 0.5
    is_head_hunter = head_strike_ratio > 0.65
    is_balanced = strikes_per_min > 2.0 and takedown_accuracy > 0.3
    
    win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
    total_fights = wins + losses
    
    # WILDLY DIFFERENT lore based on fighting style
    
    # 1. EXTREME VOLUME STRIKERS (6+ strikes/min)
    if is_extreme_volume:
        if is_precise:
            # Elite volume + precision
            intro_templates = [
                f"{fighter_name} is a {fighting_style} who {['overwhelms', 'bombards', 'assaults', 'barrages'][name_hash % 4]} opponents with an {['unprecedented', 'extraordinary', 'exceptional', 'remarkable'][name_hash % 4]} combination of {['relentless', 'ceaseless', 'unending', 'constant'][name_hash % 4]} volume and {['surgical', 'deadly', 'precise', 'devastating'][name_hash % 4]} accuracy.",
                f"Known as a {fighting_style}, {fighter_name} {['delivers', 'lands', 'connects with', 'hits'][name_hash % 4]} over {strikes_per_min:.1f} strikes per minute at {strike_accuracy*100:.0f}% accuracy—a {['rare', 'unique', 'exceptional', 'remarkable'][name_hash % 4]} blend of {['power', 'speed', 'precision', 'endurance'][name_hash % 4]} and {['technique', 'skill', 'intelligence', 'discipline'][name_hash % 4]}.",
            ]
        else:
            # High volume, lower accuracy
            intro_templates = [
                f"{fighter_name} {['operates', 'functions', 'performs', 'works'][name_hash % 4]} as a {fighting_style}, {['throwing', 'landing', 'delivering', 'connecting with'][name_hash % 4]} an {['astounding', 'incredible', 'remarkable', 'extraordinary'][name_hash % 4]} {strikes_per_min:.1f} strikes per minute—{['overwhelming', 'bombarding', 'assaulting', 'pressuring'][name_hash % 4]} opponents through {['sheer', 'pure', 'raw', 'relentless'][name_hash % 4]} volume.",
                f"A {fighting_style} with {['unmatched', 'exceptional', 'remarkable', 'extraordinary'][name_hash % 4]} output, {fighter_name} {['maintains', 'sustains', 'keeps', 'holds'][name_hash % 4]} {['constant', 'relentless', 'unending', 'ceaseless'][name_hash % 4]} pressure, {['landing', 'delivering', 'connecting with', 'hitting'][name_hash % 4]} over {strikes_per_min:.1f} strikes per minute to {['break', 'wear down', 'overwhelm', 'dominate'][name_hash % 4]} opponents.",
            ]
        intro = intro_templates[name_hash % len(intro_templates)]
        
    # 2. PRECISION COUNTER-STRIKERS (high accuracy, lower volume)
    elif is_precise and strikes_per_min < 4.0:
        intro_templates = [
            f"{fighter_name} {['excels', 'thrives', 'dominates', 'reigns'][name_hash % 4]} as a {fighting_style}, {['landing', 'connecting with', 'hitting', 'delivering'][name_hash % 4]} {strike_accuracy*100:.0f}% of strikes with {['surgical', 'devastating', 'deadly', 'precise'][name_hash % 4]} accuracy—{['waiting', 'biding', 'patiently observing', 'carefully studying'][name_hash % 4]} for the {['perfect', 'ideal', 'optimal', 'right'][name_hash % 4]} moment to {['strike', 'attack', 'counter', 'explode'][name_hash % 4]}.",
            f"A {fighting_style} who {['values', 'prioritizes', 'focuses on', 'emphasizes'][name_hash % 4]} {['quality', 'precision', 'accuracy', 'technique'][name_hash % 4]} over quantity, {fighter_name} {['lands', 'connects with', 'hits', 'delivers'][name_hash % 4]} {strike_accuracy*100:.0f}% of their strikes, {['making', 'ensuring', 'guaranteeing', 'securing'][name_hash % 4]} each {['shot', 'strike', 'punch', 'blow'][name_hash % 4]} {['counts', 'matters', 'hurts', 'damages'][name_hash % 4]}.",
        ]
        intro = intro_templates[name_hash % len(intro_templates)]
        
    # 3. DOMINANT GRAPPLERS (high control time)
    elif is_dominant_grappler:
        intro_templates = [
            f"{fighter_name} {['reigns', 'dominates', 'excels', 'thrives'][name_hash % 4]} as a {fighting_style}, {['controlling', 'dictating', 'commanding', 'dominating'][name_hash % 4]} fights with {control_time_ratio*100:.0f}% control time and {takedown_accuracy*100:.0f}% takedown accuracy—{['suffocating', 'overwhelming', 'dominating', 'controlling'][name_hash % 4]} opponents through {['superior', 'exceptional', 'dominant', 'masterful'][name_hash % 4]} grappling.",
            f"A {fighting_style} with {['exceptional', 'outstanding', 'superior', 'dominant'][name_hash % 4]} ground control, {fighter_name} {['brings', 'takes', 'drags', 'forces'][name_hash % 4]} fights to the mat and {['maintains', 'sustains', 'holds', 'keeps'][name_hash % 4]} {control_time_ratio*100:.0f}% control time, {['hunting', 'searching', 'seeking', 'looking'][name_hash % 4]} for {['submissions', 'finishes', 'opportunities', 'openings'][name_hash % 4]} while {['suffocating', 'overwhelming', 'dominating', 'controlling'][name_hash % 4]} opponents.",
        ]
        intro = intro_templates[name_hash % len(intro_templates)]
        
    # 4. GRAPPLING SPECIALISTS
    elif is_grappler:
        intro_templates = [
            f"{fighter_name} {['operates', 'functions', 'performs', 'works'][name_hash % 4]} as a {fighting_style}, {['using', 'employing', 'utilizing', 'wielding'][name_hash % 4]} {takedown_accuracy*100:.0f}% accurate takedowns to {['bring', 'take', 'drag', 'force'][name_hash % 4]} fights to the ground where they {['excel', 'thrive', 'dominate', 'reign'][name_hash % 4]}.",
            f"A {fighting_style} with {['strong', 'solid', 'exceptional', 'outstanding'][name_hash % 4]} grappling fundamentals, {fighter_name} {['relies', 'depends', 'counts', 'focuses'][name_hash % 4]} on {['takedowns', 'grappling', 'ground work', 'mat skills'][name_hash % 4]} with {takedown_accuracy*100:.0f}% accuracy to {['control', 'dominate', 'dictate', 'command'][name_hash % 4]} the {['pace', 'action', 'fight', 'bout'][name_hash % 4]}.",
        ]
        intro = intro_templates[name_hash % len(intro_templates)]
        
    # 5. HEAD HUNTERS
    elif is_head_hunter:
        intro_templates = [
            f"{fighter_name} {['specializes', 'excels', 'focuses', 'thrives'][name_hash % 4]} as a {fighting_style}, {['targeting', 'aiming for', 'focusing on', 'zeroing in on'][name_hash % 4]} the head with {head_strike_ratio*100:.0f}% of strikes—{['looking', 'seeking', 'aiming', 'trying'][name_hash % 4]} to {['end', 'finish', 'conclude', 'close'][name_hash % 4]} fights with {['devastating', 'powerful', 'precise', 'deadly'][name_hash % 4]} head shots.",
            f"A {fighting_style} who {['hunts', 'targets', 'seeks', 'aims for'][name_hash % 4]} {['knockouts', 'finishes', 'stoppages', 'KOs'][name_hash % 4]}, {fighter_name} {['directs', 'aims', 'focuses', 'concentrates'][name_hash % 4]} {head_strike_ratio*100:.0f}% of their offense at the head, {['creating', 'finding', 'opening', 'discovering'][name_hash % 4]} {['opportunities', 'openings', 'chances', 'moments'][name_hash % 4]} for {['fight-ending', 'devastating', 'powerful', 'decisive'][name_hash % 4]} strikes.",
        ]
        intro = intro_templates[name_hash % len(intro_templates)]
        
    # 6. BALANCED FIGHTERS
    elif is_balanced:
        intro_templates = [
            f"{fighter_name} {['represents', 'embodies', 'exemplifies', 'demonstrates'][name_hash % 4]} the {fighting_style} archetype, {['combining', 'merging', 'blending', 'uniting'][name_hash % 4]} {strikes_per_min:.1f} strikes per minute with {takedown_accuracy*100:.0f}% takedown accuracy to create a {['formidable', 'dangerous', 'threatening', 'lethal'][name_hash % 4]} {['well-rounded', 'complete', 'versatile', 'comprehensive'][name_hash % 4]} skill set.",
            f"A {fighting_style} with {['exceptional', 'outstanding', 'remarkable', 'impressive'][name_hash % 4]} {['versatility', 'adaptability', 'flexibility', 'range'][name_hash % 4]}, {fighter_name} {['seamlessly', 'smoothly', 'effortlessly', 'easily'][name_hash % 4]} {['transitions', 'switches', 'changes', 'moves'][name_hash % 4]} between {['striking', 'grappling', 'clinch work', 'ground control'][name_hash % 4]}, {['making', 'rendering', 'turning', 'creating'][name_hash % 4]} them {['dangerous', 'threatening', 'formidable', 'lethal'][name_hash % 4]} in {['all', 'every', 'any', 'each'][name_hash % 4]} phases.",
        ]
        intro = intro_templates[name_hash % len(intro_templates)]
        
    # 7. DEFAULT/VERSATILE
    else:
        intro_templates = [
            f"{fighter_name} {['brings', 'delivers', 'provides', 'offers'][name_hash % 4]} a {fighting_style} approach, {['adapting', 'adjusting', 'modifying', 'changing'][name_hash % 4]} their {['game plan', 'strategy', 'tactics', 'approach'][name_hash % 4]} based on the {['opponent', 'situation', 'circumstances', 'context'][name_hash % 4]}.",
            f"A {fighting_style} who {['thrives', 'excels', 'succeeds', 'performs'][name_hash % 4]} through {['adaptability', 'versatility', 'flexibility', 'versatility'][name_hash % 4]}, {fighter_name} {['adjusts', 'modifies', 'changes', 'adapts'][name_hash % 4]} their {['style', 'approach', 'method', 'tactics'][name_hash % 4]} to {['exploit', 'capitalize on', 'take advantage of', 'target'][name_hash % 4]} opponent {['weaknesses', 'vulnerabilities', 'flaws', 'gaps'][name_hash % 4]}.",
        ]
        intro = intro_templates[name_hash % len(intro_templates)]
    
    # Add specific stat details based on style
    stat_details = []
    
    if is_extreme_volume or is_high_volume:
        stat_details.append(f"Landing {strikes_per_min:.1f} significant strikes per minute")
        if strike_accuracy > 0.5:
            stat_details.append(f"at {strike_accuracy*100:.0f}% accuracy")
    
    if is_head_hunter:
        stat_details.append(f"with {head_strike_ratio*100:.0f}% targeting the head")
    elif body_strike_ratio > 0.35:
        stat_details.append(f"with {body_strike_ratio*100:.0f}% body strikes")
    elif leg_strike_ratio > 0.25:
        stat_details.append(f"with {leg_strike_ratio*100:.0f}% leg kicks")
    
    if is_grappler:
        stat_details.append(f"{takedown_accuracy*100:.0f}% takedown accuracy")
        if control_time_ratio > 0.3:
            stat_details.append(f"and {control_time_ratio*100:.0f}% control time")
    
    # Add personal details if available
    personal_info = []
    
    if nationality:
        personal_info.append(f"Hailing from {nationality}")
    
    if age:
        if age < 25:
            personal_info.append(f"At just {age} years old")
        elif age > 35:
            personal_info.append(f"At {age} years old")
    
    if height_inches and reach_inches:
        height_ft = int(height_inches // 12)
        height_in = int(height_inches % 12)
        reach_ft = int(reach_inches // 12)
        reach_in = int(reach_inches % 12)
        reach_advantage = reach_inches - height_inches
        
        if reach_advantage > 3:
            personal_info.append(f"with an exceptional {reach_ft}'{reach_in}\" reach")
        elif reach_advantage < -2:
            personal_info.append(f"compensating for reach limitations")
    
    if record and total_fights > 5:
        if win_rate > 0.7:
            personal_info.append(f"boasting a {record} record")
        elif win_rate < 0.4:
            personal_info.append(f"with a {record} record showing resilience")
        else:
            personal_info.append(f"holding a {record} professional record")
    
    if stance:
        stance_descriptions = {
            'orthodox': 'fighting from the orthodox stance',
            'southpaw': 'using the unorthodox southpaw stance',
            'switch': 'seamlessly switching stances'
        }
        personal_info.append(stance_descriptions.get(stance, ''))
    
    # Combine into lore
    lore_parts = [intro]
    
    if stat_details:
        lore_parts.append(", ".join(stat_details) + ".")
    
    if personal_info:
        lore_parts.append(" ".join(personal_info) + ".")
    
    # Add career context
    if total_fights > 10:
        if win_rate > 0.7:
            lore_parts.append(f"With {wins} professional victories, {fighter_name} has established themselves as a dominant force in their division.")
        elif win_rate < 0.4:
            lore_parts.append(f"Despite a challenging {record} record, {fighter_name} continues to compete with heart and determination.")
        else:
            lore_parts.append(f"Through {total_fights} professional fights, {fighter_name} has proven their mettle against elite competition.")
    
    # Join and clean
    lore = " ".join(lore_parts)
    lore = re.sub(r'\s+', ' ', lore)
    lore = re.sub(r'\s+([,.!?])', r'\1', lore)
    lore = lore.strip()
    
    if not lore.endswith(('.', '!', '?')):
        lore += "."
    
    if lore:
        lore = lore[0].upper() + lore[1:] if len(lore) > 1 else lore.upper()
    
    return lore


if __name__ == "__main__":
    print("Loading fighter data...")
    fighters_df = pd.read_csv('fighters_with_lore.csv')
    
    # Load cluster styles if available
    cluster_styles_dict = {}
    try:
        with open('cluster_styles.json', 'r') as f:
            cluster_data = json.load(f)
            cluster_styles_dict = {int(k): v['style'] for k, v in cluster_data.items()}
        print(f"Loaded {len(cluster_styles_dict)} cluster styles")
    except:
        print("No cluster styles file found, will infer from stats")
    
    print(f"Found {len(fighters_df)} fighters")
    print("Regenerating accurate lore based on UFC stats and fighting styles...")
    
    # Regenerate lore
    new_lore_list = []
    for idx, row in fighters_df.iterrows():
        fighter_name = row['fighter']
        lore = generate_accurate_fighter_lore(fighter_name, row, cluster_styles_dict)
        new_lore_list.append(lore)
        
        if (idx + 1) % 100 == 0:
            print(f"Processed {idx + 1}/{len(fighters_df)} fighters...")
    
    # Update lore
    fighters_df['lore'] = new_lore_list
    
    # Save
    print(f"\nSaving updated lore...")
    fighters_df.to_csv('fighters_with_lore.csv', index=False)
    
    print(f"✓ Regenerated accurate lore for {len(fighters_df)} fighters")
    print(f"✓ Unique lore entries: {fighters_df['lore'].nunique()}")
    
    # Show diverse samples
    print("\n=== Sample Diverse Lore by Style ===")
    
    # Find examples of different styles
    samples_by_cluster = {}
    for cluster_id in sorted(fighters_df['kmeans_cluster'].dropna().unique()):
        cluster_fighters = fighters_df[fighters_df['kmeans_cluster'] == cluster_id]
        if len(cluster_fighters) > 0:
            sample = cluster_fighters.iloc[0]
            samples_by_cluster[int(cluster_id)] = sample
    
    for cluster_id in sorted(samples_by_cluster.keys())[:5]:
        sample = samples_by_cluster[cluster_id]
        fighter = sample['fighter']
        lore = sample['lore']
        strikes = sample.get('strikes_landed_per_min_mean', 0)
        print(f"\nCluster {cluster_id} ({strikes:.1f} strikes/min):")
        print(f"  {fighter}: {lore[:150]}...")

