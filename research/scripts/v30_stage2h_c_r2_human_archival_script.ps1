<#
================================================================================
GUARDIAN ALPHA V30 — HUMAN-ONLY ARCHIVAL PRESERVATION SCRIPT (STAGE 2H-C-R2)
STRICT AUDIT POLICY: ZERO AGENT GIT MUTATIONS PERMITTED.
FOR MANUAL EXECUTION BY HUMAN REPOSITORY OWNER ONLY.
DO NOT EXECUTE AUTOMATICALLY.
================================================================================
Target Branch: archive/v30-stage2h-final-evidence-freeze
Base Commit:   b283ded200c777b130285b0aa56a0b044afbd339
Explicit Staging Artifacts: 198 files (Zero Wildcards / Zero Globs)
Excluded Restricted Items: tiingo_cache/ (Holdout Market Data)
Remote Push Command: NONE (Strictly Prohibited)
================================================================================
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "=================================================================="
Write-Host " GUARDIAN ALPHA V30 — HUMAN-CONTROLLED EVIDENCE ARCHIVAL SCRIPT   "
Write-Host "=================================================================="

# --- PRE-FLIGHT SAFETY ASSERTIONS ---
Write-Host "`n[PRE-FLIGHT] Checking environment prerequisites..."

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "PRE-FLIGHT FAILURE: git command not found in PATH."
}

if (-not (Test-Path ".git")) {
    throw "PRE-FLIGHT FAILURE: Current directory is not a Git repository root."
}

$currentHead = (git rev-parse HEAD).Trim()
$expectedHead = "b283ded200c777b130285b0aa56a0b044afbd339"
if ($currentHead -ne $expectedHead) {
    throw "PRE-FLIGHT FAILURE: Current HEAD ($currentHead) does not match expected baseline HEAD ($expectedHead)."
}
Write-Host " [PASS] HEAD matches expected checkpoint: $currentHead"

$existingArchiveBranch = (git branch --list "archive/v30-stage2h-final-evidence-freeze").Trim()
if ($existingArchiveBranch) {
    throw "PRE-FLIGHT FAILURE: Archive branch 'archive/v30-stage2h-final-evidence-freeze' already exists."
}
Write-Host " [PASS] Target branch does not exist yet."

$stagedDiff = (git diff --cached --name-only).Trim()
if ($stagedDiff) {
    throw "PRE-FLIGHT FAILURE: Staging area contains uncommitted staged changes."
}
Write-Host " [PASS] Staging area is clean."

Write-Host "`n[PRE-FLIGHT] Enumerating and verifying all 198 explicit approved file paths..."
$approvedFiles = @(
    "GUARDIAN_ALPHA_V29E_EXECUTED_TEST_REPORT.md",
    "GUARDIAN_ALPHA_V29E_FINAL_GATE_REPORT.md",
    "GUARDIAN_ALPHA_V29E_N_NOISE_INVENTORY.md",
    "GUARDIAN_ALPHA_V29E_N_NOISE_REDUCTION_PROPOSAL.md",
    "GUARDIAN_ALPHA_V29E_N_PUBLIC_SNAPSHOT_MINIMIZATION.md",
    "GUARDIAN_ALPHA_V29E_REFERENCE_AND_PAYLOAD_AUDIT.md",
    "GUARDIAN_ALPHA_V29E_R_DATA_RIGHTS_ASSESSMENT.md",
    "GUARDIAN_ALPHA_V29E_R_DEPENDENCY_REMEDIATION.md",
    "GUARDIAN_ALPHA_V29E_R_FINAL_GATE.md",
    "GUARDIAN_ALPHA_V29E_R_PUBLIC_HISTORY_RISK_REVIEW.md",
    "GUARDIAN_ALPHA_V29E_R_RELEASE_DOCUMENTATION_REVIEW.md",
    "GUARDIAN_ALPHA_V29E_SECURITY_AND_ANCESTRY_AUDIT.md",
    "GUARDIAN_ALPHA_V29E_S_SNAPSHOT_RECOVERY_AND_NOISE_CONTROL.md",
    "GUARDIAN_ALPHA_V29F_EVIDENCE_PRESERVATION.md",
    "GUARDIAN_ALPHA_V29F_FINAL_DECISION.md",
    "GUARDIAN_ALPHA_V29F_INDEPENDENT_ROOT_DESIGN.md",
    "GUARDIAN_ALPHA_V29F_RIGHTS_RESOLUTION.md",
    "GUARDIAN_ALPHA_V29F_SYNTHETIC_FEASIBILITY.md",
    "GUARDIAN_ALPHA_V29G_A_PRIVATE_ARCHIVAL_CONTINUATION.md",
    "GUARDIAN_ALPHA_V29G_A_PRIVATE_ARCHIVAL_VERIFICATION.md",
    "GUARDIAN_ALPHA_V30_STAGE1_DIAGNOSTIC.md",
    "GUARDIAN_ALPHA_V30_STAGE2A_BG_CONTRACT_AND_GENERALIZATION.md",
    "GUARDIAN_ALPHA_V30_STAGE2A_EXECUTION_SAFETY.md",
    "GUARDIAN_ALPHA_V30_STAGE2A_F_FINAL_ACCEPTANCE.md",
    "GUARDIAN_ALPHA_V30_STAGE2A_R_INDEPENDENT_REMEDIATION.md",
    "GUARDIAN_ALPHA_V30_STAGE2B_DEFENSIVE_ALLOCATION_RESEARCH.md",
    "GUARDIAN_ALPHA_V30_STAGE2B_R_BASELINE_RECONCILIATION.md",
    "GUARDIAN_ALPHA_V30_STAGE2C_VOLATILITY_GATING_RESEARCH.md",
    "GUARDIAN_ALPHA_V30_STAGE2D_POSITION_SIZING_RESEARCH.md",
    "GUARDIAN_ALPHA_V30_STAGE2D_R_OVERLAY_AND_ORACLE_AUDIT.md",
    "GUARDIAN_ALPHA_V30_STAGE2E_CROSS_STAGE_EVIDENCE_AND_RISK_BUDGET.md",
    "GUARDIAN_ALPHA_V30_STAGE2F_FINAL_CORRECTIONS_AND_FORWARD_PROTOCOL.md",
    "GUARDIAN_ALPHA_V30_STAGE2G_FORWARD_READINESS_CERTIFICATION.md",
    "GUARDIAN_ALPHA_V30_STAGE2G_R_FINAL_CORRECTIONS.md",
    "GUARDIAN_ALPHA_V30_STAGE2H_A_EXTENDED_READINESS_AND_OWNER_APPROVAL.md",
    "GUARDIAN_ALPHA_V30_STAGE2H_B_FINAL_GOVERNANCE_CORRECTIONS.md",
    "GUARDIAN_ALPHA_V30_STAGE2H_C_FINAL_FREEZE_AND_OWNER_HANDOVER.md",
    "GUARDIAN_ALPHA_V30_STAGE2H_C_R2_ARCHIVE_EXECUTION_PROOF.md",
    "GUARDIAN_ALPHA_V30_STAGE2H_C_R_LOSSLESS_ARCHIVE_RECONCILIATION.md",
    "research/engine/cash_affordability_model.py",
    "research/engine/v30_broker_accounting_final.py",
    "research/engine/v30_broker_accounting_r.py",
    "research/engine/v30_independent_accounting_oracle.py",
    "research/engine/v30_overlay_auditor.py",
    "research/engine/v30_sizing_oracle.py",
    "research/engine/v30_sizing_oracle_decimal.py",
    "research/engine/v30_stage2g_r_accounting_verifier.py",
    "research/engine/v30_stage2g_r_activation_guard.py",
    "research/engine/v30_stage2g_r_causal_event_engine.py",
    "research/engine/v30_stage2g_r_crash_tester.py",
    "research/engine/v30_stage2g_synthetic_dry_runner.py",
    "research/engine/v30_stage2h_a_accounting_assurance_runner.py",
    "research/engine/v30_stage2h_a_audit_runner.py",
    "research/engine/v30_stage2h_a_crash_tester.py",
    "research/engine/v30_stage2h_a_dashboard_mockup.html",
    "research/engine/v30_stage2h_a_hardened_causal_engine.py",
    "research/engine/v30_stage2h_a_security_auditor.py",
    "research/engine/v30_stage2h_b_dashboard_mockup.html",
    "research/engine/v30_stage2h_b_decimal_accounting_oracle.py",
    "research/engine/v30_stage2h_b_security_guard.py",
    "research/engine/v30_synthetic_stress_scenarios.py",
    "research/engine/v30_synthetic_stress_scenarios_stage2c.py",
    "research/engine/v30_synthetic_stress_scenarios_stage2d.py",
    "research/evidence/v29b/test_suite_400_classified_inventory.json",
    "research/evidence/v30/logs/partial_recovery_test.jsonl",
    "research/evidence/v30/logs/stage2g_r_crash_test_journal.jsonl",
    "research/evidence/v30/logs/stage2g_r_partial_journal.jsonl",
    "research/evidence/v30/logs/stage2h_a_recovery_journal.jsonl",
    "research/evidence/v30/v30_stage2c_historical_replay_results.json",
    "research/evidence/v30/v30_stage2c_preregistration_spec.json",
    "research/evidence/v30/v30_stage2d_historical_replay_results.json",
    "research/evidence/v30/v30_stage2d_preregistration_spec.json",
    "research/evidence/v30/v30_stage2d_r_overlay_audit.json",
    "research/evidence/v30/v30_stage2e_candidate_comparability_matrix.json",
    "research/evidence/v30/v30_stage2e_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2e_final_research_decision_register.json",
    "research/evidence/v30/v30_stage2e_master_evidence_inventory.json",
    "research/evidence/v30/v30_stage2e_risk_budget_decomposition.json",
    "research/evidence/v30/v30_stage2e_validation_contamination_register.json",
    "research/evidence/v30/v30_stage2f_artifact_hash_manifest.json",
    "research/evidence/v30/v30_stage2f_disputed_claim_correction_register.json",
    "research/evidence/v30/v30_stage2f_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2f_exposure_and_leverage_reconciliation.json",
    "research/evidence/v30/v30_stage2f_forward_paper_evaluation_protocol.json",
    "research/evidence/v30/v30_stage2f_independent_risk_contribution_verification.json",
    "research/evidence/v30/v30_stage2f_p4_drawdown_reconciliation.json",
    "research/evidence/v30/v30_stage2f_statistical_selection_bias_recalculation.json",
    "research/evidence/v30/v30_stage2f_updated_scientific_decision_implications.json",
    "research/evidence/v30/v30_stage2g_artifact_checksum_manifest.json",
    "research/evidence/v30/v30_stage2g_event_immutability_and_recovery_evidence.json",
    "research/evidence/v30/v30_stage2g_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2g_financial_accounting_verification.json",
    "research/evidence/v30/v30_stage2g_frozen_comparison_manifest.json",
    "research/evidence/v30/v30_stage2g_future_data_governance_checklist.json",
    "research/evidence/v30/v30_stage2g_r_activation_security_review.json",
    "research/evidence/v30/v30_stage2g_r_artifact_checksum_manifest.json",
    "research/evidence/v30/v30_stage2g_r_causal_event_specification.json",
    "research/evidence/v30/v30_stage2g_r_crash_recovery_evidence.json",
    "research/evidence/v30/v30_stage2g_r_defect_inventory.json",
    "research/evidence/v30/v30_stage2g_r_event_state_verification.json",
    "research/evidence/v30/v30_stage2g_r_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2g_r_financial_accounting_check.json",
    "research/evidence/v30/v30_stage2g_r_owner_authorization_checklist.json",
    "research/evidence/v30/v30_stage2g_r_provider_neutral_data_rights.json",
    "research/evidence/v30/v30_stage2g_r_revised_statistical_protocol.json",
    "research/evidence/v30/v30_stage2g_r_simulator_contract_parity_matrix.json",
    "research/evidence/v30/v30_stage2g_scientific_evaluation_preregistration.json",
    "research/evidence/v30/v30_stage2g_security_and_activation_boundary_audit.json",
    "research/evidence/v30/v30_stage2g_simulator_contract_compatibility_matrix.json",
    "research/evidence/v30/v30_stage2g_synthetic_dry_run_manifest.json",
    "research/evidence/v30/v30_stage2g_synthetic_scenario_specification.json",
    "research/evidence/v30/v30_stage2h_a_activation_security_audit.json",
    "research/evidence/v30/v30_stage2h_a_artifact_checksum_manifest.json",
    "research/evidence/v30/v30_stage2h_a_causal_event_hardening_audit.json",
    "research/evidence/v30/v30_stage2h_a_checkpoint_certification.json",
    "research/evidence/v30/v30_stage2h_a_crash_recovery_reliability.json",
    "research/evidence/v30/v30_stage2h_a_data_provenance_schema.json",
    "research/evidence/v30/v30_stage2h_a_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2h_a_financial_accounting_assurance.json",
    "research/evidence/v30/v30_stage2h_a_observability_and_incident_playbook.json",
    "research/evidence/v30/v30_stage2h_a_owner_decision_package.json",
    "research/evidence/v30/v30_stage2h_a_provider_due_diligence_matrix.json",
    "research/evidence/v30/v30_stage2h_a_red_team_register.json",
    "research/evidence/v30/v30_stage2h_a_scientific_protocol_review.json",
    "research/evidence/v30/v30_stage2h_a_simulator_contract_conformance.json",
    "research/evidence/v30/v30_stage2h_b_accounting_oracle_verification.json",
    "research/evidence/v30/v30_stage2h_b_adversarial_review.json",
    "research/evidence/v30/v30_stage2h_b_artifact_checksum_manifest.json",
    "research/evidence/v30/v30_stage2h_b_baseline_evidence_inventory.json",
    "research/evidence/v30/v30_stage2h_b_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2h_b_incident_controls_specification.json",
    "research/evidence/v30/v30_stage2h_b_owner_decision_package.json",
    "research/evidence/v30/v30_stage2h_b_provider_rights_matrix.json",
    "research/evidence/v30/v30_stage2h_b_security_red_team_findings.json",
    "research/evidence/v30/v30_stage2h_b_simulator_parity_assessment.json",
    "research/evidence/v30/v30_stage2h_b_statistical_protocol_audit.json",
    "research/evidence/v30/v30_stage2h_c_artifact_checksum_manifest.json",
    "research/evidence/v30/v30_stage2h_c_complete_workspace_inventory.json",
    "research/evidence/v30/v30_stage2h_c_cross_stage_consistency_register.json",
    "research/evidence/v30/v30_stage2h_c_final_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2h_c_governance_and_incident_checklist.json",
    "research/evidence/v30/v30_stage2h_c_human_git_preservation_plan.json",
    "research/evidence/v30/v30_stage2h_c_owner_decision_register.json",
    "research/evidence/v30/v30_stage2h_c_private_backup_specification.json",
    "research/evidence/v30/v30_stage2h_c_protected_source_certification.json",
    "research/evidence/v30/v30_stage2h_c_provider_decision_matrix.json",
    "research/evidence/v30/v30_stage2h_c_r2_artifact_checksum_manifest.json",
    "research/evidence/v30/v30_stage2h_c_r2_corrected_inventory.json",
    "research/evidence/v30/v30_stage2h_c_r2_corrected_staging_manifest.json",
    "research/evidence/v30/v30_stage2h_c_r2_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2h_c_r2_explicit_disposition_ledger.json",
    "research/evidence/v30/v30_stage2h_c_r2_human_powershell_instructions.json",
    "research/evidence/v30/v30_stage2h_c_r2_manifest_completeness_proof.json",
    "research/evidence/v30/v30_stage2h_c_r2_private_backup_reconciliation.json",
    "research/evidence/v30/v30_stage2h_c_r_artifact_checksum_manifest.json",
    "research/evidence/v30/v30_stage2h_c_r_artifact_disposition_ledger.json",
    "research/evidence/v30/v30_stage2h_c_r_chain_of_custody_matrix.json",
    "research/evidence/v30/v30_stage2h_c_r_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2h_c_r_fresh_workspace_inventory.json",
    "research/evidence/v30/v30_stage2h_c_r_frozen_source_verification.json",
    "research/evidence/v30/v30_stage2h_c_r_human_powershell_instructions.json",
    "research/evidence/v30/v30_stage2h_c_r_inventory_comparison.json",
    "research/evidence/v30/v30_stage2h_c_r_omitted_artifact_register.json",
    "research/evidence/v30/v30_stage2h_c_r_private_backup_manifest.json",
    "research/evidence/v30/v30_stage2h_c_r_proposed_git_staging_manifest.json",
    "research/evidence/v30/v30_stage2h_c_r_reproducibility_completeness.json",
    "research/evidence/v30/v30_stage2h_c_reproducibility_dependency_manifest.json",
    "research/evidence/v30/v30_stage2h_c_scientific_evaluation_proposal.json",
    "research/scripts/v30_stage2h_c_r2_human_archival_script.ps1",
    "research/strategies/v30_candidate_c1_tight_vol_gate.py",
    "research/strategies/v30_candidate_c2_vol_acceleration.py",
    "research/strategies/v30_candidate_c3_vol_persistence.py",
    "research/strategies/v30_candidate_c4_combined_gates.py",
    "research/strategies/v30_candidate_d1_energy_exit.py",
    "research/strategies/v30_candidate_d2_cash_cushion.py",
    "research/strategies/v30_candidate_d3_recovery_discipline.py",
    "research/strategies/v30_candidate_p1_inverse_vol.py",
    "research/strategies/v30_candidate_p2_capped_inverse_vol.py",
    "research/strategies/v30_candidate_p3_smoothed_inverse_vol.py",
    "research/strategies/v30_candidate_p4_blend_equal_inverse.py",
    "research/strategies/v30_execution_safe_agent.py",
    "research/strategies/v30_execution_safe_agent_final.py",
    "research/strategies/v30_execution_safe_agent_r.py",
    "research/tests/test_v30_execution_safety.py",
    "research/tests/test_v30_stage2a_bg_contract_and_robustness.py",
    "research/tests/test_v30_stage2a_f_final_acceptance.py",
    "research/tests/test_v30_stage2a_r_remediation.py",
    "research/tests/test_v30_stage2b_defensive_research.py",
    "research/tests/test_v30_stage2c_volatility_gating.py",
    "research/tests/test_v30_stage2d_position_sizing.py",
    "research/tests/test_v30_stage2d_r_overlay_and_oracle.py",
    "research/tests/test_v30_stage2f_mathematical_verification.py",
    "research/tests/test_v30_stage2g_forward_readiness.py",
    "research/tests/test_v30_stage2g_r_remediation.py",
    "research/tests/test_v30_stage2h_a_adversarial.py",
    "research/tests/test_v30_stage2h_b_governance.py",
    "research/tests/test_v30_stage2h_c_r2_execution_proof.py",
    "research/tests/test_v30_stage2h_c_r_manifest_validation.py",

)

if ($approvedFiles.Count -ne 198) {
    throw "PRE-FLIGHT FAILURE: Approved file list count ($($approvedFiles.Count)) does not equal 198."
}

foreach ($relPath in $approvedFiles) {
    if ($relPath -match "\.\.") {
        throw "SECURITY VIOLATION: Path traversal detected in '$relPath'."
    }
    if ($relPath -match "^([a-zA-Z]:|/|\\)") {
        throw "SECURITY VIOLATION: Absolute path detected in '$relPath'. Only repository-relative paths allowed."
    }
    if ($relPath -match "(tiingo_cache|private_agents|\.token|\.secret)") {
        throw "SECURITY VIOLATION: Restricted path detected in approved list: '$relPath'."
    }
    if (-not (Test-Path -LiteralPath $relPath)) {
        throw "PRE-FLIGHT FAILURE: Approved file missing on disk: '$relPath'."
    }
}
Write-Host " [PASS] All 198 approved files exist on disk with zero path traversal and zero restricted paths."

# --- STEP 1: CREATE AND SWITCH TO ARCHIVAL BRANCH ---
Write-Host "`n[STEP 1/10] Creating and checking out archival branch 'archive/v30-stage2h-final-evidence-freeze'..."
git checkout -b archive/v30-stage2h-final-evidence-freeze

# --- STEP 2/10: STAGE BATCH1_ROOT_REPORTS (39 FILES) ---
Write-Host "`n[STEP 2/10] Staging Batch 1: Root Markdown Research Reports (39 files)..."
$batch1_root_reports = @(
    "GUARDIAN_ALPHA_V29E_EXECUTED_TEST_REPORT.md",
    "GUARDIAN_ALPHA_V29E_FINAL_GATE_REPORT.md",
    "GUARDIAN_ALPHA_V29E_N_NOISE_INVENTORY.md",
    "GUARDIAN_ALPHA_V29E_N_NOISE_REDUCTION_PROPOSAL.md",
    "GUARDIAN_ALPHA_V29E_N_PUBLIC_SNAPSHOT_MINIMIZATION.md",
    "GUARDIAN_ALPHA_V29E_REFERENCE_AND_PAYLOAD_AUDIT.md",
    "GUARDIAN_ALPHA_V29E_R_DATA_RIGHTS_ASSESSMENT.md",
    "GUARDIAN_ALPHA_V29E_R_DEPENDENCY_REMEDIATION.md",
    "GUARDIAN_ALPHA_V29E_R_FINAL_GATE.md",
    "GUARDIAN_ALPHA_V29E_R_PUBLIC_HISTORY_RISK_REVIEW.md",
    "GUARDIAN_ALPHA_V29E_R_RELEASE_DOCUMENTATION_REVIEW.md",
    "GUARDIAN_ALPHA_V29E_SECURITY_AND_ANCESTRY_AUDIT.md",
    "GUARDIAN_ALPHA_V29E_S_SNAPSHOT_RECOVERY_AND_NOISE_CONTROL.md",
    "GUARDIAN_ALPHA_V29F_EVIDENCE_PRESERVATION.md",
    "GUARDIAN_ALPHA_V29F_FINAL_DECISION.md",
    "GUARDIAN_ALPHA_V29F_INDEPENDENT_ROOT_DESIGN.md",
    "GUARDIAN_ALPHA_V29F_RIGHTS_RESOLUTION.md",
    "GUARDIAN_ALPHA_V29F_SYNTHETIC_FEASIBILITY.md",
    "GUARDIAN_ALPHA_V29G_A_PRIVATE_ARCHIVAL_CONTINUATION.md",
    "GUARDIAN_ALPHA_V29G_A_PRIVATE_ARCHIVAL_VERIFICATION.md",
    "GUARDIAN_ALPHA_V30_STAGE1_DIAGNOSTIC.md",
    "GUARDIAN_ALPHA_V30_STAGE2A_BG_CONTRACT_AND_GENERALIZATION.md",
    "GUARDIAN_ALPHA_V30_STAGE2A_EXECUTION_SAFETY.md",
    "GUARDIAN_ALPHA_V30_STAGE2A_F_FINAL_ACCEPTANCE.md",
    "GUARDIAN_ALPHA_V30_STAGE2A_R_INDEPENDENT_REMEDIATION.md",
    "GUARDIAN_ALPHA_V30_STAGE2B_DEFENSIVE_ALLOCATION_RESEARCH.md",
    "GUARDIAN_ALPHA_V30_STAGE2B_R_BASELINE_RECONCILIATION.md",
    "GUARDIAN_ALPHA_V30_STAGE2C_VOLATILITY_GATING_RESEARCH.md",
    "GUARDIAN_ALPHA_V30_STAGE2D_POSITION_SIZING_RESEARCH.md",
    "GUARDIAN_ALPHA_V30_STAGE2D_R_OVERLAY_AND_ORACLE_AUDIT.md",
    "GUARDIAN_ALPHA_V30_STAGE2E_CROSS_STAGE_EVIDENCE_AND_RISK_BUDGET.md",
    "GUARDIAN_ALPHA_V30_STAGE2F_FINAL_CORRECTIONS_AND_FORWARD_PROTOCOL.md",
    "GUARDIAN_ALPHA_V30_STAGE2G_FORWARD_READINESS_CERTIFICATION.md",
    "GUARDIAN_ALPHA_V30_STAGE2G_R_FINAL_CORRECTIONS.md",
    "GUARDIAN_ALPHA_V30_STAGE2H_A_EXTENDED_READINESS_AND_OWNER_APPROVAL.md",
    "GUARDIAN_ALPHA_V30_STAGE2H_B_FINAL_GOVERNANCE_CORRECTIONS.md",
    "GUARDIAN_ALPHA_V30_STAGE2H_C_FINAL_FREEZE_AND_OWNER_HANDOVER.md",
    "GUARDIAN_ALPHA_V30_STAGE2H_C_R2_ARCHIVE_EXECUTION_PROOF.md",
    "GUARDIAN_ALPHA_V30_STAGE2H_C_R_LOSSLESS_ARCHIVE_RECONCILIATION.md",
)
git add $batch1_root_reports

# --- STEP 3/10: STAGE BATCH2_STRATEGIES (14 FILES) ---
Write-Host "`n[STEP 3/10] Staging Batch 2: Research Strategy Candidate Implementations (14 files)..."
$batch2_strategies = @(
    "research/strategies/v30_candidate_c1_tight_vol_gate.py",
    "research/strategies/v30_candidate_c2_vol_acceleration.py",
    "research/strategies/v30_candidate_c3_vol_persistence.py",
    "research/strategies/v30_candidate_c4_combined_gates.py",
    "research/strategies/v30_candidate_d1_energy_exit.py",
    "research/strategies/v30_candidate_d2_cash_cushion.py",
    "research/strategies/v30_candidate_d3_recovery_discipline.py",
    "research/strategies/v30_candidate_p1_inverse_vol.py",
    "research/strategies/v30_candidate_p2_capped_inverse_vol.py",
    "research/strategies/v30_candidate_p3_smoothed_inverse_vol.py",
    "research/strategies/v30_candidate_p4_blend_equal_inverse.py",
    "research/strategies/v30_execution_safe_agent.py",
    "research/strategies/v30_execution_safe_agent_final.py",
    "research/strategies/v30_execution_safe_agent_r.py",
)
git add $batch2_strategies

# --- STEP 4/10: STAGE BATCH3_ENGINE_ORACLES (24 FILES) ---
Write-Host "`n[STEP 4/10] Staging Batch 3: Research Engine Modules & Accounting Oracles (24 files)..."
$batch3_engine_oracles = @(
    "research/engine/cash_affordability_model.py",
    "research/engine/v30_broker_accounting_final.py",
    "research/engine/v30_broker_accounting_r.py",
    "research/engine/v30_independent_accounting_oracle.py",
    "research/engine/v30_overlay_auditor.py",
    "research/engine/v30_sizing_oracle.py",
    "research/engine/v30_sizing_oracle_decimal.py",
    "research/engine/v30_stage2g_r_accounting_verifier.py",
    "research/engine/v30_stage2g_r_activation_guard.py",
    "research/engine/v30_stage2g_r_causal_event_engine.py",
    "research/engine/v30_stage2g_r_crash_tester.py",
    "research/engine/v30_stage2g_synthetic_dry_runner.py",
    "research/engine/v30_stage2h_a_accounting_assurance_runner.py",
    "research/engine/v30_stage2h_a_audit_runner.py",
    "research/engine/v30_stage2h_a_crash_tester.py",
    "research/engine/v30_stage2h_a_dashboard_mockup.html",
    "research/engine/v30_stage2h_a_hardened_causal_engine.py",
    "research/engine/v30_stage2h_a_security_auditor.py",
    "research/engine/v30_stage2h_b_dashboard_mockup.html",
    "research/engine/v30_stage2h_b_decimal_accounting_oracle.py",
    "research/engine/v30_stage2h_b_security_guard.py",
    "research/engine/v30_synthetic_stress_scenarios.py",
    "research/engine/v30_synthetic_stress_scenarios_stage2c.py",
    "research/engine/v30_synthetic_stress_scenarios_stage2d.py",
)
git add $batch3_engine_oracles

# --- STEP 5/10: STAGE BATCH4_TEST_SUITES (15 FILES) ---
Write-Host "`n[STEP 5/10] Staging Batch 4: Research Automated Test Suites (15 files)..."
$batch4_test_suites = @(
    "research/tests/test_v30_execution_safety.py",
    "research/tests/test_v30_stage2a_bg_contract_and_robustness.py",
    "research/tests/test_v30_stage2a_f_final_acceptance.py",
    "research/tests/test_v30_stage2a_r_remediation.py",
    "research/tests/test_v30_stage2b_defensive_research.py",
    "research/tests/test_v30_stage2c_volatility_gating.py",
    "research/tests/test_v30_stage2d_position_sizing.py",
    "research/tests/test_v30_stage2d_r_overlay_and_oracle.py",
    "research/tests/test_v30_stage2f_mathematical_verification.py",
    "research/tests/test_v30_stage2g_forward_readiness.py",
    "research/tests/test_v30_stage2g_r_remediation.py",
    "research/tests/test_v30_stage2h_a_adversarial.py",
    "research/tests/test_v30_stage2h_b_governance.py",
    "research/tests/test_v30_stage2h_c_r2_execution_proof.py",
    "research/tests/test_v30_stage2h_c_r_manifest_validation.py",
)
git add $batch4_test_suites

# --- STEP 6/10: STAGE BATCH5_EVIDENCE_LEDGERS (105 FILES) ---
Write-Host "`n[STEP 6/10] Staging Batch 5: Research Evidence JSON Ledgers & Logs (105 files)..."
$batch5_evidence_ledgers = @(
    "research/evidence/v29b/test_suite_400_classified_inventory.json",
    "research/evidence/v30/logs/partial_recovery_test.jsonl",
    "research/evidence/v30/logs/stage2g_r_crash_test_journal.jsonl",
    "research/evidence/v30/logs/stage2g_r_partial_journal.jsonl",
    "research/evidence/v30/logs/stage2h_a_recovery_journal.jsonl",
    "research/evidence/v30/v30_stage2c_historical_replay_results.json",
    "research/evidence/v30/v30_stage2c_preregistration_spec.json",
    "research/evidence/v30/v30_stage2d_historical_replay_results.json",
    "research/evidence/v30/v30_stage2d_preregistration_spec.json",
    "research/evidence/v30/v30_stage2d_r_overlay_audit.json",
    "research/evidence/v30/v30_stage2e_candidate_comparability_matrix.json",
    "research/evidence/v30/v30_stage2e_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2e_final_research_decision_register.json",
    "research/evidence/v30/v30_stage2e_master_evidence_inventory.json",
    "research/evidence/v30/v30_stage2e_risk_budget_decomposition.json",
    "research/evidence/v30/v30_stage2e_validation_contamination_register.json",
    "research/evidence/v30/v30_stage2f_artifact_hash_manifest.json",
    "research/evidence/v30/v30_stage2f_disputed_claim_correction_register.json",
    "research/evidence/v30/v30_stage2f_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2f_exposure_and_leverage_reconciliation.json",
    "research/evidence/v30/v30_stage2f_forward_paper_evaluation_protocol.json",
    "research/evidence/v30/v30_stage2f_independent_risk_contribution_verification.json",
    "research/evidence/v30/v30_stage2f_p4_drawdown_reconciliation.json",
    "research/evidence/v30/v30_stage2f_statistical_selection_bias_recalculation.json",
    "research/evidence/v30/v30_stage2f_updated_scientific_decision_implications.json",
    "research/evidence/v30/v30_stage2g_artifact_checksum_manifest.json",
    "research/evidence/v30/v30_stage2g_event_immutability_and_recovery_evidence.json",
    "research/evidence/v30/v30_stage2g_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2g_financial_accounting_verification.json",
    "research/evidence/v30/v30_stage2g_frozen_comparison_manifest.json",
    "research/evidence/v30/v30_stage2g_future_data_governance_checklist.json",
    "research/evidence/v30/v30_stage2g_r_activation_security_review.json",
    "research/evidence/v30/v30_stage2g_r_artifact_checksum_manifest.json",
    "research/evidence/v30/v30_stage2g_r_causal_event_specification.json",
    "research/evidence/v30/v30_stage2g_r_crash_recovery_evidence.json",
    "research/evidence/v30/v30_stage2g_r_defect_inventory.json",
    "research/evidence/v30/v30_stage2g_r_event_state_verification.json",
    "research/evidence/v30/v30_stage2g_r_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2g_r_financial_accounting_check.json",
    "research/evidence/v30/v30_stage2g_r_owner_authorization_checklist.json",
    "research/evidence/v30/v30_stage2g_r_provider_neutral_data_rights.json",
    "research/evidence/v30/v30_stage2g_r_revised_statistical_protocol.json",
    "research/evidence/v30/v30_stage2g_r_simulator_contract_parity_matrix.json",
    "research/evidence/v30/v30_stage2g_scientific_evaluation_preregistration.json",
    "research/evidence/v30/v30_stage2g_security_and_activation_boundary_audit.json",
    "research/evidence/v30/v30_stage2g_simulator_contract_compatibility_matrix.json",
    "research/evidence/v30/v30_stage2g_synthetic_dry_run_manifest.json",
    "research/evidence/v30/v30_stage2g_synthetic_scenario_specification.json",
    "research/evidence/v30/v30_stage2h_a_activation_security_audit.json",
    "research/evidence/v30/v30_stage2h_a_artifact_checksum_manifest.json",
    "research/evidence/v30/v30_stage2h_a_causal_event_hardening_audit.json",
    "research/evidence/v30/v30_stage2h_a_checkpoint_certification.json",
    "research/evidence/v30/v30_stage2h_a_crash_recovery_reliability.json",
    "research/evidence/v30/v30_stage2h_a_data_provenance_schema.json",
    "research/evidence/v30/v30_stage2h_a_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2h_a_financial_accounting_assurance.json",
    "research/evidence/v30/v30_stage2h_a_observability_and_incident_playbook.json",
    "research/evidence/v30/v30_stage2h_a_owner_decision_package.json",
    "research/evidence/v30/v30_stage2h_a_provider_due_diligence_matrix.json",
    "research/evidence/v30/v30_stage2h_a_red_team_register.json",
    "research/evidence/v30/v30_stage2h_a_scientific_protocol_review.json",
    "research/evidence/v30/v30_stage2h_a_simulator_contract_conformance.json",
    "research/evidence/v30/v30_stage2h_b_accounting_oracle_verification.json",
    "research/evidence/v30/v30_stage2h_b_adversarial_review.json",
    "research/evidence/v30/v30_stage2h_b_artifact_checksum_manifest.json",
    "research/evidence/v30/v30_stage2h_b_baseline_evidence_inventory.json",
    "research/evidence/v30/v30_stage2h_b_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2h_b_incident_controls_specification.json",
    "research/evidence/v30/v30_stage2h_b_owner_decision_package.json",
    "research/evidence/v30/v30_stage2h_b_provider_rights_matrix.json",
    "research/evidence/v30/v30_stage2h_b_security_red_team_findings.json",
    "research/evidence/v30/v30_stage2h_b_simulator_parity_assessment.json",
    "research/evidence/v30/v30_stage2h_b_statistical_protocol_audit.json",
    "research/evidence/v30/v30_stage2h_c_artifact_checksum_manifest.json",
    "research/evidence/v30/v30_stage2h_c_complete_workspace_inventory.json",
    "research/evidence/v30/v30_stage2h_c_cross_stage_consistency_register.json",
    "research/evidence/v30/v30_stage2h_c_final_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2h_c_governance_and_incident_checklist.json",
    "research/evidence/v30/v30_stage2h_c_human_git_preservation_plan.json",
    "research/evidence/v30/v30_stage2h_c_owner_decision_register.json",
    "research/evidence/v30/v30_stage2h_c_private_backup_specification.json",
    "research/evidence/v30/v30_stage2h_c_protected_source_certification.json",
    "research/evidence/v30/v30_stage2h_c_provider_decision_matrix.json",
    "research/evidence/v30/v30_stage2h_c_r2_artifact_checksum_manifest.json",
    "research/evidence/v30/v30_stage2h_c_r2_corrected_inventory.json",
    "research/evidence/v30/v30_stage2h_c_r2_corrected_staging_manifest.json",
    "research/evidence/v30/v30_stage2h_c_r2_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2h_c_r2_explicit_disposition_ledger.json",
    "research/evidence/v30/v30_stage2h_c_r2_human_powershell_instructions.json",
    "research/evidence/v30/v30_stage2h_c_r2_manifest_completeness_proof.json",
    "research/evidence/v30/v30_stage2h_c_r2_private_backup_reconciliation.json",
    "research/evidence/v30/v30_stage2h_c_r_artifact_checksum_manifest.json",
    "research/evidence/v30/v30_stage2h_c_r_artifact_disposition_ledger.json",
    "research/evidence/v30/v30_stage2h_c_r_chain_of_custody_matrix.json",
    "research/evidence/v30/v30_stage2h_c_r_executed_test_ledger.json",
    "research/evidence/v30/v30_stage2h_c_r_fresh_workspace_inventory.json",
    "research/evidence/v30/v30_stage2h_c_r_frozen_source_verification.json",
    "research/evidence/v30/v30_stage2h_c_r_human_powershell_instructions.json",
    "research/evidence/v30/v30_stage2h_c_r_inventory_comparison.json",
    "research/evidence/v30/v30_stage2h_c_r_omitted_artifact_register.json",
    "research/evidence/v30/v30_stage2h_c_r_private_backup_manifest.json",
    "research/evidence/v30/v30_stage2h_c_r_proposed_git_staging_manifest.json",
    "research/evidence/v30/v30_stage2h_c_r_reproducibility_completeness.json",
    "research/evidence/v30/v30_stage2h_c_reproducibility_dependency_manifest.json",
    "research/evidence/v30/v30_stage2h_c_scientific_evaluation_proposal.json",
)
git add $batch5_evidence_ledgers

# --- STEP 7/10: STAGE BATCH6_ARCHIVAL_SCRIPTS (1 FILES) ---
Write-Host "`n[STEP 7/10] Staging Batch 6: Human Archival Tooling Scripts (1 files)..."
$batch6_archival_scripts = @(
    "research/scripts/v30_stage2h_c_r2_human_archival_script.ps1",
)
git add $batch6_archival_scripts

# --- STEP 8: POST-STAGING AUDIT & BOUNDARY GUARD ---
Write-Host "`n[STEP 8/10] Verifying staging integrity and restricted boundary safety..."
$stagedFiles = @(git diff --cached --name-only)
$stagedCount = $stagedFiles.Count
if ($stagedCount -ne 198) {
    throw "STAGING INTEGRITY FAILURE: Expected exactly 198 staged files, but found $stagedCount staged."
}

$restrictedStaged = $stagedFiles | Where-Object { $_ -match "tiingo_cache" }
if ($restrictedStaged) {
    throw "CRITICAL SECURITY VIOLATION: Restricted holdout data 'tiingo_cache' was staged! Run 'git reset' immediately."
}
Write-Host " [PASS] Staging integrity confirmed: Exactly 198 files staged, 0 restricted files staged."

# --- STEP 9: COMMIT ARCHIVAL FREEZE ---
Write-Host "`n[STEP 9/10] Creating permanent archival freeze commit..."
$commitMsg = "chore(v30-freeze): owner lossless archival freeze of complete V29E-V30 research evidence [198 artifacts]"
git commit -m $commitMsg

# --- STEP 10: VERIFY COMMIT HISTORY & STATUS ---
Write-Host "`n[STEP 10/10] Verifying committed state..."
git log -1 --stat
git status

Write-Host "`n=================================================================="
Write-Host " ARCHIVAL PRESERVATION COMPLETE!                                  "
Write-Host " Base HEAD b283ded... preserved without modification.             "
Write-Host " Archival branch 'archive/v30-stage2h-final-evidence-freeze' created. "
Write-Host " ZERO REMOTE PUSH EXECUTED.                                       "
Write-Host "=================================================================="
