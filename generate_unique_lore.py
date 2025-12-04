"""
Generate unique, accurate fighter lore and biographies using LLM API.
Each fighter gets a completely unique narrative based on their actual stats, record, and fighting style.
"""

import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
from tqdm import tqdm
import time

# API configuration - user will provide API key
API_PROVIDER = os.getenv('LLM_API_PROVIDER', 'openai')  # 'openai', 'anthropic', 'google'
API_KEY = os.getenv('LLM_API_KEY', '')

def call_llm_api(prompt, system_prompt=None, max_tokens=500):
    """
    Call LLM API to generate unique fighter lore/biography.
    Supports OpenAI, Anthropic Claude, and Google Gemini.
    
    Args:
        prompt: User prompt
        system_prompt: System prompt (optional)
        max_tokens: Maximum tokens to generate
    
    Returns:
        Generated text
    """
    if not API_KEY:
        raise ValueError("API_KEY environment variable not set. Please set LLM_API_KEY.")
    
    if API_PROVIDER.lower() == 'openai':
        try:
            import openai
            client = openai.OpenAI(api_key=API_KEY)
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # or "gpt-4" for better quality
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.9  # Higher temperature for more creativity
            )
            return response.choices[0].message.content.strip()
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    elif API_PROVIDER.lower() == 'anthropic':
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=API_KEY)
            
            messages = []
            if system_prompt:
                messages.append({"role": "user", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",  # or "claude-3-opus-20240229" for better quality
                max_tokens=max_tokens,
                temperature=0.9,
                messages=messages
            )
            return response.content[0].text.strip()
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    elif API_PROVIDER.lower() == 'google':
        try:
            import google.generativeai as genai
            genai.configure(api_key=API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.9
                )
            )
            return response.text.strip()
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
    
    else:
        raise ValueError(f"Unknown API provider: {API_PROVIDER}. Use 'openai', 'anthropic', or 'google'")


def generate_fighter_lore_with_api(fighter_name, fighter_row, cluster_styles_dict=None):
    """
    Generate unique, accurate lore for a fighter using LLM API.
    
    Args:
        fighter_name: Fighter's name
        fighter_row: DataFrame row with fighter data
        cluster_styles_dict: Dictionary mapping cluster IDs to fighting styles
    
    Returns:
        Unique lore string
    """
    # Extract fighter data
    stats = {
        'strikes_per_min': fighter_row.get('strikes_landed_per_min_mean', 0) if pd.notna(fighter_row.get('strikes_landed_per_min_mean')) else 0,
        'strike_accuracy': fighter_row.get('strike_accuracy_mean', 0) if pd.notna(fighter_row.get('strike_accuracy_mean')) else 0,
        'head_strike_ratio': fighter_row.get('head_strike_ratio_mean', 0) if pd.notna(fighter_row.get('head_strike_ratio_mean')) else 0,
        'body_strike_ratio': fighter_row.get('body_strike_ratio_mean', 0) if pd.notna(fighter_row.get('body_strike_ratio_mean')) else 0,
        'leg_strike_ratio': fighter_row.get('leg_strike_ratio_mean', 0) if pd.notna(fighter_row.get('leg_strike_ratio_mean')) else 0,
        'takedown_accuracy': fighter_row.get('takedown_accuracy_mean', 0) if pd.notna(fighter_row.get('takedown_accuracy_mean')) else 0,
        'control_time_ratio': fighter_row.get('control_time_ratio_mean', 0) if pd.notna(fighter_row.get('control_time_ratio_mean')) else 0,
    }
    
    personal = {
        'age': fighter_row.get('age', None),
        'nationality': fighter_row.get('nationality', None),
        'height_inches': fighter_row.get('height_inches', None),
        'reach_inches': fighter_row.get('reach_inches', None),
        'stance': fighter_row.get('stance', None),
        'wins': fighter_row.get('wins', None),
        'losses': fighter_row.get('losses', None),
        'draws': fighter_row.get('draws', None),
        'birthplace': fighter_row.get('birthplace', None),
    }
    
    cluster_id = fighter_row.get('kmeans_cluster', None)
    fighting_style = None
    if cluster_styles_dict and pd.notna(cluster_id):
        fighting_style = cluster_styles_dict.get(int(cluster_id), None)
    if not fighting_style:
        fighting_style = fighter_row.get('fighting_style', 'Fighter')
    
    # Format physical stats
    height_str = ""
    if pd.notna(personal['height_inches']) and personal['height_inches']:
        height_ft = int(personal['height_inches'] // 12)
        height_in = int(personal['height_inches'] % 12)
        height_str = f"{height_ft}'{height_in}\""
    
    reach_str = ""
    if pd.notna(personal['reach_inches']) and personal['reach_inches']:
        reach_ft = int(personal['reach_inches'] // 12)
        reach_in = int(personal['reach_inches'] % 12)
        reach_str = f"{reach_ft}'{reach_in}\""
    
    record_str = ""
    if pd.notna(personal['wins']) and pd.notna(personal['losses']):
        wins = int(personal['wins']) if pd.notna(personal['wins']) else 0
        losses = int(personal['losses']) if pd.notna(personal['losses']) else 0
        draws = int(personal['draws']) if pd.notna(personal['draws']) else 0
        record_str = f"{wins}-{losses}-{draws}"
    
    # Build comprehensive prompt
    system_prompt = """You are a skilled sports writer specializing in UFC fighter profiles. 
Write compelling, unique biographical narratives that are accurate to the fighter's statistics and background.
Each biography should be completely different in style, tone, and narrative structure.
Be creative but factual. Incorporate their fighting style, stats, and personal details naturally."""
    
    user_prompt = f"""Write a unique, compelling biographical narrative for UFC fighter {fighter_name}.

Fighter Statistics:
- Fighting Style: {fighting_style}
- Strikes per minute: {stats['strikes_per_min']:.1f}
- Strike accuracy: {stats['strike_accuracy']*100:.0f}%
- Head strike ratio: {stats['head_strike_ratio']*100:.0f}%
- Body strike ratio: {stats['body_strike_ratio']*100:.0f}%
- Leg strike ratio: {stats['leg_strike_ratio']*100:.0f}%
- Takedown accuracy: {stats['takedown_accuracy']*100:.0f}%
- Control time ratio: {stats['control_time_ratio']*100:.0f}%

Personal Details:
- Age: {personal['age'] if pd.notna(personal['age']) else 'Unknown'}
- Nationality: {personal['nationality'] if pd.notna(personal['nationality']) else 'Unknown'}
- Birthplace: {personal['birthplace'] if pd.notna(personal['birthplace']) else 'Unknown'}
- Height: {height_str if height_str else 'Unknown'}
- Reach: {reach_str if reach_str else 'Unknown'}
- Stance: {personal['stance'] if pd.notna(personal['stance']) else 'Unknown'}
- Record: {record_str if record_str else 'Unknown'}

Write a 2-3 paragraph biographical narrative that:
1. Is completely unique in writing style (vary sentence structure, tone, and narrative approach)
2. Accurately reflects their fighting style and statistics
3. Incorporates their personal details naturally
4. Creates a compelling story about their journey and approach to fighting
5. Is different from every other fighter's biography

Write only the biography, no labels or headers."""

    try:
        lore = call_llm_api(user_prompt, system_prompt, max_tokens=400)
        return lore
    except Exception as e:
        print(f"Error generating lore for {fighter_name}: {e}")
        # Fallback to basic description
        return f"{fighter_name} is a {fighting_style.lower()} from {personal.get('nationality', 'unknown origin')} with a {record_str if record_str else 'professional'} record."


def generate_extended_biography_with_api(fighter_profile, fighter_row, fighter_tags):
    """
    Generate extended biography using LLM API for maximum uniqueness.
    This will be called from the app when displaying fighter profiles.
    """
    fighter_name = fighter_profile['name']
    stats = fighter_profile['stats']
    personal = fighter_profile['personal']
    themes_list = fighter_tags.get('themes', [])
    archetypes = fighter_tags.get('character_archetypes', [])
    fighting_style = fighter_tags.get('fighting_style', 'Fighter')
    
    # Format details
    age = personal.get('age', 'Unknown')
    nationality = personal.get('nationality', 'Unknown')
    birthplace = personal.get('birthplace', 'Unknown')
    
    height_str = ""
    if pd.notna(personal.get('height_inches')) and personal.get('height_inches'):
        height_ft = int(personal['height_inches'] // 12)
        height_in = int(personal['height_inches'] % 12)
        height_str = f"{height_ft}'{height_in}\""
    
    reach_str = ""
    if pd.notna(personal.get('reach_inches')) and personal.get('reach_inches'):
        reach_ft = int(personal['reach_inches'] // 12)
        reach_in = int(personal['reach_inches'] % 12)
        reach_str = f"{reach_ft}'{reach_in}\""
    
    wins = personal.get('wins', 0)
    losses = personal.get('losses', 0)
    draws = personal.get('draws', 0)
    record_str = f"{int(wins) if pd.notna(wins) else 0}-{int(losses) if pd.notna(losses) else 0}-{int(draws) if pd.notna(draws) else 0}"
    total_fights = (int(wins) if pd.notna(wins) else 0) + (int(losses) if pd.notna(losses) else 0) + (int(draws) if pd.notna(draws) else 0)
    
    system_prompt = """You are a skilled sports biographer writing detailed UFC fighter profiles.
Write a 3-5 paragraph extended biography that is completely unique in style, tone, and narrative structure.
Each biography should be different from every other fighter's biography.
Be creative, engaging, and accurate to the fighter's statistics and background."""
    
    user_prompt = f"""Write a detailed 3-5 paragraph extended biography for UFC fighter {fighter_name}.

Fighter Statistics:
- Fighting Style: {fighting_style}
- Strikes per minute: {stats['strikes_per_min']:.1f}
- Strike accuracy: {stats['strike_accuracy']*100:.0f}%
- Takedown accuracy: {stats['takedown_accuracy']*100:.0f}%
- Control time ratio: {stats['control_time_ratio']*100:.0f}%

Personal Details:
- Age: {age}
- Nationality: {nationality}
- Birthplace: {birthplace}
- Height: {height_str if height_str else 'Unknown'}
- Reach: {reach_str if reach_str else 'Unknown'}
- Stance: {personal.get('stance', 'Unknown')}
- Record: {record_str} ({total_fights} fights)

Themes: {', '.join(themes_list[:10]) if themes_list else 'None'}
Character Archetypes: {', '.join(archetypes) if archetypes else 'None'}

Write a compelling, unique extended biography (3-5 paragraphs) that:
1. Has a completely unique writing style (vary sentence structure, tone, narrative approach)
2. Accurately reflects their fighting style, statistics, and themes
3. Tells a compelling story about their journey, approach, and character
4. Is different from every other fighter's biography

Write only the biography, no labels or headers."""

    try:
        biography = call_llm_api(user_prompt, system_prompt, max_tokens=600)
        return biography
    except Exception as e:
        print(f"Error generating extended biography for {fighter_name}: {e}")
        return None


def main():
    """Main function to regenerate all fighter lore with API"""
    print("=" * 60)
    print("Fighter Lore Generation with LLM API")
    print("=" * 60)
    
    # Check for API key
    if not API_KEY:
        print("\n❌ ERROR: API_KEY not set!")
        print("\nPlease set your API key using one of these methods:")
        print("  export LLM_API_KEY='your-api-key-here'")
        print("  export LLM_API_PROVIDER='openai'  # or 'anthropic' or 'google'")
        print("\nOr set them in your environment before running this script.")
        return
    
    print(f"\n✓ Using API Provider: {API_PROVIDER}")
    print(f"✓ API Key: {'*' * (len(API_KEY) - 4) + API_KEY[-4:] if len(API_KEY) > 4 else '****'}")
    
    # Load data
    print("\nLoading fighter data...")
    fighters_df = pd.read_csv('fighters_with_lore.csv')
    
    # Load cluster styles if available
    cluster_styles_dict = None
    if Path('cluster_styles.json').exists():
        with open('cluster_styles.json', 'r') as f:
            cluster_styles_dict = json.load(f)
        print(f"✓ Loaded {len(cluster_styles_dict)} cluster styles")
    
    print(f"✓ Loaded {len(fighters_df)} fighters")
    
    # Ask user how many to regenerate
    print("\n" + "=" * 60)
    print("How many fighters would you like to regenerate?")
    print("  - Enter a number (e.g., 10) to regenerate that many")
    print("  - Enter 'all' to regenerate all fighters")
    print("  - Enter 'test' to regenerate just 3 fighters as a test")
    
    choice = input("\nYour choice: ").strip().lower()
    
    if choice == 'all':
        fighters_to_process = fighters_df
    elif choice == 'test':
        fighters_to_process = fighters_df.head(3)
    else:
        try:
            num = int(choice)
            fighters_to_process = fighters_df.head(num)
        except ValueError:
            print("Invalid choice. Processing first 10 fighters.")
            fighters_to_process = fighters_df.head(10)
    
    print(f"\n✓ Will regenerate lore for {len(fighters_to_process)} fighters")
    
    # Confirm
    confirm = input("\nProceed? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        return
    
    # Generate lore
    print("\n" + "=" * 60)
    print("Generating unique lore for each fighter...")
    print("=" * 60)
    
    new_lore_list = []
    errors = []
    
    for idx, (_, row) in enumerate(tqdm(fighters_to_process.iterrows(), total=len(fighters_to_process), desc="Generating lore")):
        fighter_name = row['fighter']
        
        try:
            lore = generate_fighter_lore_with_api(fighter_name, row, cluster_styles_dict)
            new_lore_list.append(lore)
            
            # Rate limiting - be nice to the API
            time.sleep(0.5)  # 0.5 second delay between requests
            
        except Exception as e:
            print(f"\n⚠️ Error generating lore for {fighter_name}: {e}")
            errors.append((fighter_name, str(e)))
            # Use existing lore as fallback
            new_lore_list.append(row.get('lore', ''))
    
    # Update DataFrame
    print("\n" + "=" * 60)
    print("Updating fighter data...")
    
    # Create a copy for safety
    updated_df = fighters_df.copy()
    
    # Update lore for processed fighters
    for idx, (_, row) in enumerate(fighters_to_process.iterrows()):
        original_idx = fighters_df.index[fighters_df['fighter'] == row['fighter']].tolist()[0]
        updated_df.at[original_idx, 'lore'] = new_lore_list[idx]
    
    # Save updated data
    backup_file = f"fighters_with_lore_backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
    fighters_df.to_csv(backup_file, index=False)
    print(f"✓ Created backup: {backup_file}")
    
    updated_df.to_csv('fighters_with_lore.csv', index=False)
    print(f"✓ Updated fighters_with_lore.csv")
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"✓ Processed: {len(fighters_to_process)} fighters")
    print(f"✓ Successful: {len(fighters_to_process) - len(errors)}")
    print(f"⚠️ Errors: {len(errors)}")
    
    if errors:
        print("\nErrors encountered:")
        for fighter, error in errors:
            print(f"  - {fighter}: {error}")
    
    print(f"\n✓ Unique lore entries: {updated_df['lore'].nunique()}")
    print("\nDone! The app will now use the updated lore.")


if __name__ == "__main__":
    main()

