from __future__ import annotations

from papyrus.application.substrate_checks import validate_web_copy_policy


def main() -> int:
    issues = validate_web_copy_policy()
    if issues:
        for issue in issues:
            print(issue.render())
        return 1
    print("web copy policy lint passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
