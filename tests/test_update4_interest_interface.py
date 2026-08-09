from pathlib import Path


def read(relative_path):
    project_root = Path(__file__).resolve().parents[1]
    return (project_root / relative_path).read_text(encoding="utf-8")


def test_interest_overlay_exposes_locked_v14_inputs_and_disclosures():
    layout = read("kv/interest_dialog.kv")

    assert 'text: "Daily Bank Interest"' in layout
    assert 'hint_text: "APR (%)"' in layout
    assert 'helper_text: "Nominal APR; up to 6 decimal places"' in layout
    assert 'hint_text: "Effective date"' in layout
    assert 'helper_text: "YYYY-MM-DD; existing profile dates cannot be reused"' in layout
    assert 'root.day_count_text + " (fixed for v1.4.0)"' in layout
    assert 'text: "ESTIMATE ONLY · NON-POSTING"' in layout
    assert 'text: "TODAY\'S ESTIMATE"' in layout
    assert 'text: "UNPOSTED ACCRUED"' in layout
    assert 'text: "DISABLE"' in layout
    assert 'text: "SAVE"' in layout


def test_interest_overlay_is_scrollable_and_uses_touch_target_buttons():
    layout = read("kv/interest_dialog.kv")

    assert "ScrollView:" in layout
    assert "do_scroll_x: False" in layout
    assert "height: dp(48)" in layout
    assert "EnkryonSecondaryButton:" in layout
    assert "EnkryonPrimaryButton:" in layout


def test_account_card_has_text_interest_status_and_named_action():
    layout = read("kv/accounts.kv")
    card_source = read("widgets/account_card.py")

    assert "id: interest_summary" in layout
    assert "text: root.interest_summary_text" in layout
    assert 'text: "INTEREST"' in layout
    assert "on_release: root.manage_interest()" in layout
    assert 'StringProperty("Interest: Off")' in card_source


def test_app_loads_interest_overlay_definition():
    main_source = read("main.py")

    assert "Builder.load_file('kv/interest_dialog.kv')" in main_source


def test_interface_copy_keeps_estimates_non_posting():
    layout = " ".join(read("kv/interest_dialog.kv").split())
    contract = read("docs/development/daily-bank-interest.md")

    assert "Estimates do not change account balances or Income" in layout
    assert "explicitly reconcile a bank credit" in layout
    assert "effective-dated disabling" in contract
    assert "Android Back dismisses it" in " ".join(contract.split())
