"""Diff parsing utilities."""

import re
from dataclasses import dataclass
from typing import List, Tuple

from .constants import (
    COLOR_ADD,
    COLOR_NOTICE,
    COLOR_REMOVE,
    COLOR_RESET,
    COLOR_TITLE,
)


@dataclass
class ChangeEntry:
    """Represents a single line change in a diff."""
    path: str
    line: int
    change_type: str  # "add" or "remove"
    content: str


@dataclass
class GroupedChange:
    """Represents a group of consecutive changes of the same type."""
    start_line: int
    end_line: int
    change_type: str
    content: List[str]


def colorize(text: str, color: str) -> str:
    """Apply ANSI color to text."""
    return f"{color}{text}{COLOR_RESET}"


def group_entries(entries: List[ChangeEntry]) -> List[GroupedChange]:
    """Group consecutive entries of the same type."""
    if not entries:
        return []
    
    groups = []
    current = GroupedChange(
        start_line=entries[0].line,
        end_line=entries[0].line,
        change_type=entries[0].change_type,
        content=[entries[0].content],
    )
    
    for entry in entries[1:]:
        if entry.change_type == current.change_type and entry.line == current.end_line + 1:
            current.end_line = entry.line
            current.content.append(entry.content)
        else:
            groups.append(current)
            current = GroupedChange(
                start_line=entry.line,
                end_line=entry.line,
                change_type=entry.change_type,
                content=[entry.content],
            )
    
    groups.append(current)
    return groups


def summarize_diff(raw: str) -> Tuple[List[ChangeEntry], str]:
    """Parse a unified diff and return change entries and a formatted summary."""
    diff_header = re.compile(r"^diff --git a/(.+) b/(.+)$")
    hunk_header = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")
    
    summaries: dict = {}
    order: List[str] = []
    current_path: str | None = None
    old_line = 0
    new_line = 0
    results: List[ChangeEntry] = []
    
    for line in raw.splitlines():
        # Check for diff header
        match = diff_header.match(line)
        if match:
            path = match.group(2)
            if path == "/dev/null":
                path = match.group(1)
            if path not in summaries:
                summaries[path] = []
                order.append(path)
            current_path = path
            old_line, new_line = 0, 0
            continue
        
        if current_path is None:
            continue
        
        # Check for hunk header
        match = hunk_header.match(line)
        if match:
            old_line = int(match.group(1))
            new_line = int(match.group(2))
            continue
        
        if not line or line == "\\ No newline at end of file":
            continue
        
        prefix = line[0] if line else " "
        
        if prefix == " ":
            if old_line > 0:
                old_line += 1
            if new_line > 0:
                new_line += 1
        elif prefix == "-":
            if old_line == 0:
                continue
            content = line[1:].strip() or "(empty)"
            entry = ChangeEntry(
                path=current_path,
                line=old_line,
                change_type="remove",
                content=content,
            )
            summaries[current_path].append(entry)
            results.append(entry)
            old_line += 1
        elif prefix == "+":
            if new_line == 0:
                continue
            content = line[1:].strip() or "(empty)"
            entry = ChangeEntry(
                path=current_path,
                line=new_line,
                change_type="add",
                content=content,
            )
            summaries[current_path].append(entry)
            results.append(entry)
            new_line += 1
    
    # Build formatted summary
    lines = []
    for path in order:
        entries = summaries[path]
        if not entries:
            continue
        
        lines.append(colorize(path, COLOR_TITLE))
        
        for grp in group_entries(entries):
            if grp.start_line == grp.end_line:
                line_label = f"line {grp.start_line}"
            else:
                line_label = f"lines {grp.start_line}-{grp.end_line}"
            
            if grp.change_type == "remove":
                action_color = COLOR_REMOVE
                action_label = "Removed"
            else:
                action_color = COLOR_ADD
                action_label = "Added"
            
            lines.append(
                f"  - {colorize(action_label, action_color)} {colorize(line_label, COLOR_NOTICE)}:"
            )
            for content in grp.content:
                lines.append(f"      {content}")
    
    return results, "\n".join(lines)


def extract_code_snippet(
    raw_diff: str,
    file_path: str,
    line_ref: str | int,
    context_lines: int = 1,
) -> str | None:
    """Extract code snippet from diff for a specific file and line range.
    
    Args:
        raw_diff: The raw unified diff content
        file_path: The file path to extract from
        line_ref: Line number or range (e.g., 42 or "40-45")
        context_lines: Number of context lines to include
    
    Returns:
        The code snippet or None if not found
    """
    # Parse line reference
    line_str = str(line_ref)
    if "-" in line_str:
        parts = line_str.split("-")
        try:
            start_line = int(parts[0])
            end_line = int(parts[1])
        except (ValueError, IndexError):
            return None
    else:
        try:
            start_line = int(line_str)
            end_line = start_line
        except ValueError:
            return None
    
    # Find the file section in the diff
    diff_header = re.compile(r"^diff --git a/(.+) b/(.+)$")
    hunk_header = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")
    
    in_target_file = False
    current_new_line = 0
    collected_lines: list[tuple[int, str]] = []
    
    for line in raw_diff.splitlines():
        # Check for diff header
        match = diff_header.match(line)
        if match:
            path = match.group(2)
            if path == "/dev/null":
                path = match.group(1)
            in_target_file = (path == file_path)
            continue
        
        if not in_target_file:
            continue
        
        # Check for hunk header
        match = hunk_header.match(line)
        if match:
            current_new_line = int(match.group(2))
            continue
        
        if not line:
            continue
        
        prefix = line[0] if line else " "
        
        if prefix == "-":
            # Removed lines don't affect new line numbers
            continue
        elif prefix in (" ", "+"):
            # Context or added lines
            if current_new_line > 0:
                # Check if this line is in our target range (with context)
                if start_line - context_lines <= current_new_line <= end_line + context_lines:
                    # Show the actual content without the diff prefix
                    content = line[1:] if len(line) > 1 else ""
                    marker = ">" if start_line <= current_new_line <= end_line else " "
                    collected_lines.append((current_new_line, f"{marker} {current_new_line}: {content}"))
                current_new_line += 1
    
    if collected_lines:
        return "\n".join(line for _, line in collected_lines)
    
    return None
