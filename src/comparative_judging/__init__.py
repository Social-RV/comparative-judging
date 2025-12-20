"""
Comparative Judging for Remote Viewing Sessions

This package provides tools for evaluating remote viewing sessions using
AI-powered comparative judging against target and decoy images.
"""

from .agent import (
    SessionFile,
    TargetImage,
    DecoyJudgeInput,
    RankedTarget,
    RankingResult,
    VerificationResult,
    DecoyJudgeOutput,
    DecoyJudgeState,
    create_decoy_judge_graph,
    judge_session_against_decoys,
    create_initial_state,
    graph,
)

from .utils import (
    encode_image_to_base64,
    encode_pdf_to_base64,
    download_and_encode_image,
    download_and_encode_file,
    create_session_file_from_url,
    create_target_from_url,
    create_session_files_from_urls,
    create_targets_from_urls,
    create_test_data_from_urls,
)

from .api_client import (
    SocialRVClient,
)

__all__ = [
    # Agent types
    "SessionFile",
    "TargetImage",
    "DecoyJudgeInput",
    "RankedTarget",
    "RankingResult",
    "VerificationResult",
    "DecoyJudgeOutput",
    "DecoyJudgeState",
    # Agent functions
    "create_decoy_judge_graph",
    "judge_session_against_decoys",
    "create_initial_state",
    "graph",
    # Utils
    "encode_image_to_base64",
    "encode_pdf_to_base64",
    "download_and_encode_image",
    "download_and_encode_file",
    "create_session_file_from_url",
    "create_target_from_url",
    "create_session_files_from_urls",
    "create_targets_from_urls",
    "create_test_data_from_urls",
    # API Client
    "SocialRVClient",
]

