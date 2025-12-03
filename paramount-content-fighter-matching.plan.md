# Paramount+ Content to Fighter Matching System

## Overview
Scrape Paramount+ website content, extract themes and character information, map content stories to fighter lore using weighted matching (Theme > Genre > Narrative), use OCEAN profiles to predict content preferences, and create bidirectional recommendations (content → fighters and fighters → content).

## Implementation Plan

### 1. Scrape Paramount+ Content Catalog
- **File**: `ufc_fighter_analysis.ipynb` (new section)
- Scrape Paramount+ website (paramountplus.com) to get:
  - Content titles
  - Genres
  - Descriptions/synopses
  - Themes (extract from descriptions)
  - Character information
  - Content type (movie, TV show, sports, etc.)
- Handle pagination and different content categories
- Rate limiting and error handling
- Save to CSV (`paramount_content_catalog.csv`)

### 2. Extract Themes and Characters from Content
- **File**: `ufc_fighter_analysis.ipynb` (new cell)
- Use NLP/text analysis to extract:
  - **Themes**: underdog, redemption, rivalry, triumph, struggle, legacy, etc.
  - **Character archetypes**: hero, anti-hero, mentor, challenger, etc.
  - **Narrative patterns**: rise-to-glory, comeback story, rivalry arc, etc.
- Use keyword extraction and sentiment analysis
- Create theme vectors for each content item

### 3. Map Content Stories to Fighter Lore
- **File**: `ufc_fighter_analysis.ipynb` (new cell)
- Create mapping function with weighted importance:
  1. **Theme matching** (highest weight - 50%):
     - Match content themes to fighter lore themes
     - Example: "underdog story" content → fighters with comeback narratives
  2. **Genre matching** (medium weight - 30%):
     - Match content genres to fighting styles
     - Example: "action" content → aggressive strikers
  3. **Narrative matching** (lower weight - 20%):
     - Match narrative arcs to fighter career patterns
     - Example: "redemption arc" → fighters who overcame losses
- Create similarity scores between content and fighters
- Store mapping in DataFrame

### 4. Predict Content Preferences from OCEAN Profiles
- **File**: `ufc_fighter_analysis.ipynb` (new cell)
- Create function `predict_content_preferences(ocean_scores)` that:
  - Maps OCEAN traits to content preferences:
    - High Extraversion → action, sports, competitive content
    - High Openness → diverse genres, creative content
    - High Conscientiousness → structured narratives, sports documentaries
    - Low Agreeableness → competitive, rivalry-focused content
    - High Neuroticism → dramatic, emotional content
  - Returns preferred content themes/genres/narratives
- Use same cosine similarity approach as fighter preferences

### 5. Bidirectional Recommendation System
- **File**: `ufc_fighter_analysis.ipynb` (new cell)
- **Content → Fighter Recommendations**:
  - Function: `recommend_fighters_for_content(content_title)`
  - Find content's themes/genres/narratives
  - Match to fighters using weighted mapping
  - Return top N fighters with explanations
  
- **Fighter → Content Recommendations**:
  - Function: `recommend_content_for_fighter(fighter_name)`
  - Extract fighter's lore themes
  - Match to content using weighted mapping
  - Return top N content items with explanations

### 6. User-Centric Recommendations
- **File**: `ufc_fighter_analysis.ipynb` (new cell)
- Function: `recommend_for_user(ocean_profile, viewing_history=None)`:
  - Predict content preferences from OCEAN
  - Optionally incorporate viewing history
  - Recommend both content AND fighters
  - Explain connections: "Based on your personality, you might enjoy [content] and fighters like [fighter] because..."

### 7. Visualization and Analysis
- **File**: `ufc_fighter_analysis.ipynb` (new cell)
- Visualizations:
  - Content theme distribution
  - Theme-fighter cluster heatmap
  - User preference flow (OCEAN → Content → Fighters)
  - Sample recommendations with explanations

## Technical Considerations
- **Paramount+ Website Structure**: May require inspection of actual HTML structure
- **Theme Extraction**: Use keyword matching, NLP libraries (spaCy, NLTK), or LLM-based extraction
- **Weighted Matching**: Implement custom similarity function combining theme (50%), genre (30%), narrative (20%)
- **OCEAN to Content Mapping**: Create preference profiles similar to fighter cluster preferences
- **Bidirectional Matching**: Ensure consistency in both directions

## Dependencies
- `requests`, `beautifulsoup4` - Web scraping (already installed)
- `spaCy` or `nltk` - NLP for theme extraction (may need to install)
- `pandas`, `numpy`, `scikit-learn` - Data manipulation (already installed)

## File Structure
Add new cells to `ufc_fighter_analysis.ipynb`:
1. Scrape Paramount+ content catalog
2. Extract themes and characters
3. Create content-fighter mapping function
4. Predict content preferences from OCEAN
5. Content → Fighter recommendations
6. Fighter → Content recommendations
7. User-centric recommendations
8. Visualizations

## Output Files
- `paramount_content_catalog.csv` - Scraped content data
- `content_fighter_mapping.csv` - Similarity scores between content and fighters
- `user_content_fighter_recommendations.csv` - Sample recommendations

