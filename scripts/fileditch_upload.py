#!/usr/bin/env python3
"""Upload build packages to FileDitch and write a public URL manifest."""

from __future__ import annotations

import argparse
import http.client
import json
import sys
from pathlib import Path
from urllib.parse import SplitResult, urlencode, urlsplit

HOST = "new.fileditch.com"
MAX_RESPONSE = 1024 * 1024
MAX_UPLOAD = 150 * 1024**3
CHUNK_SIZE = 1024 * 1024
ALLOWED_FILE_HOSTS = {"fileditchvids.st", "itsfileditchfiles.st"}


class UploadError(RuntimeError):
    """A safe-to-display upload failure."""


def upload_path(filename: str) -> str:
    return "/upload.php?" + urlencode({"filename": filename})


def validate_result(raw: bytes, filename: str, size: int) -> dict[str, object]:
    if len(raw) > MAX_RESPONSE:
        raise UploadError("FileDitch response exceeded the JSON size limit")
    try:
        result = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UploadError("FileDitch returned invalid JSON") from exc
    if not isinstance(result, dict) or result.get("success") is not True:
        raise UploadError("FileDitch rejected the upload")
    url = result.get("url")
    parsed = urlsplit(url) if isinstance(url, str) else None
    if (
        parsed is None
        or parsed.scheme != "https"
        or parsed.hostname not in ALLOWED_FILE_HOSTS
        or parsed.username
        or parsed.password
        or _unexpected_port(parsed)
    ):
        raise UploadError("FileDitch returned an unexpected download URL")
    if result.get("filename") != filename or result.get("size") != size:
        raise UploadError("FileDitch upload confirmation did not match the local file")
    return {"filename": filename, "size": size, "url": url}


def _unexpected_port(parsed: SplitResult) -> bool:
    try:
        return parsed.port not in (None, 443)
    except ValueError:
        return True


def upload_file(path: Path) -> dict[str, object]:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise UploadError(f"cannot read build package {path.name}") from exc
    if not path.is_file() or size <= 0:
        raise UploadError(f"refusing to upload an empty or invalid file: {path.name}")
    if size > MAX_UPLOAD:
        raise UploadError(f"{path.name} exceeds FileDitch's 150 GB upload limit")

    connection = http.client.HTTPSConnection(HOST, timeout=300)
    try:
        connection.putrequest("PUT", upload_path(path.name))
        connection.putheader("Content-Type", "application/octet-stream")
        connection.putheader("Content-Length", str(size))
        connection.endheaders()
        with path.open("rb") as source:
            while chunk := source.read(CHUNK_SIZE):
                connection.send(chunk)
        response = connection.getresponse()
        if not 200 <= response.status < 300:
            raise UploadError(f"FileDitch upload failed (HTTP {response.status})")
        raw = response.read(MAX_RESPONSE + 1)
        return validate_result(raw, path.name, size)
    except (OSError, http.client.HTTPException, TimeoutError) as exc:
        raise UploadError(f"FileDitch upload could not be completed for {path.name}") from exc
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()
    files = [upload_file(path) for path in args.files]
    manifest = {"schema": 1, "storage": "fileditch", "files": files}
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for file in files:
        print(f"Uploaded {file['filename']}")
    print(f"Wrote public URL index to {args.output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except UploadError as exc:
        print(f"Upload failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
