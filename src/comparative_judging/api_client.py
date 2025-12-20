"""
Social RV API Client

This module provides a client for interacting with the Social RV Research API
to fetch sessions, targets, and related data.
"""

import os
import time
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
import requests
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


@dataclass
class SessionData:
    """Represents a remote viewing session."""
    id: str
    user_id: str
    user_display_name: Optional[str]
    tasking_time: Optional[str]
    submission_time: Optional[str]
    target_coordinate: str
    weekly_target_id: Optional[str]
    is_public: bool
    is_low_value: Optional[bool]
    is_blockchain_verified: bool
    self_score: Optional[int]
    community_score_average: Optional[float]
    community_score_count: Optional[int]
    comparative_judging_rank: Optional[int]
    p_value: Optional[float]
    rank: Optional[int]
    rank_denominator: Optional[int]
    z_score: Optional[float]
    vector_text_similarity: Optional[float]
    num_comments: int
    # Research-specific fields
    target_id: Optional[str]
    target_description: Optional[str]
    target_image_url: Optional[str]
    session_media_urls: List[Dict[str, str]]
    decoy_ids: List[str]


@dataclass
class TargetData:
    """Represents a remote viewing target."""
    id: str
    coordinate: str
    description: str
    pool_name: Optional[str]
    target_pool_id: Optional[str]
    created_at: Optional[str]
    image_url: Optional[str]
    ai_caption: Optional[str]


class SocialRVClient:
    """Client for the Social RV Research API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize the API client.
        
        Args:
            api_key: Research API key. Defaults to RESEARCH_API_KEY env var.
            base_url: Base URL for the API. Defaults to SOCIAL_RV_API_URL env var.
        """
        self.api_key = api_key or os.getenv("RESEARCH_API_KEY")
        self.base_url = (base_url or os.getenv("SOCIAL_RV_API_URL", "https://social-rv.com")).rstrip("/")
        
        if not self.api_key:
            raise ValueError(
                "API key is required. Provide it as argument or set RESEARCH_API_KEY env var."
            )
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """Make an API request."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    
    # ========== Sessions API ==========
    
    def get_session(self, session_id: str) -> SessionData:
        """
        Fetch a single session by ID.
        
        Args:
            session_id: UUID of the session
            
        Returns:
            SessionData object
        """
        data = self._request("GET", "/api/research/sessions", params={"id": session_id})
        return self._parse_session(data["session"])
    
    def get_sessions_by_ids(self, session_ids: List[str]) -> Dict[str, Any]:
        """
        Fetch multiple sessions by IDs.
        
        Args:
            session_ids: List of session UUIDs (max 100)
            
        Returns:
            Dict with sessions, found_ids, missing_ids
        """
        if len(session_ids) > 100:
            raise ValueError("Maximum 100 IDs allowed per request")
        
        data = self._request(
            "GET",
            "/api/research/sessions",
            params={"ids": ",".join(session_ids)}
        )
        
        return {
            "sessions": [self._parse_session(s) for s in data["sessions"]],
            "total_count": data["total_count"],
            "found_ids": data["found_ids"],
            "missing_ids": data["missing_ids"]
        }
    
    def list_sessions(
        self,
        page: int = 1,
        page_size: int = 25,
        display_name: Optional[str] = None,
        include_unsubmitted: bool = False,
        include_non_public: bool = True,
        include_low_value: bool = False,
        sort_key: str = "SUBMITTED",
        sort_direction: str = "desc"
    ) -> Dict[str, Any]:
        """
        List sessions with pagination and filtering.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of sessions per page
            display_name: Filter by user display name
            include_unsubmitted: Include unsubmitted sessions
            include_non_public: Include private sessions
            include_low_value: Include low-value sessions
            sort_key: Sort column
            sort_direction: "asc" or "desc"
            
        Returns:
            Dict with sessions, total_count, page, page_size, total_pages
        """
        params = {
            "page": page,
            "page_size": page_size,
            "include_unsubmitted": str(include_unsubmitted).lower(),
            "include_non_public": str(include_non_public).lower(),
            "include_low_value_sessions": str(include_low_value).lower(),
            "sort_key": sort_key,
            "sort_direction": sort_direction
        }
        
        if display_name:
            params["display_name"] = display_name
        
        data = self._request("GET", "/api/research/sessions", params=params)
        
        return {
            "sessions": [self._parse_session(s) for s in data["sessions"]],
            "total_count": data["total_count"],
            "page": data["page"],
            "page_size": data["page_size"],
            "total_pages": data["total_pages"]
        }
    
    def fetch_all_sessions(
        self,
        include_unsubmitted: bool = False,
        include_non_public: bool = True,
        include_low_value: bool = False,
        max_sessions: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[SessionData]:
        """
        Fetch all sessions with automatic pagination.
        
        Args:
            include_unsubmitted: Include unsubmitted sessions
            include_non_public: Include private sessions
            include_low_value: Include low-value sessions
            max_sessions: Maximum number of sessions to fetch
            progress_callback: Optional callback(current, total) for progress
            
        Returns:
            List of SessionData objects
        """
        all_sessions = []
        page = 1
        page_size = 100
        
        while True:
            result = self.list_sessions(
                page=page,
                page_size=page_size,
                include_unsubmitted=include_unsubmitted,
                include_non_public=include_non_public,
                include_low_value=include_low_value
            )
            
            all_sessions.extend(result["sessions"])
            
            if progress_callback:
                progress_callback(len(all_sessions), result["total_count"])
            
            # Check limits
            if max_sessions and len(all_sessions) >= max_sessions:
                all_sessions = all_sessions[:max_sessions]
                break
            
            if page >= result["total_pages"]:
                break
            
            page += 1
            time.sleep(0.1)  # Small delay to avoid rate limiting
        
        return all_sessions
    
    def _parse_session(self, data: Dict[str, Any]) -> SessionData:
        """Parse session data from API response."""
        user = data.get("user") or {}
        community_score = data.get("community_score") or {}
        target_data = data.get("targetData") or {}
        
        return SessionData(
            id=data["id"],
            user_id=user.get("user_id"),
            user_display_name=user.get("display_name"),
            tasking_time=data.get("tasking_time"),
            submission_time=data.get("submission_time"),
            target_coordinate=data.get("target_coordinate"),
            weekly_target_id=data.get("weekly_target_id"),
            is_public=data.get("is_public", False),
            is_low_value=data.get("is_low_value"),
            is_blockchain_verified=data.get("is_blockchain_verified", False),
            self_score=data.get("self_score"),
            community_score_average=community_score.get("average"),
            community_score_count=community_score.get("num_scores"),
            comparative_judging_rank=data.get("comparative_judging_rank"),
            p_value=data.get("p_value"),
            rank=data.get("rank"),
            rank_denominator=data.get("rank_denominator"),
            z_score=data.get("z_score"),
            vector_text_similarity=data.get("vectorTextSimilarity"),
            num_comments=data.get("num_comments", 0),
            target_id=target_data.get("targetId"),
            target_description=target_data.get("description"),
            target_image_url=target_data.get("imageUrl"),
            session_media_urls=data.get("sessionMediaUrls", []),
            decoy_ids=data.get("decoyIds", [])
        )
    
    # ========== Targets API ==========
    
    def get_target(self, target_id: str) -> TargetData:
        """
        Fetch a single target by ID.
        
        Args:
            target_id: UUID of the target
            
        Returns:
            TargetData object
        """
        data = self._request("GET", "/api/research/targets", params={"id": target_id})
        return self._parse_target(data["target"])
    
    def get_targets_by_ids(self, target_ids: List[str]) -> Dict[str, Any]:
        """
        Fetch multiple targets by IDs.
        
        Args:
            target_ids: List of target UUIDs (max 100)
            
        Returns:
            Dict with targets, found_ids, missing_ids
        """
        if len(target_ids) > 100:
            raise ValueError("Maximum 100 IDs allowed per request")
        
        data = self._request(
            "GET",
            "/api/research/targets",
            params={"ids": ",".join(target_ids)}
        )
        
        return {
            "targets": [self._parse_target(t) for t in data["targets"]],
            "total_count": data["total_count"],
            "found_ids": data["found_ids"],
            "missing_ids": data["missing_ids"]
        }
    
    def list_targets(
        self,
        page: int = 1,
        page_size: int = 25,
        pool_name: Optional[str] = None,
        target_pool_id: Optional[str] = None,
        sort_key: str = "created_at",
        sort_direction: str = "desc"
    ) -> Dict[str, Any]:
        """
        List targets with pagination and filtering.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of targets per page
            pool_name: Filter by pool name
            target_pool_id: Filter by target pool UUID
            sort_key: Sort column
            sort_direction: "asc" or "desc"
            
        Returns:
            Dict with targets, total_count, page, page_size, total_pages
        """
        params = {
            "page": page,
            "page_size": page_size,
            "sort_key": sort_key,
            "sort_direction": sort_direction
        }
        
        if pool_name:
            params["pool_name"] = pool_name
        if target_pool_id:
            params["target_pool_id"] = target_pool_id
        
        data = self._request("GET", "/api/research/targets", params=params)
        
        return {
            "targets": [self._parse_target(t) for t in data["targets"]],
            "total_count": data["total_count"],
            "page": data["page"],
            "page_size": data["page_size"],
            "total_pages": data["total_pages"]
        }
    
    def fetch_all_targets(
        self,
        max_targets: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[TargetData]:
        """
        Fetch all targets with automatic pagination.
        
        Args:
            max_targets: Maximum number of targets to fetch
            progress_callback: Optional callback(current, total) for progress
            
        Returns:
            List of TargetData objects
        """
        all_targets = []
        page = 1
        page_size = 100
        
        while True:
            result = self.list_targets(page=page, page_size=page_size)
            
            all_targets.extend(result["targets"])
            
            if progress_callback:
                progress_callback(len(all_targets), result["total_count"])
            
            # Check limits
            if max_targets and len(all_targets) >= max_targets:
                all_targets = all_targets[:max_targets]
                break
            
            if page >= result["total_pages"]:
                break
            
            page += 1
            time.sleep(0.1)  # Small delay to avoid rate limiting
        
        return all_targets
    
    def _parse_target(self, data: Dict[str, Any]) -> TargetData:
        """Parse target data from API response."""
        return TargetData(
            id=data["id"],
            coordinate=data.get("coordinate"),
            description=data.get("description"),
            pool_name=data.get("pool_name"),
            target_pool_id=data.get("target_pool_id"),
            created_at=data.get("created_at"),
            image_url=data.get("imageUrl"),
            ai_caption=data.get("ai_caption")
        )
    
    # ========== Convenience Methods ==========
    
    def get_session_with_decoys(self, session_id: str) -> Dict[str, Any]:
        """
        Fetch a session and all its decoy targets.
        
        Args:
            session_id: UUID of the session
            
        Returns:
            Dict with session, target, and decoys
        """
        session = self.get_session(session_id)
        
        # Get the correct target
        target = None
        if session.target_id:
            target = self.get_target(session.target_id)
        
        # Get decoys
        decoys = []
        if session.decoy_ids:
            result = self.get_targets_by_ids(session.decoy_ids)
            decoys = result["targets"]
        
        return {
            "session": session,
            "target": target,
            "decoys": decoys
        }

