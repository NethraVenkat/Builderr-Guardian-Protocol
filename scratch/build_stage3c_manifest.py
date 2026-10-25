import os, json, hashlib

artifacts = [
    'GUARDIAN_ALPHA_V30_STAGE3C_SCIENTIFIC_DECISION_AND_EVIDENCE_FREEZE.md',
    'research/evidence/v30/v30_stage3c_frozen_checkpoint_certification.json',
    'research/evidence/v30/v30_stage3c_eligible_evidence_inventory.json',
    'research/evidence/v30/v30_stage3c_exclusion_and_disposition_ledger.json',
    'research/evidence/v30/v30_stage3c_historical_evidence_integrity_reconciliation.json',
    'research/evidence/v30/v30_stage3c_scientific_alternatives_decision_matrix.json',
    'research/evidence/v30/v30_stage3c_exploratory_only_preregistration_draft.json',
    'research/evidence/v30/v30_stage3c_statistical_failure_preservation_record.json',
    'research/evidence/v30/v30_stage3c_canonical_owner_decision_register.json',
    'research/evidence/v30/v30_stage3c_provider_independent_retention_taxonomy.json',
    'research/evidence/v30/v30_stage3c_human_archival_staging_manifest.json',
    'research/evidence/v30/v30_stage3c_human_only_git_archival_instructions.json',
    'research/evidence/v30/v30_stage3c_executed_verification_ledger.json',
    'research/tests/test_v30_stage3c_governance_and_freeze.py'
]

manifest = {
    'manifest_metadata': {
        'title': 'Guardian Alpha V30 Stage 3C - Artifact Checksum Manifest',
        'timestamp_utc': '2026-10-25T19:05:00Z',
        'git_branch': 'archive/v30-stage2h-final-evidence-freeze',
        'git_head': 'ce6b4c21b832044d0ffb45dce2ba949ab867d520',
        'git_parent': 'b283ded200c777b130285b0aa56a0b044afbd339',
        'total_stage3c_artifacts': len(artifacts),
        'exclusion_notice': 'This manifest records independent external cryptographic hashes of the other 14 Stage 3C deliverables and test suites. Self-hashing is explicitly excluded to avoid self-referential paradoxes.'
    },
    'artifacts': {}
}

for path in artifacts:
    assert os.path.exists(path), f'Missing: {path}'
    with open(path, 'rb') as f:
        content = f.read()
    raw_hash = hashlib.sha256(content).hexdigest()
    lf_hash = hashlib.sha256(content.replace(b'\r\n', b'\n')).hexdigest()
    size_bytes = len(content)
    manifest['artifacts'][path] = {
        'size_bytes': size_bytes,
        'raw_sha256': raw_hash,
        'lf_sha256': lf_hash
    }

manifest_path = 'research/evidence/v30/v30_stage3c_artifact_checksum_manifest.json'
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2)

print('Wrote Stage 3C manifest successfully')
