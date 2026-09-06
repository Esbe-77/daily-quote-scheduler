# Daily Quote Scheduler

Emails one quote, one practical chess lesson, and one philosophical reading each day at 05:00 AWST (21:00 UTC the previous day), using GitHub Actions.

## Content

- 530 quotes in `stoic_quotes.json`.
- 47 chess lessons and 120 readings in `Quotes.py`.
- The latest additions are 100 original philosophical aphorisms, 20 chess lessons built from first principles, and 20 original reflective essays of similar length to the existing readings. New philosophical content is labelled **Original reflection**, rather than attributed to historical authors.
- News sources and the expired World Cup feed have been removed. Previous versions remain available in Git history.

## Running

Use Python 3.12 or later and set `EMAIL_SENDER`, `EMAIL_PASSWORD`, and `EMAIL_RECEIVER` in the environment. Run `python Quotes.py` from the repository directory. The script sends a real email through Gmail SMTP; the same values must be configured as GitHub Actions secrets for scheduled runs. There are no third-party Python dependencies.

Selection uses a four-week recency weighting. Local runs save quote history in `stoic_quotes.json` and reading/chess history in `passages_state.json`. The current GitHub Actions workflow does not persist those updated files between runs, so scheduled runs do not retain that history.
