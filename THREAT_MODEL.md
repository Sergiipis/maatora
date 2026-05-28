# Threat model

This document is the formal threat model for the `maatora` library. It is
intended for security reviewers, regulators, and integrators who need to
understand *precisely* what cryptographic properties the library
guarantees, what it does not, and how to deploy it without inheriting
silent assumptions.

It complements:

- `SECURITY.md` — how to report a concern, response SLAs, scope of
  vulnerability handling.
- `COMPLIANCE.md` — clause-by-clause mapping to EU AI Act Article 12,
  SOC 2 CC controls, HIPAA §164.312(b), GDPR Article 30.

If anything in this document contradicts the implementation, the
implementation is the source of truth. Please file a security advisory
under the process in `SECURITY.md` so we can correct the documentation.

## 1. Assets

Ordered from most to least sensitive:

1. **Ed25519 signing key (private)** — possession of this key is
   equivalent to authority to produce indistinguishable receipts. The
   library never stores or transmits it; the operator is responsible for
   its lifecycle.
2. **Receipts in transit and at rest** — the canonical record of what an
   AI agent did. Their integrity is the primary product of the library.
3. **The append-only Merkle log** — links receipts into a chain such
   that any retroactive insertion, deletion, or reordering is detectable.
4. **Public keys distributed to verifiers** — must reach the verifier
   intact; substitution would let an attacker forge receipts.
5. **The audit trail completeness property** — that *every* qualifying
   action produced a receipt. This is a deployment-time property; the
   library can only make it cheap to enforce, not enforce it itself.

## 2. Trust boundaries

```
+--------------------+   sign    +---------------+   verify   +-------------+
|  Agent process     | --------> |  Receipt      | ---------> |  External   |
|  (holds priv key)  |           |  store / log  |            |  verifier   |
+--------------------+           +---------------+            +-------------+
        |                              ^                            ^
        v                              |                            |
   key file / HSM              ingest API (FastAPI)            public key
                                                              (out of band)
```

Boundaries crossed:

- **Agent → store**: trust is transferred from "process memory" to
  "persistent storage." A receipt that leaves the agent signed remains
  verifiable thereafter; storage need not be trusted.
- **Store → verifier**: trust is transferred from "your operator" to
  "anyone with the public key." This is the differentiator vs.
  tamper-resistant SaaS logs.
- **Operator → verifier (key distribution)**: trust must be established
  out of band — TLS-pinned download, key fingerprint published in a
  signed announcement, manual exchange, etc. The library does not
  prescribe a method.

## 3. Adversary model

We consider three adversary classes, in order of expected likelihood:

### 3.1 External adversary (network)

- **Capabilities**: can read traffic, can submit arbitrary payloads to
  the FastAPI ingest server (if exposed), cannot read the operator's
  private key.
- **Goals**: insert false receipts; tamper with receipts in transit;
  cause denial of service against ingest.
- **In scope**: the library must make tampering and forgery detectable
  by any verifier.

### 3.2 Internal adversary (post-incident insider)

- **Capabilities**: read/write access to the receipt store, no access
  to the signing key.
- **Goals**: retroactively edit, delete, or reorder receipts to hide
  agent misbehavior; substitute a "better-looking" history.
- **In scope**: every such modification must break verification, either
  per-receipt (signature) or per-chain (Merkle root).

### 3.3 Compromised operator (signing key holder)

- **Capabilities**: possession of the signing key.
- **Goals**: produce false receipts that verify against the published
  public key.
- **Out of scope** for the library. The library can prove that a receipt
  came from the holder of a specific key, not that the holder is
  honest. Detection of operator dishonesty requires external controls:
  cross-signature with a regulator's key, anchoring the Merkle root to a
  third-party log (e.g., a transparency log), or hardware-backed key
  attestation. Future versions may add helpers for these patterns.

## 4. Threats (STRIDE)

### Spoofing (S)

| # | Threat | Mitigation in library | Residual risk |
|---|--------|----------------------|---------------|
| S1 | Attacker claims a receipt was produced by Agent A when it was not | Ed25519 signature over canonical JSON of the receipt; verifier rejects on any signature mismatch | Key compromise (§3.3) is out of scope |
| S2 | Attacker substitutes the verifier's copy of the public key | None — key distribution is out of band | Operator must pin / publish key fingerprint; library docs say so explicitly |

### Tampering (T)

| # | Threat | Mitigation in library | Residual risk |
|---|--------|----------------------|---------------|
| T1 | Modify a receipt's `input_hash`, `output_hash`, `action`, `actor_id`, `timestamp`, `status`, or `error` field after signing | Canonical-JSON serialization (sorted keys, no whitespace) before signing; any single-bit change breaks the Ed25519 signature | None for fields covered by signature |
| T2 | Reorder, insert, or delete entries in the chain without re-signing every successor | Merkle log over SHA-256: each leaf hashed with the previous root produces a new root; retroactive change invalidates the root | None if verifier checks the published root |
| T3 | Modify the data that the receipt references (the *actual* tool input/output beyond its hash) | The library hashes the canonical input/output. If the caller hashed the wrong bytes, the hash is wrong | Caller responsibility — the `@receipt` decorator hashes the function's actual arguments and return value automatically |

### Repudiation (R)

| # | Threat | Mitigation in library | Residual risk |
|---|--------|----------------------|---------------|
| R1 | Operator denies producing a specific receipt | Receipt signed with operator's key; non-repudiation up to key compromise | Operator can still claim the key was stolen — that is a procedural, not cryptographic, question |
| R2 | Operator claims an action never happened (no receipt to find) | Out of scope — library cannot prove non-existence | Mitigated by chained Merkle root if periodically published to a third party; not enforced by library |

### Information disclosure (I)

| # | Threat | Mitigation in library | Residual risk |
|---|--------|----------------------|---------------|
| I1 | Sensitive payload leaks into receipt's `action`, `actor_id`, or `error` fields | These are operator-supplied strings — the library does not introspect them. Caller must not put secrets in `action` names or error messages | Library convention is to put payload hashes in receipts and the actual payloads in a separately-controlled store |
| I2 | Timing side channel during Ed25519 signing reveals key bits | `cryptography` package uses libsodium-style constant-time Ed25519 (libcrypto / pyca/cryptography backend) | Inherited from `cryptography>=42`; we track CVEs against that dep via Dependabot |
| I3 | Public key, alone, lets an attacker decrypt receipts | Receipts are *not encrypted* — signatures provide integrity, not confidentiality. Confidentiality is the caller's responsibility (transport TLS, at-rest encryption) | Documented |

### Denial of service (D)

| # | Threat | Mitigation in library | Residual risk |
|---|--------|----------------------|---------------|
| D1 | Flood the FastAPI ingest endpoint with garbage | None — the library does not implement rate limiting | Operator must place ingest behind a rate limiter / auth proxy. Documented in `SECURITY.md` scope |
| D2 | Submit pathological payloads to cause O(N²) Merkle reconstruction | Merkle reconstruction is O(N) in receipts and O(log N) in proof length; no pathological input known | Tracked; report as a security issue if found |

### Elevation of privilege (E)

| # | Threat | Mitigation in library | Residual risk |
|---|--------|----------------------|---------------|
| E1 | Code execution via deserialization of a malicious receipt | Receipts are parsed with Pydantic-validated models, not `pickle` or `eval`. JSON parsing path uses the standard library | Any future code path that ingests external receipts must continue to use validated parsers — covered by CI ruff + CodeQL scans |
| E2 | Path traversal via operator-supplied filenames in `cli_viewer` | CLI takes explicit `--file` arguments, no shell evaluation; opens files via `pathlib.Path` | Standard library guarantees |

## 5. Cryptographic primitives — choices and rationale

| Primitive | Choice | Reason | Alternatives considered |
|-----------|--------|--------|-------------------------|
| Digital signature | Ed25519 (RFC 8032) | Small keys (32 B), small signatures (64 B), deterministic, constant-time, no nonce reuse risk | ECDSA-P256 (nonce-reuse vector), RSA-PSS (10× larger artifacts), Dilithium (PQC, not yet stable for FIPS) |
| Hash | SHA-256 (FIPS 180-4) | Wide deployment, hardware acceleration, no known weaknesses for 256-bit security | BLAKE3 (faster, less audited in compliance contexts), SHA-3 (slower in pure software) |
| Canonical JSON | Custom canonicalization following RFC 8785 style (sorted keys, no whitespace, no exponent in numbers) | Determinism for signature replay; signed bytes must round-trip across reader implementations | JCS (RFC 8785) — close to what we do; we will align fully when the spec is stable across stdlib JSON encoders |

Forward-compatibility:

- All receipts include an algorithm identifier (currently implicit:
  `ed25519+sha256+canonical-json-v1`). When we migrate to a PQC
  signature scheme, old receipts will still verify with their original
  algorithm; new receipts will declare the new one.
- We do not pre-emptively add PQC signatures because every shipped PQC
  scheme is currently larger, slower, and more recently audited than
  Ed25519. We will revisit when NIST PQC standards stabilize and a
  well-audited Python implementation lands in `cryptography`.

## 6. Known limitations and non-goals

The library does **not** address, and is not intended to address:

1. **Honest-operator assumption**: see §3.3. The signature proves the
   holder of the key signed; the library makes no claim about the
   honesty of the holder.
2. **Real-time intrusion detection**: receipts are an after-the-fact
   forensic chain. They do not stop an agent from doing something bad;
   they make it expensive to hide it after the fact.
3. **End-to-end encryption**: receipts are not encrypted. If your
   action names or actor IDs are sensitive, encrypt at rest and in
   transit using standard mechanisms.
4. **Hardware key attestation**: not implemented in v0.1.0. Operators
   who want HSM-backed keys can wrap the signer themselves; a helper is
   on the roadmap.
5. **Anchoring to external transparency log**: not implemented in
   v0.1.0. Publishing Merkle roots to a third-party log (Sigstore /
   custom witness) is a recommended deployment pattern; a helper is on
   the roadmap.
6. **Authentication of the ingest endpoint**: the example FastAPI
   server is open by default. Production deployments must add an auth
   layer (mTLS, signed JWT, etc.) at the network edge.

## 7. Changes to this document

Changes to the threat model — particularly to the adversary model and
to the cryptographic choices — are themselves auditable events. They
will be recorded in `CHANGELOG.md` under the corresponding release and
explained in the release notes. The git history of this file is the
authoritative record.
