# Enkryon Color Audit

## Purpose

This document records the current hardcoded color usage before migrating the UI to centralized design tokens.

The goal is to replace colors gradually and safely instead of redesigning every screen at once.

## Current Issue

The app still uses many hardcoded colors directly inside Python and KV files.

Most of the colors belong to the older pale-green UI direction. The new direction is to adapt the app UI to the existing icon and splash screen using a more premium emerald and gold identity.

## Search Command Used

```powershell
Select-String -Path .\screens\*.py, .\widgets\*.py, .\kv\*.kv -Pattern "#[0-9A-Fa-f]{6}"
```

## Main Hardcoded Colors Found

```text
#1B5E20 - old primary green, used for text, icons, headers, and widget accents
#D5F4BE - old selected state / light green button color
#B7E892 - old header/card green
#F8F7F4 - old app background
#D8D8D8 - old divider/border color
#CCF0B3 - old dashboard action card color
#9E9E9E - muted dashboard text
#757575 - muted widget text
#224B1F - older dark green
#388E3C - older action green
#A2D672 - older date/time picker green
#E8F5E9 - older selected date background
#FFFFFF - white surface / inactive button color
```

## Files With the Most Styling Work

```text
kv/dashboard.kv
kv/add_transaction.kv
kv/categories.kv
kv/widgets.kv
kv/date_time_pickers.kv
kv/transactions.kv
```

## Python Files With Active/Inactive Color Logic

```text
screens/add_transaction.py
screens/categories.py
screens/dashboard.py
screens/transactions.py
```

These files mainly use hardcoded colors for selected and unselected buttons.

## Migration Order

Colors should be migrated gradually in this order:

1. Shared widgets
2. Date/time picker and input dialogs
3. Filter buttons
4. Dashboard
5. Add Transaction
6. Transactions
7. Accounts
8. Categories
9. Settings

## Token Mapping Direction

Current hardcoded colors should eventually map to semantic design tokens.

```text
#1B5E20 -> Colors.BRAND_PRIMARY or Colors.TEXT_PRIMARY
#D5F4BE -> Colors.BRAND_PRIMARY_LIGHT or selected state token
#B7E892 -> Colors.SURFACE_MUTED or brand surface token
#F8F7F4 -> Colors.BACKGROUND
#D8D8D8 -> Colors.BORDER
#FFFFFF -> Colors.SURFACE
#9E9E9E -> Colors.TEXT_MUTED
#757575 -> Colors.TEXT_SECONDARY
```

## Migration Rule

Do not replace every hardcoded color in one commit.

Each commit should focus on one safe area.

Good examples:

```text
refactor: apply design tokens to shared widgets
refactor: apply design tokens to date time pickers
refactor: apply design tokens to transaction filters
refactor: apply design tokens to dashboard cards
```

Avoid:

```text
style: redesign all screens
```

## Next Action

Start with `kv/widgets.kv` because it contains shared UI components used across multiple screens.
