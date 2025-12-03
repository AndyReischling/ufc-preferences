"""
Streamlit UFC Fighter Recommendation App
Main application file
"""

import streamlit as st
import pandas as pd
import numpy as np
from utils import data_loader
from utils import recommendations
from utils import themes
from utils import fighter_profile
from utils import visualizations
from utils import bundles
from utils import fight_finder
import config

# Page configuration
st.set_page_config(
    page_title="UFC Fighter Recommendations",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished UI
st.markdown("""
    <style>
    /* Import Proxima Nova Regular font */
    @import url('https://fonts.googleapis.com/css2?family=Proxima+Nova:wght@400&display=swap');
    
    /* Apply Proxima Nova Regular to all text */
    * {
        font-family: 'Proxima Nova', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    /* Main styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Content cards */
    .content-card {
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .content-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    .selected-content {
        background: #ffffff;
        border-color: #0064FF;
        box-shadow: 0 4px 12px rgba(0, 100, 255, 0.3);
    }
    
    /* Theme badges */
    .theme-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        margin: 0.3rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 400;
        background: linear-gradient(135deg, #0064FF 0%, #00D86D 100%);
        color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Fighter cards */
    .fighter-card {
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 4px solid #0064FF;
        margin: 1rem 0;
        background: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%);
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    
    /* Bundle cards */
    .bundle-card {
        padding: 1.5rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #0064FF 0%, #00D86D 100%);
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Headers */
    h1 {
        color: #000000;
        font-weight: 400;
        margin-bottom: 1rem;
    }
    h2 {
        color: #000000;
        font-weight: 400;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    h3 {
        color: #000000;
        font-weight: 400;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_content' not in st.session_state:
    st.session_state.selected_content = []
if 'show_fighters' not in st.session_state:
    st.session_state.show_fighters = False


def main():
    """Main application function"""
    
    # Load data
    try:
        with st.spinner("Loading data..."):
            data = data_loader.load_all_data()
            content_df = data['content']
            fighters_df = data['fighters']
            mapping_df = data['mapping']
            fight_data = data['fights']
        
        if content_df.empty:
            st.error("Content catalog not found. Please ensure 'paramount_content_features.csv' exists.")
            return
        
        if fighters_df.empty:
            st.error("Fighter data not found. Please ensure 'fighters_with_lore.csv' exists.")
            return
        
        if mapping_df.empty:
            st.error("Content-fighter mapping not found. Please ensure 'content_fighter_mapping.csv' exists.")
            return
        
        # Fight data is optional - app can function without it
        if fight_data.empty:
            # Silently continue - fight data is only used for bundles
            pass
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please ensure all required CSV files are in the project directory.")
        return
    
    # Sidebar with content catalog and filters
    render_sidebar(content_df, fighters_df)
    
    # Main content area with polished header
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0; background: #0064FF; 
                    border-radius: 12px; margin-bottom: 2rem; color: white;">
            <h1 style="color: white; margin: 0; font-size: 3rem; font-weight: 400;">UFC Fighter Recommendations</h1>
            <p style="font-size: 1.2rem; margin-top: 1rem; opacity: 0.9; font-weight: 400;">
                Discover fighters whose stories match your favorite Paramount+ content
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # See Fighters button in main area
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("See Fighters", type="primary", use_container_width=True, key="see_fighters_btn"):
            st.session_state.show_fighters = True
            st.rerun()
    
    # Fighter recommendations section - show only after button is pressed
    if st.session_state.show_fighters:
        has_filters = (st.session_state.selected_genres or 
                       st.session_state.selected_themes or 
                       st.session_state.selected_characters or
                       st.session_state.selected_content)
        
        if has_filters or st.session_state.selected_content:
            render_fighter_recommendations(
                st.session_state.selected_genres,
                st.session_state.selected_themes,
                None,  # No type filter
                st.session_state.selected_characters,
                st.session_state.selected_content,
                mapping_df,
                fighters_df,
                content_df
            )
            
            # Bundle recommendations section (only if content selected)
            if st.session_state.selected_content:
                render_bundle_recommendations(
                    st.session_state.selected_content,
                    content_df,
                    fighters_df,
                    fight_data,
                    mapping_df
                )
        else:
            st.warning("Please select at least one filter (Genre or Theme) or content title to see fighter recommendations.")


def render_sidebar(content_df, fighters_df=None):
    """Render sidebar with content catalog and filters"""
    with st.sidebar:
        st.header("Filters & Content")
        
        # Get unique values for filters
        # Use shared vocabulary for themes - get all themes from both fighters and content
        if fighters_df is None:
            fighters_df = pd.DataFrame()
        all_themes = themes.get_all_themes(content_df, fighters_df)
        all_genres = themes.get_all_genres(content_df)
        
        # Get all character archetypes
        all_characters = set()
        if 'character_archetypes' in content_df.columns:
            for char_list in content_df['character_archetypes']:
                all_characters.update(themes.parse_list_column(char_list))
        all_characters = sorted(list(all_characters))
        
        # Store filters in session state
        if 'selected_genres' not in st.session_state:
            st.session_state.selected_genres = []
        if 'selected_themes' not in st.session_state:
            st.session_state.selected_themes = []
        if 'selected_characters' not in st.session_state:
            st.session_state.selected_characters = []
        
        # Filters
        st.subheader("Filters")
        selected_genres = st.multiselect("Genre", all_genres, default=st.session_state.selected_genres, key="genre_filter")
        
        # Narrative Themes filter
        st.write("**Narrative Themes**")
        st.caption("Select themes to find fighters with matching narratives")
        selected_themes = st.multiselect(
            "Choose themes", 
            all_themes, 
            default=st.session_state.selected_themes, 
            key="theme_filter",
            label_visibility="collapsed"
        )
        
        selected_characters = st.multiselect("Characters", all_characters, default=st.session_state.selected_characters, key="character_filter")
        
        # Update session state
        st.session_state.selected_genres = selected_genres
        st.session_state.selected_themes = selected_themes
        st.session_state.selected_characters = selected_characters
        
        st.markdown("---")
        
        # Content catalog in sidebar
        st.subheader("Content Catalog")
        st.caption(f"{len(content_df)} titles available")
        
        # Search for content
        search_query = st.text_input("Search content", key="content_search_sidebar", placeholder="Type to search...")
        
        # Filter content by search
        filtered_content = content_df.copy()
        if search_query:
            filtered_content = filtered_content[
                filtered_content['title'].str.contains(search_query, case=False, na=False)
            ]
        
        # Display filtered content (scrollable)
        st.caption(f"Showing {len(filtered_content)} of {len(content_df)} titles")
        
        # Use a container with max height for scrolling
        content_container = st.container()
        with content_container:
            for idx, (_, row) in enumerate(filtered_content.iterrows()):
                title = row['title']
                content_type = row.get('type', 'Unknown')
                is_selected = title in st.session_state.selected_content
                
                # Compact display
                col_check, col_title = st.columns([1, 10])
                with col_check:
                    if st.checkbox("", value=is_selected, key=f"sidebar_content_{idx}", label_visibility="collapsed"):
                        if title not in st.session_state.selected_content:
                            st.session_state.selected_content.append(title)
                            st.rerun()
                    else:
                        if title in st.session_state.selected_content:
                            st.session_state.selected_content.remove(title)
                            st.rerun()
                with col_title:
                    st.markdown(f"**{title}**")
                    st.caption(content_type)
        
        st.markdown("---")
        
        # Display selected content summary
        if st.session_state.selected_content:
            st.subheader("Selected Content")
            st.write(f"{len(st.session_state.selected_content)} title(s)")
            if st.button("Clear Selection", key="clear_content_sidebar"):
                st.session_state.selected_content = []
                st.session_state.show_fighters = False
                st.rerun()
        
        # Clear all filters button
        if st.button("Clear All", key="clear_all_sidebar"):
            st.session_state.selected_genres = []
            st.session_state.selected_themes = []
            st.session_state.selected_characters = []
            st.session_state.selected_content = []
            st.session_state.show_fighters = False
            st.rerun()


def render_content_browser(content_df):
    """Render content browser section - show all content in a scrollable list"""
    # Display all content in a vertical list (better for left column)
    for idx, (_, row) in enumerate(content_df.iterrows()):
        title = row['title']
        content_type = row.get('type', 'Unknown')
        content_tags = themes.tag_content(row)
        
        # Card styling
        is_selected = title in st.session_state.selected_content
        card_class = "selected-content" if is_selected else ""
        
        st.markdown(f'<div class="content-card {card_class}">', unsafe_allow_html=True)
        
        # Title and checkbox in same row
        col_title, col_check = st.columns([5, 1])
        with col_title:
            st.markdown(f"**{title}**")
            st.caption(content_type)
        with col_check:
            if st.checkbox("", value=is_selected, key=f"content_check_{idx}", label_visibility="collapsed"):
                if title not in st.session_state.selected_content:
                    st.session_state.selected_content.append(title)
                    st.rerun()
            else:
                if title in st.session_state.selected_content:
                    st.session_state.selected_content.remove(title)
                    st.rerun()
        
        # Display themes and genres compactly
        if content_tags['themes'] or content_tags['genres']:
            theme_text = ", ".join(content_tags['themes'][:2]) if content_tags['themes'] else ""
            genre_text = ", ".join(content_tags['genres'][:2]) if content_tags['genres'] else ""
            if theme_text or genre_text:
                st.caption(f"{theme_text}{' • ' if theme_text and genre_text else ''}{genre_text}")
        
        st.markdown('</div>', unsafe_allow_html=True)


def render_fighter_recommendations(selected_genres, selected_themes, selected_types,
                                   selected_characters, selected_content, mapping_df, fighters_df, content_df):
    """Render fighter recommendations section"""
    st.header("Fighter Recommendations")
    st.markdown("---")
    
    # Show active filters
    active_filters = []
    if selected_genres:
        active_filters.append(f"Genres: {', '.join(selected_genres[:3])}")
    if selected_themes:
        active_filters.append(f"Narratives: {', '.join(selected_themes[:3])}")
    if selected_characters:
        active_filters.append(f"Characters: {', '.join(selected_characters[:3])}")
    if selected_content:
        active_filters.append(f"{len(selected_content)} content title(s)")
    
    if active_filters:
        st.info("Active filters: " + " | ".join(active_filters))
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Discover fighters whose stories and fighting styles match your preferences**")
    with col2:
        n_recommendations = st.slider("Recommendations", 5, 20, 10, key="n_recs")
    
    # Get recommendations based on filters
    try:
        fighter_recs = recommendations.get_fighters_for_filters(
            selected_genres=selected_genres,
            selected_themes=selected_themes,
            selected_types=selected_types,
            selected_characters=selected_characters,
            selected_content=selected_content if selected_content else None,
            mapping_df=mapping_df,
            fighters_df=fighters_df,
            content_df=content_df,
            n_recommendations=n_recommendations
        )
        
        if fighter_recs.empty:
            st.warning("No fighter recommendations found for selected content.")
            return
    except Exception as e:
        st.error(f"Error getting recommendations: {str(e)}")
        return
    
    # Display recommendations in a polished grid
    cols = st.columns(2)
    for idx, rec in fighter_recs.iterrows():
        with cols[idx % 2]:
            # Fighter card header
            similarity_pct = rec['similarity_score'] * 100
            st.markdown(f"""
                <div class="fighter-card">
                    <h3>{rec['fighter_name']}</h3>
                    <p><strong>Style:</strong> {rec['fighting_style']}</p>
                    <p><strong>Match Score:</strong> {similarity_pct:.1f}%</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Toggle checkbox for profile
            profile_key = f"show_profile_{rec['fighter_name']}_{idx}"
            show_profile = st.checkbox("View Full Profile", key=profile_key, value=False)
            
            if show_profile:
                render_fighter_profile(rec['fighter_name'], fighters_df, mapping_df, content_df)
            
            st.markdown("<br>", unsafe_allow_html=True)


def render_fighter_profile(fighter_name, fighters_df, mapping_df, content_df):
    """Render detailed fighter profile"""
    profile = fighter_profile.get_fighter_profile(fighter_name, fighters_df)
    
    if profile is None:
        st.error(f"Fighter profile not found: {fighter_name}")
        return
    
    # Extended Biography
    st.subheader("Fighter Biography")
    
    # Get thematic tags for biography generation
    fighter_row = fighters_df[fighters_df['fighter'] == fighter_name]
    if len(fighter_row) > 0:
        fighter_tags = themes.tag_fighter(fighter_row.iloc[0], mapping_df)
        # Generate extended biography
        extended_bio = fighter_profile.generate_extended_biography(
            profile, fighter_row.iloc[0], fighter_tags
        )
        st.write(extended_bio)
    else:
        # Fallback to original lore
        lore = fighter_profile.format_fighter_lore(profile['other']['lore'])
        st.write(lore)
    
    # Personal details
    st.subheader("Personal Details")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if pd.notna(profile['personal']['age']) and profile['personal']['age']:
            st.metric("Age", f"{int(profile['personal']['age'])}")
        if profile['personal']['nationality'] and pd.notna(profile['personal']['nationality']):
            st.write(f"**Nationality:** {profile['personal']['nationality']}")
    
    with col2:
        if pd.notna(profile['personal']['height_inches']) and profile['personal']['height_inches']:
            height_reach = fighter_profile.format_height_reach(
                profile['personal']['height_inches'],
                profile['personal']['reach_inches']
            )
            st.write(f"**Height/Reach:** {height_reach}")
        if profile['personal']['stance'] and pd.notna(profile['personal']['stance']):
            st.write(f"**Stance:** {profile['personal']['stance']}")
    
    with col3:
        if profile['personal']['record'] and pd.notna(profile['personal']['record']):
            st.write(f"**Record:** {profile['personal']['record']}")
        if profile['personal']['wins'] is not None:
            wins = int(profile['personal']['wins']) if pd.notna(profile['personal']['wins']) else 0
            losses = int(profile['personal']['losses']) if pd.notna(profile['personal']['losses']) else 0
            draws = int(profile['personal']['draws']) if pd.notna(profile['personal']['draws']) else 0
            st.write(f"**W-L-D:** {wins}-{losses}-{draws}")
    
    # Stats visualization
    st.subheader("Fighting Statistics")
    fighter_stats = fighter_profile.get_fighter_stats_for_chart(profile)
    
    if fighter_stats:
        # Radar chart
        radar_fig = visualizations.create_radar_chart(fighter_stats, fighter_name)
        if radar_fig:
            st.plotly_chart(radar_fig, use_container_width=True)
        
        # Bar chart
        key_stats = ['strikes_per_min', 'strike_accuracy', 'takedown_accuracy', 'control_time_ratio']
        bar_fig = visualizations.create_stat_bar_chart(fighter_stats, key_stats, fighter_name)
        if bar_fig:
            st.plotly_chart(bar_fig, use_container_width=True)
    
    # Thematic tags - use collapsible container instead of expander (to avoid nesting)
    fighter_row = fighters_df[fighters_df['fighter'] == fighter_name]
    if len(fighter_row) > 0:
        fighter_tags = themes.tag_fighter(fighter_row.iloc[0], mapping_df)
        
        # Use a collapsible container with checkbox to toggle visibility
        show_tags = st.checkbox("Show Thematic Tags", value=False, key=f"show_tags_{fighter_name}")
        
        if show_tags:
            if fighter_tags['themes']:
                st.write("**Themes:**")
                for theme in fighter_tags['themes']:
                    st.markdown(f'<span class="theme-badge">{theme}</span>', unsafe_allow_html=True)
            
            if fighter_tags['character_archetypes']:
                st.write("**Character Archetypes:**")
                for archetype in fighter_tags['character_archetypes']:
                    st.markdown(f'<span class="theme-badge">{archetype}</span>', unsafe_allow_html=True)
    
    # Associated Titles Section - Content recommendations based on fighter themes
    st.subheader("Associated Titles")
    st.caption("Paramount+ content that matches this fighter's themes and characteristics")
    
    # Get content recommendations for this fighter
    try:
        content_recs = recommendations.get_content_for_fighter(
            fighter_name=fighter_name,
            mapping_df=mapping_df,
            content_df=content_df,
            n_recommendations=8
        )
        
        if len(content_recs) > 0:
            # Display content recommendations in a grid
            cols = st.columns(2)
            for idx, rec in content_recs.iterrows():
                with cols[idx % 2]:
                    similarity_pct = rec['similarity_score'] * 100
                    
                    # Content card
                    st.markdown(f"""
                        <div class="content-card" style="margin-bottom: 1rem;">
                            <h4 style="margin-bottom: 0.5rem;">{rec['content_title']}</h4>
                            <p style="margin: 0.25rem 0;"><strong>Type:</strong> {rec['content_type']}</p>
                            <p style="margin: 0.25rem 0;"><strong>Match Score:</strong> {similarity_pct:.0f}%</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Show matching themes/genres
                    if rec.get('common_themes') and str(rec['common_themes']).strip():
                        themes_list = [t.strip() for t in str(rec['common_themes']).split(',') if t.strip()]
                        for theme in themes_list[:4]:
                            st.markdown(f'<span class="theme-badge">{theme}</span>', unsafe_allow_html=True)
                    
                    if rec.get('common_genres') and str(rec['common_genres']).strip():
                        genres_list = [g.strip() for g in str(rec['common_genres']).split(',') if g.strip()]
                        if genres_list:
                            st.caption(f"**Genres:** {', '.join(genres_list[:3])}")
                    
                    if rec.get('content_description'):
                        desc = rec['content_description']
                        if len(desc) > 120:
                            desc = desc[:120] + "..."
                        st.caption(f"*{desc}*")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.info("No content recommendations available for this fighter.")
    except Exception as e:
        st.warning(f"Could not load content recommendations: {str(e)}")


def render_bundle_recommendations(selected_content, content_df, fighters_df, fight_data, mapping_df):
    """Render bundle recommendations section"""
    st.header("Thematic Bundles")
    st.markdown("Curated bundles combining content, fighters, and related fights.")
    
    n_bundles = st.slider("Number of bundles", 1, 5, 3, key="n_bundles")
    
    # Create bundles
    try:
        bundle_list = bundles.create_bundles_for_content(
            selected_content,
            content_df,
            fighters_df,
            fight_data,
            mapping_df,
            n_bundles=n_bundles,
            n_fighters_per_bundle=3
        )
        
        if not bundle_list:
            st.warning("No bundles available.")
            return
    except Exception as e:
        st.error(f"Error creating bundles: {str(e)}")
        return
    
    # Display bundles
    for idx, bundle in enumerate(bundle_list):
        bundle_title = bundle['content']['title'] if bundle['content'] else f"Bundle {idx + 1}"
        
        # Use checkbox toggle instead of expander to avoid icon rendering issues
        bundle_key = f"show_bundle_{idx}"
        show_bundle = st.checkbox(f"{bundle_title} - Thematic Bundle", key=bundle_key, value=False)
        
        if show_bundle:
            # Content
            if bundle['content']:
                st.subheader("Content")
                st.write(f"**{bundle['content']['title']}** ({bundle['content']['type']})")
                if bundle['content'].get('description'):
                    st.write(bundle['content']['description'])
                
                # Content themes
                if bundle['content']['themes']:
                    st.write("**Themes:**")
                    for theme in bundle['content']['themes']:
                        st.markdown(f'<span class="theme-badge">{theme}</span>', unsafe_allow_html=True)
            
            # Fighters
            if bundle['fighters']:
                st.subheader("Featured Fighters")
                for fighter in bundle['fighters']:
                    # Use a card instead of nested expander
                    st.markdown(f"""
                        <div class="fighter-card">
                            <h4>{fighter['name']} - {fighter['fighting_style']}</h4>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Fighter lore
                    lore_text = fighter['lore'][:300] + "..." if len(fighter['lore']) > 300 else fighter['lore']
                    st.write(lore_text)
                    
                    # Fighter themes
                    if fighter['themes']:
                        st.write("**Themes:**")
                        for theme in fighter['themes']:
                            st.markdown(f'<span class="theme-badge">{theme}</span>', unsafe_allow_html=True)
                    
                    st.markdown("---")  # Separator between fighters
            
            # Fights
            if bundle['fights']:
                st.subheader("Related Fights")
                fights_df = pd.DataFrame(bundle['fights'])
                st.dataframe(
                    fights_df[['event_name', 'event_date', 'fighter_1', 'fighter_2', 'winner', 'method']],
                    use_container_width=True,
                    hide_index=True
                )
            
            # Thematic connection
            if bundle['thematic_connection']:
                st.subheader("Why This Bundle Works")
                st.write(bundle['thematic_connection'])
            
            st.markdown("---")


if __name__ == "__main__":
    main()

