# Technical Documentation - Comparative Judging

> **Note for Researchers:** This is the detailed technical documentation. For a quick start guide, see [`README.md`](README.md).

This repository provides tools for running comparative judging on remote viewing sessions using the **exact same logic** as Social RV's production system.

## Overview

Comparative judging is a method for evaluating remote viewing sessions by comparing session data against multiple potential targets simultaneously. The AI judge is presented with the user's session alongside the correct target mixed randomly with decoy targets. This blinded approach prevents bias and provides a more objective assessment.

**What You'll Need:**

- Python 3.10 or higher
- Node.js 18 or higher
- OpenAI API key (for AI judging)
- Social RV Research API key (for accessing session data)

**This guide includes complete installation instructions for all tools.**

## How It Works

This implementation uses Social RV's **multi-pass elimination algorithm**:

1. **Pass 1**: AI sees all 10 targets (1 correct + 9 decoys) and selects top 3 matches (ranks 1-3)
   - If correct target is found → STOP
2. **Pass 2**: AI sees remaining 7 targets and selects top 3 (ranks 4-6)
   - If correct target is found → STOP
3. **Pass 3**: AI sees remaining 4 targets and selects top 3 (ranks 7-9)
   - If correct target is found → STOP
4. **Final**: Last remaining target automatically gets rank 10

This approach is more efficient than ranking all 10 targets at once and stops early when the correct target is found.

## Architecture

The system consists of two parts:

1. **Python API Client** (`src/comparative_judging/`) - Fetches session data from Social RV's Research API
2. **TypeScript Judging Logic** (`nodejs_wrapper/`) - Exact copy of Social RV's production code

The Python code calls the TypeScript implementation via a Node.js subprocess, ensuring 100% identical logic to Social RV's production system.

## Installation

### Prerequisites

Before you begin, you'll need:

- **OpenAI API key** - [Get one here](https://platform.openai.com/api-keys)
- **Social RV Research API key** - Contact Social RV for research access

### Step 1: Install uv (Python Package Manager)

`uv` is a fast Python package manager. Install it using the official installer:

**macOS/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, restart your terminal or run:

```bash
source $HOME/.cargo/env
```

**Verify installation:**

```bash
uv --version
```

For more installation options, see [uv documentation](https://docs.astral.sh/uv/getting-started/installation/).

### Step 2: Install Node.js and npm

Node.js 18+ is required for running the TypeScript judging logic.

**Option A: Using Official Installer (Recommended for beginners)**

1. Visit [nodejs.org](https://nodejs.org/)
2. Download and install the LTS version (includes npm)

**Option B: Using Homebrew (macOS/Linux)**

```bash
brew install node
```

**Option C: Using nvm (Version Manager)**

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Install Node.js LTS
nvm install --lts
nvm use --lts
```

**Verify installation:**

```bash
node --version  # Should show v18.x.x or higher
npm --version   # Should show 9.x.x or higher
```

### Step 3: Clone the Repository

```bash
git clone https://github.com/yourusername/comparative-judging.git
cd comparative-judging
```

### Step 4: Install Python Dependencies

Using `uv` (recommended):

```bash
uv pip install -e .
```

Or using traditional pip:

```bash
pip install -e .
```

This will install all required Python packages including:

- LangChain & OpenAI SDK
- Pandas & data processing tools
- Jupyter notebook support

### Step 5: Install Node.js Dependencies

```bash
cd nodejs_wrapper
npm install
cd ..
```

### Step 6: Configure Environment Variables

Create a `.env` file in the project root directory with your API keys.

**Using a text editor:**

```bash
# Create and edit the file
nano .env  # or use your preferred editor (vim, code, etc.)
```

**Or using command line:**

```bash
cat > .env << 'EOF'
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-your_openai_key_here

# Social RV Research API Configuration
RESEARCH_API_KEY=your_social_rv_research_key_here
SOCIAL_RV_API_URL=https://social-rv.com
EOF
```

Then **replace the placeholder values** with your actual API keys:

- Replace `sk-proj-your_openai_key_here` with your OpenAI API key
- Replace `your_social_rv_research_key_here` with your Social RV Research API key
- The `SOCIAL_RV_API_URL` should remain `https://social-rv.com` unless using a staging environment

**Important:** Never commit your `.env` file to version control. It's already included in `.gitignore`.

### Verify Installation

Test that everything is working:

```bash
# Test Python installation
python -c "from comparative_judging import SocialRVClient; print('✓ Python package installed')"

# Test Node.js installation
cd nodejs_wrapper && npm run judge -- --help && cd ..
```

If both commands succeed, you're ready to go!

## Quick Start

The fastest way to get started is using the Jupyter notebooks:

1. **Start Jupyter:**

```bash
jupyter notebook
```

2. **Open and run the notebooks in order:**
   - `notebooks/01_api_example.ipynb` - Learn the API basics
   - `notebooks/02_export_to_xlsx.ipynb` - Export session data
   - `notebooks/03_run_judging.ipynb` - Run comparative judging

Each notebook includes detailed explanations and examples.

## Usage

### Jupyter Notebooks (Recommended for Exploration)

The easiest way to get started is with the included notebooks:

1. **`notebooks/01_api_example.ipynb`** - Learn how to use the Social RV API
2. **`notebooks/02_export_to_xlsx.ipynb`** - Export session data to Excel
3. **`notebooks/03_run_judging.ipynb`** - Run comparative judging on sessions

### Python API (Programmatic Access)

For integrating comparative judging into your own scripts or applications:

```python
from comparative_judging import (
    SocialRVClient,
    perform_comparative_judging,
    create_session_file_from_url,
    create_target_from_url,
)

# Initialize client (reads API keys from .env)
client = SocialRVClient()

# Fetch a session with its target and decoys
session_id = "your-session-id-here"
data = client.get_session_with_decoys(session_id)

# Prepare session files (images/PDFs)
session_files = [
    create_session_file_from_url(media['url'])
    for media in data['session'].session_media_urls
]

# Prepare the correct target
target = create_target_from_url(
    target_id=data['target'].id,
    description=data['target'].description,
    image_url=data['target'].image_url
)

# Prepare 9 decoy targets
decoys = [
    create_target_from_url(
        target_id=d.id,
        description=d.description,
        image_url=d.image_url
    )
    for d in data['decoys']
]

# Run comparative judging (calls Node.js subprocess)
result = perform_comparative_judging(
    session_files=session_files,
    current_target=target,
    historical_targets=decoys
)

# Display results
print(f"✓ Judging complete!")
print(f"Correct target ranked: {result.correct_target_rank} out of 10")
print(f"Total targets ranked: {result.total_targets_ranked}")
print(f"\nTop 3 matches:")
for i, match in enumerate(result.top_matches[:3], 1):
    print(f"  {i}. Target {match.target_id}")
    print(f"     Score: {match.match_score}")
    print(f"     {match.reasoning[:100]}...")
```

**Note:** The function spawns a Node.js process to run the TypeScript judging logic, ensuring 100% consistency with Social RV's production system.

## API Documentation

### Social RV Research API

See `docs/research-api-endpoints.md` for full API documentation.

Key endpoints:

- `GET /api/research/sessions` - List or fetch sessions
- `GET /api/research/targets` - List or fetch targets

### Comparative Judging

```python
perform_comparative_judging(
    session_files: List[SessionFile],
    current_target: Target,
    historical_targets: List[Target]
) -> ComparativeJudgingResult
```

**Parameters:**

- `session_files`: List of session files (images/PDFs) with URLs
- `current_target`: The correct target
- `historical_targets`: List of 9 decoy targets

**Returns:**

- `overall_reasoning`: AI's overall analysis
- `top_matches`: List of ranked targets with reasoning
- `correct_target_rank`: Where the correct target ranked (1-10)
- `total_targets_ranked`: How many targets were ranked before stopping

## Validation

To validate that this implementation matches Social RV's production system:

1. Run comparative judging on a session that already has a rank in Social RV
2. Compare the results - they should be similar but may differ due to:
   - Random shuffling of targets
   - AI non-determinism (even with low temperature)
   - Different decoys if you're not using the same ones

The **logic is identical**, but the **results will vary** due to randomization.

## Troubleshooting

### Common Issues

**"uv: command not found"**

- Solution: Restart your terminal after installing uv, or run `source $HOME/.cargo/env`

**"node: command not found"**

- Solution: Install Node.js following Step 2 above, then restart your terminal

**"ModuleNotFoundError: No module named 'comparative_judging'"**

- Solution: Make sure you installed the package with `uv pip install -e .` from the project root

**"Error: Cannot find module 'openai'"**

- Solution: Install Node.js dependencies: `cd nodejs_wrapper && npm install && cd ..`

**"Authentication failed" or API errors**

- Solution: Check your `.env` file has valid API keys
- Verify your OpenAI API key at [platform.openai.com](https://platform.openai.com/api-keys)
- Contact Social RV if you need a Research API key

**Node.js subprocess fails**

- Solution: Ensure Node.js 18+ is installed: `node --version`
- Try rebuilding Node modules: `cd nodejs_wrapper && rm -rf node_modules && npm install && cd ..`

**Jupyter notebook won't start**

- Solution: Make sure Jupyter is installed: `uv pip install jupyter`
- Try: `python -m jupyter notebook`

### Getting Help

- Check the example notebooks in `notebooks/` for working code
- See `docs/research-api-endpoints.md` for API documentation
- Open an issue on GitHub if you find a bug

## Development

### Project Structure

```
comparative-judging/
├── src/comparative_judging/
│   ├── __init__.py
│   ├── api_client.py       # Social RV API client
│   ├── judging.py          # Python wrapper for TypeScript
│   └── utils.py            # Helper functions
├── nodejs_wrapper/
│   ├── comparative-judging.server.ts  # Exact copy from Social RV
│   ├── cli.ts              # Command-line interface
│   ├── types.ts            # Type definitions
│   └── package.json        # Node.js dependencies
├── notebooks/              # Jupyter notebooks
└── docs/                   # Documentation
```

### Keeping in Sync with Social RV

The TypeScript judging logic in `nodejs_wrapper/comparative-judging.server.ts` is an exact copy of Social RV's production implementation at `app/services/ai/comparative-judging.server.ts`.

To update to the latest version from Social RV:

```bash
# From the comparative-judging repository root
cp /path/to/social-rv/app/services/ai/comparative-judging.server.ts nodejs_wrapper/

# Verify it still works
cd nodejs_wrapper
npm install  # Install any new dependencies if needed
npm run judge -- --help
cd ..
```

**Note:** This repository is designed to stay in sync with Social RV's production code to ensure research results are comparable to the live platform.

## License

MIT

## Contributing

This is a research tool for validating Social RV's comparative judging system. If you find discrepancies or bugs, please open an issue.

## Citation

If you use this tool in your research, please cite:

```
[Citation information to be added]
```
