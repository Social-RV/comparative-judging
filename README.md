# Comparative Judging for Remote Viewing Research

This repository provides tools for running comparative judging on remote viewing sessions using the **exact same logic** as Social RV's production system.

## Overview

Comparative judging is a method for evaluating remote viewing sessions by comparing session data against multiple potential targets simultaneously. The AI judge is presented with the user's session alongside the correct target mixed randomly with decoy targets. This blinded approach prevents bias and provides a more objective assessment.

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

- Python 3.8+
- Node.js 18+ and npm
- OpenAI API key
- Social RV Research API key

### Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/comparative-judging.git
cd comparative-judging
```

2. Install Python dependencies:
```bash
pip install -e .
# or with uv:
uv pip install -e .
```

3. Install Node.js dependencies:
```bash
cd nodejs_wrapper
npm install
cd ..
```

4. Create a `.env` file with your API keys:
```bash
OPENAI_API_KEY=your_openai_key_here
RESEARCH_API_KEY=your_social_rv_research_key_here
SOCIAL_RV_API_URL=https://social-rv.com
```

## Usage

### Jupyter Notebooks

The easiest way to get started is with the included notebooks:

1. **`notebooks/01_api_example.ipynb`** - Learn how to use the Social RV API
2. **`notebooks/02_export_to_xlsx.ipynb`** - Export session data to Excel
3. **`notebooks/03_run_judging.ipynb`** - Run comparative judging on sessions

### Python API

```python
from comparative_judging import (
    SocialRVClient,
    perform_comparative_judging,
    create_session_file_from_url,
    create_target_from_url,
)

# Initialize client
client = SocialRVClient()

# Fetch a session with its target and decoys
data = client.get_session_with_decoys(session_id)

# Prepare inputs
session_files = [
    create_session_file_from_url(media['url'])
    for media in data['session'].session_media_urls
]

target = create_target_from_url(
    target_id=data['target'].id,
    description=data['target'].description,
    image_url=data['target'].image_url
)

decoys = [
    create_target_from_url(
        target_id=d.id,
        description=d.description,
        image_url=d.image_url
    )
    for d in data['decoys']
]

# Run comparative judging
result = perform_comparative_judging(
    session_files=session_files,
    current_target=target,
    historical_targets=decoys
)

print(f"Correct target ranked: {result.correct_target_rank}")
print(f"Total targets ranked: {result.total_targets_ranked}")
```

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

To update the TypeScript implementation:

```bash
cp /path/to/social-rv/app/services/ai/comparative-judging.server.ts nodejs_wrapper/
```

## License

MIT

## Contributing

This is a research tool for validating Social RV's comparative judging system. If you find discrepancies or bugs, please open an issue.

## Citation

If you use this tool in your research, please cite:

```
[Citation information to be added]
```
