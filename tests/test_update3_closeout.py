from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_project_file(relative_path):
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_v1_3_release_identity_is_consistent():
    main_source = read_project_file("main.py")
    readme = read_project_file("README.md")
    changelog = read_project_file("CHANGELOG.md")
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.3.0-release-notes.md"
    )

    assert '__version__ = "1.3.0"' in main_source
    assert "Enkryon-v1.3.0.apk" in readme
    assert "## [1.3.0] - 2026-08-08" in changelog
    assert "# Enkryon v1.3.0" in release_notes
    assert "Release status: `RELEASED`" in release_notes
    assert "Release date: `2026-08-08`" in release_notes


def test_v1_3_user_copy_describes_balance_neutral_exchange():
    transfer_screen = read_project_file("screens/transfer.py")
    card = read_project_file("widgets/transaction_card.py")
    transfer_kv = read_project_file("kv/transfer.kv")
    contract = read_project_file(
        "docs/development/pass-through-transfers.md"
    )
    normalized_contract = " ".join(contract.split())

    assert "neither account balance changes" in transfer_screen
    assert "PAID FROM" in transfer_kv
    assert "RECEIVED INTO" in transfer_kv
    assert "paid from | " in card
    assert " received into" in card
    assert "source account balance change = 0" in normalized_contract
    assert "destination account balance change = 0" in normalized_contract


def test_v1_3_release_docs_lock_final_accounting_and_upgrade_gate():
    changelog = read_project_file("CHANGELOG.md")
    readme = read_project_file("README.md")
    roadmap = read_project_file("ROADMAP.md")
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.3.0-release-notes.md"
    )
    normalized_notes = " ".join(release_notes.split())

    assert "balance effect on every participating account" in changelog
    assert "without changing either participating account balance" in readme
    assert "Current release: `v1.3.0`" in roadmap
    assert "Next planned release: `v1.4.0`" in roadmap
    assert "Pass-through paid-from account change = 0" in release_notes
    assert "Pass-through received-into account change = 0" in release_notes
    assert "official `v1.2.0`" in normalized_notes
    assert "Migration 9 removes the temporary Pass-through movement" in normalized_notes
    assert "Backup format 4 preserves transfer kind and counterparty" in normalized_notes


def test_v1_3_release_evidence_records_final_artifact():
    verification = read_project_file(
        "docs/audits/update-3-pass-through-transfers-verification.md"
    )
    release_notes = read_project_file(
        "docs/releases/Enkryon-v1.3.0-release-notes.md"
    )

    assert "Released as v1.3.0" in verification
    assert "## Final v1.3.0 Release Evidence" in verification
    assert "830 passed in 23.65s" in verification
    assert "1a0867c45ab7922c0d304cbc47331e485319e2b6" in verification
    assert "Enkryon-v1.3.0.apk" in release_notes
    assert "45,776,720 bytes" in release_notes
    assert "EBEBFD56F1FFE55785E5C289D945F4C85BB8375FB81F0CF7A185142B904FBE78" in release_notes
    assert "E3:D2:9B:10:8A:69:4A:ED:75:87:FD:99:5F:00:B0:22:64:97:B5:66:A6:53:3A:E8:47:EF:23:71:A0:12:C4:3D" in release_notes
