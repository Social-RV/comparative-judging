"""
Comparative Judging System for Remote Viewing Research

This package provides tools for running comparative judging on remote viewing sessions
using the exact same logic as Social RV's production system.
"""

from .api_client import SocialRVClient, SessionData, TargetData
from .judging import (
    perform_comparative_judging,
    install_nodejs_dependencies,
    SessionFile,
    Target,
    RankedMatch,
    ComparativeJudgingResult,
    ComparativeJudgingError,
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

__all__ = [
    # API Client
    "SocialRVClient",
    "SessionData",
    "TargetData",
    # Judging
    "perform_comparative_judging",
    "install_nodejs_dependencies",
    "SessionFile",
    "Target",
    "RankedMatch",
    "ComparativeJudgingResult",
    "ComparativeJudgingError",
    # Utilities
    "encode_image_to_base64",
    "encode_pdf_to_base64",
    "download_and_encode_image",
    "download_and_encode_file",
    "create_session_file_from_url",
    "create_target_from_url",
    "create_session_files_from_urls",
    "create_targets_from_urls",
    "create_test_data_from_urls",
]

__version__ = "1.0.0"
