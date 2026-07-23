# Analytics and Experiments

Last verified: 2026-07-23

## Metrics

Metrics may be submitted individually through the API or imported as UTF-8 CSV.
The CSV importer:

- requires platform, views, impressions, engagement, saves, and shares;
- accepts optional capture time, content ID, and watch time;
- rejects negative or invalid rows without discarding valid rows;
- creates one durable MetricSnapshot per valid row;
- records an explicit raw observation for the imported batch.

Generated insights state that an isolated import does not establish causation.

## Experiments

Each experiment stores one primary variable, explicit control conditions, platform,
content type, expected outcome, success metric, measurement window, result,
interpretation, confidence, and decision. Failed tests remain in the ledger.

The current interface creates planned experiments. Public scheduling and strategy
promotion remain approval-gated.
