"""Phabricator API client."""

from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class RevisionInfo:
    """Information about a Phabricator revision."""
    id: str
    title: str
    status: str
    uri: str
    summary: str
    diff_phid: str


class PhabricatorClient:
    """Client for interacting with Phabricator Conduit API."""
    
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip("/")
        # Ensure the URL ends with /api
        if not self.base_url.endswith("/api"):
            self.base_url = f"{self.base_url}/api"
        self.api_token = api_token
    
    def _post_conduit(self, endpoint: str, params: dict) -> dict:
        """Make a POST request to a Conduit endpoint."""
        params["api.token"] = self.api_token
        url = f"{self.base_url}/{endpoint}"
        
        response = requests.post(url, data=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get("error_code"):
            raise Exception(
                f"Phabricator error ({data['error_code']}): {data.get('error_info', 'Unknown error')}"
            )
        
        return data
    
    def get_revision(self, revision_id: str) -> RevisionInfo:
        """Fetch revision metadata by ID (e.g., 'D12345' or '12345')."""
        clean_id = revision_id.strip()
        if clean_id and clean_id[0].upper() == "D":
            clean_id = clean_id[1:]
        
        if not clean_id.isdigit():
            raise ValueError(f"Invalid revision ID: {revision_id}")
        
        params = {
            "constraints[ids][0]": clean_id,
            "attachments[reviewers]": "false",
        }
        
        data = self._post_conduit("differential.revision.search", params)
        
        results = data.get("result", {}).get("data", [])
        if not results:
            raise Exception(f"Revision {revision_id} not found")
        
        revision = results[0]
        fields = revision.get("fields", {})
        
        return RevisionInfo(
            id=clean_id,
            title=fields.get("title", ""),
            status=fields.get("status", {}).get("name", "Unknown"),
            uri=fields.get("uri", ""),
            summary=fields.get("summary", ""),
            diff_phid=fields.get("diffPHID", ""),
        )
    
    def get_raw_diff(self, diff_phid: str) -> str:
        """Fetch the raw diff content for a given diff PHID."""
        # First, get the diff ID from the PHID
        params = {
            "constraints[phids][0]": diff_phid,
        }
        
        data = self._post_conduit("differential.diff.search", params)
        
        results = data.get("result", {}).get("data", [])
        if not results:
            raise Exception(f"Diff {diff_phid} not found")
        
        diff_id = results[0].get("id")
        
        # Now fetch the raw diff
        params = {
            "diffID": str(diff_id),
        }
        
        data = self._post_conduit("differential.getrawdiff", params)
        
        return data.get("result", "")
    
    def get_revision_diff(self, revision_id: str) -> tuple[RevisionInfo, str]:
        """Fetch revision info and its raw diff."""
        revision = self.get_revision(revision_id)
        
        if not revision.diff_phid:
            raise Exception(f"No diff available for revision {revision_id}")
        
        raw_diff = self.get_raw_diff(revision.diff_phid)
        
        return revision, raw_diff
