from pathlib import Path

from kivy.app import App


DATABASE_FILENAME = "database.db"
LOCAL_DATABASE_PATH = Path("database") / DATABASE_FILENAME


def get_database_path():
    app = App.get_running_app()

    if app is None:
        database_path = LOCAL_DATABASE_PATH
    else:
        database_path = Path(app.user_data_dir) / DATABASE_FILENAME

    database_path.parent.mkdir(parents=True, exist_ok=True)
    return str(database_path)