"""
Thematic metadata extraction and tagging module.
Enhanced with wider theme vocabulary and nuanced tagging logic.
"""

import pandas as pd
import numpy as np
import ast
import re
import config


def format_theme_for_display(theme: str) -> str:
    """
    Format theme for display by replacing underscores with spaces and capitalizing.
    Converts "championship_quest" to "Championship Quest"
    
    Args:
        theme: Theme string with underscores
    
    Returns:
        Formatted theme string with spaces
    """
    if not theme or pd.isna(theme):
        return ""
    return str(theme).replace('_', ' ').title()


def format_themes_for_display(themes: list) -> list:
    """
    Format a list of themes for display.
    
    Args:
        themes: List of theme strings
    
    Returns:
        List of formatted theme strings
    """
    if not themes:
        return []
    return [format_theme_for_display(theme) for theme in themes if theme and pd.notna(theme)]


def parse_list_column(value):
    """Parse string representation of list or return list as-is"""
    # Handle pandas Series/arrays - extract scalar value
    if isinstance(value, pd.Series):
        if len(value) == 0:
            return []
        value = value.iloc[0]
    elif isinstance(value, np.ndarray):
        if len(value) == 0:
            return []
        value = value.item() if value.size == 1 else value[0]
    
    # Check for NaN - handle scalar values only
    try:
        is_na = pd.isna(value)
        # If pd.isna returns an array, convert to scalar
        if isinstance(is_na, (pd.Series, np.ndarray)):
            is_na = bool(is_na.any()) if len(is_na) > 0 else True
        elif not isinstance(is_na, bool):
            is_na = bool(is_na)
    except:
        is_na = False
    
    # Check for empty string
    is_empty_str = isinstance(value, str) and value.strip() == ''
    
    if is_na or is_empty_str:
        return []
    
    if isinstance(value, str):
        try:
            return ast.literal_eval(value)
        except:
            # If it's a comma-separated string, split it
            return [item.strip() for item in value.split(',') if item.strip()]
    if isinstance(value, list):
        return value
    return []


# SHARED UNIFIED THEME VOCABULARY
# This vocabulary is used by BOTH fighters and content for consistent matching
# Extensive and varied themes (100+ themes) for rich, specific recommendations
SHARED_THEME_KEYWORDS = {
    # Combat & Fighting Style (More Specific)
    'aggression': ['aggressive', 'relentless', 'overwhelming', 'barrage', 'assault', 'furious', 'intense', 'combat', 'ceaseless', 'unending', 'constant pressure'],
    'precision': ['precise', 'surgical', 'methodical', 'calculated', 'accurate', 'technical', 'skilled', 'disciplined', 'deadly accuracy', 'surgical precision'],
    'strategy': ['strategic', 'tactical', 'smart', 'calculated', 'game plan', 'intelligent', 'cunning', 'clever', 'tactical brilliance', 'strategic approach'],
    'brutal_power': ['brutal', 'devastating', 'crushing', 'overpowering', 'destructive', 'savage', 'ruthless', 'merciless'],
    'technical_mastery': ['technical', 'masterful', 'skilled', 'expert', 'proficient', 'polished', 'refined', 'crafted'],
    'explosive_speed': ['explosive', 'lightning', 'rapid', 'swift', 'quick', 'fast', 'blazing', 'sudden'],
    'pressure_fighting': ['pressure', 'forward', 'pressing', 'advancing', 'pushing', 'overwhelming', 'relentless pressure'],
    'counter_striking': ['counter', 'counter-striker', 'reactive', 'waiting', 'patient', 'opportunistic', 'counter-attack'],
    
    # Narrative Arcs & Story Types (More Specific)
    'underdog': ['underdog', 'comeback', 'against odds', 'overcame', 'defied expectations', 'unlikely', 'surprise', 'underestimated'],
    'redemption': ['redemption', 'second chance', 'returned', 'bounced back', 'make amends', 'forgiven', 'renewed', 'rebirth'],
    'rivalry': ['rival', 'competition', 'faced', 'battled', 'opponent', 'challenge', 'confrontation', 'enemy', 'nemesis'],
    'triumph': ['champion', 'victory', 'dominated', 'won', 'success', 'conquer', 'achievement', 'glory', 'conquered'],
    'struggle': ['struggled', 'hardship', 'difficulty', 'challenged', 'obstacle', 'adversity', 'trial', 'tribulation', 'hardship'],
    'legacy': ['legacy', 'career', 'veteran', 'experienced', 'heritage', 'tradition', 'history', 'legend', 'veteran savvy'],
    'survival': ['survived', 'endured', 'persevered', 'persist', 'escape', 'endurance', 'resilience', 'toughness', 'endured'],
    'rise_to_glory': ['rising', 'emerging', 'ascending', 'climbing', 'progress', 'development', 'growth', 'breakthrough', 'climbing'],
    'fall_from_grace': ['fallen', 'decline', 'downfall', 'lost', 'defeated', 'broken', 'crushed', 'fallen champion'],
    'revenge': ['revenge', 'vengeance', 'avenge', 'retaliation', 'payback', 'retribution', 'settle the score'],
    'proving_grounds': ['proving', 'test', 'trial', 'challenge', 'demonstrate', 'show', 'establish', 'validate'],
    'master_apprentice': ['master', 'apprentice', 'student', 'teacher', 'mentor', 'learning', 'teaching', 'passing knowledge'],
    
    # Emotional & Psychological States (More Nuanced)
    'determination': ['determined', 'focused', 'driven', 'committed', 'dedicated', 'persistent', 'unwavering', 'single-minded'],
    'resilience': ['resilient', 'tough', 'durable', 'unyielding', 'unbreakable', 'strong', 'hardy', 'indomitable'],
    'courage': ['courage', 'brave', 'fearless', 'bold', 'daring', 'valiant', 'heroic', 'gallant', 'fearless'],
    'discipline': ['disciplined', 'controlled', 'composed', 'calm', 'steady', 'measured', 'restrained', 'composed'],
    'rage': ['rage', 'fury', 'anger', 'wrath', 'furious', 'enraged', 'incensed', 'livid'],
    'calm_under_pressure': ['calm', 'composed', 'steady', 'unflappable', 'cool', 'collected', 'unshaken'],
    'mental_toughness': ['mental toughness', 'fortitude', 'grit', 'resolve', 'willpower', 'strength of mind'],
    'vulnerability': ['vulnerable', 'exposed', 'weak', 'fragile', 'susceptible', 'open', 'defenseless'],
    
    # Social & Relationship Dynamics (More Specific)
    'brotherhood': ['team', 'together', 'loyal', 'unit', 'bond', 'alliance', 'partnership', 'fellowship', 'brotherhood'],
    'leadership': ['leader', 'captain', 'guided', 'command', 'mentor', 'influence', 'authority', 'inspiration', 'leads'],
    'isolation': ['alone', 'solitary', 'independent', 'lone', 'isolated', 'self-reliant', 'autonomous', 'loner'],
    'betrayal': ['betrayed', 'betrayal', 'treachery', 'deception', 'backstab', 'disloyal', 'treason', 'double-cross'],
    'loyalty': ['loyal', 'faithful', 'devoted', 'dedicated', 'committed', 'allegiance', 'fidelity'],
    'rivalry_turned_respect': ['respect', 'mutual respect', 'honor', 'acknowledgment', 'recognition', 'worthy opponent'],
    'family_legacy': ['family', 'heritage', 'lineage', 'bloodline', 'ancestry', 'generations', 'family tradition'],
    
    # Physical Attributes & Fighting Characteristics (More Specific)
    'power': ['powerful', 'forceful', 'strong', 'mighty', 'dominant', 'overpowering', 'crushing', 'devastating power'],
    'speed': ['fast', 'quick', 'swift', 'rapid', 'lightning', 'explosive', 'agile', 'nimble', 'blazing speed'],
    'endurance': ['endurance', 'stamina', 'lasting', 'durable', 'persistent', 'long-lasting', 'sustained', 'cardio'],
    'versatility': ['versatile', 'adaptable', 'flexible', 'well-rounded', 'diverse', 'multi-faceted', 'complete', 'all-around'],
    'physical_dominance': ['dominant', 'overpowering', 'imposing', 'commanding', 'overwhelming', 'superior'],
    'size_advantage': ['tall', 'large', 'big', 'imposing', 'massive', 'giant', 'towering'],
    'speed_advantage': ['quick', 'fast', 'agile', 'nimble', 'lightning-fast', 'blur', 'speed demon'],
    'reach_advantage': ['reach', 'long arms', 'extended', 'range', 'distance control', 'reach advantage'],
    
    # Mental & Tactical Approaches (More Specific)
    'patience': ['patient', 'waiting', 'biding', 'methodical', 'careful', 'deliberate', 'thoughtful', 'patient approach'],
    'instinct': ['instinct', 'intuitive', 'natural', 'innate', 'inborn', 'gut feeling', 'reactive', 'natural instinct'],
    'innovation': ['innovative', 'creative', 'unconventional', 'unique', 'original', 'novel', 'experimental', 'creative approach'],
    'calculated_risk': ['calculated', 'risk', 'gamble', 'bold move', 'strategic risk', 'daring play'],
    'adaptability': ['adapt', 'adjust', 'modify', 'change', 'evolve', 'flexible', 'versatile', 'adapts'],
    'game_planning': ['game plan', 'strategy', 'tactical', 'planned', 'prepared', 'strategic approach'],
    
    # Conflict & Resolution Types (More Specific)
    'conflict': ['conflict', 'struggle', 'battle', 'war', 'fight', 'clash', 'confrontation', 'dispute', 'combat'],
    'resolution': ['resolution', 'solution', 'resolve', 'conclusion', 'ending', 'settlement', 'closure', 'resolution'],
    'transformation': ['transformed', 'changed', 'evolved', 'metamorphosis', 'growth', 'development', 'shift', 'evolution'],
    'unfinished_business': ['unfinished', 'unresolved', 'pending', 'outstanding', 'remaining', 'left to do'],
    'decisive_moment': ['decisive', 'critical', 'pivotal', 'turning point', 'moment of truth', 'crucial'],
    
    # Values & Morality (More Specific)
    'honor': ['honor', 'honorable', 'dignity', 'integrity', 'respect', 'noble', 'principled', 'code of honor'],
    'justice': ['justice', 'fair', 'righteous', 'moral', 'ethical', 'right', 'correct', 'just'],
    'sacrifice': ['sacrifice', 'sacrificed', 'gave up', 'forfeited', 'surrendered', 'yielded', 'self-sacrifice'],
    'corruption': ['corrupt', 'corruption', 'dishonest', 'unethical', 'immoral', 'unscrupulous'],
    'redemption_through_struggle': ['redemption', 'atone', 'make amends', 'redeem', 'forgiveness', 'second chance'],
    
    # Time & Journey Types (More Specific)
    'journey': ['journey', 'path', 'road', 'quest', 'adventure', 'voyage', 'expedition', 'pilgrimage', 'road traveled'],
    'destiny': ['destiny', 'fate', 'destined', 'meant to be', 'predetermined', 'inevitable', 'written in the stars'],
    'past': ['past', 'history', 'memories', 'remembered', 'former', 'previous', 'old', 'back in the day'],
    'future': ['future', 'ahead', 'coming', 'next', 'forward', 'prospect', 'potential', 'what lies ahead'],
    'present_moment': ['now', 'present', 'current', 'moment', 'here and now', 'living in the moment'],
    
    # Career & Achievement Types (More Specific)
    'championship_quest': ['championship', 'title', 'belt', 'crown', 'champion', 'title shot', 'championship run'],
    'comeback_story': ['comeback', 'return', 'come back', 'resurgence', 'revival', 'returning', 'back in action'],
    'rookie_rise': ['rookie', 'newcomer', 'debut', 'first', 'beginning', 'starting out', 'fresh'],
    'veteran_wisdom': ['veteran', 'experienced', 'seasoned', 'wise', 'knowledgeable', 'been there', 'seen it all'],
    'peak_performance': ['peak', 'prime', 'best', 'top form', 'at their best', 'peak performance'],
    'decline': ['decline', 'fading', 'past prime', 'slowing', 'diminishing', 'waning'],
    
    # Fighting Style Specific Narratives
    'volume_striker_narrative': ['volume', 'output', 'strikes per minute', 'relentless', 'overwhelming', 'constant pressure'],
    'precision_striker_narrative': ['precision', 'accuracy', 'surgical', 'calculated', 'methodical', 'precise'],
    'grappler_narrative': ['grappling', 'ground', 'takedown', 'submission', 'mat work', 'ground control'],
    'knockout_artist': ['knockout', 'ko', 'finish', 'stoppage', 'lights out', 'put to sleep'],
    'decision_fighter': ['decision', 'points', 'judges', 'scorecards', 'unanimous', 'split'],
    'finisher': ['finish', 'end', 'conclude', 'stop', 'terminate', 'put away'],
    
    # Additional Narrative Themes
    'hometown_hero': ['hometown', 'local', 'hometown hero', 'hometown favorite', 'local legend'],
    'immigrant_story': ['immigrant', 'immigration', 'came to', 'moved to', 'from another country'],
    'college_athlete': ['college', 'university', 'collegiate', 'NCAA', 'college wrestling', 'college football'],
    'military_background': ['military', 'army', 'navy', 'marines', 'air force', 'served', 'veteran'],
    'street_fighting': ['street', 'underground', 'backyard', 'bare knuckle', 'street fighting'],
    'martial_arts_lineage': ['lineage', 'master', 'grandmaster', 'tradition', 'martial arts family'],
    'injury_comeback': ['injury', 'injured', 'recovery', 'rehab', 'came back from injury', 'recovered'],
    'weight_class_journey': ['weight', 'cutting weight', 'weight class', 'moved up', 'moved down'],
    'coaching_philosophy': ['coach', 'training', 'camp', 'gym', 'team', 'training camp'],
    'family_support': ['family', 'parents', 'wife', 'children', 'kids', 'supportive family'],
    'financial_struggle': ['struggle', 'poverty', 'poor', 'money', 'financial', 'worked', 'job'],
    'early_losses': ['early', 'started', 'began', 'first fights', 'early career'],
    'title_contender': ['contender', 'ranked', 'top', 'number one', 'championship'],
    'gatekeeper': ['gatekeeper', 'test', 'prove', 'challenger', 'established'],
    'fan_favorite': ['fan', 'popular', 'beloved', 'favorite', 'crowd favorite'],
    'controversial': ['controversy', 'controversial', 'trash talk', 'outspoken', 'polarizing'],
    'quiet_professional': ['quiet', 'humble', 'professional', 'respectful', 'soft-spoken'],
    'showman': ['showman', 'entertainer', 'personality', 'charismatic', 'showmanship'],
    'training_partner': ['training partner', 'sparring', 'helped train', 'training with'],
    'late_bloomer': ['late', 'older', 'started late', 'began late', 'later in life'],
    'early_prodigy': ['young', 'prodigy', 'started young', 'early start', 'child'],
    'cross_training': ['cross training', 'multiple disciplines', 'various arts', 'diverse training'],
    'specialist': ['specialist', 'specialized', 'expert in', 'master of', 'focused on'],
    'well_rounded': ['well rounded', 'complete', 'versatile', 'all around', 'diverse'],
    
    # Content & Story Themes (Universal - apply to both fighters and content)
    'competition': ['competition', 'compete', 'competitive', 'tournament', 'championship', 'contest', 'match'],
    'family': ['family', 'familial', 'parent', 'child', 'sibling', 'brother', 'sister', 'mother', 'father'],
    'friendship': ['friendship', 'friend', 'friends', 'companionship', 'buddy', 'ally', 'companion'],
    'romance': ['romance', 'romantic', 'love', 'relationship', 'dating', 'couple', 'partner'],
    'adventure': ['adventure', 'adventurous', 'quest', 'journey', 'exploration', 'expedition'],
    'mystery': ['mystery', 'mysterious', 'secret', 'hidden', 'unknown', 'puzzle', 'enigma'],
    'thriller': ['thriller', 'thrilling', 'suspense', 'tense', 'edge of seat', 'nail-biting'],
    'comedy': ['comedy', 'comic', 'funny', 'humor', 'humorous', 'laugh', 'joke'],
    'drama': ['drama', 'dramatic', 'emotional', 'intense', 'serious', 'powerful'],
    'action': ['action', 'action-packed', 'exciting', 'thrilling', 'fast-paced', 'intense'],
    'horror': ['horror', 'horrifying', 'scary', 'frightening', 'terrifying', 'fear'],
    'sci_fi': ['science fiction', 'sci-fi', 'futuristic', 'space', 'technology', 'alien'],
    'fantasy': ['fantasy', 'magical', 'magic', 'supernatural', 'mythical', 'legendary'],
    'western': ['western', 'cowboy', 'frontier', 'wild west', 'ranch', 'outlaw'],
    'crime': ['crime', 'criminal', 'heist', 'robbery', 'gang', 'mafia', 'underworld'],
    'war': ['war', 'warfare', 'battle', 'military', 'soldier', 'combat', 'conflict'],
    'sports': ['sports', 'athletic', 'game', 'match', 'team', 'player', 'competition'],
    'biography': ['biography', 'biographical', 'life story', 'true story', 'based on'],
    'documentary': ['documentary', 'documentary', 'real', 'factual', 'non-fiction'],
    'superhero': ['superhero', 'superheroes', 'powers', 'superhuman', 'hero', 'villain'],
    'coming_of_age': ['coming of age', 'growing up', 'maturation', 'youth', 'teenage'],
    'road_trip': ['road trip', 'journey', 'travel', 'adventure', 'on the road'],
    'heist': ['heist', 'robbery', 'steal', 'thief', 'criminal', 'caper'],
    'revenge_tale': ['revenge', 'vengeance', 'retaliation', 'payback', 'settle score'],
    'survival_story': ['survival', 'survive', 'endure', 'persevere', 'overcome'],
    'fish_out_of_water': ['fish out of water', 'out of place', 'unfamiliar', 'new environment'],
    'buddy_cop': ['buddy cop', 'partners', 'duo', 'team up', 'partnership'],
    'found_family': ['found family', 'chosen family', 'adoptive', 'unlikely family'],
    'time_travel': ['time travel', 'time machine', 'past', 'future', 'temporal'],
    'parallel_universe': ['parallel universe', 'alternate reality', 'multiverse', 'dimension'],
    'post_apocalyptic': ['post-apocalyptic', 'apocalypse', 'aftermath', 'ruins', 'survival'],
    'dystopian': ['dystopian', 'dystopia', 'oppressive', 'totalitarian', 'future society'],
    'utopian': ['utopian', 'utopia', 'perfect', 'ideal', 'paradise'],
    'space_opera': ['space opera', 'space', 'galaxy', 'starship', 'cosmic'],
    'cyberpunk': ['cyberpunk', 'cyber', 'hacker', 'digital', 'virtual', 'neon'],
    'steampunk': ['steampunk', 'steam', 'victorian', 'industrial', 'mechanical'],
    'noir': ['noir', 'film noir', 'dark', 'gritty', 'detective', 'mystery'],
    'romantic_comedy': ['romantic comedy', 'rom-com', 'romance', 'comedy', 'love story'],
    'musical': ['musical', 'music', 'song', 'dance', 'singing', 'performance'],
    'historical': ['historical', 'history', 'period piece', 'era', 'past'],
    'contemporary': ['contemporary', 'modern', 'present day', 'current', 'today'],
    'period_drama': ['period drama', 'historical drama', 'period piece', 'era'],
    'courtroom': ['courtroom', 'legal', 'lawyer', 'trial', 'judge', 'jury'],
    'medical': ['medical', 'doctor', 'hospital', 'medicine', 'health', 'surgery'],
    'educational': ['educational', 'learning', 'teach', 'education', 'school'],
    'inspirational': ['inspirational', 'inspiring', 'motivational', 'uplifting', 'encouraging'],
    'heartwarming': ['heartwarming', 'touching', 'emotional', 'sweet', 'tender'],
    'tearjerker': ['tearjerker', 'sad', 'emotional', 'crying', 'touching'],
    'uplifting': ['uplifting', 'positive', 'hopeful', 'encouraging', 'inspiring'],
    'dark': ['dark', 'darkness', 'grim', 'bleak', 'somber', 'serious'],
    'lighthearted': ['lighthearted', 'light', 'fun', 'cheerful', 'bright', 'happy'],
    'intense': ['intense', 'intensity', 'powerful', 'strong', 'forceful'],
    'subtle': ['subtle', 'understated', 'gentle', 'quiet', 'soft'],
    'epic': ['epic', 'grand', 'large scale', 'sweeping', 'vast', 'massive'],
    'intimate': ['intimate', 'personal', 'close', 'small scale', 'personal'],
    'ensemble': ['ensemble', 'multiple characters', 'group', 'cast', 'many'],
    'character_study': ['character study', 'character driven', 'focused', 'deep'],
    'plot_driven': ['plot driven', 'story focused', 'narrative', 'action'],
    'atmospheric': ['atmospheric', 'mood', 'tone', 'ambiance', 'feeling'],
    'visually_stunning': ['visually stunning', 'beautiful', 'cinematic', 'stunning'],
    'dialogue_heavy': ['dialogue heavy', 'talkative', 'conversation', 'speech'],
    'minimal_dialogue': ['minimal dialogue', 'quiet', 'visual', 'silent'],
    'fast_paced': ['fast paced', 'quick', 'rapid', 'swift', 'brisk'],
    'slow_burn': ['slow burn', 'gradual', 'slow', 'methodical', 'patient'],
    'non_linear': ['non-linear', 'out of order', 'flashback', 'time jumps'],
    'linear': ['linear', 'chronological', 'order', 'sequence', 'timeline'],
    'experimental': ['experimental', 'avant-garde', 'unconventional', 'unique'],
    'traditional': ['traditional', 'classic', 'conventional', 'standard'],
    'subversive': ['subversive', 'challenging', 'rebellious', 'defiant'],
    'mainstream': ['mainstream', 'popular', 'commercial', 'accessible'],
    'indie': ['indie', 'independent', 'small', 'artistic', 'creative'],
    'blockbuster': ['blockbuster', 'big budget', 'major', 'large scale'],
    'cult_classic': ['cult classic', 'cult', 'niche', 'dedicated fans'],
    'award_winner': ['award winner', 'acclaimed', 'prized', 'honored'],
    'underrated': ['underrated', 'overlooked', 'hidden gem', 'unsung'],
    'overrated': ['overrated', 'hyped', 'overhyped', 'disappointing'],
    'nostalgic': ['nostalgic', 'nostalgia', 'remember', 'past', 'memory'],
    'futuristic': ['futuristic', 'future', 'ahead', 'forward', 'tomorrow'],
    'retro': ['retro', 'vintage', 'old', 'classic', 'throwback'],
    'modern': ['modern', 'contemporary', 'current', 'today', 'now'],
    'timeless': ['timeless', 'eternal', 'enduring', 'classic', 'evergreen'],
    'dated': ['dated', 'old', 'outdated', 'past', 'obsolete'],
    'relevant': ['relevant', 'current', 'topical', 'timely', 'now'],
    'escapist': ['escapist', 'escape', 'fantasy', 'getaway', 'retreat'],
    'realistic': ['realistic', 'real', 'true to life', 'authentic', 'genuine'],
    'surreal': ['surreal', 'dreamlike', 'unreal', 'fantastical', 'bizarre'],
    'grounded': ['grounded', 'realistic', 'down to earth', 'practical'],
    'fantastical': ['fantastical', 'fantasy', 'magical', 'unreal', 'wondrous'],
    'gritty': ['gritty', 'rough', 'harsh', 'tough', 'raw'],
    'polished': ['polished', 'smooth', 'refined', 'elegant', 'sophisticated'],
    'raw': ['raw', 'unfiltered', 'honest', 'real', 'authentic'],
    'stylized': ['stylized', 'artistic', 'designed', 'crafted', 'aesthetic'],
    'naturalistic': ['naturalistic', 'natural', 'real', 'authentic', 'genuine'],
    'melodramatic': ['melodramatic', 'dramatic', 'over the top', 'exaggerated'],
    'understated': ['understated', 'subtle', 'quiet', 'restrained', 'minimal'],
    'complex': ['complex', 'complicated', 'layered', 'multifaceted', 'intricate'],
    'simple': ['simple', 'straightforward', 'clear', 'easy', 'basic'],
    'deep': ['deep', 'profound', 'meaningful', 'significant', 'important'],
    'surface_level': ['surface level', 'shallow', 'superficial', 'light'],
    'thought_provoking': ['thought provoking', 'provocative', 'challenging', 'stimulating'],
    'mindless': ['mindless', 'simple', 'easy', 'light', 'entertaining'],
    'challenging': ['challenging', 'difficult', 'complex', 'demanding', 'hard'],
    'accessible': ['accessible', 'easy', 'simple', 'clear', 'understandable'],
    'niche': ['niche', 'specialized', 'specific', 'targeted', 'focused'],
    'universal': ['universal', 'broad', 'general', 'wide', 'all'],
    'mature': ['mature', 'adult', 'serious', 'grown up', 'sophisticated'],
    'family_friendly': ['family friendly', 'all ages', 'suitable', 'appropriate'],
    'adult': ['adult', 'mature', 'grown up', 'serious', 'sophisticated'],
    'youth_focused': ['youth focused', 'young', 'teen', 'adolescent', 'juvenile'],
    'all_ages': ['all ages', 'everyone', 'universal', 'family', 'general'],
}

# Alias for backward compatibility
THEME_KEYWORDS = SHARED_THEME_KEYWORDS


def extract_themes_from_text(text, theme_keywords=None):
    """
    Extract themes from text using keyword matching.
    
    Args:
        text: Text to analyze
        theme_keywords: Dictionary of theme -> keywords (uses THEME_KEYWORDS if None)
    
    Returns:
        List of themes found in text
    """
    if not text or pd.isna(text):
        return []
    
    text_lower = str(text).lower()
    themes = []
    
    if theme_keywords is None:
        theme_keywords = SHARED_THEME_KEYWORDS
    
    for theme, keywords in theme_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            themes.append(theme)
    
    return list(set(themes))  # Remove duplicates


def extract_fighter_themes_from_stats(fighter_row):
    """
    Extract varied and specific themes from fighter statistics.
    Creates more nuanced and diverse narrative tags based on actual performance data.
    
    Args:
        fighter_row: Fighter DataFrame row with stats
    
    Returns:
        List of specific themes based on fighting statistics and style
    """
    themes = []
    
    # Extract key stats
    strikes_per_min = fighter_row.get('strikes_landed_per_min_mean', 0) if pd.notna(fighter_row.get('strikes_landed_per_min_mean')) else 0
    strike_accuracy = fighter_row.get('strike_accuracy_mean', 0) if pd.notna(fighter_row.get('strike_accuracy_mean')) else 0
    takedown_accuracy = fighter_row.get('takedown_accuracy_mean', 0) if pd.notna(fighter_row.get('takedown_accuracy_mean')) else 0
    control_time_ratio = fighter_row.get('control_time_ratio_mean', 0) if pd.notna(fighter_row.get('control_time_ratio_mean')) else 0
    head_strike_ratio = fighter_row.get('head_strike_ratio_mean', 0) if pd.notna(fighter_row.get('head_strike_ratio_mean')) else 0
    body_strike_ratio = fighter_row.get('body_strike_ratio_mean', 0) if pd.notna(fighter_row.get('body_strike_ratio_mean')) else 0
    leg_strike_ratio = fighter_row.get('leg_strike_ratio_mean', 0) if pd.notna(fighter_row.get('leg_strike_ratio_mean')) else 0
    clinch_time_ratio = fighter_row.get('clinch_time_ratio_mean', 0) if pd.notna(fighter_row.get('clinch_time_ratio_mean')) else 0
    
    # Win rate and record - handle NaN properly
    wins_val = fighter_row.get('wins', None)
    wins = int(float(wins_val)) if pd.notna(wins_val) and wins_val != '' and wins_val != 0 else 0
    
    losses_val = fighter_row.get('losses', None)
    losses = int(float(losses_val)) if pd.notna(losses_val) and losses_val != '' else 0
    
    # Use fight count from stats if wins/losses not available
    fight_count_from_stats = fighter_row.get('strikes_landed_per_min_count', 0)
    if pd.notna(fight_count_from_stats):
        fight_count_from_stats = int(float(fight_count_from_stats))
    else:
        fight_count_from_stats = 0
    
    total_fights = wins + losses if (wins > 0 or losses > 0) else fight_count_from_stats
    win_rate = wins / total_fights if total_fights > 0 else 0
    
    # Age/experience - handle NaN properly
    age_val = fighter_row.get('age', None)
    age = int(float(age_val)) if pd.notna(age_val) and age_val != '' and age_val > 0 else 0
    
    # If no age but have fights, estimate age based on experience
    if age == 0 and total_fights > 0:
        # Rough estimate: fighters typically start around 20-25, add years based on fights
        age = 25 + min(total_fights // 2, 15)  # Estimate: 2 fights per year, max 15 years
    
    # Physical attributes
    height_inches = fighter_row.get('height_inches', 0) if pd.notna(fighter_row.get('height_inches')) else 0
    reach_inches = fighter_row.get('reach_inches', 0) if pd.notna(fighter_row.get('reach_inches')) else 0
    reach_advantage = reach_inches - height_inches if (height_inches > 0 and reach_inches > 0) else 0
    
    # STRIKING STYLE THEMES (More Specific)
    if strikes_per_min > 6.0:
        themes.append('aggression')
        themes.append('volume_striker_narrative')
        themes.append('pressure_fighting')
        if strike_accuracy > 0.5:
            themes.append('brutal_power')
    elif strikes_per_min > 4.0:
        themes.append('determination')
        themes.append('volume_striker_narrative')
    elif strikes_per_min > 2.0:
        themes.append('patience')
    
    # PRECISION THEMES (More Nuanced)
    if strike_accuracy > 0.65:
        themes.append('precision')
        themes.append('precision_striker_narrative')
        themes.append('technical_mastery')
        if strikes_per_min < 3.0:
            themes.append('counter_striking')
            themes.append('calm_under_pressure')
    elif strike_accuracy > 0.55:
        themes.append('precision')
        themes.append('precision_striker_narrative')
    
    # GRAPPLING THEMES (More Specific)
    if control_time_ratio > 0.5:
        themes.append('grappler_narrative')
        themes.append('physical_dominance')
        themes.append('strategy')
        themes.append('discipline')
    elif takedown_accuracy > 0.6:
        themes.append('grappler_narrative')
        themes.append('strategy')
        themes.append('technical_mastery')
    elif takedown_accuracy > 0.4 or control_time_ratio > 0.3:
        themes.append('grappler_narrative')
        themes.append('versatility')
    
    # STRIKE TARGET THEMES (More Specific)
    if head_strike_ratio > 0.7:
        themes.append('knockout_artist')
        themes.append('courage')
        themes.append('precision')
    elif head_strike_ratio > 0.65:
        themes.append('knockout_artist')
        themes.append('precision')
    
    if body_strike_ratio > 0.45:
        themes.append('strategy')
        themes.append('endurance')
        themes.append('calculated_risk')
    elif body_strike_ratio > 0.35:
        themes.append('strategy')
    
    if leg_strike_ratio > 0.35:
        themes.append('technical_mastery')
        themes.append('strategy')
        themes.append('innovation')
    
    # CLINCH WORK
    if clinch_time_ratio > 0.3:
        themes.append('pressure_fighting')
        themes.append('physical_dominance')
    
    # CAREER NARRATIVE THEMES (More Specific)
    if win_rate > 0.75 and total_fights > 10:
        themes.append('triumph')
        themes.append('championship_quest')
        themes.append('peak_performance')
    elif win_rate > 0.7 and total_fights > 10:
        themes.append('triumph')
        themes.append('legacy')
    elif win_rate < 0.35 and total_fights > 5:
        themes.append('underdog')
        themes.append('resilience')
        themes.append('struggle')
    elif win_rate < 0.4 and total_fights > 5:
        themes.append('underdog')
        themes.append('resilience')
    
    # AGE/EXPERIENCE NARRATIVES (More Specific)
    if age > 38 and total_fights > 15:
        themes.append('veteran_wisdom')
        themes.append('legacy')
        themes.append('decline')
        themes.append('mature')
    elif age > 35 and total_fights > 15:
        themes.append('veteran_wisdom')
        themes.append('legacy')
        themes.append('mature')
    elif age > 30 and total_fights > 10:
        themes.append('legacy')
        themes.append('veteran_wisdom')
    elif age < 24 and total_fights > 3:
        themes.append('rookie_rise')
        themes.append('rise_to_glory')
        themes.append('explosive_speed')
        themes.append('youth_focused')
    elif age < 27 and total_fights > 3:
        themes.append('rise_to_glory')
        themes.append('speed')
        themes.append('youth_focused')
    
    # COMEBACK STORY
    if losses > 0 and wins > losses and total_fights > 8:
        # Has losses but winning record suggests comeback
        if win_rate > 0.6:
            themes.append('comeback_story')
            themes.append('resilience')
    
    # VERSATILITY & ADAPTABILITY (More Specific)
    if (strikes_per_min > 2.0 and takedown_accuracy > 0.3) or (strike_accuracy > 0.45 and control_time_ratio > 0.2):
        themes.append('versatility')
        themes.append('adaptability')
        themes.append('well_rounded')
    
    # COMPETITION & RIVALRY (Universal themes - always add for fighters)
    # All fighters compete, so always add competition
    themes.append('competition')
    if total_fights > 3:
        themes.append('rivalry')
    
    # FAMILY & SUPPORT (Universal theme - many fighters have family support)
    # Use name hash for consistent assignment
    name_hash = hash(str(fighter_row.get('fighter', ''))) % 100
    if name_hash % 2 == 0:  # Add to ~50% of fighters for variety
        themes.append('family_support')
        themes.append('family')
    
    # LEGACY - add based on experience even without exact age
    if total_fights > 15:
        themes.append('legacy')
        themes.append('veteran_wisdom')
    elif total_fights > 10:
        themes.append('legacy')
    
    # PHYSICAL ATTRIBUTES (More Specific)
    if reach_advantage > 4:
        themes.append('reach_advantage')
        themes.append('strategic')
    elif reach_advantage < -3:
        themes.append('underdog')  # Reach disadvantage
        themes.append('determination')
    
    if height_inches > 72:  # Over 6 feet
        themes.append('size_advantage')
        themes.append('physical_dominance')
    
    # FINISHING ABILITY
    if strike_accuracy > 0.6 and head_strike_ratio > 0.65:
        themes.append('finisher')
        themes.append('knockout_artist')
    
    # MENTAL TOUGHNESS INDICATORS
    if strike_accuracy > 0.55 and strikes_per_min > 4.0:
        themes.append('mental_toughness')
        themes.append('calm_under_pressure')
    
    return list(set(themes))  # Remove duplicates


def get_fighting_style_description(fighter_row):
    """
    Get nuanced fighting style description based on stats.
    
    Args:
        fighter_row: Fighter DataFrame row
    
    Returns:
        Detailed fighting style string
    """
    strikes_per_min = fighter_row.get('strikes_landed_per_min_mean', 0) if pd.notna(fighter_row.get('strikes_landed_per_min_mean')) else 0
    strike_accuracy = fighter_row.get('strike_accuracy_mean', 0) if pd.notna(fighter_row.get('strike_accuracy_mean')) else 0
    takedown_accuracy = fighter_row.get('takedown_accuracy_mean', 0) if pd.notna(fighter_row.get('takedown_accuracy_mean')) else 0
    control_time_ratio = fighter_row.get('control_time_ratio_mean', 0) if pd.notna(fighter_row.get('control_time_ratio_mean')) else 0
    head_strike_ratio = fighter_row.get('head_strike_ratio_mean', 0) if pd.notna(fighter_row.get('head_strike_ratio_mean')) else 0
    
    # Determine primary style
    is_high_volume_striker = strikes_per_min > 5.0
    is_precise_striker = strike_accuracy > 0.55 and strikes_per_min < 4.0
    is_grappler = takedown_accuracy > 0.5 or control_time_ratio > 0.4
    is_head_hunter = head_strike_ratio > 0.65
    is_balanced = strikes_per_min > 2.0 and takedown_accuracy > 0.3
    
    style_parts = []
    
    if is_high_volume_striker:
        if is_head_hunter:
            style_parts.append("Aggressive Head Hunter")
        else:
            style_parts.append("High-Volume Striker")
    elif is_precise_striker:
        style_parts.append("Precision Counter-Striker")
    
    if is_grappler:
        if control_time_ratio > 0.4:
            style_parts.append("Dominant Grappler")
        else:
            style_parts.append("Takedown Specialist")
    
    if is_balanced:
        style_parts.append("Well-Rounded Fighter")
    
    if not style_parts:
        # Fallback to cluster-based style
        cluster_id = fighter_row.get('kmeans_cluster', None)
        if pd.notna(cluster_id):
            style_parts.append(f"Cluster {int(cluster_id)} Fighter")
        else:
            style_parts.append("Versatile Fighter")
    
    return " / ".join(style_parts) if style_parts else "Fighter"


def get_all_themes(content_df, fighters_df):
    """
    Extract all unique themes from content and fighters.
    
    Args:
        content_df: Content DataFrame
        fighters_df: Fighters DataFrame
    
    Returns:
        Set of all unique themes
    """
    themes = set()
    
    # Get themes from content
    if 'themes' in content_df.columns:
        for themes_list in content_df['themes']:
            themes.update(parse_list_column(themes_list))
    
    # Extract themes from fighter lore
    if fighters_df is not None and len(fighters_df) > 0:
        if 'lore' in fighters_df.columns:
            for lore in fighters_df['lore']:
                if pd.notna(lore) and lore:
                    themes.update(extract_themes_from_text(lore))
        
        # Extract themes from fighter stats
        for idx, fighter_row in fighters_df.iterrows():
            themes.update(extract_fighter_themes_from_stats(fighter_row))
    
    return sorted(list(themes))


def get_all_genres(content_df):
    """
    Extract all unique genres from content.
    
    Args:
        content_df: Content DataFrame
    
    Returns:
        Set of all unique genres
    """
    genres = set()
    
    if 'genres' in content_df.columns:
        for genres_list in content_df['genres']:
            genres.update(parse_list_column(genres_list))
    
    return sorted(list(genres))


def get_theme_color(theme):
    """Get color for a theme"""
    return config.THEME_COLORS.get(theme.lower(), '#888888')


def get_genre_color(genre):
    """Get color for a genre"""
    return config.GENRE_COLORS.get(genre.lower(), '#CCCCCC')


def tag_content(content_row):
    """
    Extract comprehensive thematic metadata from content row with enhanced analysis.
    Extracts themes from multiple sources for MORE VARIED and specific tagging to match fighter diversity.
    
    Args:
        content_row: Single row from content DataFrame
    
    Returns:
        Dictionary with themes, genres, character_archetypes, narrative_patterns
    """
    themes_list = parse_list_column(content_row.get('themes', []))
    
    # Extract additional themes from description if available (more thorough)
    description = content_row.get('description', '')
    desc_lower = ''
    if description and pd.notna(description):
        additional_themes = extract_themes_from_text(description)
        themes_list.extend(additional_themes)
        
        # Also extract themes from description using more aggressive matching
        desc_lower = str(description).lower()
        
        # Add themes based on description patterns
        if any(word in desc_lower for word in ['family', 'parent', 'child', 'sibling', 'brother', 'sister']):
            themes_list.extend(['family', 'family_support', 'brotherhood', 'loyalty'])
        if any(word in desc_lower for word in ['young', 'teen', 'teenager', 'youth', 'adolescent']):
            themes_list.extend(['youth_focused', 'coming_of_age', 'rookie_rise'])
        if any(word in desc_lower for word in ['old', 'veteran', 'experienced', 'seasoned', 'elder']):
            themes_list.extend(['veteran_wisdom', 'legacy', 'mature'])
        if any(word in desc_lower for word in ['fight', 'battle', 'war', 'combat', 'conflict']):
            themes_list.extend(['conflict', 'aggression', 'competition', 'rivalry'])
        if any(word in desc_lower for word in ['journey', 'quest', 'adventure', 'travel', 'road']):
            themes_list.extend(['journey', 'adventure', 'road_trip'])
        if any(word in desc_lower for word in ['mystery', 'secret', 'hidden', 'unknown']):
            themes_list.extend(['mystery', 'unfinished_business'])
        if any(word in desc_lower for word in ['love', 'romance', 'relationship', 'dating']):
            themes_list.extend(['romance', 'friendship'])
        if any(word in desc_lower for word in ['comedy', 'funny', 'humor', 'laugh']):
            themes_list.extend(['comedy', 'lighthearted', 'uplifting'])
        if any(word in desc_lower for word in ['dark', 'grim', 'bleak', 'serious', 'intense']):
            themes_list.extend(['dark', 'gritty', 'intense', 'challenging'])
        if any(word in desc_lower for word in ['hero', 'heroic', 'save', 'protect', 'defend']):
            themes_list.extend(['courage', 'heroic', 'protector', 'justice'])
        if any(word in desc_lower for word in ['revenge', 'vengeance', 'avenge', 'payback']):
            themes_list.extend(['revenge', 'revenge_tale', 'rivalry'])
        if any(word in desc_lower for word in ['redemption', 'forgive', 'second chance', 'return']):
            themes_list.extend(['redemption', 'redemption_through_struggle', 'comeback_story'])
        if any(word in desc_lower for word in ['underdog', 'unlikely', 'against odds', 'surprise']):
            themes_list.extend(['underdog', 'proving_grounds'])
        if any(word in desc_lower for word in ['champion', 'victory', 'win', 'triumph', 'success']):
            themes_list.extend(['triumph', 'championship_quest', 'peak_performance'])
        if any(word in desc_lower for word in ['survive', 'endure', 'persevere', 'overcome']):
            themes_list.extend(['survival', 'survival_story', 'resilience', 'determination'])
        if any(word in desc_lower for word in ['transform', 'change', 'evolve', 'grow']):
            themes_list.extend(['transformation', 'rise_to_glory', 'journey'])
        if any(word in desc_lower for word in ['betray', 'treachery', 'deception', 'backstab']):
            themes_list.extend(['betrayal', 'corruption'])
        if any(word in desc_lower for word in ['team', 'together', 'united', 'group']):
            themes_list.extend(['brotherhood', 'friendship', 'found_family'])
        if any(word in desc_lower for word in ['alone', 'isolated', 'lonely', 'solitary']):
            themes_list.extend(['isolation', 'loner'])
        if any(word in desc_lower for word in ['future', 'futuristic', 'sci-fi', 'space', 'technology']):
            themes_list.extend(['sci_fi', 'futuristic', 'space_opera', 'future'])
        if any(word in desc_lower for word in ['past', 'historical', 'period', 'era', 'ancient']):
            themes_list.extend(['historical', 'period_drama', 'past'])
        if any(word in desc_lower for word in ['fantasy', 'magic', 'magical', 'supernatural']):
            themes_list.extend(['fantasy', 'fantastical', 'escapist'])
        if any(word in desc_lower for word in ['thriller', 'suspense', 'tense', 'edge']):
            themes_list.extend(['thriller', 'intense', 'challenging'])
        if any(word in desc_lower for word in ['horror', 'scary', 'frightening', 'terrifying']):
            themes_list.extend(['horror', 'dark', 'gritty'])
    
    # Extract themes from title (often contains narrative hints)
    title = content_row.get('title', '')
    if title and pd.notna(title):
        title_themes = extract_themes_from_text(title)
        themes_list.extend(title_themes)
        
        # Title-specific theme extraction
        title_lower = str(title).lower()
        if 'star trek' in title_lower:
            themes_list.extend(['sci_fi', 'space_opera', 'brotherhood', 'adventure', 'exploration'])
        if 'trek' in title_lower:
            themes_list.extend(['journey', 'adventure', 'quest'])
        if 'gun' in title_lower or 'maverick' in title_lower:
            themes_list.extend(['action', 'courage', 'rebel', 'determination'])
        if 'yellowstone' in title_lower or '1883' in title_lower or '1923' in title_lower:
            themes_list.extend(['western', 'family_legacy', 'survival', 'historical'])
        if 'ncis' in title_lower:
            themes_list.extend(['crime', 'mystery', 'brotherhood', 'justice'])
        if 'halo' in title_lower:
            themes_list.extend(['sci_fi', 'action', 'war', 'competition'])
        if 'godfather' in title_lower:
            themes_list.extend(['crime', 'family_legacy', 'betrayal', 'power'])
        if 'mission' in title_lower:
            themes_list.extend(['action', 'adventure', 'thriller', 'competition'])
        if 'avatar' in title_lower:
            themes_list.extend(['sci_fi', 'fantasy', 'adventure', 'transformation'])
        if 'survivor' in title_lower:
            themes_list.extend(['competition', 'survival', 'strategy', 'rivalry'])
        if 'nfl' in title_lower or 'football' in title_lower:
            themes_list.extend(['sports', 'competition', 'rivalry', 'triumph'])
        if 'ufc' in title_lower or 'fight' in title_lower:
            themes_list.extend(['sports', 'competition', 'aggression', 'rivalry', 'triumph'])
    
    # Extract themes from type/genre (adds context with MORE themes)
    content_type = content_row.get('type', '')
    if content_type and pd.notna(content_type):
        type_lower = str(content_type).lower()
        if 'sports' in type_lower:
            themes_list.extend(['competition', 'rivalry', 'triumph', 'struggle', 'determination', 'resilience', 'championship_quest'])
        elif 'action' in type_lower:
            themes_list.extend(['aggression', 'conflict', 'power', 'courage', 'explosive_speed', 'pressure_fighting', 'intense'])
        elif 'drama' in type_lower:
            themes_list.extend(['struggle', 'transformation', 'redemption', 'journey', 'deep', 'complex', 'thought_provoking'])
        elif 'western' in type_lower:
            themes_list.extend(['legacy', 'survival', 'honor', 'justice', 'historical', 'gritty', 'raw'])
        elif 'comedy' in type_lower:
            themes_list.extend(['comedy', 'lighthearted', 'uplifting', 'accessible', 'family_friendly'])
        elif 'thriller' in type_lower:
            themes_list.extend(['thriller', 'suspense', 'intense', 'challenging', 'dark'])
        elif 'sci-fi' in type_lower or 'science fiction' in type_lower:
            themes_list.extend(['sci_fi', 'futuristic', 'space_opera', 'innovation', 'fantastical'])
        elif 'horror' in type_lower:
            themes_list.extend(['horror', 'dark', 'gritty', 'intense', 'challenging'])
        elif 'fantasy' in type_lower:
            themes_list.extend(['fantasy', 'fantastical', 'escapist', 'adventure'])
        elif 'crime' in type_lower:
            themes_list.extend(['crime', 'mystery', 'dark', 'gritty', 'corruption', 'justice'])
        elif 'documentary' in type_lower:
            themes_list.extend(['documentary', 'realistic', 'grounded', 'thought_provoking', 'deep'])
        elif 'reality' in type_lower:
            themes_list.extend(['competition', 'rivalry', 'survival', 'realistic'])
    
    # Extract themes from genres (map genres to multiple related themes)
    genres_list = parse_list_column(content_row.get('genres', []))
    genre_theme_map = {
        'action': ['action', 'aggression', 'power', 'courage', 'explosive_speed', 'intense', 'fast_paced'],
        'drama': ['drama', 'deep', 'complex', 'thought_provoking', 'emotional', 'intense'],
        'comedy': ['comedy', 'lighthearted', 'uplifting', 'accessible', 'family_friendly'],
        'thriller': ['thriller', 'suspense', 'intense', 'challenging', 'dark'],
        'sci-fi': ['sci_fi', 'futuristic', 'space_opera', 'innovation', 'fantastical'],
        'horror': ['horror', 'dark', 'gritty', 'intense', 'challenging'],
        'fantasy': ['fantasy', 'fantastical', 'escapist', 'adventure'],
        'western': ['western', 'historical', 'gritty', 'raw', 'legacy', 'survival'],
        'crime': ['crime', 'mystery', 'dark', 'gritty', 'corruption'],
        'sports': ['sports', 'competition', 'rivalry', 'triumph', 'determination'],
        'family': ['family', 'family_friendly', 'all_ages', 'heartwarming', 'uplifting'],
        'adventure': ['adventure', 'journey', 'quest', 'exploration'],
        'romance': ['romance', 'romantic_comedy', 'heartwarming', 'uplifting'],
        'mystery': ['mystery', 'suspense', 'thriller', 'challenging'],
        'war': ['war', 'conflict', 'brotherhood', 'survival', 'courage'],
        'biography': ['biography', 'realistic', 'grounded', 'deep', 'thought_provoking'],
        'documentary': ['documentary', 'realistic', 'grounded', 'thought_provoking'],
        'musical': ['musical', 'uplifting', 'heartwarming', 'lighthearted'],
        'superhero': ['superhero', 'action', 'courage', 'justice', 'power'],
        'historical': ['historical', 'period_drama', 'legacy', 'past']
    }
    
    for genre in genres_list:
        genre_lower = genre.lower()
        if genre_lower in genre_theme_map:
            themes_list.extend(genre_theme_map[genre_lower])
    
    # Get character archetypes - also extract from description
    character_archetypes = parse_list_column(content_row.get('character_archetypes', []))
    if description and pd.notna(description):
        desc_lower = str(description).lower()
        # Check for character archetype keywords in description
        archetype_keywords = {
            'warrior': ['warrior', 'fighter', 'soldier', 'champion'],
            'protector': ['protector', 'guardian', 'defender'],
            'survivor': ['survivor', 'endures', 'survived'],
            'leader': ['leader', 'captain', 'commands'],
            'underdog': ['underdog', 'unlikely', 'against odds'],
            'veteran': ['veteran', 'experienced', 'seasoned'],
            'prodigy': ['prodigy', 'talented', 'gifted'],
            'rebel': ['rebel', 'rebellious', 'defiant'],
            'mentor': ['mentor', 'teacher', 'coach'],
            'loner': ['alone', 'solitary', 'independent']
        }
        for archetype, keywords in archetype_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                if archetype not in character_archetypes:
                    character_archetypes.append(archetype)
    
    # Map character archetypes to themes
    archetype_theme_map = {
        'warrior': ['aggression', 'courage', 'competition', 'power', 'knockout_artist', 'finisher'],
        'protector': ['courage', 'justice', 'honor', 'leadership', 'discipline'],
        'survivor': ['survival', 'resilience', 'determination', 'endurance', 'pressure_fighting'],
        'leader': ['leadership', 'brotherhood', 'power', 'determination', 'discipline', 'mental_toughness'],
        'underdog': ['underdog', 'struggle', 'resilience', 'proving_grounds', 'pressure_fighting'],
        'veteran': ['veteran_wisdom', 'legacy', 'mature', 'experience', 'calm_under_pressure'],
        'prodigy': ['rookie_rise', 'rise_to_glory', 'youth_focused', 'speed', 'explosive_speed'],
        'rebel': ['rebel', 'defiance', 'innovation', 'nonconformist', 'adaptability'],
        'mentor': ['master_apprentice', 'leadership', 'wisdom', 'teaching', 'veteran_wisdom'],
        'loner': ['isolation', 'independence', 'self_reliance', 'adaptability']
    }
    
    for archetype in character_archetypes:
        if archetype in archetype_theme_map:
            themes_list.extend(archetype_theme_map[archetype])
    
    # ADD FIGHTER-SPECIFIC THEMES TO CONTENT BASED ON CONTENT CHARACTERISTICS
    # These themes are common in fighters and should be matched in content
    
    # Versatility & Adaptability (for content with multiple genres/themes)
    if len(genres_list) > 2 or len(themes_list) > 10:
        themes_list.extend(['versatility', 'well_rounded', 'adaptability'])
    
    # Pressure Fighting & Intensity (for fast-paced, intense content)
    if desc_lower and any(word in desc_lower for word in ['intense', 'fast', 'rapid', 'relentless', 'non-stop', 'constant']):
        themes_list.extend(['pressure_fighting', 'intense', 'fast_paced'])
    
    # Physical Dominance (for action/power-focused content)
    if 'action' in genres_list or (desc_lower and any(word in desc_lower for word in ['power', 'dominant', 'overpowering', 'force'])):
        themes_list.extend(['physical_dominance', 'power', 'brutal_power'])
    
    # Precision & Technical Mastery (for well-crafted, methodical content)
    if desc_lower and any(word in desc_lower for word in ['precise', 'methodical', 'crafted', 'polished', 'refined', 'technical', 'surgical', 'calculated']):
        themes_list.extend(['precision', 'technical_mastery', 'precision_striker_narrative'])
    elif 'drama' in genres_list and len(themes_list) > 8:
        # Dramas often have precision in storytelling
        themes_list.extend(['precision', 'technical_mastery', 'precision_striker_narrative'])
    elif 'thriller' in genres_list or 'mystery' in genres_list:
        # Thrillers/mysteries often have precise, calculated narratives
        themes_list.extend(['precision_striker_narrative', 'precision'])
    
    # Volume/High Output (for content with lots of action/events)
    if desc_lower and any(word in desc_lower for word in ['constant', 'relentless', 'non-stop', 'barrage', 'overwhelming', 'fast-paced', 'rapid-fire']):
        themes_list.extend(['volume_striker_narrative', 'aggression', 'pressure_fighting'])
    elif 'action' in genres_list:
        # Action content typically has high volume
        themes_list.extend(['volume_striker_narrative', 'pressure_fighting'])
    
    # Grappler Narrative (for strategic, controlling content)
    if desc_lower and any(word in desc_lower for word in ['strategic', 'control', 'dominate', 'tactical', 'methodical', 'manipulate', 'orchestrate']):
        themes_list.extend(['grappler_narrative', 'strategy', 'discipline'])
    elif 'thriller' in genres_list or 'crime' in genres_list:
        # Thrillers and crime shows often involve strategic control
        themes_list.extend(['grappler_narrative', 'strategy'])
    
    # Family Support (for family-themed content)
    if 'family' in genres_list or (desc_lower and any(word in desc_lower for word in ['family', 'parent', 'child', 'sibling'])):
        themes_list.extend(['family', 'family_support', 'family_friendly'])
    
    # Discipline (for military, sports, training content)
    if desc_lower and any(word in desc_lower for word in ['military', 'soldier', 'training', 'discipline', 'regiment', 'drill']):
        themes_list.extend(['discipline', 'mental_toughness', 'determination'])
    
    # Knockout Artist & Finisher (for action/thriller with decisive endings)
    if 'action' in genres_list or 'thriller' in genres_list:
        if desc_lower and any(word in desc_lower for word in ['finish', 'end', 'conclude', 'decisive', 'final']):
            themes_list.extend(['knockout_artist', 'finisher'])
    
    # Past/Retro/Dated/Historical (for period/historical content)
    content_type = content_row.get('type', '')
    if 'historical' in genres_list or (content_type and 'period' in str(content_type).lower()):
        themes_list.extend(['historical', 'period_drama', 'past', 'retro', 'dated'])
    elif desc_lower and any(word in desc_lower for word in ['past', 'history', 'historical', 'era', 'period', 'ancient']):
        themes_list.extend(['historical', 'past', 'retro'])
    
    # Conflict (for war/battle/conflict content)
    if 'war' in genres_list or (desc_lower and any(word in desc_lower for word in ['war', 'battle', 'conflict', 'fight', 'combat'])):
        themes_list.extend(['conflict', 'war', 'aggression'])
    
    # Calm Under Pressure (for content with composed characters in tense situations)
    if desc_lower and any(word in desc_lower for word in ['calm', 'composed', 'steady', 'unflappable', 'cool under pressure']):
        themes_list.extend(['calm_under_pressure', 'mental_toughness'])
    
    # Mental Toughness (for content about resilience, grit, fortitude)
    if desc_lower and any(word in desc_lower for word in ['tough', 'grit', 'fortitude', 'resilience', 'mental strength']):
        themes_list.extend(['mental_toughness', 'resilience', 'determination'])
    
    # Mature (for adult/serious content)
    if (content_type and 'adult' in str(content_type).lower()) or (desc_lower and any(word in desc_lower for word in ['mature', 'serious', 'adult', 'sophisticated'])):
        themes_list.extend(['mature', 'adult'])
    
    # Present Moment (for contemporary/modern content)
    if 'contemporary' in genres_list or (desc_lower and any(word in desc_lower for word in ['modern', 'current', 'today', 'present', 'now'])):
        themes_list.extend(['present_moment', 'modern', 'contemporary'])
    
    # Specialist (for content focused on specific expertise)
    if desc_lower and any(word in desc_lower for word in ['specialist', 'expert', 'master', 'focused', 'specialized']):
        themes_list.extend(['specialist', 'technical_mastery'])
    
    # Well Rounded (for content that balances multiple elements)
    if len(genres_list) >= 2 and len(themes_list) > 8:
        themes_list.append('well_rounded')
    
    # Remove duplicates
    themes_list = list(set(themes_list))
    
    return {
        'themes': themes_list,
        'genres': genres_list,
        'character_archetypes': list(set(character_archetypes)),  # Remove duplicates
        'narrative_patterns': parse_list_column(content_row.get('narrative_patterns', []))
    }


def tag_fighter(fighter_row, mapping_df=None):
    """
    Extract comprehensive thematic metadata from fighter row with enhanced analysis.
    Uses lore, stats, and mapping data for varied and specific tagging.
    
    Args:
        fighter_row: Single row from fighters DataFrame
        mapping_df: Optional content-fighter mapping DataFrame
    
    Returns:
        Dictionary with themes, fighting_style, character_archetypes
    """
    fighter_name = fighter_row.get('fighter', '')
    themes = []
    
    # Extract themes from lore (primary source for narrative themes)
    lore = fighter_row.get('lore', '')
    if pd.notna(lore) and lore:
        lore_themes = extract_themes_from_text(lore)
        themes.extend(lore_themes)
        
        # Extract additional narrative themes from specific lore patterns
        lore_lower = str(lore).lower()
        
        # Check for specific narrative patterns in lore
        if 'overwhelms' in lore_lower or 'barrage' in lore_lower or 'relentless' in lore_lower:
            themes.append('aggression')
            themes.append('pressure_fighting')
        
        if 'surgical' in lore_lower or 'precision' in lore_lower or 'accurate' in lore_lower:
            themes.append('precision')
            themes.append('technical_mastery')
        
        if 'ground' in lore_lower or 'takedown' in lore_lower or 'grappling' in lore_lower:
            themes.append('grappler_narrative')
            themes.append('strategy')
        
        if 'head' in lore_lower and ('hunt' in lore_lower or 'target' in lore_lower):
            themes.append('knockout_artist')
            themes.append('courage')
        
        if 'veteran' in lore_lower or 'experienced' in lore_lower or 'years old' in lore_lower:
            themes.append('veteran_wisdom')
            themes.append('legacy')
        
        if 'young' in lore_lower or 'just' in lore_lower and 'years old' in lore_lower:
            themes.append('rookie_rise')
            themes.append('rise_to_glory')
        
        if 'comeback' in lore_lower or 'returned' in lore_lower or 'bounced back' in lore_lower:
            themes.append('comeback_story')
            themes.append('resilience')
        
        if 'champion' in lore_lower or 'championship' in lore_lower:
            themes.append('championship_quest')
            themes.append('triumph')
    
    # Extract themes from stats (adds fighting style specific themes)
    stats_themes = extract_fighter_themes_from_stats(fighter_row)
    themes.extend(stats_themes)
    
    # Get themes from mapping if available (content connections)
    if mapping_df is not None and len(mapping_df) > 0:
        fighter_mappings = mapping_df[mapping_df['fighter_name'] == fighter_name]
        if len(fighter_mappings) > 0:
            for common_themes in fighter_mappings['common_themes']:
                if pd.notna(common_themes) and common_themes:
                    themes.extend([t.strip() for t in str(common_themes).split(',') if t.strip()])
    
    # Remove duplicates
    themes = list(set(themes))
    
    # Get nuanced fighting style
    fighting_style = get_fighting_style_description(fighter_row)
    
    # Extract character archetypes from lore (expanded detection)
    character_archetypes = []
    if pd.notna(lore) and lore:
        lore_lower = str(lore).lower()
        
        archetype_keywords = {
            'warrior': ['warrior', 'fighter', 'combatant', 'soldier', 'champion', 'warrior', 'gladiator'],
            'protector': ['protector', 'guardian', 'defender', 'shield', 'safeguard', 'protects', 'defending'],
            'survivor': ['survivor', 'endures', 'perseveres', 'endured', 'survived', 'survives', 'endurance'],
            'leader': ['leader', 'captain', 'guides', 'commands', 'leads', 'leading', 'leadership'],
            'underdog': ['underdog', 'against odds', 'unlikely', 'underestimated', 'overcame', 'defied'],
            'veteran': ['veteran', 'experienced', 'seasoned', 'old guard', 'veteran savvy', 'been there'],
            'prodigy': ['prodigy', 'talented', 'gifted', 'natural', 'phenomenon', 'rising star', 'young talent'],
            'rebel': ['rebel', 'rebellious', 'defiant', 'nonconformist', 'maverick', 'rebellion'],
            'mentor': ['mentor', 'teacher', 'coach', 'instructor', 'guide', 'teaching', 'coaching'],
            'loner': ['alone', 'solitary', 'independent', 'lone', 'isolated', 'self-reliant', 'lone wolf'],
            'hunter': ['hunter', 'hunts', 'seeks', 'pursues', 'targets', 'hunting', 'head-hunting'],
            'guardian': ['guardian', 'protects', 'defends', 'safeguards', 'shields', 'guards'],
            'challenger': ['challenger', 'challenges', 'tests', 'proves', 'demonstrates', 'challenging'],
            'phoenix': ['phoenix', 'rises', 'rebirth', 'reborn', 'resurrected', 'renewed'],
            'tactician': ['tactical', 'strategic', 'calculating', 'planner', 'strategist', 'tactician', 'game plan'],
            'berserker': ['berserker', 'furious', 'rage', 'fury', 'uncontrolled', 'wild', 'savage', 'relentless'],
            'samurai': ['samurai', 'honor', 'code', 'discipline', 'bushido', 'honorable'],
            'gladiator': ['gladiator', 'arena', 'combat', 'battle', 'warrior', 'fighter'],
            'outlaw': ['outlaw', 'renegade', 'rogue', 'outcast', 'exile', 'banished'],
            'noble': ['noble', 'honorable', 'dignified', 'principled', 'upright', 'righteous']
        }
        
        for archetype, keywords in archetype_keywords.items():
            if any(keyword in lore_lower for keyword in keywords):
                character_archetypes.append(archetype)
    
    # Also infer archetypes from stats if not found in lore
    if not character_archetypes:
        strikes_per_min = fighter_row.get('strikes_landed_per_min_mean', 0) if pd.notna(fighter_row.get('strikes_landed_per_min_mean')) else 0
        strike_accuracy = fighter_row.get('strike_accuracy_mean', 0) if pd.notna(fighter_row.get('strike_accuracy_mean')) else 0
        
        if strikes_per_min > 6.0:
            character_archetypes.append('berserker')
        elif strike_accuracy > 0.65:
            character_archetypes.append('tactician')
        
        age = fighter_row.get('age', 0) or 0
        if age > 35:
            character_archetypes.append('veteran')
        elif age < 25:
            character_archetypes.append('prodigy')
    
    return {
        'themes': themes,
        'fighting_style': fighting_style,
        'character_archetypes': list(set(character_archetypes))  # Remove duplicates
    }
