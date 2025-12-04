# LLM API Setup for Unique Fighter Lore Generation

This guide explains how to use an LLM API to generate unique, accurate biographies and lore for each fighter.

## Why Use an API?

- **Unique Writing Styles**: Each fighter gets a completely different narrative voice
- **Accuracy**: Biographies accurately reflect each fighter's stats, record, and fighting style
- **Variety**: No template repetition - every biography is unique
- **Themes**: Themes are accurately extracted from the generated content

## Supported APIs

1. **OpenAI** (GPT-4, GPT-4o-mini)
2. **Anthropic** (Claude 3.5 Sonnet, Claude 3 Opus)
3. **Google** (Gemini Pro)

## Setup Instructions

### 1. Install Required Packages

For OpenAI:
```bash
pip install openai
```

For Anthropic:
```bash
pip install anthropic
```

For Google:
```bash
pip install google-generativeai
```

### 2. Set Your API Key

**Option A: Environment Variables (Recommended)**
```bash
export LLM_API_KEY='your-api-key-here'
export LLM_API_PROVIDER='openai'  # or 'anthropic' or 'google'
export USE_API_FOR_BIO='true'  # Enable API generation in the app
```

**Option B: Set in Script**
Edit `generate_unique_lore.py` and set:
```python
API_KEY = 'your-api-key-here'
API_PROVIDER = 'openai'  # or 'anthropic' or 'google'
```

### 3. Generate Lore for Fighters

Run the generation script:
```bash
python generate_unique_lore.py
```

The script will:
- Ask how many fighters to regenerate (test, all, or a number)
- Generate unique lore for each fighter using the API
- Update `fighters_with_lore.csv` with the new lore
- Create a backup of the original file

### 4. Enable API in the App (Optional)

To use API-generated extended biographies in the Streamlit app:

```bash
export USE_API_FOR_BIO='true'
streamlit run app.py
```

## Cost Estimates

**OpenAI GPT-4o-mini:**
- ~$0.15 per 1M input tokens, $0.60 per 1M output tokens
- ~400 tokens per fighter biography
- ~1000 fighters = ~$0.24-0.40

**Anthropic Claude 3.5 Sonnet:**
- ~$3 per 1M input tokens, $15 per 1M output tokens
- ~400 tokens per fighter biography
- ~1000 fighters = ~$6-7

**Google Gemini Pro:**
- Free tier available (with limits)
- Check current pricing

## Notes

- The script includes rate limiting (0.5s delay between requests)
- Errors are handled gracefully with fallback to template-based generation
- Original data is backed up before updating
- You can regenerate specific fighters or all fighters
- API-generated biographies are cached in the CSV file

## Troubleshooting

**"API_KEY not set" error:**
- Make sure you've exported the environment variable
- Or set it directly in the script

**Import errors:**
- Install the required package for your chosen API provider
- See "Install Required Packages" above

**Rate limiting errors:**
- Increase the delay in `generate_unique_lore.py` (currently 0.5s)
- Check your API provider's rate limits

**Cost concerns:**
- Start with a small test (3-10 fighters)
- Use GPT-4o-mini for lower costs
- Consider caching results to avoid regeneration

