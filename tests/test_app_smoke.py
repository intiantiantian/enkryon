from importlib import import_module


def test_application_module_imports_ui_dependencies():
    application = import_module("main")

    imported_screen_names = {
        application.DashboardScreen.__name__,
        application.AddTransactionScreen.__name__,
        application.SettingsScreen.__name__,
        application.AccountsScreen.__name__,
        application.CategoriesScreen.__name__,
        application.TransactionsScreen.__name__,
    }

    assert imported_screen_names == {
        "DashboardScreen",
        "AddTransactionScreen",
        "SettingsScreen",
        "AccountsScreen",
        "CategoriesScreen",
        "TransactionsScreen",
    }
    assert callable(application.EnkryonApp.build)
