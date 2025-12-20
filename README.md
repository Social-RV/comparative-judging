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

**You'll receive a 1Password link** with all the API keys you need:

- **Social RV Research API Key** - gives you access to our research data
- **OpenAI API Key** - needed to run the AI judging system (uses GPT-4o)

Once you have the keys from 1Password, create a `.env` file in the root of this project:

```env
RESEARCH_API_KEY=your_research_key_here
OPENAI_API_KEY=your_openai_key_here
```

### 2. Clone this repo from github

Use either a git-compatible tool or click "Download Zip" on Github under the Code button

### 3. Download Cursor, and open the cloned Repo

This repository is designed to work with **Cursor AI** (cursor.com), an AI-powered code editor.

1. Install Cursor if you haven't already: [cursor.com](https://cursor.com)
2. Open this repository in Cursor
3. Press `Cmd+Shift+I` (Mac) or `Ctrl+Shift+I` (Windows/Linux) to open Cursor Agent

### 4. Let Cursor Help You Set Up

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

### Data Privacy

The data you're accessing is anonymized:

- User display names are shown (but not real names or emails)
- Session drawings are public data submitted to Social RV
- Target information is public
- Users have an ability to opt-out of having their sessions shared with vetted researchers on the settings page. Our api respects these settings.

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
- **Technical README:** See `README_TECHNICAL.md` for detailed technical documentation
- **Example Notebooks:** See `notebooks/` for working examples
- **Cursor Rules:** The `.cursorrules` file contains comprehensive context for Cursor AI

### Still Stuck?

If Cursor can't help, reach out to the Social RV team with your questions.

## Let's Get Started!

1. ✅ Get your API keys from 1Password
2. ✅ Open this repo in Cursor
3. ✅ Ask Cursor to help set up your environment
4. ✅ Open `notebooks/01_api_example.ipynb` and start exploring!

Happy researching! 🔬✨
