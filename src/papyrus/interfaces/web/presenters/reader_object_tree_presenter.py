from __future__ import annotations

from typing import Any

from papyrus.application.role_visibility import READER_ROLE
from papyrus.interfaces.web.urls import object_url
from papyrus.interfaces.web.view_helpers import escape, join_html, link


def _render_object_item(*, node: dict[str, Any]) -> str:
    is_current = bool(node.get("current"))
    return (
        '<li class="reader-object-tree__item">'
        + link(
            str(node["label"]),
            object_url(READER_ROLE, str(node["object_id"])),
            css_class="reader-object-tree__link is-current"
            if is_current
            else "reader-object-tree__link",
            attrs={"aria-current": "page"} if is_current else None,
        )
        + "</li>"
    )


def _render_tree_node(*, node: dict[str, Any]) -> str:
    if str(node.get("kind") or "") != "group":
        return _render_object_item(node=node)
    branch_classes = ["reader-object-tree__branch"]
    if bool(node.get("contains_current")):
        branch_classes.append("is-current-branch")
    children: list[str] = []
    if isinstance(node.get("object"), dict):
        children.append(_render_object_item(node=dict(node["object"])))
    children.extend(_render_tree_node(node=child) for child in node.get("children") or [])
    details_open = " open" if bool(node.get("expanded")) else ""
    return (
        f'<li class="{" ".join(branch_classes)}">'
        f'<details class="reader-object-tree__branch-disclosure"{details_open}>'
        f'<summary class="reader-object-tree__group">{escape(node["label"])}</summary>'
        f'<ul class="reader-object-tree__list">{join_html(children)}</ul>'
        "</details></li>"
    )


def render_reader_object_tree_nav(tree: dict[str, Any] | None) -> str:
    nodes = list((tree or {}).get("nodes") or [])
    if not nodes:
        return ""
    return (
        '<details class="reader-object-tree" data-component="reader-object-tree-nav">'
        f'<summary class="reader-object-tree__summary">{escape(tree.get("label") or "Browse objects")}</summary>'
        f'<nav class="reader-object-tree__nav" aria-label="{escape(tree.get("label") or "Browse objects")}">'
        f'<ul class="reader-object-tree__list">{join_html(_render_tree_node(node=node) for node in nodes)}</ul>'
        "</nav></details>"
    )
