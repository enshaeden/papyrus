# Reader and Operator View Separation

Status: Accepted

## Context

Papyrus serves materially different user intents. A reader needs a legible, focused content experience oriented around consuming knowledge. An operator needs broader structural visibility, metadata, workflow state, and internal document composition details. Earlier UI patterns allowed governance-heavy and operator-oriented structures to bleed into reading surfaces, producing views that felt dense, administrative, and hostile to actual reading.

This blurred the product’s purpose. Context changes sometimes rearranged navigation chrome without meaningfully changing what information was shown or hidden. As a result, different modes felt cosmetically different but functionally similar, even when their users and goals were distinct.

Papyrus requires explicit separation between reader-facing and operator-facing views.

## Options Considered

- Use one unified surface for all users with minor conditional panels
- Separate modes only at the navigation level
- Build explicit reader and operator view models with different information density and priorities
- Keep current mixed model and improve styling only

## Decision

Papyrus will treat reader and operator experiences as distinct view responsibilities. Reader-facing surfaces must prioritise legibility, content flow, and minimal interruption. Operator-facing surfaces may expose additional metadata, structure, validation state, governance details, and management controls, but must still remain organised and readable.

Mode or context changes must materially change the information model presented to the user, not merely reposition navigation or surrounding chrome.

Where the same underlying knowledge object is presented to both audiences, the system may reuse domain data, but it must not force both audiences through the same UI shape.

## Consequences

### This enables

- Reading surfaces that look and behave like actual content experiences
- Operator surfaces that expose deeper structure without polluting reader views
- Clearer product positioning across modes
- Better control over hierarchy, density, and workflow affordances
- Stronger future support for permissions and role-aware presentation

### This restricts

- Reader mode cannot be treated as a lightly skinned governance screen
- Context switches cannot be considered complete if they only reshuffle navigation
- Shared templates cannot flatten reader and operator needs into one compromised surface
- Metadata-heavy operator concerns cannot dominate reader-first views

### This now requires

- Separate view models, presenters, or templates where reader and operator needs diverge materially
- Reader views to emphasise title, content flow, section hierarchy, and reading affordances
- Operator views to expose management and structural controls intentionally, not incidentally
- UX reviews to verify that context changes alter substance, not only layout
- Existing mixed surfaces to be split where governance density is degrading reading quality