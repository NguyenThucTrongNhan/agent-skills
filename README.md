# Agent Skills

Reusable skills for AI coding agents. Each skill is maintained in its own folder under `skills/`.

## Available skills

| Skill | Purpose | Requirements |
|---|---|---|
| [Repository Onboarding Context](skills/repo-onboarding-context/SKILL.md) | Produce a read-only, evidence-based report about an unfamiliar repository. | Python 3 and an agent with access to the local project and command execution. |

## Install through the Claude Code marketplace

After the marketplace metadata has been pushed to this repository, run this inside a Claude Code session:

```text
/plugin install agent-skills --marketplace NguyenThucTrongNhan/agent-skills
```

This installs the `agent-skills` plugin from the `nhan-agent-skills` marketplace. Repository access is required if the repository is private. Start a fresh session after installation and invoke the packaged skill with:

```text
/agent-skills:repo-onboarding-context Review this repository using the read-only onboarding workflow. Keep the report in chat.
```

A local marketplace installation smoke scenario has passed with limited evidence. Installation by fetching this marketplace from GitHub remains to be verified. This marketplace is maintained in this repository; it is separate from Anthropic's reviewed directory.

## Download

Open [Releases](https://github.com/NguyenThucTrongNhan/agent-skills/releases) and select the release for the skill you need. For Repository Onboarding Context 1.0.0, download both assets into the same folder:

- `repo-onboarding-context-1.0.0-portable.zip`
- `repo-onboarding-context-1.0.0-portable.zip.sha256`

Use these release assets rather than GitHub's automatically generated source archives for the installation steps below.

## Verify the download

On Windows, open a normal PowerShell window. Administrator rights are not required. Change the ZIP path below to the file you downloaded, then run the complete block:

```powershell
$skillZip = 'C:\Users\YOUR-NAME\Downloads\repo-onboarding-context-1.0.0-portable.zip'
$skillExpected = (Get-Content -Raw -LiteralPath ($skillZip + '.sha256')).Trim().ToLowerInvariant()
$skillActual = (Get-FileHash -Algorithm SHA256 -LiteralPath $skillZip).Hash.ToLowerInvariant()
if ($skillExpected -notmatch '^[a-f0-9]{64}$' -or $skillActual -ne $skillExpected) {
    throw 'Checksum verification failed. Do not install this ZIP.'
}
'PASS: ZIP checksum matches its sidecar.'
```

The checksum detects a mismatch with the expected file. It is not a publisher signature. For stronger assurance, obtain the expected hash through a trusted channel separate from the download.

## Install in a project

Review the skill instructions and bundled files before enabling it. Extract the verified ZIP into a temporary folder. It contains a folder named `repo-onboarding-context`.

Copy that whole folder into the target project's skill directory for your agent:

| Agent | Destination relative to your project root |
|---|---|
| Codex | `.agents/skills/repo-onboarding-context/` |
| Claude Code | `.claude/skills/repo-onboarding-context/` |

Create the parent directories if needed. The final paths must include:

```text
YOUR-PROJECT/
  .agents/skills/repo-onboarding-context/SKILL.md       # Codex
  .claude/skills/repo-onboarding-context/SKILL.md       # Claude Code
```

Use the location for your chosen agent. Avoid an extra nested `repo-onboarding-context` directory. Keep the bundled `scripts/`, `references/`, and `examples/` directories alongside `SKILL.md`.

Python 3 must be available to the agent. Confirm with `python --version`, or on Windows with `py -3 --version`. The tree generator uses the Python standard library; installing the test dependencies in `requirements.txt` is not required to use the skill.

These instructions install into one project. They do not configure a global skill installation or submit anything to a host's public directory.

## Use the skill

Open the target project in your agent and start a fresh chat. Use its skill selector if available, or explicitly invoke the skill:

**Codex:**

```text
$repo-onboarding-context Review this repository for developer onboarding using the skill's read-only workflow.
```

**Claude Code:**

```text
/repo-onboarding-context Review this repository for developer onboarding using the skill's read-only workflow.
```

The workflow reads the installed `SKILL.md`, runs its bundled directory-tree generator from the project root, reads the architecture baseline and report template, and inspects relevant permitted project files. It produces a report with evidence, findings, unknowns, and coverage limits.

The default workflow does not modify the reviewed project, install dependencies, execute application code, run builds or tests, or access protected configuration contents. If a required script or reference is missing, it should report `BLOCKED`. If the tree output is truncated, it should state that coverage is incomplete.

If discovery fails, check the final `SKILL.md` path and restart the chat. If Python or a required bundled resource is unavailable, resolve the reported prerequisite before retrying.

## Update or remove

Before updating, preserve any local modifications to the installed skill. Download and verify the new release, then replace only that skill's folder. Start a fresh chat after updating.

To remove the skill, delete only its `repo-onboarding-context` folder from your agent's project skill directory. This manual portable installation has no automatic conflict detection or rollback.

## Verification and compatibility

Source-copy integrity, package checksum, and automated script and packaging checks have passed. Manual host QA is partial: Codex desktop scenarios passed in one session, but the exact app version and model were not recorded. The unrelated-prompt scenario was not run. Antigravity has not been tested. Installation paths documented by a host do not by themselves prove this skill's behavior in that host.

Claude Code 2.1.305, Opus 5.5: basic onboarding scenario passed on 2026-10-30. Git status showed only the installed skill directory as untracked, matching the reported starting state. Compatibility remains partial: the complete tool trace and changes to ignored files were not independently verified.

## References

- [Codex skills](https://developers.openai.com/codex/skills/)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Report an issue](https://github.com/NguyenThucTrongNhan/agent-skills/issues)
