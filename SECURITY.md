# Security policy

Because `maatora` is used to produce records that downstream systems
rely on for compliance and forensics, we take reports about its integrity
seriously.

## Supported versions

While the project is pre-1.0, only the latest released version is
supported. Once we reach `1.0.0`, this section will be updated with a
table of supported minor releases.

| Version | Supported |
|---------|-----------|
| latest  | ✅        |
| older   | ❌        |

## How to report a concern

**Please do not open a public GitHub issue for matters that affect the
integrity of receipts, the signing process, or anything that could
mislead a downstream auditor.** Public discussion of such issues before
a fix is available creates needless risk for everyone using the library.

Preferred channel:

1. Open a private GitHub Security Advisory at
   `https://github.com/OWNER/REPO/security/advisories/new`.
   GitHub will keep the report private and let us coordinate a fix.

Backup channel:

2. If you cannot use GitHub advisories, contact the maintainer via the
   email listed on the maintainer's GitHub profile. Please include
   "maatora security" in the subject line.

When reporting, please include:

- The version of `maatora` and Python that you tested with.
- A minimal reproduction (a short script or sequence of commands) that
  demonstrates the issue.
- The impact you observed, in plain terms — what could a downstream
  reader of the receipts be misled about?
- Any suggested mitigation or fix, if you have one. (Optional — diagnosis
  alone is valuable.)

## What to expect

- Acknowledgment within **3 working days**.
- A first assessment within **10 working days**.
- A coordinated disclosure timeline of **up to 90 days** from the
  acknowledgment, by default. We will discuss adjustments with the
  reporter if the situation warrants.
- Credit in the release notes and a public advisory once a fix is
  released, unless you prefer to remain anonymous.

## Scope

In scope:

- The Python package `maatora` itself and its public API.
- The behavior of the `@receipt` decorator, the `ReceiptMiddleware`, the
  signing module, the Merkle log, and the FastAPI ingest server as
  shipped in this repository.
- The cryptographic claims made in `README.md` and `COMPLIANCE.md` — in
  particular, that a modified receipt fails verification.

Out of scope (please report to the relevant project instead):

- Dependencies of `maatora` (FastAPI, Pydantic, cryptography, jinja2,
  psycopg). Report those upstream; we will track and bump when fixes
  ship.
- The user's own operational setup — for example, leaking the Ed25519
  private key, storing receipts on a writable bucket, or running an
  unauthenticated ingest endpoint on the public internet. The library
  documents these as user responsibilities.
- Third-party agent frameworks (LangGraph, AutoGen, CrewAI) — they are
  separate projects.

## Security model — what `maatora` does and does not promise

`maatora` provides *tamper-evident* records: any modification to a
receipt or to the append-only chain is detectable by anyone holding the
signer's public key. The default mode produces SHA-256 hashes and
Ed25519 signatures.

`maatora` does **not** promise:

- That an operator with the private key cannot produce false records.
  The signer's process must be trusted; the library only proves that
  records came from a holder of the key and have not changed since.
- That the storage backend is highly available, replicated, or
  geographically distributed. That is the user's deployment choice.
- Protection against denial-of-service against the ingest server. Use
  standard rate-limiting and authentication at your network edge.

If you find a case where the documented properties do not hold — for
example, a way to produce two different receipts that verify against
the same signature, or a path where a single-byte modification still
passes verification — please report it via the private channel above.

## Acknowledgments

Reporters who follow this process will be acknowledged in the
project's release notes, the GitHub Security Advisory, and (when a
website exists) in a public hall-of-thanks page, unless they prefer to
remain anonymous.
