# Remote Viewing Research Repository

Welcome! This repository gives you access to Social RV's remote viewing data and AI scoring system for academic research.

## What's This About?

**Social RV** (social-rv.com) is a platform where users practice remote viewing - attempting to perceive distant or hidden targets using extrasensory perception. We've built an AI-based scoring system to measure how well users perform.

This repository contains:

- 🔌 API access to ~7,000 remote viewing sessions and ~300 targets
- 🤖 The exact AI judging system we use in production
- 📊 Example Python notebooks to analyze the data

## Quick Start

### 1. Get Your API Keys

You'll need two API keys:

**Social RV Research API Key:**

- Get it from this 1Password link: [LINK TO BE PROVIDED]
- This gives you access to our research data

**OpenAI API Key:**

- Get one at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- Needed to run the AI judging system (uses GPT-4o)
- ⚠️ Note: Running AI judgments costs money (~$0.05-0.15 per session)

### 2. Open in Cursor

This repository is designed to work with **Cursor AI** (cursor.com), an AI-powered code editor.

1. Install Cursor if you haven't already: [cursor.com](https://cursor.com)
2. Open this repository in Cursor
3. Press `Cmd+Shift+I` (Mac) or `Ctrl+Shift+I` (Windows/Linux) to open Cursor Agent

### 3. Let Cursor Help You Set Up

Tell Cursor Agent:

> "Help me set up my development environment for this research project"

Cursor will guide you through:

- Installing Python (3.10+) and Node.js (18+)
- Installing all required dependencies
- Creating your `.env` file with API keys

Don't worry if you're not familiar with TypeScript or development tools - Cursor will help you through everything!

## What You Can Do

### Explore the Data

Use the example notebooks in `/notebooks/`:

1. **`01_api_example.ipynb`** - Learn how to fetch session data from the API
2. **`02_export_to_xlsx.ipynb`** - Export data to Excel for analysis
3. **`03_run_judging.ipynb`** - Run the AI judging system on sessions

### Get Help From Cursor

Cursor AI knows all about this repository (we've configured special rules for it). Just ask things like:

- "How do I fetch all sessions from 2024?"
- "Can you help me run the judging system on 100 sessions and save the results?"
- "Show me how to export session data to Excel"
- "How do I analyze which users perform best?"
- "Help me create a visualization of judging results"

### Common Tasks

**Fetch data from the API:**

```python
from comparative_judging import SocialRVClient
client = SocialRVClient()
sessions = client.fetch_all_sessions()
```

**Run judging on a session:**

```python
from comparative_judging import perform_comparative_judging
# See notebook 03 for complete example
result = perform_comparative_judging(session_files, target, decoys)
```

**Export to Excel:**

```python
import pandas as pd
df = pd.DataFrame([s.to_dict() for s in sessions])
df.to_excel('sessions.xlsx', index=False)
```

## Understanding the System

### Remote Viewing Sessions

A **session** is when a user attempts to perceive a target:

- User gets a random coordinate (e.g., "X9K42")
- User meditates and records their impressions as drawings
- User submits their drawings (PNG or PDF files)

### The AI Scoring System

We use **comparative judging** to score sessions:

1. Take the user's drawings
2. Show them to an AI judge alongside 10 targets:
   - 1 correct target (what they were supposed to see)
   - 9 decoy targets (random other targets)
3. AI ranks which target best matches the drawings
4. Rank 1 = perfect match, Rank 10 = worst match

The AI uses a smart multi-pass system that stops early when it finds a good match.

### Your Research Goals

You're here to:

- ✅ Validate that our AI scoring system is fair and accurate
- 📈 Analyze whether users perform better than random chance
- 🔍 Identify what makes a successful remote viewing session
- 📝 Write academic papers about the results

## Important Notes

### Costs

Running the AI judging system uses OpenAI's API, which costs money:

- ~$0.05 to $0.15 per session judged
- If you're running judgments on 1,000 sessions, budget ~$50-150
- Cursor can help you estimate costs before running large batches

### Data Privacy

The data you're accessing is anonymized:

- User display names are shown (but not real names or emails)
- Session drawings are public data submitted to Social RV
- Target information is public

### Technical Architecture

This repo uses both Python and TypeScript:

- **Python:** For data analysis and notebooks (what you'll work with)
- **TypeScript:** Contains the exact judging logic from our production system

You don't need to understand TypeScript - Python calls it automatically. This ensures your research uses the exact same scoring as our live platform.

## Getting Help

### Use Cursor AI First

Cursor has been specially configured with all the context about this repository. It can help with:

- Setting up your environment
- Understanding the code
- Writing analysis scripts
- Debugging errors
- Creating visualizations
- Batch processing

Just open Cursor Agent and ask!

### Documentation

- **API Docs:** See `docs/research-api-endpoints.md` for complete API reference
- **Technical README:** See `README.md` for detailed technical documentation
- **Example Notebooks:** See `notebooks/` for working examples

### Still Stuck?

If Cursor can't help, reach out to the Social RV team with your questions.

## Let's Get Started!

1. ✅ Get your API keys from 1Password
2. ✅ Open this repo in Cursor
3. ✅ Ask Cursor to help set up your environment
4. ✅ Open `notebooks/01_api_example.ipynb` and start exploring!

Happy researching! 🔬✨
