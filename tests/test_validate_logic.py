import sys
from pathlib import Path

# Add project root to sys.path so we can import scripts
PROJECT_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# Import specific functions from validate.py
# Note: This might fail if validate.py runs code at module level without if __name__ == "__main__":
# We checked validate.py earlier and it has if __name__ == "__main__": so it's safe.
from scripts.validate import (
    _PLACEHOLDER_RE,
    _SEMVER_RE,
    slugify_heading,
)


def test_semver_regex():
    assert _SEMVER_RE.match("1.0.0")
    assert _SEMVER_RE.match("0.1.0-beta")
    assert _SEMVER_RE.match("2026.01.01")
    assert not _SEMVER_RE.match("1.0")
    assert not _SEMVER_RE.match("v1.0.0")  # We expect pure semver without 'v' in the regex used?
    # Let's check the regex again: ^\d+\.\d+\.\d+(-[\w.]+)?(\+[\w.]+)?$
    # So yes, no 'v'.


def test_slugify_heading():
    assert slugify_heading("My Heading") == "my-heading"
    assert slugify_heading("Hello World!") == "hello-world"
    assert slugify_heading("  Spaced  Out  ") == "spaced-out"


def test_placeholder_regex():
    text = "Hello {name}, welcome to {place}."
    placeholders = _PLACEHOLDER_RE.findall(text)
    assert "name" in placeholders
    assert "place" in placeholders
    assert len(placeholders) == 2
