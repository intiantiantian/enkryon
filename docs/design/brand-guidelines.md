# Enkryon Brand Guidelines

## Purpose

Enkryon is a personal finance tracker designed to help users understand their money clearly, calmly, and confidently.

The visual identity should make the app feel:

* Trustworthy
* Organized
* Calm
* Premium but approachable
* Simple enough for daily use

Enkryon should not feel playful, noisy, overly casual, or visually cluttered.

## Brand Personality

Enkryon should feel like a calm financial companion.

The app should communicate:

* Stability
* Clarity
* Control
* Growth
* Discipline
* Confidence

The design should avoid unnecessary decoration. Visual choices should support readability, financial awareness, and user trust.

## Design Principles

### 1. Clarity first

Financial information should be easy to read at a glance.

Important values such as current balance, income, expenses, and transaction amounts should have clear hierarchy.

### 2. Calm over flashy

The app should avoid loud colors, excessive shadows, and distracting effects.

The design should feel focused and steady.

### 3. Premium but usable

The icon and splash screen suggest a premium emerald-and-gold identity. The in-app interface should match that direction without becoming too dark or heavy.

### 4. Consistency everywhere

Cards, buttons, dialogs, filters, empty states, and screen headers should follow the same spacing, color, typography, and shape rules.

### 5. Helpful empty states

Empty screens should guide the user toward the next useful action instead of looking broken or unfinished.

## Color Direction

Enkryon’s main visual identity should be based on:

* Deep emerald
* Soft emerald
* Warm gold
* Clean warm background
* Neutral text colors

## Role of Emerald

Emerald is the primary brand color.

Use emerald for:

* Main app identity
* Primary buttons
* Important headers
* Selected states
* Positive financial emphasis
* Strong surfaces when needed

Emerald should communicate trust, growth, and stability.

## Role of Gold

Gold is the accent color.

Use gold sparingly for:

* Highlights
* Premium accents
* Selected indicators
* Important but small visual emphasis
* Brand details

Gold should not dominate the interface. It should support emerald, not compete with it.

## Semantic Color Usage

Future design tokens should use semantic names instead of raw hex values.

Recommended semantic roles:

```text
BRAND_PRIMARY
BRAND_PRIMARY_DARK
BRAND_PRIMARY_LIGHT
BRAND_ACCENT
BACKGROUND
SURFACE
SURFACE_MUTED
TEXT_PRIMARY
TEXT_SECONDARY
TEXT_ON_PRIMARY
BORDER
SUCCESS
WARNING
ERROR
INCOME
EXPENSE
```

## Income and Expense Color Rules

Income and expense should be visually distinguishable but not overly bright.

Recommended direction:

* Income: emerald or positive green
* Expense: warm red, muted red, or clear negative tone

Expense colors should be noticeable but not alarming unless the action is destructive.

## Typography Direction

Typography should prioritize readability.

Recommended roles:

* Display amount
* Screen title
* Section title
* Card title
* Body text
* Supporting text
* Field label
* Button text

Large money values should be readable and visually stable.

## Spacing Direction

Spacing should be consistent across all screens.

Recommended spacing roles:

* Extra small
* Small
* Medium
* Large
* Extra large

Screens should avoid random padding values. Future layouts should use centralized spacing tokens.

## Shape Direction

Cards and buttons should use consistent radius values.

The app should avoid mixing sharp corners, heavily rounded corners, and inconsistent card shapes.

Recommended direction:

* Cards: medium radius
* Buttons: medium radius
* Dialogs: medium-to-large radius
* Small chips/filters: pill or rounded shape only if used consistently

## Component Direction

Future reusable components should include:

* EnkryonTopBar
* EnkryonCard
* EnkryonPrimaryButton
* EnkryonSecondaryButton
* EnkryonFilterButton
* EnkryonSectionTitle
* EnkryonEmptyState
* EnkryonDivider

## Visual Identity Rule

The launcher icon, splash screen, and in-app UI should feel like they belong to the same product.

If a color, component, or layout choice does not match the emerald-and-gold identity, it should be revised or replaced during the design-system migration.

## Phase 1.3 Design Rule

Do not redesign every screen at once.

The correct order is:

1. Define brand identity.
2. Review current assets.
3. Create design tokens.
4. Replace hardcoded colors gradually.
5. Create reusable components.
6. Apply the design system screen by screen.
