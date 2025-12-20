# Comparative Judging for Remote Viewing

Open source implementation of the Comparative Judging system used by [Social RV](https://social-rv.com) for evaluating remote viewing sessions.

## Overview

Comparative Judging is an AI-powered method for evaluating remote viewing sessions by comparing them against the correct target and several decoy targets. This approach:

- **Reduces bias**: The AI doesn't know which target is correct
- **Provides ranking**: Sessions are ranked from best match (1) to worst match
- **Includes reasoning**: Detailed explanations for each ranking decision
- **Is verifiable**: Built-in verification to ensure consistent reasoning

## Setup

### Prerequisites

- Python 3.10+
- [UV](https://docs.astral.sh/uv/) package manager
- OpenAI API key
- Social RV Research API key (for accessing session data)

### Installation

1. Clone this repository:

```bash
git clone https://github.com/your-org/comparative-judging.git
cd comparative-judging
```

2. Install dependencies with UV:

```bash
uv sync
```

3. Create a `.env` file with your credentials, you should have recieved a 1password link with the two secrets you need:

```env
# OpenAI API key for running the comparative judging model
OPENAI_API_KEY=sk-...

# Social RV Research API key for fetching session data
RESEARCH_API_KEY=your-research-api-key
```

## Project Structure

```
comparative-judging/
├── README.md                    # This file
├── pyproject.toml               # Python dependencies
├── .env.example                 # Environment template
├── docs/
│   └── research-api-endpoints.md   # API documentation
├── src/
│   └── comparative_judging/
│       ├── __init__.py
│       ├── agent.py             # Main LangGraph agent
│       └── utils.py             # Helper utilities
└── notebooks/
    ├── 01_api_example.ipynb     # API usage examples
    ├── 02_export_to_xlsx.ipynb  # Export sessions to Excel
    └── 03_run_judging.ipynb     # Run comparative judging
```

## Usage

### Using the Agent Programmatically

```python
from comparative_judging import judge_session_against_decoys, SessionFile, TargetImage

# Create session files from URLs
session_files = [
    SessionFile(
        filename="session.pdf",
        mime_type="application/pdf",
        base64_content="..."  # Base64 encoded content
    )
]

# Create target and decoys
target = TargetImage(
    id="target-uuid",
    description="A red brick building",
    base64_image="..."  # Base64 encoded image
)

decoys = [
    TargetImage(id="decoy1", description="...", base64_image="..."),
    TargetImage(id="decoy2", description="...", base64_image="..."),
    # ... more decoys
]

# Run the judge
result = await judge_session_against_decoys(
    session_files=session_files,
    target=target,
    decoys=decoys
)

print(f"Correct target ranked: {result.correct_target_rank}")
print(f"Verification passed: {result.verification_passed}")
```

## How It Works

### The Comparative Judging Process

1. **Input Preparation**: Session files (PDFs, images) and target images are encoded to base64
2. **Ranking Node**: GPT-4 Vision analyzes session content against all targets
3. **Verification Node**: A second pass verifies the reasoning is consistent
4. **Result**: Rankings with detailed reasoning for each target

### Key Concepts

- **Session Files**: The viewer's work (drawings, notes, impressions)
- **Target**: The correct target the viewer was attempting to perceive
- **Decoys**: Other valid targets used for comparison
- **Rank**: Position from 1 (best match) to N (worst match)

## API Reference

See [docs/research-api-endpoints.md](docs/research-api-endpoints.md) for full API documentation.

### Quick Examples

```python
import requests

api_key = "YOUR_API_KEY"
base_url = "https://social-rv.com"
headers = {"X-API-Key": api_key}

# Fetch sessions
response = requests.get(
    f"{base_url}/api/research/sessions",
    headers=headers,
    params={"page_size": 100}
)
sessions = response.json()["sessions"]

# Fetch a specific target
response = requests.get(
    f"{base_url}/api/research/targets",
    headers=headers,
    params={"id": "target-uuid"}
)
target = response.json()["target"]
```

## Contributing

We welcome contributions! Please see our contributing guidelines for more information.

## License

MIT License - see LICENSE file for details.
