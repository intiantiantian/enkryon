# Database Architecture

Enkryon uses SQLite for local persistence.

## Database location

When Enkryon is running, the database is stored as `database.db`
inside Kivy's `App.user_data_dir`.

On Windows, the current runtime location is:

```text
%APPDATA%\enkryon\database.db