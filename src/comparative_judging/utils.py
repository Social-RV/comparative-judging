"""
Utility functions for the Comparative Judging system

This module provides helper functions for downloading files from URLs
and preparing data for comparative judging.
"""

import base64
from pathlib import Path
from typing import List, Optional, Tuple

import requests

from .judging import SessionFile, Target


def encode_image_to_base64(image_path: str) -> str:
    """Helper function to encode an image file to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def encode_pdf_to_base64(pdf_path: str) -> str:
    """Helper function to encode a PDF file to base64."""
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode("utf-8")


def download_and_encode_image(url: str, timeout: int = 30) -> str:
    """
    Download an image from a URL and encode it to base64.

    Args:
        url: The URL of the image to download
        timeout: Request timeout in seconds

    Returns:
        Base64 encoded string of the image

    Raises:
        requests.RequestException: If download fails
        ValueError: If the response is not a valid image
    """
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()

    # Verify it's an image by checking content type
    content_type = response.headers.get("content-type", "")
    if not content_type.startswith("image/"):
        raise ValueError(f"URL does not point to an image. Content-Type: {content_type}")

    return base64.b64encode(response.content).decode("utf-8")


def download_and_encode_file(url: str, timeout: int = 30) -> Tuple[str, str]:
    """
    Download a file from a URL and encode it to base64.

    Args:
        url: The URL of the file to download
        timeout: Request timeout in seconds

    Returns:
        Tuple of (base64_content, mime_type)

    Raises:
        requests.RequestException: If download fails
    """
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()

    mime_type = response.headers.get("content-type", "application/octet-stream")
    base64_content = base64.b64encode(response.content).decode("utf-8")

    return base64_content, mime_type


def create_session_file_from_url(url: str, filename: Optional[str] = None) -> SessionFile:
    """
    Create a SessionFile from a URL (no encoding needed - uses URL directly).

    Args:
        url: URL of the file
        filename: Optional filename override

    Returns:
        SessionFile with URL and metadata
    """
    # Extract filename from URL if not provided
    if not filename:
        filename = Path(url.split("?")[0]).name or "downloaded_file"

    # Determine mime type from URL or filename
    mime_type = "application/octet-stream"
    if filename.lower().endswith((".jpg", ".jpeg")):
        mime_type = "image/jpeg"
    elif filename.lower().endswith(".png"):
        mime_type = "image/png"
    elif filename.lower().endswith(".pdf"):
        mime_type = "application/pdf"

    return SessionFile(url=url, mime_type=mime_type, file_name=filename)


def create_target_from_url(target_id: str, description: str, image_url: str) -> Target:
    """
    Create a Target from an image URL (no encoding needed - uses URL directly).

    Args:
        target_id: Unique identifier for the target
        description: Text description of the target
        image_url: URL of the target image

    Returns:
        Target with URL and metadata
    """
    return Target(id=target_id, description=description, url=image_url)


def create_session_files_from_urls(urls: List[str]) -> List[SessionFile]:
    """
    Create a list of SessionFiles from a list of URLs.

    Args:
        urls: List of file URLs

    Returns:
        List of SessionFile objects
    """
    session_files = []

    for i, url in enumerate(urls):
        try:
            session_file = create_session_file_from_url(url, f"session_file_{i + 1}")
            session_files.append(session_file)
            print(f"✅ Created session file: {url[:80]}...")
        except Exception as e:
            print(f"❌ Failed to create session file {url[:80]}...: {e}")

    return session_files


def create_targets_from_urls(target_data: List[dict]) -> List[Target]:
    """
    Create a list of Targets from target data with URLs.

    Args:
        target_data: List of dicts with keys: id, description, image_url

    Returns:
        List of Target objects
    """
    targets = []

    for data in target_data:
        try:
            target = create_target_from_url(
                target_id=data["id"], description=data["description"], image_url=data["image_url"]
            )
            targets.append(target)
            print(f"✅ Created target: {data['id']}")
        except Exception as e:
            print(f"❌ Failed to create target {data.get('id', 'unknown')}: {e}")

    return targets


def create_test_data_from_urls(
    session_urls: List[str], correct_target_data: dict, decoy_targets_data: List[dict]
) -> Tuple[List[SessionFile], Target, List[Target]]:
    """
    One-stop function to create all test data from URLs.

    Args:
        session_urls: List of session file URLs
        correct_target_data: Dict with id, description, image_url for correct target
        decoy_targets_data: List of dicts with id, description, image_url for decoys

    Returns:
        Tuple of (session_files, target, decoys)
    """
    print("📥 Creating session files...")
    session_files = create_session_files_from_urls(session_urls)

    print("\n🎯 Creating correct target...")
    target = create_target_from_url(
        target_id=correct_target_data["id"],
        description=correct_target_data["description"],
        image_url=correct_target_data["image_url"],
    )

    print("\n🎭 Creating decoy targets...")
    decoys = create_targets_from_urls(decoy_targets_data)

    print("\n✅ Test data ready!")
    print(f"   Session files: {len(session_files)}")
    print(f"   Correct target: {target.id}")
    print(f"   Decoys: {len(decoys)}")

    return session_files, target, decoys
