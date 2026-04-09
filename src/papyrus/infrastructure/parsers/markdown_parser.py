from __future__ import annotations

import re


HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$")
LIST_PATTERN = re.compile(r"^\s*(?:[-*]|\d+\.)\s+(.*)$")
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def parse_markdown_bytes(payload: bytes) -> dict[str, object]:
    text = payload.decode("utf-8")
    title = ""
    headings: list[dict[str, object]] = []
    paragraphs: list[str] = []
    lists: list[list[str]] = []
    links: list[dict[str, str]] = []
    current_list: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if heading_match := HEADING_PATTERN.match(line):
            if current_list:
                lists.append(current_list)
                current_list = []
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            headings.append({"level": level, "text": heading_text})
            if not title and level == 1:
                title = heading_text
            continue
        if list_match := LIST_PATTERN.match(line):
            current_list.append(list_match.group(1).strip())
            continue
        if current_list:
            lists.append(current_list)
            current_list = []
        stripped = line.strip()
        if stripped:
            paragraphs.append(stripped)
            links.extend({"label": label, "target": target} for label, target in LINK_PATTERN.findall(stripped))
    if current_list:
        lists.append(current_list)

    return {
        "title": title or (headings[0]["text"] if headings else ""),
        "headings": headings,
        "paragraphs": paragraphs,
        "lists": lists,
        "tables": [],
        "links": links,
        "raw_text": "\n".join(paragraphs),
    }
