# Project Cognitive Layer (MVP)

> Design projects from day one for long-term AI participation.

This repository is a first working prototype of an **AI-native project cognitive layer**: a project-owned, model-agnostic foundation that gives coding agents a stable way to understand a repository, retrieve task-relevant context, track current state, and propose knowledge updates after code changes.

The core idea is simple:

**Project knowledge should belong to the project, not to Claude, Codex, Cursor, Gemini, or any single agent session.**

AI tools are replaceable clients. The project should retain its own architecture knowledge, constraints, decisions, state, history, and working conventions across models and sessions.

## MVP scope

The first version intentionally implements only three capabilities:

1. `aiproj init` — inspect a repository and create a `.ai/` cognitive layer.
2. `aiproj context "<task>"` — compile a compact task-relevant context from project knowledge and repository files.
3. `aiproj update` — inspect the current Git diff and produce a **knowledge delta proposal** plus a state update, instead of silently treating agent inference as truth.

The MVP is deterministic and local-first. It does not require an LLM, embedding service, MCP server, cloud database, or vendor-specific API.

## Why this exists

Most coding-agent workflows repeatedly do this:

```text
request
  -> scan repository
  -> infer architecture
  -> make changes
  -> session ends
  -> next session starts from scratch
```

The intended long-term workflow is:

```text
User Intent
    ↓
Context Compilation
    ↓
Plan
    ↓
Execution
    ↓
Verification
    ↓
Diff Analysis
    ↓
Knowledge Delta Proposal
    ↓
Project State / Knowledge Update
    ↺
```

The project itself becomes the durable source of cognition.

## Quick start

Requires Python 3.10+.

```bash
pip install -e .
```

Inside any Git repository:

```bash
aiproj init
```

This creates:

```text
.ai/
├── project.md
├── architecture.md
├── constraints.md
├── state.md
├── knowledge/
│   └── README.md
└── proposals/
```

Compile context for a task:

```bash
aiproj context "add GitHub OAuth login"
```

After changing code:

```bash
aiproj update
```

The update command reads `git diff`, identifies affected files and likely architectural/state changes, writes a timestamped proposal under `.ai/proposals/`, and refreshes `.ai/state.md` with the working-tree state. The proposal is deliberately reviewable: inference is not automatically promoted to canonical project truth.

## Design principles

### 1. Memory is not context

The project may eventually contain a large knowledge base. An agent context window should contain only the subset relevant to the task. This MVP therefore treats **context compilation** as a separate concern from storage.

### 2. State is not history

`state.md` answers: **what state is the project in now?**

Project history and learned knowledge answer: **what do we know and what happened before?**

These are intentionally separate concepts.

### 3. Inference is not fact

A coding agent may infer that a changed file represents an architectural decision. That inference should not silently become canonical knowledge. The MVP emits a **knowledge delta proposal** for review.

A mature implementation should distinguish at least:

- `verified` — directly supported by source/config/tests;
- `accepted` — explicitly adopted by a human/team/authorized workflow;
- `inferred` — agent-generated hypothesis.

### 4. Knowledge needs provenance

Long-term project knowledge should eventually carry metadata such as:

```text
value
source / evidence
created_at
updated_at
confidence
scope
repo / branch / commit
status
```

This is necessary to prevent stale or hallucinated memories from becoming permanent project facts.

### 5. Humans retain cognitive sovereignty

Canonical project knowledge should not become an unreviewed accumulation of agent summaries. A useful hierarchy is:

```text
Canonical  — accepted project truth
Working    — active task/project context
Ephemeral  — temporary inference
Archived   — historical knowledge
```

## Current implementation

### `aiproj init`

The initializer:

- finds the Git repository root;
- inventories top-level files/directories;
- detects common language/build manifests;
- detects likely source/test/documentation directories;
- records the current branch and commit when available;
- writes conservative starter documents under `.ai/`;
- never overwrites existing cognitive-layer files unless `--force` is supplied.

### `aiproj context`

The context compiler:

- loads canonical `.ai/*.md` files;
- tokenizes the requested task;
- scores repository files by path/name relevance;
- selects a bounded set of relevant text files;
- includes short excerpts rather than whole repositories;
- emits one Markdown context packet suitable for pasting or piping into an agent.

Example:

```bash
aiproj context "change authentication callback behavior" > /tmp/context.md
```

### `aiproj update`

The updater:

- reads branch, commit, status, and `git diff --stat` / `git diff`;
- summarizes changed files;
- heuristically identifies likely areas affected (tests, docs, config, dependencies, API, migrations, authentication, etc.);
- writes a reviewable knowledge-delta proposal;
- refreshes `.ai/state.md` with the current working-tree state.

It does **not** automatically rewrite architecture or constraints based on heuristics.

## Repository layout

```text
src/aiproj/
├── __init__.py
├── cli.py
├── repository.py
├── init_layer.py
├── context.py
└── update.py

tests/
├── test_context.py
└── test_init.py
```

## Intended final system

The long-term target is not merely an “AI memory plugin.” It is a **Project Cognitive Infrastructure** layer that remains valid even if the team switches models, IDEs, coding agents, or vendors.

Conceptually:

```text
Claude ─┐
Codex ──┼──> Project Cognitive Layer
Cursor ─┤          │
Gemini ─┘          ├── project identity
                   ├── architecture
                   ├── constraints
                   ├── decisions
                   ├── current state
                   ├── memory/history
                   ├── workflows
                   ├── evidence/provenance
                   └── tools
```

The project cognitive layer should support a closed engineering loop:

```text
Intent
  -> Context
  -> Plan
  -> Action
  -> Verification
  -> State Transition
  -> Knowledge Update
  -> next Context
```

## Future design dimensions

The following areas are intentionally **not fully implemented** in this MVP and form the roadmap.

### Knowledge model and lifecycle

Define explicit categories such as project identity, architecture, constraints, decisions, current state, tasks, learnings, history, team preferences, and evidence. Specify creation, promotion, invalidation, supersession, archival, and deletion semantics.

### Fact, inference, confidence, and provenance

Prevent agent-generated summaries from becoming durable facts without evidence. Attach source paths, commits, tests, ADRs, human approvals, timestamps, confidence, and validity scope.

### A real Context Compiler

Move beyond path/keyword scoring toward hybrid retrieval: structural code analysis, symbols, dependency graphs, semantic search, recency, current task state, architecture relationships, and token-budget optimization.

### State and memory separation

Maintain an explicit state machine for active work, blockers, completed steps, pending verification, and current branch/worktree while keeping historical memory independently queryable.

### Verification-driven cognitive updates

Knowledge changes should be derived after tests/build/lint/evals and other verification steps. Failed verification should prevent or downgrade proposed canonical changes.

### Git-aware versioning

Bind knowledge to repository, branch, commit, worktree, and possibly release. Checking out an older commit should make it possible to reconstruct the cognitive state valid for that code version.

### Multi-agent concurrency

Multiple agents may read and update project cognition simultaneously. A mature system needs versions, optimistic concurrency, transactions, conflict detection, merge semantics, and possibly scoped locks.

### Human governance / cognitive sovereignty

Define which changes agents may apply automatically and which require review. Make promotion from inferred/working knowledge to canonical knowledge an explicit policy decision.

### Explainability and traceability

Every important instruction or memory should answer: “Why does the agent believe this?” and trace back to source code, configuration, ADR, issue, commit, test, or human decision.

### Security and persistent prompt injection

Repository content is untrusted data, not automatically trusted instruction. A malicious README or source comment must not be able to promote itself into persistent agent rules. Future versions need trust boundaries, sanitization, provenance policies, secret detection, and safe tool permissions.

### Cost and context economics

Optimize context tokens, indexing cost, embedding/model calls, refresh frequency, storage, and latency. More memory is not automatically better context.

### Model and vendor portability

Support Codex, Claude Code, Cursor, Gemini CLI, and future agents through stable project-owned formats rather than vendor-owned hidden memory.

### MCP server and agent integrations

Expose project cognition through MCP resources/tools. Add adapters for `AGENTS.md`, `CLAUDE.md`, IDE rules, hooks, agent lifecycle events, and CI systems without duplicating the canonical knowledge source.

### IDE and developer UX

Provide review UIs for knowledge deltas, provenance, stale-memory warnings, conflicts, task state, and context previews.

### Cloud sync and team collaboration

Optionally support shared remote indexes and team policies while preserving a Git-native/local-first source of truth wherever practical.

### Structured architecture and code knowledge

Add symbol indexes, module relationships, dependency graphs, APIs, schemas, migrations, ownership boundaries, and architectural decision records.

### Knowledge freshness and invalidation

Detect when source evidence changes, mark affected knowledge as stale, and re-verify or invalidate it instead of continuing to inject outdated context.

### Evaluation

Measure whether the cognitive layer actually improves engineering outcomes: time-to-first-correct-change, repeated repository scanning, context token usage, regression rate, stale-context errors, cross-session continuity, and cross-agent portability.

## Non-goals of the MVP

This version is not:

- an autonomous coding agent;
- a vector database;
- a replacement for Git;
- a hidden chat-memory service;
- a vendor-specific plugin;
- an authority that silently rewrites project truth.

It is a small, inspectable foundation for testing whether **project-owned cognition** can become a practical engineering primitive.

## License

MIT
