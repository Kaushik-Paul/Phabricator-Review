"""LLM-based code reviewer using OpenAI/OpenRouter."""

import json
from dataclasses import dataclass
from typing import List, Optional

from openai import OpenAI

from .constants import DEFAULT_MODEL, OPENROUTER_BASE_URL
from .prompts import SYSTEM_PROMPT, build_user_prompt


@dataclass
class RequestedChange:
    """A single requested change from the review."""
    path: str
    line: str | int
    change: str


@dataclass
class ReviewResult:
    """The result of a code review."""
    summary: List[str]
    requested_changes: List[RequestedChange]
    raw_response: Optional[str] = None


class CodeReviewer:
    """Reviews code diffs using LLM via OpenRouter."""
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        self.client = OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL)
        self.model = model or DEFAULT_MODEL
    
    def review(
        self,
        diff: str,
        change_summary: str = "",
        revision_summary: str = "",
    ) -> ReviewResult:
        """Review a code diff and return structured feedback."""
        user_prompt = build_user_prompt(diff, change_summary, revision_summary)
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        
        content = response.choices[0].message.content or ""
        
        return self._parse_response(content)
    
    def _parse_response(self, content: str) -> ReviewResult:
        """Parse the LLM response into a structured ReviewResult."""
        # Try to extract JSON from the response
        text = content.strip()
        
        # Handle markdown code blocks
        if text.startswith("```"):
            # Remove opening fence
            text = text.lstrip("`")
            if text.startswith("json"):
                text = text[4:]
            elif text.startswith("JSON"):
                text = text[4:]
            text = text.strip()
            # Remove closing fence
            if text.endswith("```"):
                text = text[:-3].strip()
        
        try:
            data = json.loads(text)
            
            summary = data.get("summary", [])
            if isinstance(summary, str):
                summary = [summary]
            
            requested_changes = []
            for rc in data.get("requested_changes", []):
                requested_changes.append(
                    RequestedChange(
                        path=rc.get("path", ""),
                        line=rc.get("line", ""),
                        change=rc.get("change", ""),
                    )
                )
            
            return ReviewResult(
                summary=summary,
                requested_changes=requested_changes,
                raw_response=content,
            )
        except json.JSONDecodeError:
            # Fallback: treat the entire response as a summary
            return ReviewResult(
                summary=[content] if content else ["(model returned empty response)"],
                requested_changes=[],
                raw_response=content,
            )
