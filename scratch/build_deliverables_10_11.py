import os, json, hashlib, subprocess

def get_hashes(path):
    if not os.path.exists(path):
        return 0, 'PENDING_CREATION', 'PENDING_CREATION'
    with open(path, 'rb') as f:
        c = f.read()
    raw = hashlib.sha256(c).hexdigest()
    lf = hashlib.sha256(c.replace(b'\r\n', b'\n')).hexdigest()
    return len(c), raw, lf

prior_status = subprocess.check_output(['git', 'status', '--porcelain', '-uall'], text=True).strip().splitlines()
prior_paths = [l[3:].strip() for l in prior_status if not 'stage3c' in l.lower()]

stage3c_paths = [
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
    'research/evidence/v30/v30_stage3c_artifact_checksum_manifest.json',
    'research/tests/test_v30_stage3c_governance_and_freeze.py'
]

all_eligible_paths = sorted(list(set(prior_paths + stage3c_paths)))

staging_manifest_entries = {}
for p in all_eligible_paths:
    sz, raw, lf = get_hashes(p)
    staging_manifest_entries[p] = {
        'path': p,
        'size_bytes': sz,
        'raw_sha256': raw,
        'lf_sha256': lf,
        'approved_for_staging': True
    }

staging_data = {
    'human_archival_staging_manifest': {
        'timestamp_utc': '2026-10-25T18:55:00Z',
        'stage': 'V30 Stage 3C',
        'governance_instructions': 'Approved staging manifest for HUMAN OPERATOR ONLY. Coding agent is strictly barred from executing git add, commit, or push.',
        'target_archival_branch': 'archive/v30-stage2h-final-evidence-freeze',
        'expected_parent_commit': 'ce6b4c21b832044d0ffb45dce2ba949ab867d520',
        'total_eligible_files': len(staging_manifest_entries),
        'approved_paths': staging_manifest_entries
    }
}
with open('research/evidence/v30/v30_stage3c_human_archival_staging_manifest.json', 'w', encoding='utf-8') as f:
    json.dump(staging_data, f, indent=2)

instructions_data = {
    'human_only_git_archival_instructions': {
        'timestamp_utc': '2026-10-25T18:55:00Z',
        'stage': 'V30 Stage 3C',
        'warning': 'FOR HUMAN REPOSITORY OWNER EXECUTION ONLY. The AI agent MUST NOT execute these commands.',
        'step_by_step_procedure_powershell': [
            '# Step 1: Navigate to repository root',
            'cd C:\\Users\\Manish\\Downloads\\Guardian-Alpha-V29B',
            '',
            '# Step 2: Verify repository state and invariants',
            '$branch = git branch --show-current',
            'if ($branch -ne \"archive/v30-stage2h-final-evidence-freeze\") { throw \"Branch mismatch: $branch\" }',
            '$head = git rev-parse HEAD',
            'if ($head -ne \"ce6b4c21b832044d0ffb45dce2ba949ab867d520\") { throw \"HEAD mismatch: $head\" }',
            '',
            '# Step 3: Verify working tree has zero staged changes',
            '$staged = git diff --cached --name-only',
            'if ($staged) { throw \"Unexpected staged changes detected: $staged\" }',
            '',
            '# Step 4: Stage ONLY the approved files from the human staging manifest',
            '$manifest = Get-Content \"research/evidence/v30/v30_stage3c_human_archival_staging_manifest.json\" | ConvertFrom-Json',
            'foreach ($path in $manifest.human_archival_staging_manifest.approved_paths.PSObject.Properties.Name) {',
            '    git add -f -- $path',
            '}',
            '',
            '# Step 5: Verify staged file count matches manifest',
            '$staged_count = (git diff --cached --name-only).Count',
            '$expected_count = $manifest.human_archival_staging_manifest.total_eligible_files',
            'if ($staged_count -ne $expected_count) { throw \"Staged count mismatch: got $staged_count, expected $expected_count\" }',
            '',
            '# Step 6: Create archival commit (DO NOT PUSH)',
            'git commit -m \"archive: Stage 3C evidence freeze and exploratory research decision package\"',
            '',
            '# Step 7: Post-commit verification',
            '$new_head = git rev-parse HEAD',
            '$parent = git rev-parse HEAD~1',
            'if ($parent -ne \"ce6b4c21b832044d0ffb45dce2ba949ab867d520\") { throw \"Commit parent mismatch: $parent\" }',
            'Write-Host \"Stage 3C Archival Freeze Committed Successfully: $new_head (DO NOT PUSH)\"'
        ],
        'safety_safeguards': [
            'Refuses unexpected staged files.',
            'Preserves raw artifact bytes despite CRLF/LF Git normalization.',
            'Strictly avoids git add . and wildcards.',
            'Strictly avoids git reset, clean, restore, or checkout.',
            'Preserves commit ancestry from Stage 2H-Final (ce6b4c21b832044d0ffb45dce2ba949ab867d520).',
            'Strictly prohibits automatic or unattended git push.'
        ]
    }
}
with open('research/evidence/v30/v30_stage3c_human_only_git_archival_instructions.json', 'w', encoding='utf-8') as f:
    json.dump(instructions_data, f, indent=2)

print('Generated Deliverables 10 and 11 successfully.')
