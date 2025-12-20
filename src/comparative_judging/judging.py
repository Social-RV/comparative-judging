"""
Comparative Judging using Social RV's exact TypeScript implementation

This module provides a Python interface to the exact comparative judging logic
used in Social RV by invoking the TypeScript implementation via Node.js.
"""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class SessionFile:
    """A session file with URL and metadata."""

    url: str
    mime_type: str
    file_name: str


@dataclass
class Target:
    """A target with image URL, description, and ID."""

    url: str
    description: str
    id: str


@dataclass
class RankedMatch:
    """A single ranked target result."""

    rank: int
    target_id: str
    reasoning: str


@dataclass
class ComparativeJudgingResult:
    """Result from comparative judging."""

    overall_reasoning: str
    top_matches: List[RankedMatch]
    correct_target_rank: Optional[int]
    total_targets_ranked: int


class ComparativeJudgingError(Exception):
    """Error during comparative judging."""

    def __init__(self, message: str, code: str = "UNKNOWN", details: dict = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


def perform_comparative_judging(
    session_files: List[SessionFile],
    current_target: Target,
    historical_targets: List[Target],
    node_executable: str = "node",
    tsx_executable: str = "npx tsx",
) -> ComparativeJudgingResult:
    """
    Perform comparative judging using Social RV's exact TypeScript implementation.

    This function invokes the Node.js wrapper which uses the actual TypeScript
    code from Social RV, ensuring 100% identical logic.

    Args:
        session_files: List of session files with URLs
        current_target: The correct target
        historical_targets: List of decoy targets
        node_executable: Path to node executable (default: "node")
        tsx_executable: Command to run TypeScript with tsx (default: "npx tsx")

    Returns:
        ComparativeJudgingResult with rankings and analysis

    Raises:
        ComparativeJudgingError: If judging fails
    """
    # Find the nodejs_wrapper directory
    wrapper_dir = Path(__file__).parent.parent.parent / "nodejs_wrapper"
    cli_script = wrapper_dir / "cli.ts"

    if not cli_script.exists():
        raise ComparativeJudgingError(
            f"Node.js wrapper not found at {cli_script}. "
            "Run 'npm install' in the nodejs_wrapper directory.",
            code="MISSING_WRAPPER",
        )

    # Prepare input JSON
    input_data = {
        "sessionFiles": [
            {"url": sf.url, "mimeType": sf.mime_type, "fileName": sf.file_name}
            for sf in session_files
        ],
        "currentTarget": {
            "url": current_target.url,
            "description": current_target.description,
            "id": current_target.id,
        },
        "historicalTargets": [
            {"url": ht.url, "description": ht.description, "id": ht.id} for ht in historical_targets
        ],
    }

    # Call the Node.js wrapper
    try:
        # Try using tsx first (for TypeScript)
        result = subprocess.run(
            tsx_executable.split() + [str(cli_script)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            check=False,
            cwd=str(wrapper_dir),
        )

        if result.returncode != 0:
            # Parse error from stderr
            try:
                error_data = json.loads(result.stderr)
                raise ComparativeJudgingError(
                    error_data.get("message", "Unknown error"),
                    code=error_data.get("code", "UNKNOWN"),
                    details=error_data.get("details", {}),
                )
            except json.JSONDecodeError:
                raise ComparativeJudgingError(
                    f"Node.js wrapper failed: {result.stderr}", code="WRAPPER_ERROR"
                )

        # Parse result from stdout
        result_data = json.loads(result.stdout)

        # Convert to Python dataclass
        return ComparativeJudgingResult(
            overall_reasoning=result_data["overallReasoning"],
            top_matches=[
                RankedMatch(
                    rank=match["rank"], target_id=match["targetId"], reasoning=match["reasoning"]
                )
                for match in result_data["topMatches"]
            ],
            correct_target_rank=result_data.get("correctTargetRank"),
            total_targets_ranked=result_data["totalTargetsRanked"],
        )

    except subprocess.SubprocessError as e:
        raise ComparativeJudgingError(
            f"Failed to execute Node.js wrapper: {e}", code="SUBPROCESS_ERROR"
        )
    except json.JSONDecodeError as e:
        raise ComparativeJudgingError(f"Failed to parse Node.js output: {e}", code="PARSE_ERROR")


def install_nodejs_dependencies(wrapper_dir: Optional[Path] = None) -> bool:
    """
    Install Node.js dependencies for the wrapper.

    Args:
        wrapper_dir: Path to nodejs_wrapper directory (auto-detected if None)

    Returns:
        True if successful, False otherwise
    """
    if wrapper_dir is None:
        wrapper_dir = Path(__file__).parent.parent.parent / "nodejs_wrapper"

    try:
        result = subprocess.run(
            ["npm", "install"], cwd=str(wrapper_dir), capture_output=True, text=True, check=True
        )
        return result.returncode == 0
    except subprocess.SubprocessError:
        return False
