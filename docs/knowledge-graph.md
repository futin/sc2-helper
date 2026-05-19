# Knowledge Graph

This project uses [understand-anything](https://github.com/understand-anything/understand-anything) — a Claude Code plugin that statically analyzes the codebase and produces a `knowledge-graph.json`. The graph powers an interactive browser dashboard for exploring architecture, layers, imports, and guided tours.

---

## What it produces

| Artifact | Path | Description |
|---|---|---|
| Knowledge graph | `.understand-anything/knowledge-graph.json` | 101 nodes, 135 edges, 7 layers, 15-step tour |
| Ignore config | `.understand-anything/.understandignore` | gitignore-style exclusions |
| Intermediates | `.understand-anything/intermediate/` | Per-batch analysis results (safe to delete) |

### Node types

- **file** — every source file, config, doc
- **function** — extracted functions and methods
- **class** — Python classes
- **document** — markdown docs

### Edge types

- `imports` — module-level imports between files
- `contains` — file → function/class membership
- `exports` — public API surface
- `tested_by` — source file → test file

### Layers (7)

1. **UI Layer** — customtkinter views (`views/`)
2. **Frontend Logic Layer** — `RunnerController`, `GameHistoryLoader`
3. **Backend Core** — polling loop, OCR, detectors, TTS
4. **Voice & Audio Layer** — `WakeWordDetector`, `VoiceListener`
5. **Data Layer** — SQLite db abstraction, schema, `GameHistoryManager`
6. **Tests** — `tests/`
7. **Project Support** — config, constants, `requirements.txt`, docs

---

## Commands

### Generate / update the graph

```
/understand
```

Incremental by default — only re-analyzes files changed since last run. Force full rebuild:

```
/understand --full
```

### Open the dashboard

```
/understand-dashboard
```

Starts a local Vite dev server and prints a tokenized URL:

```
http://127.0.0.1:5173/?token=<TOKEN>
```

Open in browser. The dashboard shows the full node/edge graph, layer breakdown, and guided tour.

### Requirements

- Node.js ≥ 20
- pnpm ≥ 10

---

## How it works

1. **Scan** — walks the project tree, respects `.understandignore`, detects languages and frameworks, resolves internal imports
2. **Analyze** — batches files (25 per batch) and dispatches LLM subagents to extract nodes and edges from each batch in parallel
3. **Merge** — `merge-batch-graphs.py` combines all batch outputs, normalizes IDs, deduplicates, and drops dangling edges
4. **Layer assignment** — `architecture-analyzer` agent groups nodes into logical architectural layers
5. **Tour** — `tour-builder` agent produces a 15-step guided walkthrough ordered from entry point inward

The graph is static — it reflects the state of the code at analysis time. Re-run `/understand` after significant changes.

---

## Ignoring files

Edit `.understand-anything/.understandignore`. Same syntax as `.gitignore`. Built-in defaults always exclude `node_modules/`, `.git/`, `dist/`, `*.lock`, `*.min.js`, binary assets, etc.

Example — exclude test files:

```
*.test.*
*.spec.*
tests/
```
