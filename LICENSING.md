# Licensing — maatora

This document explains the licensing model of `maatora` and
its planned extensions. It is informational, not legal advice.

## Promise: core SDK stays MIT forever

The code in this repository — every module under
`src/maatora/` — is and will remain licensed under the
MIT License. This is a deliberate, public commitment, not a temporary state:

- code you integrate today will not become paywalled or relicensed tomorrow
- you can use this SDK in commercial products without paying us
- you can fork it, modify it, redistribute it, run it on someone else's
  managed service
- you can build a competing product on top of it (we'd rather you didn't,
  but the license permits it)

We make this promise explicit because some open-source projects have
relicensed their core to AGPL, BSL, or Elastic License after building an
audience, breaking trust with downstream users. We are not doing that.

If the project ever launches commercial extensions (see below), those will
be **separate packages in separate repositories**, not relicensed versions
of this core.

## Layered licensing model

The full product roadmap uses a layered license model. Each layer has a
specific license chosen for its purpose:

| Layer | What it contains | License | Why this license |
|-------|------------------|---------|-------------------|
| Core SDK | This repository — canonical JSON, signing, Merkle log, decorators, FastAPI ingest, Postgres store, LangGraph middleware, CLI viewer, HTML renderer | MIT | maximum adoption, integrates anywhere |
| Recipe-packs and integrations | `examples/` and future per-framework adapters (CrewAI, AutoGen, LlamaIndex, etc.) | MIT | viral hook, encourages community contributions |
| Premium modules (future) | Advanced retention policies, multi-tenant ingest, SIEM exporters (Splunk, Datadog), compliance-report generator, KMS integrations, enterprise SSO/RBAC | BSL (Business Source License), 4 years → MIT | protects against cloud-clone competitors for 4 years; eventually becomes fully open |
| Cloud service (future) | Managed receipts service: web UI, hosted ingest, multi-tenant infrastructure, billing | Proprietary | not part of the open-source promise |
| Documentation | README, COMPLIANCE.md, this file, examples, guides | MIT (via repository LICENSE) | one license per repository, simple for contributors |

Premium modules and the cloud service do not yet exist. They are listed here
so the architecture is transparent and so users can evaluate the long-term
direction.

## On BSL (Business Source License) for premium modules

If and when premium modules are released, they will use Business Source
License version 1.1 with a 4-year conversion window. This means:

- the source code is public from day one
- you can read it, fork it, and self-host it for internal use
- you **cannot** offer it as a managed/hosted commercial service for the
  first 4 years after release
- after 4 years, each release automatically converts to the MIT License

This is the same model used by Sentry, MongoDB Server, CockroachDB, and
HashiCorp Terraform (originally). It allows us to fund development while
keeping the source visible and ensuring everything becomes fully open over
time.

## Why not AGPL

AGPL would force every downstream user (including users of the SDK inside
their own products) to publish their entire codebase under AGPL. For a
library/SDK whose purpose is to be embedded into other software, this would
make the SDK effectively unusable. AGPL is appropriate for self-contained
servers, not for libraries.

## Contributor agreement: DCO

Contributions are accepted under the Developer Certificate of Origin (DCO).
By signing off your commits with `git commit -s`, you certify that you wrote
the code or have the right to submit it under the project's license.

We do not require a separate CLA (Contributor License Agreement). This is a
deliberate choice to minimize friction for first-time contributors. If the
project grows to require enterprise-grade contributor management, we will
reconsider.

Concrete contribution rules are in [CONTRIBUTING.md](CONTRIBUTING.md).

## Trademark

The project name is currently descriptive (`maatora`) and
not registered as a trademark. The trademark question will be revisited
when:

- the project has stabilized on a brandable name (see project rename plan)
- there is enough audience to make trademark registration economical
  (USPTO costs ~$250 plus legal fees)

Until then, the name is freely usable. After trademark registration, the
project name and logo will be protected, but the code license is unaffected.

## Questions

If you have a specific licensing question (typically: "can my company use
this in product X under license Y") — open a GitHub Discussion or contact
the maintainer. The short answer is almost always "yes" because MIT is
extremely permissive, but happy to confirm in writing.

## Change history

- 2026-05-25: initial version, core MIT + planned BSL for premium + DCO for
  contributors
