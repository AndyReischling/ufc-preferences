"""
Bundle generator module.
Creates bundles combining content, fighters, and related fights with thematic explanations.
"""

import pandas as pd
import numpy as np
from . import fight_finder
from . import themes


def create_bundle(content_title, fighter_names, content_df, fighters_df, fight_data, mapping_df=None):
    """
    Create a bundle combining content, fighters, and related fights.
    
    Args:
        content_title: Title of the content
        fighter_names: List of fighter names in the bundle
        content_df: Content catalog DataFrame
        fighters_df: Fighters DataFrame
        fight_data: UFC fight data DataFrame
        mapping_df: Optional content-fighter mapping DataFrame
    
    Returns:
        Dictionary with bundle components and thematic explanation
    """
    bundle = {
        'content': None,
        'fighters': [],
        'fights': [],
        'thematic_connection': '',
        'themes': [],
        'genres': []
    }
    
    # Get content metadata
    content_row = content_df[content_df['title'] == content_title]
    if len(content_row) > 0:
        content_row = content_row.iloc[0]
        content_tags = themes.tag_content(content_row)
        bundle['content'] = {
            'title': content_title,
            'type': content_row.get('type', ''),
            'description': content_row.get('description', ''),
            'themes': content_tags['themes'],
            'genres': content_tags['genres'],
            'character_archetypes': content_tags['character_archetypes']
        }
        bundle['themes'] = content_tags['themes']
        bundle['genres'] = content_tags['genres']
    
    # Get fighter profiles
    bundle_themes = set(bundle['themes'])
    for fighter_name in fighter_names:
        fighter_row = fighters_df[fighters_df['fighter'] == fighter_name]
        if len(fighter_row) > 0:
            fighter_row = fighter_row.iloc[0]
            fighter_tags = themes.tag_fighter(fighter_row, mapping_df)
            
            fighter_profile = {
                'name': fighter_name,
                'fighting_style': fighter_tags.get('fighting_style', 'Unknown'),
                'lore': fighter_row.get('lore', ''),
                'themes': fighter_tags.get('themes', []),
                'character_archetypes': fighter_tags.get('character_archetypes', [])
            }
            
            bundle['fighters'].append(fighter_profile)
            bundle_themes.update(fighter_tags.get('themes', []))
    
    bundle['themes'] = list(bundle_themes)
    
    # Find related fights
    if fight_data is not None and len(fight_data) > 0:
        fights = fight_finder.find_fights_for_fighters(fighter_names, fight_data, limit=10)
        if len(fights) > 0:
            bundle['fights'] = fights.to_dict('records')
    
    # Generate thematic connection explanation
    bundle['thematic_connection'] = generate_bundle_explanation(bundle)
    
    return bundle


def generate_bundle_explanation(bundle):
    """
    Generate explanation of why the bundle components fit together thematically.
    
    Args:
        bundle: Bundle dictionary
    
    Returns:
        String explanation
    """
    content = bundle.get('content', {})
    fighters = bundle.get('fighters', [])
    themes_list = bundle.get('themes', [])
    
    if not content or len(fighters) == 0:
        return "Bundle components available."
    
    explanation_parts = []
    
    # Content description
    content_title = content.get('title', 'This content')
    content_themes = content.get('themes', [])[:3]
    if content_themes:
        explanation_parts.append(f"{content_title} features themes of {', '.join(content_themes)}")
    else:
        explanation_parts.append(f"{content_title} offers compelling storytelling")
    
    # Fighter connection
    if len(fighters) > 0:
        fighter_names = [f['name'] for f in fighters[:3]]
        if len(fighter_names) == 1:
            explanation_parts.append(f"Fighter {fighter_names[0]} embodies similar themes")
        else:
            explanation_parts.append(f"Fighters {', '.join(fighter_names[:-1])} and {fighter_names[-1]} share these thematic elements")
    
    # Common themes
    if themes_list:
        explanation_parts.append(f"connecting through themes like {', '.join(themes_list[:3])}")
    
    return ". ".join(explanation_parts) + "."


def create_bundles_for_content(content_titles, content_df, fighters_df, fight_data, mapping_df, n_bundles=3, n_fighters_per_bundle=3):
    """
    Create multiple bundles for selected content.
    
    Args:
        content_titles: List of content titles
        content_df: Content catalog DataFrame
        fighters_df: Fighters DataFrame
        fight_data: UFC fight data DataFrame
        mapping_df: Content-fighter mapping DataFrame
        n_bundles: Number of bundles to create
        n_fighters_per_bundle: Number of fighters per bundle
    
    Returns:
        List of bundle dictionaries
    """
    if isinstance(content_titles, str):
        content_titles = [content_titles]
    
    bundles = []
    
    for content_title in content_titles[:n_bundles]:
        # Get top fighters for this content
        from utils import recommendations
        fighter_recs = recommendations.get_fighters_for_content(
            content_title, 
            mapping_df, 
            fighters_df, 
            n_recommendations=n_fighters_per_bundle
        )
        
        if len(fighter_recs) > 0:
            fighter_names = fighter_recs['fighter_name'].tolist()
            bundle = create_bundle(
                content_title,
                fighter_names,
                content_df,
                fighters_df,
                fight_data,
                mapping_df
            )
            bundles.append(bundle)
    
    return bundles

