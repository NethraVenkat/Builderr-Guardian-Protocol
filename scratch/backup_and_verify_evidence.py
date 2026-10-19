r"""Backup and verification script for Builderr research evidence.

Executes:
1. Byte-preserving backup of scratch JSON files to C:\Users\Manish\Downloads\Builderr-Evidence-Archive
2. Hash comparison (SHA-256)
3. Byte-by-byte comparison
4. JSON syntax validation
5. Non-destructive restore test to temporary directory
6. Creation of external backup manifest
"""
import os
import sys
import json
import shutil
import hashlib
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\Manish\Downloads\New folder\Builderr-Trading-Agent")
ARCHIVE_ROOT = Path(r"C:\Users\Manish\Downloads\Builderr-Evidence-Archive")
SNAPSHOT_ID = "snapshot-20261019-233800-commit-471d390"
SNAPSHOT_DIR = ARCHIVE_ROOT / SNAPSHOT_ID
RESTORE_TEST_DIR = ARCHIVE_ROOT / "test_restore_verify"

FILES_TO_BACKUP = [
    {
        "rel_path": "scratch/agent_day_logs.json",
        "description": "Full daily positions, fills, and equity trace during COVID vol spike snapback regime",
        "generating_script": "scratch/deep_baseline_profile.py",
        "source_dataset": "sample_regimes.json.gz (vol_spike_snapback)",
        "source_commit": "54d867a78200b04c629d43a74882324e392fc358"
    },
    {
        "rel_path": "scratch/deep_profile_metrics.json",
        "description": "Comprehensive multi-metric baseline and agent profiles across all 3 regimes",
        "generating_script": "scratch/deep_baseline_profile.py",
        "source_dataset": "sample_regimes.json.gz (all 3 regimes)",
        "source_commit": "54d867a78200b04c629d43a74882324e392fc358"
    },
    {
        "rel_path": "scratch/hypotheses_results.json",
        "description": "Empirical results for hypothesis testing H1, H5, and baseline reference",
        "generating_script": "scratch/test_hypotheses.py",
        "source_dataset": "sample_regimes.json.gz (all 3 regimes)",
        "source_commit": "54d867a78200b04c629d43a74882324e392fc358"
    }
]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def run_backup_and_verification():
    print("=" * 80)
    print("STARTING EVIDENCE BACKUP AND VERIFICATION AUDIT")
    print(f"Archive Directory: {ARCHIVE_ROOT}")
    print(f"Snapshot Directory: {SNAPSHOT_DIR}")
    print("=" * 80)

    # 1. Create Archive & Snapshot directory
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    RESTORE_TEST_DIR.mkdir(parents=True, exist_ok=True)

    backup_records = []
    all_passed = True

    for item in FILES_TO_BACKUP:
        src_path = PROJECT_ROOT / item["rel_path"]
        assert src_path.exists(), f"Source file missing: {src_path}"

        src_bytes = src_path.read_bytes()
        src_size = len(src_bytes)
        src_hash = hashlib.sha256(src_bytes).hexdigest()

        # Destination path
        dst_path = SNAPSHOT_DIR / src_path.name
        # Byte-preserving copy
        shutil.copy2(src_path, dst_path)

        # 1. Check destination exists
        assert dst_path.exists(), f"Destination file missing: {dst_path}"

        # 2. Compare file sizes
        dst_bytes = dst_path.read_bytes()
        dst_size = len(dst_bytes)
        size_match = (src_size == dst_size)

        # 3. Compute destination hash independently
        dst_hash = hashlib.sha256(dst_bytes).hexdigest()
        hash_match = (src_hash == dst_hash)

        # 4. Byte-by-byte comparison
        bytes_match = (src_bytes == dst_bytes)

        # 5. Parse destination JSON
        json_valid = False
        try:
            parsed = json.loads(dst_bytes.decode("utf-8"))
            json_valid = True
            item_count = len(parsed) if isinstance(parsed, (dict, list)) else 1
        except Exception as e:
            item_count = 0

        # 6. Test restore into separate temporary verification directory
        restore_path = RESTORE_TEST_DIR / src_path.name
        shutil.copy2(dst_path, restore_path)
        assert restore_path.exists(), f"Restored file missing: {restore_path}"
        restore_bytes = restore_path.read_bytes()
        restore_hash = hashlib.sha256(restore_bytes).hexdigest()
        restore_match = (restore_hash == src_hash and restore_bytes == src_bytes)

        status_item = {
            "file_name": src_path.name,
            "original_path": str(src_path),
            "backup_path": str(dst_path),
            "restore_test_path": str(restore_path),
            "size_bytes": src_size,
            "sha256": src_hash,
            "backup_sha256": dst_hash,
            "restored_sha256": restore_hash,
            "size_match": size_match,
            "hash_match": hash_match,
            "bytes_match": bytes_match,
            "json_valid": json_valid,
            "item_count": item_count,
            "restore_match": restore_match,
            "generating_script": item["generating_script"],
            "source_dataset": item["source_dataset"],
            "source_commit": item["source_commit"],
            "description": item["description"]
        }
        backup_records.append(status_item)

        print(f"Verified: {src_path.name}")
        print(f"  Size: {src_size} bytes (Match: {size_match})")
        print(f"  SHA-256: {src_hash} (Match: {hash_match})")
        print(f"  Byte-exact: {bytes_match}")
        print(f"  JSON Parse Valid: {json_valid} (Top-level items: {item_count})")
        print(f"  Restore Test: {restore_match}")
        print()

        if not (size_match and hash_match and bytes_match and json_valid and restore_match):
            all_passed = False

    # Create external backup manifest
    manifest_data = {
        "snapshot_id": SNAPSHOT_ID,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "created_at_local": "2026-10-19T23:38:00+05:30",
        "original_project_path": str(PROJECT_ROOT),
        "source_git_commit": "471d3908b9e889f58723f6b5b9be20617e258eea",
        "backup_storage_path": str(SNAPSHOT_DIR),
        "restore_test_path": str(RESTORE_TEST_DIR),
        "backup_verification_verdict": "BACKUP_VERIFIED" if all_passed else "BACKUP_FAILED",
        "backup_limitations": [
            "Single-drive risk: Backup archive resides on C: drive (same physical volume).",
            "Local protection: Protects completely against accidental project deletion, folder reset, Git corruption, or file modification.",
            "Disaster recovery notice: Does not protect against physical hardware drive loss or complete disk failure. No cloud transmission performed per competition privacy rules."
        ],
        "files": backup_records
    }

    manifest_file = ARCHIVE_ROOT / "manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    # Also save snapshot-specific manifest
    snapshot_manifest_file = SNAPSHOT_DIR / "snapshot_manifest.json"
    with open(snapshot_manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print("=" * 80)
    print(f"Manifest written to: {manifest_file}")
    print(f"Snapshot manifest written to: {snapshot_manifest_file}")
    print(f"Final Verification Verdict: {'BACKUP_VERIFIED' if all_passed else 'BACKUP_FAILED'}")
    print("=" * 80)

    return all_passed, manifest_data

if __name__ == "__main__":
    success, data = run_backup_and_verification()
    sys.exit(0 if success else 1)
