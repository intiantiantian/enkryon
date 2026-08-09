from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def test_interest_settings_exposes_explicit_reconciliation_action():
    layout = read("kv/interest_dialog.kv")
    widget = read("widgets/interest_dialog.py")
    screen = read("screens/accounts.py")

    assert 'text: "RECONCILE BANK CREDIT"' in layout
    assert "on_release: root.reconcile()" in layout
    assert "reconcile_callback" in widget
    assert "open_interest_reconciliation" in screen


def test_reconciliation_dialog_collects_actual_credit_date_and_income_category():
    layout = " ".join(read("kv/interest_dialog.kv").split())
    widget = read("widgets/interest_dialog.py")
    screen = read("screens/accounts.py")

    assert "<InterestReconciliationDialog>:" in layout
    assert 'hint_text: "Actual credited amount (₱)"' in layout
    assert 'hint_text: "Credit date"' in layout
    assert 'text: "POST CREDIT"' in layout
    assert 'title="Select Income Category"' in screen
    assert 'get_categories_by_type("income")' in screen
    assert "category_id = ObjectProperty(None, allownone=True)" in widget


def test_reconciliation_copy_keeps_estimates_non_posting_and_shows_variance():
    layout = " ".join(read("kv/interest_dialog.kv").split())
    contract = " ".join(
        read("docs/development/daily-bank-interest.md").split()
    )

    assert "ESTIMATE VS ACTUAL" in layout
    assert "Variance:" in read("widgets/interest_dialog.py")
    assert "creates one normal posted Income transaction" in layout
    assert "The estimate itself never changes your balance" in layout
    assert "variance" in contract.lower()


def test_reconciliation_dialog_keeps_scroll_inset_and_outlined_cancel():
    layout = read("kv/interest_dialog.kv")

    assert 'padding: [dp(6), dp(4), dp(8), dp(24)]' in layout
    assert "MDRectangleFlatButton:" in layout
    assert 'text: "CANCEL"' in layout
