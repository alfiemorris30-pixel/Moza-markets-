#!/usr/bin/env python3
"""Check a MOZA Markets Instagram caption before it goes to Buffer (Master System Section 50.19).

Usage: python3 tools/check_caption.py caption.txt
Prints CAPTION CHECK: PASS, or CAPTION CHECK: FAIL — reasons (exit 1).
"""
import re
import sys

MAX_HASHTAGS = 5
MAX_CHARS = 2200  # Instagram caption limit; Buffer allows up to 2,196 for this channel
BANNED = ("guaranteed", "100% profit", "easy money", "buy now", "free signal", "risk-free", "risk free")


def check(text):
    problems = []
    tags = re.findall(r"(?<!\w)#\w+", text)
    if len(tags) > MAX_HASHTAGS:
        problems.append(f"{len(tags)} hashtags (maximum {MAX_HASHTAGS})")
    if len(set(t.lower() for t in tags)) != len(tags):
        problems.append("duplicate hashtag")
    if len(text) > 2196:
        problems.append(f"{len(text)} characters (Buffer limit 2,196)")
    low = text.lower()
    for word in BANNED:
        if word in low:
            problems.append(f'banned wording: "{word}"')
    return problems


if __name__ == "__main__":
    caption = open(sys.argv[1], encoding="utf-8").read()
    issues = check(caption)
    if issues:
        print("CAPTION CHECK: FAIL — " + "; ".join(issues))
        sys.exit(1)
    print("CAPTION CHECK: PASS")
