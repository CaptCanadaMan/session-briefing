# Session Briefing Template (chat variant)

This is the canonical section structure for session briefing documents. Every numbered
section must be present in every version of the briefing. When updating, carry all
sections forward — only §3 is replaced.

Produce as a markdown (`.md`) file.

---

## Document header

```
# [PROJECT NAME] — Session Briefing

**v[X.Y] — [brief description of this session's focus]**
_For use as context in the next working session._
```

---

## Section structure

### §1. Project Context

One to three paragraphs covering:
- What the project is
- Where it sits in a broader ecosystem (if applicable)
- Platform targets and key constraints
- Current phase (design / engineering / testing / submission)
- Who is building it (solo, team size, relevant background)

This section is relatively stable — update only when the project context genuinely changes
(e.g., phase transition from design to engineering).

### §2. Current Status

A table with every workstream or component and its status. Use unambiguous status values:

| Area | Status | Notes |
|------|--------|-------|
| [Workstream] | COMPLETE / IN PROGRESS / NOT STARTED / PENDING / UPDATED vX.X | Brief detail |

Keep this table comprehensive. It should be possible to glance at §2 and know exactly
where everything stands without reading any other section.

For complex projects, group rows by category (e.g., Design, Engineering, Testing).

### §3. This Session — What Was Done

The only section that gets fully replaced on each update. Document:
- Each distinct piece of work as a sub-section (§3.1, §3.2, etc.)
- What was produced or changed
- What files were affected
- Implementation details a future session would need
- Decisions made and their rationale

Be specific. "Updated the settings view" is not useful. "Wired UNUserNotificationCenter
scheduling in SettingsView.swift — auth request on toggle-on, calendar trigger with
repeats:true, fixed identifier so each call replaces prior schedule" is useful.

### §4. Next Steps / Priorities

What should the next session focus on? Ordered by priority. Include:
- Recommended sequence
- Any blockers or prerequisites
- Estimated complexity where relevant

### §5. Design Decisions Log

Cumulative list of all design decisions made across all sessions. Append-only — never
remove prior entries. Format:

| # | Decision | Detail | Session |
|---|----------|--------|---------|
| 1 | [Decision name] | [What was decided and why] | v1.0 |

This section can grow long on complex projects. That is correct — it is a reference log,
not a summary. Group by topic area if it exceeds ~30 entries.

### §6. Open Questions

Questions that have been raised but not yet resolved. Include:

| # | Question | Deadline | Context |
|---|----------|----------|---------|
| 1 | [The question] | [When this blocks progress] | [Why it matters] |

Remove entries when resolved — but move them to §5 (Design Decisions) so the decision
is captured.

### §7. Outstanding Discrepancies

Cross-document conflicts. Carry forward until resolved.

| Discrepancy | Incorrect (source) | Correct | Resolution status |
|---|---|---|---|
| [What conflicts] | [Doc A: value] | [Correct value — Doc B] | [Carried / Resolved in vX.X] |

If no discrepancies exist, include the section header with "None identified."

### §8. File Inventory

Every deliverable file tracked by the project.

| File | Version / Status | Description |
|------|-----------------|-------------|
| [filename] | Complete vX.X / In progress / Draft | Brief description |

Update this table whenever files are created, modified, or superseded.

### §9. Working Style Notes

Observations about how the collaboration works. Two sub-sections:

#### §9.1 How This Person Works
Traits and preferences observed across sessions. These are project-contextual —
personality-level preferences belong in User Preferences, not here.

| Area | Notes |
|------|-------|
| Domain expertise | [What domain knowledge they bring to THIS project] |
| [Other observations] | [Details] |

#### §9.2 What Works Well
Collaboration patterns that have proven effective on this project.

| Pattern | Detail |
|---------|--------|
| [Pattern name] | [How and why it works] |

### §10. Operational Notes

Project-specific tooling and environment constraints.

| Area | Notes |
|------|-------|
| [Tool/environment] | [Constraint or convention] |

Examples: "Git via Xcode UI only," "StoreKit config file active,"
"No network access in build environment."

### §11. Quick-Start: New Session

A numbered checklist that a user follows to verify the project is in the state the
briefing claims. Project-specific — should reference actual files to load, builds to
run, features to verify.

| Step | Action |
|------|--------|
| 1 | Load [briefing version] + [key context docs] |
| 2 | [Verify build / environment] |
| 3 | [Verify key feature] |
| ... | ... |

### §12. Session Opening Prompt

A pre-written message the user can paste into a new Claude session. Should be specific
and actionable:

```
I'm building [project], a [one-line description]. Read the Session Briefing v[X.Y] first.
[Current status summary in 1-2 sentences]. Next priorities: [ordered list].
Files: [key documents to load].
```

### §13. Version History

One-line entry per version. Append-only.

| Version | Summary |
|---------|---------|
| v1.0 | Initial briefing. [Key content]. |
| v1.1 | [What changed]. |

---

## Formatting notes

- Use tables for structured data — they scan faster than prose in a reference document.
- Use sub-sections (§3.1, §3.2) within §3 for each piece of work.
- Bold section headers. Use consistent heading levels.
- Keep prose concise. The briefing is a reference document, not a narrative.
- *(Optional)* A `Confidential — Internal Use Only` footer line, only if you keep briefings
  private — not required by the method.
