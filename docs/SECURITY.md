# Security

## Supported boundary

The verified release is a local, single-founder deployment on a trusted
workstation. It is not approved for direct public-internet exposure.

## Implemented controls

- Signed, expiring session cookie: HttpOnly, SameSite=Lax, and Secure in production.
- Constant-time credential and Telegram secret comparisons.
- Per-client in-memory login attempt window with `429` and `Retry-After`.
- Production startup rejects default credentials, default session secret, and
  insecure cookies.
- Explicit CORS origins with credentials; no wildcard origin.
- CSP, `frame-ancestors`, `X-Frame-Options`, `nosniff`, referrer policy, and
  restrictive permissions policy.
- API responses are `no-store` and receive a request ID.
- Secrets stay in ignored `.env` or a deployment secret manager; browser
  variables contain only the API base URL.
- Uploaded names are normalized; bytes have a hard limit, atomic storage, SHA-256,
  deduplication, and explicit rights status.
- Vault restore rejects absolute paths, parent traversal, symlinks, hard links,
  and any target outside the configured vault/storage roots.
- Telegram requires an enabled adapter, webhook secret, sender allowlist, and
  update idempotency.
- Public actions, canonical writes, and high-risk transitions are backend-gated.

Run the local gate:

```powershell
.\scripts\security-check.ps1
```

It rejects a tracked `.env`, scans tracked runtime files for common token/private
key forms without printing secret values, fails critical production dependency
advisories, and runs Git whitespace validation.

## Active release blockers

- `R-012`: the current latest stable Next.js dependency tree reports three high
  advisories and no critical advisories. npm's proposed Next 9 downgrade is not
  an acceptable fix.
- `R-015`: local single-user auth is not a production identity perimeter. A
  remote release also needs TLS termination, production secret storage, an
  external backup destination, monitoring, and a reviewed identity/access design.

## Residual local risks

- Offline ideas are unencrypted in this browser origin's local storage. Do not
  capture credentials or restricted personal data in an offline idea.
- Login limiting is process-local and intended as local hardening, not distributed
  edge protection.
- CSP permits inline scripts/styles required by the current Next.js runtime.
- Optional provider paths remain unverified until project-scoped credentials and
  model aliases are configured.

Any suspected secret exposure requires credential rotation, Git history review,
and a new backup after remediation.
