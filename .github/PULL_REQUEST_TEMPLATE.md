<!--
Thanks for contributing to maatora. A few things before you submit:
- Read CONTRIBUTING.md if you haven't.
- Make sure every commit is signed off (`git commit -s`) — DCO is required.
- Keep the PR focused; small, single-purpose PRs merge faster.
-->

## Summary

<!-- One or two sentences: what changes, and why. Don't restate the diff. -->

## Related issue

<!-- e.g. Closes #123, Refs #456. Use "Closes" only if this PR fully resolves the issue. -->

## Type of change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing code to behave differently)
- [ ] Documentation only
- [ ] CI / build / packaging only

## Checklist

- [ ] Every commit is signed off (`git commit -s`)
- [ ] `ruff check src tests examples` passes locally
- [ ] `ruff format --check src tests examples` passes locally
- [ ] `mypy src examples` passes locally
- [ ] `pytest` passes locally and coverage does not regress
- [ ] New behavior has tests (positive path and edge case)
- [ ] Public API changes are mentioned in `CHANGELOG.md` under `## [Unreleased]`
- [ ] Documentation reflects the change (README, examples, or module docstrings)
- [ ] If this change touches cryptographic code: there is both a positive-path
  test and a check that modifying one byte of input causes verification to fail.

## Notes for the reviewer

<!-- Anything non-obvious: a design choice you considered and rejected, a
followup you plan to do in a separate PR, a benchmark result, etc. -->
