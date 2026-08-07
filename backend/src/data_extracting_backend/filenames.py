from pathlib import PurePosixPath, PureWindowsPath


def sanitize_source_filename(value: str) -> str:
    """Basename only — reject path separators / traversal (MVP security baseline)."""
    raw = value.strip()
    if not raw:
        raise ValueError("source_filename must not be blank")

    if "/" in raw or "\\" in raw or raw in {".", ".."}:
        raise ValueError(
            "source_filename must be a basename without path separators"
        )

    name = PureWindowsPath(raw).name
    name = PurePosixPath(name).name
    if not name or name in {".", ".."} or name != raw:
        raise ValueError(
            "source_filename must be a basename without path separators"
        )
    return name
