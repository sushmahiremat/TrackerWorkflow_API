"""
Utility functions for parsing @mentions and other text processing
"""
import re
from typing import List

def parse_mentions(text: str) -> List[str]:
    """
    Parse @mentions from text and return list of mentioned usernames.
    Supports formats: @username, @user name, @user-name
    """
    if not text:
        return []
    
    # Pattern to match @mentions: @ followed by word characters, spaces, or hyphens
    # Examples: @john, @john doe, @john-doe
    pattern = r'@([a-zA-Z0-9\s\-]+)'
    matches = re.findall(pattern, text)
    
    # Clean up matches (strip whitespace, remove empty)
    mentions = [match.strip() for match in matches if match.strip()]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_mentions = []
    for mention in mentions:
        if mention.lower() not in seen:
            seen.add(mention.lower())
            unique_mentions.append(mention)
    
    return unique_mentions

def format_mentions_for_display(text: str) -> str:
    """
    Format text with @mentions highlighted (for frontend display).
    Returns text with HTML-like tags that can be processed by frontend.
    """
    if not text:
        return text
    
    # Replace @mentions with formatted version
    pattern = r'@([a-zA-Z0-9\s\-]+)'
    formatted = re.sub(
        pattern,
        r'<mention>@\1</mention>',
        text
    )
    return formatted

