# Decision: Luxury Read View Aesthetics

**Date**: 2026-04-18
**Status**: Approved

## Context

The user requested a high-tech, luxury-grade visual interface for the Papyrus reading experience, specifically for knowledge objects. The provided mockups featured glassmorphic cards, modern typography (Outfit), and a refined dark-mode palette with cyan accents.

The root `AGENTS.md` prioritizes structural correctness (Priority 1) over cosmetic polish (Priority 7) and states "Do not sacrifice structural correctness for visual polish".

## Decision

We are authorizing a deviation from the strictly structural presentation model for the `READER` role reading surface. The web application will implement a "luxury-grade" aesthetic to improve readability and user engagement, while the underlying data model remains strictly canonical and structural.

Key changes:
- Introduction of glassmorphism (backdrop-blur) for callout blocks.
- Transition to a more expressive typography scale (3xl for headlines).
- Metadata presented with user avatars and icons.

## Rationale

The user explicitly granted permission to override `AGENTS.md` and `decisions` to achieve this aesthetic. Providing a premium interface for reading knowledge objects aligns with the goal of "UX clarity for operators and readers" (Priority 5), even if it adds "cosmetic polish" (Priority 7).

## Consequences

- Increased complexity in CSS components.
- Deviation from a strictly minimal "IT support" feel to a more "product-led" knowledge platform feel.
- Future UI components for the reading surface should follow these luxury aesthetic guidelines.
