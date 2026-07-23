# Telegram Adapter

Last verified: 2026-07-23

## Live boundary

The webhook is implemented but disabled by default. Live use requires all of:

- `TELEGRAM_ENABLED=true`;
- a server-only `TELEGRAM_WEBHOOK_SECRET`;
- a dedicated `TELEGRAM_BOT_TOKEN`;
- at least one numeric `TELEGRAM_ALLOWED_USER_IDS` entry.

The webhook verifies the `X-Telegram-Bot-Api-Secret-Token` header with a
constant-time comparison and rejects non-allowlisted senders before any write.
Telegram update IDs are unique, making retries idempotent.

## Supported capture

- text and `/idea` create Ideas;
- voice updates are preserved as `pending_transcription` until a transcription
  provider is configured;
- signed voice fixtures with an supplied transcript create Ideas in tests;
- `/benchmark URL` creates an evidence-needed benchmark record;
- `/status` returns local record totals;
- `/approve` does not make a decision and directs the founder to the authenticated
  approval record.

The Daily Intelligence page includes a clearly labeled local fixture simulator.
Simulator messages are marked Demo and do not claim that a live Telegram bot sent
or received anything.
