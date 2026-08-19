# Machine-auditable authorization

Record each action independently under `## Authorization matrix`. Never infer one permission from another.

## Required syntax

```text
- inspection: decision=allowed; approved_by=operator-alias; approved_at=2026-08-18T09:00:00+08:00; scope=all listed sites; expires_at=2026-09-18T09:00:00+08:00
- form filling: decision=ask; approved_by=not applicable; approved_at=not applicable; scope=not applicable; expires_at=not applicable
```

Allowed decisions are `allowed`, `ask`, and `prohibited`.

Every `allowed` entry requires a non-secret approver alias, an ISO 8601 approval time with timezone, `all listed sites` or a comma-separated platform-domain scope, and an ISO 8601 expiry with timezone or `no expiry`.

## Required actions

```text
inspection
form filling
account creation
native registration-email verification
terms/privacy acceptance
final form submission
email sending
article publication
claim ownership
payment/upgrade
reciprocal link/site modification
dns/html/domain verification
```

## Event enforcement

Record every executed action in the site's append-only `Attempt/Event log`. The auditor must find a valid authorization entry at that event's timestamp and for that platform domain. `ask` is not approval. A prior campaign instruction is valid only after it is represented as a scoped `allowed` entry.

Inspection permission does not authorize form filling. Form-filling permission does not authorize registration, agreements, submission, email, publication, claims, payment, or website changes.

Stop on ambiguous identities, unexpected OAuth scopes, Passkeys, security keys, recovery flows, 2FA, or any request that changes an existing credential. Never bypass or outsource a safeguard.
