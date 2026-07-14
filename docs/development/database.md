# Database Notes

Enkryon uses SQLite for local persistence.

## Runtime database path

The app uses `database/path.py` to determine where the SQLite database should be stored.

When no Kivy app instance is running, the fallback path is:

```text
database/database.db