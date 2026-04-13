# Experience Principles

Status: Approved
Owner: Product / UX / Architecture
Scope: Cross-surface experience boundaries, role separation, visibility, and shell ownership

## Principles
- Reader is for consumption.
- Operator is for work.
- Admin is for control.
- Hidden means both absent and disabled *for that specific user*
- Search visibility must match route visibility.
- Global search is shell-owned and remains centered in the top bar. Brand and shell controls may change around it, but they must not displace it.
- Separate route groups and shells are mandatory.
- Shared primitives are allowed. Shared blended experiences are not.
- Production role switching is forbidden.
- Transitional development personas must not define permanent production information architecture.

## Tonal language
- Papyrus uses a governed tonal family centered on Pantone 7659 C, not a single-color theme.
- Pantone 7659 C (`#5D3754`) is identity and intent. Use it for primary actions, active navigation, object identity cues, command highlights, summary chips, and review-intent controls.
- Pantone 7658 C (`#6A3460`) is authority and depth. Use it for shell bars, pressed or hover states of hero controls, dense metadata emphasis, and other high-contrast depth cues.
- Pantone 7660 C (`#9991A4`) is context and grouping. Use it for contextual fills, selected rows, grouped secondary controls, filter states, timeline rails, and governance or metadata panels.
- Semantic success, warning, error, and info colors remain separate from the 7658/7659/7660 family.
- Most surfaces remain neutral. The purple family is reserved for orientation, context, and high-intent actions.
- Use one dominant purple-family tone per component. Do not mix hero, depth, and context equally on the same element.
- Avoid decorative purple gradients and theme flooding. The product should feel calm, operational, governed, and precise.
