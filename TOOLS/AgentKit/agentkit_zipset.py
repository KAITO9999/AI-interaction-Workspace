"""Sequential ZIP extraction with manifest-backed tags and safe managed cleanup."""
from __future__ import annotations
import argparse
import json
import os
import shutil
import sys
import time
import uuid
import zipfile
from pathlib import Path, PurePosixPath

VERSION = "0.1.0"
MANIFEST = ".agentkit-zip-manifest.json"
MAX_MEMBERS = 100_000
MAX_TOTAL_BYTES = 2 * 1024 * 1024 * 1024

def load_manifest(root: Path) -> dict:
    path = root / MANIFEST
    if not path.exists():
        return {"version": 1, "items": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("version") != 1 or not isinstance(data.get("items"), list):
            raise ValueError("unsupported manifest structure")
        return data
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read manifest safely: {exc}") from exc

def save_manifest(root: Path, data: dict) -> None:
    root.mkdir(parents=True, exist_ok=True)
    tmp = root / (MANIFEST + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(root / MANIFEST)

def safe_member_path(name: str) -> PurePosixPath:
    path = PurePosixPath(name.replace("\\", "/"))
    if path.is_absolute() or any(part in {"..", ""} for part in path.parts) or (path.parts and ":" in path.parts[0]):
        raise ValueError(f"unsafe ZIP member path: {name}")
    return path

def extract_one(archive_path: Path, output_root: Path, tags: list[str], overwrite: bool = False) -> dict:
    archive_path = archive_path.resolve()
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        if len(infos) > MAX_MEMBERS:
            raise ValueError(f"archive has too many members ({len(infos)})")
        total = sum(item.file_size for item in infos)
        if total > MAX_TOTAL_BYTES:
            raise ValueError(f"archive expands beyond {MAX_TOTAL_BYTES} byte safety limit")
        for item in infos:
            safe_member_path(item.filename)
            mode = (item.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                raise ValueError(f"symbolic link entry is not extracted: {item.filename}")
        base = f"{archive_path.stem}（{archive_path.suffix.lstrip('.').lower() or 'archive'}）"
        destination = output_root / base
        index = 2
        while destination.exists():
            if overwrite:
                raise ValueError("--overwrite is intentionally unsupported for existing extraction directories")
            destination = output_root / f"{base}-{index}"
            index += 1
        destination.mkdir(parents=True, exist_ok=False)
        try:
            for item in infos:
                relative = safe_member_path(item.filename)
                target = destination.joinpath(*relative.parts)
                resolved = target.resolve()
                if not resolved.is_relative_to(destination.resolve()):
                    raise ValueError(f"ZIP member escapes extraction root: {item.filename}")
                if item.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(item, "r") as src, target.open("xb") as dst:
                        shutil.copyfileobj(src, dst, length=1024 * 1024)
        except Exception:
            shutil.rmtree(destination, ignore_errors=True)
            raise
    return {"id": uuid.uuid4().hex[:12], "archive": str(archive_path), "destination": str(destination.resolve()), "tags": sorted(set(tags + ["zip", archive_path.suffix.lstrip(".").lower()])), "created_epoch": time.time(), "created_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "member_count": len(infos), "expanded_bytes": total}

def is_managed_child(root: Path, value: str) -> Path:
    path = Path(value).resolve()
    base = root.resolve()
    if path == base or not path.is_relative_to(base):
        raise ValueError(f"refusing to manage path outside output root: {value}")
    return path

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    extract = sub.add_parser("extract", help="Extract ZIP files in sorted sequence.")
    extract.add_argument("source", help="ZIP file or directory containing ZIP files.")
    extract.add_argument("--output", required=True)
    extract.add_argument("--tag", action="append", default=[])
    extract.add_argument("--recursive", action="store_true", help="Include ZIP files in child directories.")
    listing = sub.add_parser("list", help="List managed extraction records.")
    listing.add_argument("--output", required=True)
    listing.add_argument("--tag")
    delete = sub.add_parser("delete", help="Delete only manifest-tracked extraction directories.")
    delete.add_argument("--output", required=True)
    selector = delete.add_mutually_exclusive_group(required=True)
    selector.add_argument("--id")
    selector.add_argument("--older-than-days", type=float)
    selector.add_argument("--all", action="store_true")
    delete.add_argument("--yes", action="store_true", help="Required to actually delete; otherwise dry-run.")
    args = parser.parse_args()
    output = Path(args.output).expanduser().resolve()
    try:
        manifest = load_manifest(output)
        if args.action == "extract":
            source = Path(args.source).expanduser().resolve()
            if source.is_file():
                archives = [source] if source.suffix.lower() == ".zip" else []
            elif source.is_dir():
                pattern = "**/*.zip" if args.recursive else "*.zip"
                archives = sorted(source.glob(pattern), key=lambda p: (p.name.casefold(), str(p)))
            else:
                print(f"ERROR: source does not exist: {source}", file=sys.stderr)
                return 2
            if not archives:
                print("No ZIP archives found.")
                return 0
            output.mkdir(parents=True, exist_ok=True)
            successes, failures = 0, 0
            for archive in archives:
                try:
                    record = extract_one(archive, output, args.tag)
                    manifest["items"].append(record)
                    save_manifest(output, manifest)
                    print(f"EXTRACTED id={record['id']} tags={','.join(record['tags'])} -> {record['destination']}")
                    successes += 1
                except (OSError, ValueError, zipfile.BadZipFile, RuntimeError) as exc:
                    print(f"ERROR {archive}: {exc}", file=sys.stderr)
                    failures += 1
            print(f"Finished in sequence: success={successes} failed={failures}.")
            return 1 if failures else 0
        if args.action == "list":
            items = manifest["items"]
            if args.tag:
                items = [item for item in items if args.tag in item.get("tags", [])]
            for item in sorted(items, key=lambda x: x.get("created_epoch", 0)):
                print(f"{item['id']}\t{item.get('created_local','')}\t{','.join(item.get('tags',[]))}\t{item.get('destination','')}")
            print(f"Records: {len(items)}")
            return 0
        now = time.time()
        if args.id:
            chosen = [item for item in manifest["items"] if item.get("id") == args.id]
            if not chosen:
                print(f"ERROR: no record with id {args.id}", file=sys.stderr)
                return 2
        elif args.older_than_days is not None:
            cutoff = now - max(0, args.older_than_days) * 86400
            chosen = [item for item in manifest["items"] if item.get("created_epoch", now) < cutoff]
        else:
            chosen = list(manifest["items"])
        for item in chosen:
            target = is_managed_child(output, item["destination"])
            exists = target.exists()
            print(f"{'DELETE' if args.yes else 'DRY-RUN'} id={item['id']} path={target} exists={exists}")
        if not args.yes:
            print("Dry run only. Add --yes after reviewing the exact targets.")
            return 0
        removed_ids = set()
        for item in chosen:
            target = is_managed_child(output, item["destination"])
            if target.exists():
                shutil.rmtree(target)
            removed_ids.add(item["id"])
        manifest["items"] = [item for item in manifest["items"] if item.get("id") not in removed_ids]
        save_manifest(output, manifest)
        print(f"Deleted {len(removed_ids)} managed extraction(s).")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
