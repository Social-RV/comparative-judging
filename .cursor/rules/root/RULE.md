---
alwaysApply: true
---

# Comparative Judging Research Repository - Cursor AI Context

## Project Overview

This is a research repository for Social RV (social-rv.com), a platform where users practice Remote Viewing - the ability to perceive information about distant or unseen targets using extrasensory perception. This was famously explored by the US government in the Stargate Program during the Cold War.

Social RV has ~7,000 remote viewing sessions and ~300 targets. This repository provides researchers with:

1. API access to Social RV's session data via a special `RESEARCH_API_KEY`
2. The exact AI-based comparative judging system used in production to score user performance
3. Python notebooks for data analysis and validation

## Purpose

Social RV is sharing this repository with academic researchers to:

- Validate their AI scoring methodology
- Analyze remote viewing performance data
- Enable researchers to write academic papers about the platform and remote viewing

## User Profile

The researchers using this repo:

- Are somewhat familiar with coding but not TypeScript experts
- Work primarily in Python (especially Jupyter notebooks)
- May need help with environment setup
- Often want to export data to Excel for analysis
- Need to run batch analyses on large datasets
- Should rely on Cursor AI (you!) to help them understand and modify the code

## Architecture

### Dual-Language System

The project uses both Python and TypeScript:

**Python** (`src/comparative_judging/`):

- API client for fetching data from Social RV's Research API
- Wrapper functions to call the TypeScript judging system
- Utility functions for data processing
- Used in Jupyter notebooks for analysis

**TypeScript** (`nodejs_wrapper/`):

- Contains the EXACT comparative judging logic from Social RV's production codebase
- This ensures research results use identical scoring to the live platform
- Python calls this via Node.js subprocess
- Cannot be simplified or rewritten - must stay identical to production

### Why This Architecture?

Social RV's main codebase is in TypeScript. To ensure research uses the exact same scoring logic as production (not a port or approximation), the TypeScript code is copied directly and wrapped with a Python CLI interface.

## Key Concepts

### Remote Viewing Sessions

A **session** is when a user attempts to perceive a target:

- User is given a random coordinate (e.g., "A7B92")
- User meditates/focuses and records impressions
- User submits drawings (PNG/PDF files) of what they perceived
- Session is later judged against the actual target

### Targets

A **target** is the thing users try to perceive:

- Has an image (the actual thing to be perceived)
- Has a text description
- Examples: "A red barn", "The Eiffel Tower", "A stormy ocean"

### Comparative Judging (The Scoring System)

Social RV uses a **decoy-based AI scoring system**:

1. Take 1 session (user's drawings)
2. Mix the correct target with 9 decoy targets (total: 10 targets)
3. AI judge ranks which target best matches the session
4. If correct target ranks #1 = perfect match, #10 = worst match

**Multi-Pass Elimination Algorithm:**

- Pass 1: AI sees all 10 targets, picks top 3 (ranks 1-3), stops if correct found
- Pass 2: AI sees remaining 7, picks top 3 (ranks 4-6), stops if correct found
- Pass 3: AI sees remaining 4, picks top 3 (ranks 7-9), stops if correct found
- Final: Last target gets rank 10

This is more efficient than ranking all 10 at once and uses early stopping.

## API Access

### Authentication

Researchers need two API keys in their `.env` file:

```env
OPENAI_API_KEY=sk-proj-xxx  # For AI judging (GPT-4o)
RESEARCH_API_KEY=xxx        # For Social RV data access
SOCIAL_RV_API_URL=https://social-rv.com
```

The `RESEARCH_API_KEY` comes from a 1Password link shared by Social RV.

### Research API

See `docs/research-api-endpoints.md` for exhaustive documentation.

**Key endpoints:**

- `GET /api/research/sessions` - Fetch sessions (with filters)
- `GET /api/research/targets` - Fetch targets
- `GET /api/research/sessions/:id/with-decoys` - Get session + target + 9 decoys

**Data scale:**

- ~7,000 sessions available
- ~300 targets
- Sessions have drawing files (PNG/PDF)
- Targets have reference images

## File Structure

```
/src/comparative_judging/     # Python package
  - api_client.py            # Social RV API client
  - judging.py               # Python wrapper for TypeScript judge
  - utils.py                 # Helper functions

/nodejs_wrapper/              # TypeScript judging system
  - comparative-judging.server.ts  # EXACT copy from Social RV production
  - cli.ts                   # Command-line interface for Python to call
  - types.ts                 # TypeScript type definitions

/notebooks/                   # Example notebooks for researchers
  - 01_api_example.ipynb     # How to use the API
  - 02_export_to_xlsx.ipynb  # Export data to Excel
  - 03_run_judging.ipynb     # Run comparative judging

/docs/
  - research-api-endpoints.md # Complete API documentation
```

## Environment Setup

Researchers need:

**Python:**

- Python 3.10+
- `uv` package manager (recommended) or pip
- Install: `uv pip install -e .`
- Dependencies include: pandas, jupyter, langchain, openai, openpyxl, etc.

**Node.js:**

- Node.js 18+
- Install dependencies: `cd nodejs_wrapper && npm install`

**Environment file:**

- `.env` file in project root with API keys

## Common Researcher Tasks

### 1. Environment Setup

When researchers ask for help setting up:

- Check if `uv` is installed (fast Python package manager)
- Check if Node.js 18+ is installed
- Help install Python dependencies: `uv pip install -e .`
- Help install Node dependencies: `cd nodejs_wrapper && npm install`
- Help create `.env` file with API keys

### 2. Fetching Data

Researchers will want to:

- Fetch all sessions or filtered sessions
- Get specific sessions by ID
- Export data to Excel (they love Excel!)
- See `notebooks/01_api_example.ipynb` and `02_export_to_xlsx.ipynb`

### 3. Running Judging

**Current state:** The `perform_comparative_judging()` function processes ONE session at a time and isn't batched.

**What researchers will need:**

- Help running judging on MANY sessions (batching)
- Saving results to persistent storage (SQLite database or JSON/CSV files)
- Progress tracking for long-running batches
- Error handling (some sessions may fail)
- Cost estimation (each session costs ~$0.05-0.15 in OpenAI API calls)

**When they ask for batch processing, suggest:**

1. Create a SQLite database to store results
2. Process sessions in a loop with progress bar
3. Save results after each session (in case of crashes)
4. Skip sessions already processed
5. Include error handling and retry logic
6. Show cost estimates before running

### 4. Data Analysis

Researchers will want to:

- Compare AI rankings with other metrics
- Analyze performance across different users/targets
- Generate visualizations
- Export results to Excel for further analysis
- Calculate statistics (correlation, significance tests, etc.)

Available Python libraries for help:

- `pandas` - data manipulation
- `numpy`, `scipy` - numerical computing
- `matplotlib`, `seaborn`, `plotly` - visualization
- `scikit-learn`, `statsmodels` - statistics
- `openpyxl` - Excel export

## Important Notes

### TypeScript Code is Sacred

The `nodejs_wrapper/comparative-judging.server.ts` file is an EXACT copy from Social RV's production system.

**DO NOT:**

- Rewrite it in Python
- Modify the judging logic
- "Improve" or "optimize" it

**WHY:** Research must use the exact same code as production for results to be comparable.

### Random Results

Even with identical code, running comparative judging twice on the same session will give different results because:

1. Targets are randomly shuffled before judging
2. AI (GPT-4o) has inherent non-determinism
3. Different decoys may be used

This is expected and normal.

### API Costs

- OpenAI API calls cost money (~$0.05-0.15 per session)
- Researchers should be aware before running large batches
- Multi-pass system can make up to 3 API calls per session

### Data Format

Sessions have:

- `id`, `user_display_name`, `target_coordinate`
- `session_media_urls` - array of drawing files (PNG/PDF)
- `target_id` - the correct target
- `decoy_ids` - array of 9 decoy target IDs
- `comparative_judging_rank` - existing rank from Social RV (if available)

Targets have:

- `id`, `description` - text description
- `image_url` - URL to target image

## Helping Researchers

### Your Role

You are helping researchers who:

- Know some Python but aren't TypeScript experts
- Are focused on data analysis, not software engineering
- Want to validate Social RV's scoring methodology
- Need to produce academic-quality results

### Best Practices

1. **Be proactive about batching:** When they want to run judging on many sessions, immediately suggest a proper batching solution with persistence
2. **Suggest SQLite:** It's simple, file-based, and perfect for research data
3. **Show cost estimates:** Always warn about OpenAI API costs for batch jobs
4. **Explain the data:** Help them understand sessions, targets, and judging results
5. **Support Excel:** They like Excel - help with pandas DataFrames and openpyxl
6. **Handle errors gracefully:** Sessions may fail - build in error handling
7. **Use progress bars:** Long-running jobs should show progress (tqdm)
8. **Respect the TypeScript:** Never suggest rewriting the judging logic in Python
9. **Utils out of Notebooks:** When modifying python notebooks, make sure to put the bulk of the logic in util functions outside of the notebook, so they stay clean and easy for the user to read

### Common Issues

1. **"ModuleNotFoundError"** - Python package not installed
2. **"node: command not found"** - Node.js not installed or not in PATH
3. **"npm install failed"** - Need to cd into nodejs_wrapper first
4. **API authentication errors** - Check .env file and API keys
5. **Subprocess errors** - Node.js dependencies not installed
6. **Memory issues** - Loading too many sessions at once
7. **Rate limiting** - OpenAI API rate limits (handle with retries)

## Research Goals

Researchers are trying to:

1. **Validate the scoring system** - Is the AI judge accurate and fair?
2. **Analyze performance** - Do users actually perform better than chance?
3. **Identify patterns** - What makes a successful session?
4. **Write academic papers** - Produce peer-reviewed research about Social RV

Be supportive of these goals and help them produce rigorous, reproducible research.

## Final Notes

- This is cutting-edge research at the intersection of AI and parapsychology
- Researchers may be skeptical or believers - remain neutral and scientific
- Focus on helping them analyze the data objectively
- The goal is to produce credible academic research, not prove or disprove remote viewing
- Help them understand both the technical system and the domain concepts

When in doubt, encourage researchers to explore the example notebooks and API documentation, and remind them you're here to help with environment setup, batching, data analysis, and understanding the codebase.
