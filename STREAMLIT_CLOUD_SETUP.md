# Streamlit Cloud Deployment Setup

This guide explains how to deploy the app to Streamlit Cloud with API key support.

## Setting Up Secrets in Streamlit Cloud

1. **Go to your Streamlit Cloud dashboard**: https://share.streamlit.io/

2. **Select your app** (or create a new one)

3. **Go to Settings** → **Secrets**

4. **Add the following secrets** (replace `your-api-key-here` with your actual OpenAI API key):

```toml
[llm_api]
key = "your-api-key-here"
provider = "openai"
use_for_bio = "true"
```

**Note**: Your API key is already configured locally. Use the same key value in Streamlit Cloud secrets.

5. **Save** - Streamlit Cloud will automatically redeploy your app

## What This Enables

- **API-Generated Biographies**: Fighter profiles will use unique, AI-generated biographies
- **Unique Lore**: Each fighter gets a completely different narrative style
- **Accurate Themes**: Themes are extracted from the generated content

## Local Development

For local development, create `.streamlit/secrets.toml`:

```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Then edit .streamlit/secrets.toml with your API key
```

Or use the `.env` file (already set up):
```bash
# .env file (already created)
LLM_API_KEY=your-key-here
LLM_API_PROVIDER=openai
USE_API_FOR_BIO=true
```

## Security Notes

- ✅ API key is stored securely in Streamlit Cloud secrets
- ✅ Never commit `.env` or `.streamlit/secrets.toml` to git
- ✅ Secrets are encrypted and only accessible to your app
- ✅ `.gitignore` is configured to prevent accidental commits

## Troubleshooting

**App not using API-generated biographies:**
- Check that `use_for_bio = "true"` in secrets
- Verify API key is correct
- Check app logs for API errors

**API errors:**
- Verify API key is valid
- Check API provider matches your key type
- Ensure you have API credits/quota

