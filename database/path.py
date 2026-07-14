from pathlib import Path

from kivy.app import App

DATABASE_FILENAME = "database.db"
LOCAL_DATABASE_PATH = Path("database") / DATABASE_FILENAME

def get_database_path():
    app = App.get_running_app()

    if app is None:
        return str(LOCAL_DATABASE_PATH)

    return str(Path(app.user_data_dir) / DATABASE_FILENAME)