---
id: {{id}}
title: {{title}}
canonical_path: {{canonical_path}}
summary: Replace with a concise operational summary.
type: {{type}}
status: {{status}}
owner: {{owner}}
source_type: native
source_system: repository
source_title: {{title}}
team: {{team}}
{{systems_field}}
{{services_field}}
{{tags_field}}
created: {{today}}
updated: {{today}}
last_reviewed: {{today}}
review_cadence: quarterly
audience: {{audience}}
prerequisites:
- Document the information needed before troubleshooting starts.
steps:
- Capture the exact symptom, scope, and error text before changing anything.
verification:
- Document how to confirm the issue is resolved.
rollback:
- Document how to undo any change or revert temporary mitigation.
{{related_articles_field}}
replaced_by: null
retirement_reason: null
references:
- title: Replace with a supporting document, local path, or canonical article reference.
change_log:
- date: {{today}}
  summary: Initial article scaffold.
  author: new_article.py
---

## Use When

Describe the symptom pattern, scope, and the first signals that should lead an operator to this article.

## Escalation Threshold

Describe when to stop local troubleshooting and escalate.

## Related Knowledge Notes

- Note the prerequisite, follow-on, fallback, or sibling procedures that should also be linked in `related_articles` or `references`.
