# Repository Onboarding Context

An evidence-based, read-only onboarding skill for mapping an unfamiliar
software repository. It summarizes architecture, entry points, configuration,
tests, and delivery context while distinguishing confirmed facts, inferences,
unknowns, and review limits.

## Included skill resources

- `SKILL.md` defines the workflow and safety constraints.
- `scripts/generate_context_tree.py` creates a bounded repository tree.
- `references/architecture-baseline.md` provides the architecture
  baseline used by the workflow.
- `examples/expected-onboarding-report.md` shows a report structure.
- `tests/` contains tests and prompt scenarios specific to this skill.

Python 3 is required to run the bundled tree-generation script. The default
workflow is read-only: it does not install dependencies, build or run the
application, or modify the reviewed repository.

## Compatibility status

Manual QA is partial. Codex desktop scenarios passed in one session, but the
exact app version and model were not recorded. The unrelated-prompt scenario
was not run. Antigravity and Claude Code have not been tested. Do not interpret
the package format or local installation support as proof of host behavior.
