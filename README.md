# Daily Quote Scheduler

Emails one quote, one practical chess lesson, and one philosophical reading each day at 05:00 AWST (21:00 UTC the previous day), using GitHub Actions.

## Content

- 530 quotes in `stoic_quotes.json`.
- 47 chess lessons and 120 readings in `Quotes.py`.
- The latest additions are 100 verified quotations from real authors, 20 chess lessons built from first principles, and 20 AI-written reflective essays of similar length to the existing readings. Those essays are labelled **Original reflection**, rather than attributed to historical authors. The 100 AI-written aphorisms originally added have been replaced.
- Each of the 100 replacement quotes includes its source work, a link to the published text, and the translator where identified. The source also appears below the quote in the email. See [quotation sources](QUOTE_SOURCES.md). The original 430 quotes have not undergone a full attribution audit.
- News sources and the expired World Cup feed have been removed. Previous versions remain available in Git history.

## Running

Use Python 3.12 or later and set `EMAIL_SENDER`, `EMAIL_PASSWORD`, and `EMAIL_RECEIVER` in the environment. Run `python Quotes.py` from the repository directory. The script sends a real email through Gmail SMTP; the same values must be configured as GitHub Actions secrets for scheduled runs. There are no third-party Python dependencies.

## Rotation

Each category has its own least-recently-shown rotation. Unseen items are chosen in random order first; after every distinct item has appeared, the oldest shown item comes next. This guarantees coverage instead of merely making recent repeats less likely. Identical text with different punctuation, spacing or capitalisation shares one slot. Similar ideas with different wording remain separate items.

History is stored in `rotation_state.json`, using content identifiers so reordering the lists does not reset progress. New items get priority, removed items stop being selected, and remaining items retain their history. Existing `weight` and `last_sent` fields in the quote collection are legacy data and are no longer used.

The first run starts a fresh rotation because earlier scheduled runs did not retain their history. History advances only after the SMTP server accepts the email. Missing credentials or rejected sends fail the run without saving selections. SMTP acceptance cannot guarantee inbox delivery.

GitHub Actions commits the history back to `main` after each successful send, using its built-in token with `contents: write` permission. Runs are serialised to avoid overlapping history updates. Repository rules must allow the workflow to commit to `main`; a failed history push is reported as a failed run and must be resolved to preserve rotation. See [GitHub's token documentation](https://docs.github.com/en/actions/concepts/security/github_token). Local runs retain their own history; pull the current history first if using the same delivery stream, and do not run a separate sender concurrently.

Run the offline checks with `python -m unittest discover -s tests -v`. They simulate multiple complete rotations and email failures without sending real emails.
