# Risk Register

| ID | Risk | Probability | Impact | Mitigation | Current status |
|---|---|---:|---:|---|---|
| R-001 | MVP breadth produces disconnected placeholder screens | High | High | Deliver connected vertical slices and label deferred integration states honestly | Controlled across the local MVP |
| R-002 | Source documents conflict or silently drift | Medium | High | Preserve sources; inventory conflicts; version canonical records; decision log | Controlled |
| R-003 | Secrets enter Git, logs, model prompts, or vault | Medium | Critical | `.env` exclusion, server-only adapters, secret scanning, redacted integration status | Controlled locally by repeatable security gate |
| R-004 | Public or high-risk action bypasses UI-only approval | Medium | Critical | Central backend approval policy and negative tests | Controlled for implemented transitions |
| R-005 | Mock metrics or integration states are mistaken for live data | High | High | `is_demo` metadata, visible Demo badges, explicit provider state | Controlled for implemented screens |
| R-006 | Database and vault diverge | Medium | High | Version IDs, hashes, provenance, conflict records, reconciliation tests | Controlled; canonical conflicts preserve both copies |
| R-007 | Heartbeat duplicates runs or spends beyond budget | Medium | High | Date uniqueness, idempotency keys, source caps, zero-cost deterministic default | Controlled locally |
| R-008 | Creator benchmarking becomes copying | Medium | High | Evidence levels, protected-identity split, original adaptation templates, eight-word overlap test | Controlled for operator-supplied evidence |
| R-009 | Financial content implies advice or certainty | Medium | Critical | Risk classification, fact-check state, blocked claims, approval gate | Controlled for script workflow |
| R-010 | Windows/OneDrive file locking affects dev services | Medium | Medium | Keep runtime data in Docker volumes; avoid watching generated data trees | Controlled in current Compose run |
| R-011 | Python host is 3.11 while target is 3.12+ | High | Medium | 3.11-compatible code; Python 3.12 Docker image | Controlled |
| R-012 | Current stable Next.js dependency tree contains high-severity advisories | High | High | Keep Next.js current, monitor upstream, do not apply npm's unsafe Next 9 downgrade, and block public release until patched or explicitly mitigated | Active release blocker: 3 high, 0 critical |
| R-013 | Existing CreedAI changes are overwritten or coupled | Low | Critical | Read-only audit; contract adapter; separate vault; no writes to `C:\CreedAI` | Controlled |
| R-014 | Source files contain mojibake from prior export | High | Medium | Preserve originals; normalize only imported application text with provenance | Active |
| R-015 | Authentication is insufficient for remote exposure | Medium | Critical | Local-only default, strong password/session secrets, secure-cookie mode, deployment gate | Active release blocker for remote exposure |
| R-016 | Browser-local offline idea contains sensitive data | Low | High | Queue ideas only, disclose unencrypted local storage, never store credentials/API data, replay through normal validation | Controlled locally; restricted offline capture prohibited |
