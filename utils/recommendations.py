"""
Recommendation engine module.
Extracted and adapted from ufc_fighter_analysis.ipynb sections 9.3-9.5
"""

import pandas as pd
import numpy as np
from . import themes


def get_fighters_for_content(content_titles, mapping_df, fighters_df, n_recommendations=10):
    """
    Get fighter recommendations for one or more content titles.
    Aggregates recommendations when multiple content items are selected.
    
    Args:
        content_titles: List of content titles or single title string
        mapping_df: Content-fighter mapping DataFrame
        fighters_df: Fighters DataFrame with lore
        n_recommendations: Number of fighters to return
    
    Returns:
        DataFrame with recommended fighters, similarity scores, and explanations
    """
    if mapping_df is None or len(mapping_df) == 0:
        return pd.DataFrame()
    
    if isinstance(content_titles, str):
        content_titles = [content_titles]
    
    if len(content_titles) == 0:
        return pd.DataFrame()
    
    # Get matches for all selected content
    all_matches = []
    for content_title in content_titles:
        content_matches = mapping_df[
            mapping_df['content_title'] == content_title
        ].nlargest(n_recommendations * 2, 'similarity_score')  # Get more to account for aggregation
        
        if len(content_matches) > 0:
            content_matches['source_content'] = content_title
            all_matches.append(content_matches)
    
    if len(all_matches) == 0:
        return pd.DataFrame()
    
    # Combine all matches
    combined_matches = pd.concat(all_matches, ignore_index=True)
    
    # Aggregate by fighter (take max similarity score, combine explanations)
    fighter_recs = combined_matches.groupby('fighter_name').agg({
        'similarity_score': 'max',
        'fighting_style': 'first',
        'fighter_cluster': 'first',
        'common_themes': lambda x: ', '.join(set([str(t) for t in x if pd.notna(t) and str(t).strip()])),
        'common_genres': lambda x: ', '.join(set([str(t) for t in x if pd.notna(t) and str(t).strip()])),
        'common_narratives': lambda x: ', '.join(set([str(t) for t in x if pd.notna(t) and str(t).strip()])),
        'source_content': lambda x: ', '.join(x.unique()[:3])  # Show up to 3 source content
    }).reset_index()
    
    # Sort by similarity score and take top N
    fighter_recs = fighter_recs.sort_values('similarity_score', ascending=False).head(n_recommendations)
    
    # Add fighter lore
    recommendations = []
    for idx, match in fighter_recs.iterrows():
        fighter_name = match['fighter_name']
        
        # Get fighter data
        fighter_row = fighters_df[fighters_df['fighter'] == fighter_name]
        fighter_lore = ""
        if len(fighter_row) > 0:
            fighter_lore = fighter_row.iloc[0].get('lore', '')
        
        # Create explanation
        explanation_parts = []
        if match['common_themes'] and str(match['common_themes']).strip():
            explanation_parts.append(f"shared themes: {match['common_themes']}")
        if match['common_genres'] and str(match['common_genres']).strip():
            explanation_parts.append(f"matching genres: {match['common_genres']}")
        if match['common_narratives'] and str(match['common_narratives']).strip():
            explanation_parts.append(f"similar narratives: {match['common_narratives']}")
        
        explanation = " and ".join(explanation_parts) if explanation_parts else "general match"
        
        recommendations.append({
            'fighter_name': fighter_name,
            'fighting_style': match['fighting_style'],
            'similarity_score': match['similarity_score'],
            'explanation': explanation,
            'fighter_lore': fighter_lore,
            'common_themes': match['common_themes'],
            'common_genres': match['common_genres'],
            'source_content': match['source_content'],
            'fighter_cluster': match['fighter_cluster']
        })
    
    return pd.DataFrame(recommendations)


def get_fighters_for_filters(selected_genres=None, selected_themes=None, selected_types=None,
                              selected_characters=None, selected_content=None, mapping_df=None, 
                              fighters_df=None, content_df=None, n_recommendations=10):
    """
    Get fighter recommendations based on filters (genre, theme, type) and optionally selected content.
    
    Args:
        selected_genres: List of selected genres
        selected_themes: List of selected themes
        selected_types: List of selected content types
        selected_content: Optional list of selected content titles (additional filtering)
        mapping_df: Content-fighter mapping DataFrame
        fighters_df: Fighters DataFrame
        content_df: Content catalog DataFrame
        n_recommendations: Number of fighters to return
    
    Returns:
        DataFrame with recommended fighters
    """
    if mapping_df is None or len(mapping_df) == 0:
        return pd.DataFrame()
    
    if content_df is None or len(content_df) == 0:
        return pd.DataFrame()
    
    # Start with all content that matches filters
    # Use OR logic: content matches if it matches ANY filter category
    filtered_content = content_df.copy()
    
    # Build masks for each filter type
    genre_mask = pd.Series([True] * len(filtered_content), index=filtered_content.index)
    theme_mask = pd.Series([True] * len(filtered_content), index=filtered_content.index)
    char_mask = pd.Series([True] * len(filtered_content), index=filtered_content.index)
    
    # Apply genre filter
    if selected_genres:
        genre_mask = filtered_content['genres'].apply(
            lambda x: any(g.lower() in str(g2).lower() for g in selected_genres for g2 in themes.parse_list_column(x))
        )
    
    # Apply theme filter
    if selected_themes:
        theme_mask = filtered_content['themes'].apply(
            lambda x: any(t.lower() in str(t2).lower() for t in selected_themes for t2 in themes.parse_list_column(x))
        )
    
    # Apply character filter
    if selected_characters:
        char_mask = filtered_content['character_archetypes'].apply(
            lambda x: any(c.lower() in str(c2).lower() for c in selected_characters for c2 in themes.parse_list_column(x))
        )
    
    # Combine masks with OR logic: content matches if it matches ANY filter
    if selected_genres or selected_themes or selected_characters:
        combined_mask = genre_mask | theme_mask | char_mask
        filtered_content = filtered_content[combined_mask]
    
    # Apply type filter (if provided)
    if selected_types:
        filtered_content = filtered_content[filtered_content['type'].isin(selected_types)]
    
    # If specific content is selected, use only those
    if selected_content:
        filtered_content = filtered_content[filtered_content['title'].isin(selected_content)]
    
    # If no filters and no content selected, return empty
    if len(filtered_content) == 0:
        return pd.DataFrame()
    
    # Get fighters for filtered content
    content_titles = filtered_content['title'].tolist()
    
    # Get fighters mapped to filtered content
    fighter_recs = get_fighters_for_content(content_titles, mapping_df, fighters_df, n_recommendations)
    
    # If we have filters but no fighters from mapping, try direct theme/genre matching
    if len(fighter_recs) == 0 and (selected_genres or selected_themes or selected_characters):
        # Fallback: match fighters directly by themes/genres
        fighter_recs = match_fighters_by_filters(
            selected_genres, selected_themes, selected_characters,
            fighters_df, content_df, n_recommendations
        )
    
    return fighter_recs


def match_fighters_by_filters(selected_genres=None, selected_themes=None, selected_characters=None,
                              fighters_df=None, content_df=None, n_recommendations=10):
    """
    Fallback: Match fighters directly by themes/genres when content-fighter mapping fails.
    
    Args:
        selected_genres: List of selected genres
        selected_themes: List of selected themes (narratives)
        selected_characters: List of selected character archetypes
        fighters_df: Fighters DataFrame
        content_df: Content catalog DataFrame
        n_recommendations: Number of fighters to return
    
    Returns:
        DataFrame with recommended fighters
    """
    if fighters_df is None or len(fighters_df) == 0:
        return pd.DataFrame()
    
    fighter_scores = []
    
    for idx, fighter_row in fighters_df.iterrows():
        fighter_name = fighter_row.get('fighter', '')
        if not fighter_name:
            continue
        
        # Get fighter tags
        fighter_tags = themes.tag_fighter(fighter_row)
        fighter_themes = fighter_tags.get('themes', [])
        fighter_archetypes = fighter_tags.get('character_archetypes', [])
        
        # Calculate match score
        score = 0.0
        match_details = []
        
        # Match themes (narratives)
        if selected_themes:
            theme_matches = [t for t in selected_themes if t in fighter_themes]
            if theme_matches:
                score += len(theme_matches) * 0.5
                match_details.append(f"themes: {', '.join(theme_matches[:3])}")
        
        # Match character archetypes
        if selected_characters:
            char_matches = [c for c in selected_characters if c in fighter_archetypes]
            if char_matches:
                score += len(char_matches) * 0.3
                match_details.append(f"characters: {', '.join(char_matches[:3])}")
        
        # Match genres (check if fighter themes align with genre themes)
        if selected_genres:
            # Get themes associated with selected genres from content
            genre_themes = set()
            for _, content_row in content_df.iterrows():
                content_tags = themes.tag_content(content_row)
                content_genres = [g.lower() for g in content_tags.get('genres', [])]
                if any(g in selected_genres for g in content_genres):
                    genre_themes.update(content_tags.get('themes', []))
            
            # Check if fighter themes match genre themes
            genre_theme_matches = [t for t in fighter_themes if t in genre_themes]
            if genre_theme_matches:
                score += len(genre_theme_matches) * 0.2
                match_details.append(f"genre themes: {', '.join(genre_theme_matches[:3])}")
        
        # Only include fighters with some match
        if score > 0:
            fighter_scores.append({
                'fighter_name': fighter_name,
                'fighting_style': fighter_tags.get('fighting_style', 'Fighter'),
                'similarity_score': min(1.0, score),  # Cap at 1.0
                'explanation': ' | '.join(match_details) if match_details else 'general match',
                'fighter_themes': ', '.join(fighter_themes[:5]),
                'fighter_archetypes': ', '.join(fighter_archetypes[:3])
            })
    
    if len(fighter_scores) == 0:
        return pd.DataFrame()
    
    # Sort by score and return top N
    fighter_recs_df = pd.DataFrame(fighter_scores)
    fighter_recs_df = fighter_recs_df.sort_values('similarity_score', ascending=False).head(n_recommendations)
    
    return fighter_recs_df


def get_content_for_fighter(fighter_name, mapping_df, content_df, n_recommendations=5):
    """
    Get content recommendations for a fighter.
    
    Args:
        fighter_name: Name of the fighter
        mapping_df: Content-fighter mapping DataFrame
        content_df: Content catalog DataFrame
        n_recommendations: Number of content items to return
    
    Returns:
        DataFrame with recommended content and explanations
    """
    if mapping_df is None or len(mapping_df) == 0:
        return pd.DataFrame()
    
    # Get top matches for this fighter
    fighter_matches = mapping_df[
        mapping_df['fighter_name'] == fighter_name
    ].nlargest(n_recommendations, 'similarity_score')
    
    if len(fighter_matches) == 0:
        return pd.DataFrame()
    
    # Add content details
    recommendations = []
    for idx, match in fighter_matches.iterrows():
        content_title = match['content_title']
        
        # Get content details
        content_row = content_df[content_df['title'] == content_title]
        content_desc = ""
        content_type = ""
        if len(content_row) > 0:
            content_desc = content_row.iloc[0].get('description', '')
            content_type = content_row.iloc[0].get('type', '')
        
        # Create explanation
        explanation_parts = []
        if match['common_themes'] and str(match['common_themes']).strip():
            explanation_parts.append(f"shared themes: {match['common_themes']}")
        if match['common_genres'] and str(match['common_genres']).strip():
            explanation_parts.append(f"matching genres: {match['common_genres']}")
        if match['common_narratives'] and str(match['common_narratives']).strip():
            explanation_parts.append(f"similar narratives: {match['common_narratives']}")
        
        explanation = " and ".join(explanation_parts) if explanation_parts else "general match"
        
        recommendations.append({
            'content_title': content_title,
            'content_type': content_type,
            'content_description': content_desc,
            'similarity_score': match['similarity_score'],
            'explanation': explanation,
            'common_themes': match['common_themes'],
            'common_genres': match['common_genres']
        })
    
    return pd.DataFrame(recommendations)


def get_fighter_themes(fighter_name, fighters_df, mapping_df=None):
    """
    Extract themes for a fighter from their lore/stats or mapping data.
    
    Args:
        fighter_name: Name of the fighter
        fighters_df: Fighters DataFrame
        mapping_df: Optional content-fighter mapping DataFrame
    
    Returns:
        List of theme strings
    """
    fighter_row = fighters_df[fighters_df['fighter'] == fighter_name]
    if len(fighter_row) == 0:
        return []
    
    fighter_row = fighter_row.iloc[0]
    tags = themes.tag_fighter(fighter_row, mapping_df)
    return tags.get('themes', [])


def get_content_themes(content_title, content_df):
    """
    Extract themes for content.
    
    Args:
        content_title: Title of the content
        content_df: Content catalog DataFrame
    
    Returns:
        List of theme strings
    """
    content_row = content_df[content_df['title'] == content_title]
    if len(content_row) == 0:
        return []
    
    content_row = content_row.iloc[0]
    tags = themes.tag_content(content_row)
    return tags.get('themes', [])

