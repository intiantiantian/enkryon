# Legacy Database Fixtures

`enkryon_v0_3_0.db` represents the database structure used before the
`v0.4.0` financial-correctness migrations.

The fixture intentionally:

- has no `schema_migrations` table;
- stores transaction values in the legacy `amount REAL` column;
- preserves non-sequential transaction IDs;
- includes income, expense, whole-centavo, and optional-note data;
- contains valid foreign-key relationships and names that can pass the
  newer validation rules.

## Stored Records

| Table | Expected records |
|---|---:|
| Accounts | 2 |
| Category groups | 2 |
| Categories | 2 |
| Transactions | 3 |

The transactions use IDs `7`, `11`, and `15`. After migration, their
expected integer values are `123456`, `1`, and `1020` centavos.

Expected migrated totals:

- Income: `123456` centavos
- Expenses: `1021` centavos
- Balance: `122435` centavos

The fixture must never be opened directly by a migration test. Each test
must copy it to a temporary directory before running migrations so the
committed historical file remains unchanged.

## v0.7.0 Database

`enkryon_v0_7_0.db` was generated from the official `v0.7.0` source
snapshot at commit `8ddc6e932217c5d850f0de96c6fe0f0b22f46480`.

The fixture records migrations 1–3 and intentionally has no transaction
history indexes. It contains two accounts, two category groups, two
categories, and three transactions with non-sequential IDs.

Expected totals:

- Income: `123456` centavos
- Expenses: `1021` centavos
- Balance: `122435` centavos

Fixture SHA-256:
`8d54bcefaa1c66d7ee07811e284a78bfe69d0984c16bcc9c5daabfce124de11f`
