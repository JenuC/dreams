# DREAMS monorepo migration — task document

**Goal:** consolidate `JenuC/dreams`, `JenuC/dreams-supervisor`, and `uw-loci/dreams-mcp-synapse-datasets` into a single `uw-loci/dreams` uv workspace, with independently installable packages and a reproducible setup path.

**Non-goals:** rewriting server logic, changing the MCP tool surface, publishing to PyPI. Move code first, refactor later.

---

## 0. Decisions to confirm before starting

| # | Decision | Default if you don't care |
|---|---|---|
| D1 | Does `uw-loci/dreams` already exist? | Create empty, no README (subtree add wants a commit — see 2.0) |
| D2 | Import style | PEP 420 namespace: `dreams.core`, `dreams.microscope`, `dreams.supervisor` |
| D3 | Minimum Python | 3.11 (LangGraph + FastMCP are both fine there) |
| D4 | Keep `.kiro/specs/` at repo root? | No — move to `docs/specs/`, unless Kiro requires the root path |
| D5 | Is synapse-datasets private? | If it stays private, import it last and keep the repo private until reviewed |
| D6 | Old repos | Archive, don't delete |

---

## 1. Target layout

```
uw-loci/dreams/
├─ README.md
├─ pyproject.toml              # workspace root, no importable code
├─ uv.lock                     # single lockfile
├─ .python-version
├─ .gitignore
├─ packages/
│  ├─ dreams-core/
│  │  ├─ pyproject.toml
│  │  └─ dreams/core/
│  │     ├─ config.py          # paths, env, transport selection
│  │     ├─ registry.py        # instrument plugin discovery
│  │     └─ types.py           # shared dataclasses / pydantic models
│  ├─ dreams-microscope/
│  │  ├─ pyproject.toml
│  │  └─ dreams/microscope/
│  │     ├─ server.py          # FastMCP app + main()
│  │     ├─ tools/             # one module per tool group
│  │     └─ backends/          # real hardware vs simulator
│  ├─ dreams-synapse/
│  │  ├─ pyproject.toml
│  │  └─ dreams/synapse/
│  │     ├─ server.py
│  │     └─ client.py
│  └─ dreams-supervisor/
│     ├─ pyproject.toml
│     └─ dreams/supervisor/
│        ├─ graph.py           # was src/main.py
│        ├─ mcp_graph.py       # was src/mcp_main.py
│        └─ agents/
├─ templates/
│  └─ mcp-server/              # copier template for a new instrument server
├─ configs/
│  ├─ claude_desktop.json.example
│  ├─ mcp.json.example         # for Claude Code / .mcp.json
│  └─ openwebui.md
├─ examples/
├─ docs/
│  ├─ quickstart.md
│  ├─ architecture.md
│  ├─ specs/                   # from .kiro/specs/
│  └─ workshop/
└─ .github/workflows/ci.yml
```

**Rule:** no `__init__.py` in any `packages/*/dreams/` directory. Each leaf (`dreams/core/`, `dreams/microscope/`, ...) does get one. That is what makes the namespace package work across separately-installed distributions.

---

## 2. Import the three repos with history

### 2.0 Seed the target

```bash
git clone git@github.com:uw-loci/dreams.git
cd dreams
# subtree add requires at least one commit on the branch
git commit --allow-empty -m "chore: init workspace"
git push -u origin main
```

### 2.1 Subtree each source into its final directory

```bash
git remote add src-dreams git@github.com:JenuC/dreams.git
git remote add src-sup    git@github.com:JenuC/dreams-supervisor.git
git remote add src-syn    git@github.com:uw-loci/dreams-mcp-synapse-datasets.git
git fetch --all

git subtree add --prefix=_import/dreams     src-dreams main
git subtree add --prefix=_import/supervisor src-sup    main
git subtree add --prefix=_import/synapse    src-syn    main
```

Import into a staging `_import/` directory, not directly into `packages/`. Reshaping happens in step 3 as ordinary `git mv` commits, which keeps the subtree merge commits clean and readable.

### 2.2 Checkpoint

```bash
git log --oneline --graph | head -20   # three merge commits, full history behind each
git push
```

---

## 3. Reshape into packages (one commit per package)

Do these as separate commits so `git log --follow` stays useful.

### 3.1 `dreams-supervisor`

```bash
mkdir -p packages/dreams-supervisor/dreams/supervisor
git mv _import/supervisor/src/main.py      packages/dreams-supervisor/dreams/supervisor/graph.py
git mv _import/supervisor/src/mcp_main.py  packages/dreams-supervisor/dreams/supervisor/mcp_graph.py
git mv _import/supervisor/src/mcp_server.py packages/dreams-microscope/dreams/microscope/server.py  # if that's the microscope server
touch packages/dreams-supervisor/dreams/supervisor/__init__.py
git commit -m "refactor: move supervisor into packages/dreams-supervisor"
```

### 3.2 `dreams-microscope`

Source is `_import/dreams/servers/` plus whatever the README's `microscope_real/server.py` resolves to. Split it:

- HTTP/stdio transport wiring → `dreams/core/config.py`
- tool definitions → `dreams/microscope/tools/*.py`
- hardware I/O → `dreams/microscope/backends/{real,sim}.py`

The simulator backend is what makes the workshop demo runnable without a rig. If one doesn't exist yet, stub it in this step and fill it in later — it belongs in the layout now.

### 3.3 `dreams-synapse`

Straight move from `_import/synapse/` into `packages/dreams-synapse/dreams/synapse/`. Check for credentials or tokens in history before making anything public (`git log -p -- '*config*' | grep -i -E 'token|key|secret'`).

### 3.4 Everything else

```bash
git mv _import/dreams/.kiro/specs docs/specs
git mv _import/dreams/README.md   docs/notes/original-readme.md   # salvage the DReAMS blurb for the new README
rm -rf _import
git commit -m "refactor: relocate docs, drop staging dir"
```

Delete the three old `pyproject.toml`, `requirements.txt`, and `uv.lock` files. Their contents get folded into the per-package `pyproject.toml` files in step 4; a stale lockfile in a subdirectory will confuse uv.

---

## 4. Package metadata

### 4.1 Root `pyproject.toml`

```toml
[project]
name = "dreams-workspace"
version = "0"
requires-python = ">=3.11"

[tool.uv.workspace]
members = ["packages/*"]

[tool.uv.sources]
dreams-core = { workspace = true }
dreams-microscope = { workspace = true }
dreams-synapse = { workspace = true }
dreams-supervisor = { workspace = true }

[dependency-groups]
dev = ["pytest>=8", "ruff>=0.6"]

[tool.ruff]
line-length = 100
```

### 4.2 `packages/dreams-core/pyproject.toml`

```toml
[project]
name = "dreams-core"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["pydantic>=2"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["dreams"]
```

### 4.3 `packages/dreams-microscope/pyproject.toml`

```toml
[project]
name = "dreams-microscope"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["dreams-core", "fastmcp>=2", "numpy>=1.26"]

[project.scripts]
dreams-microscope = "dreams.microscope.server:main"

[project.entry-points."dreams.instruments"]
microscope = "dreams.microscope.server:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["dreams"]
```

`dreams-synapse` mirrors this with `dreams-synapse = "dreams.synapse.server:main"`.

### 4.4 `packages/dreams-supervisor/pyproject.toml`

```toml
[project]
name = "dreams-supervisor"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["dreams-core", "langgraph>=0.2", "langchain-mcp-adapters", "fastmcp>=2"]

[project.optional-dependencies]
all = ["dreams-microscope", "dreams-synapse"]

[project.scripts]
dreams-local = "dreams.supervisor.graph:main"
dreams-mcp = "dreams.supervisor.mcp_graph:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["dreams"]
```

### 4.5 Resolve

```bash
uv sync --all-packages
uv run dreams-local
uv run dreams-mcp
git add uv.lock && git commit -m "build: single workspace lockfile"
```

---

## 5. Plugin hook in `dreams-core`

`packages/dreams-core/dreams/core/registry.py`:

```python
from importlib.metadata import entry_points

GROUP = "dreams.instruments"

def discover() -> dict[str, object]:
    return {ep.name: ep.load() for ep in entry_points(group=GROUP)}

def get(name: str):
    eps = entry_points(group=GROUP).select(name=name)
    if not eps:
        raise KeyError(f"no instrument {name!r}; have {sorted(discover())}")
    return next(iter(eps)).load()
```

This is the escape valve: a future instrument adapter can live in its own repo, declare the same entry point, and the supervisor picks it up without a monorepo change.

---

## 6. Config generation

Hand-editing absolute paths in `claude_desktop_config.json` is the most common way a new user fails. Add to `dreams-core`:

```python
# dreams/core/cli.py
def emit_claude_desktop(servers: list[str]) -> dict:
    import shutil
    return {
        "mcpServers": {
            s: {"command": shutil.which(f"dreams-{s}") or f"dreams-{s}", "args": []}
            for s in servers
        }
    }
```

Expose as `dreams config claude-desktop > out.json`. Commit the generated examples to `configs/` so people can diff against a known-good file.

Also add `dreams doctor`: checks Python version, which servers are importable, whether each console script is on PATH, and whether the configured transport port is free.

---

## 7. README skeleton

```markdown
# DReAMS — Data-Reactive Acquisition and Microscope Steering

Bringing AI to the microscope: LLM agents that observe, decide, and steer
acquisition through MCP tool servers.

## Quickstart (5 min, no hardware)
    git clone https://github.com/uw-loci/dreams && cd dreams
    uv sync --all-packages
    uv run dreams-microscope --sim        # simulated instrument
    uv run dreams-mcp                     # supervisor drives it

## What's in here
| Package | Install | What it does |
|---|---|---|
| dreams-core | `uv pip install -e packages/dreams-core` | config, types, instrument registry |
| dreams-microscope | ... | MCP server: stage, focus, acquire |
| dreams-synapse | ... | MCP server: dataset search + fetch |
| dreams-supervisor | ... | LangGraph supervisor and agents |

## Connect a client
- Claude Desktop → `docs/quickstart.md#claude-desktop`
- Copilot / OpenWebUI (HTTP :4201) → `configs/openwebui.md`

## Add your own instrument
    copier copy templates/mcp-server my-instrument
See `docs/architecture.md` for the tool contract.

## Docs
architecture · quickstart · specs · workshop materials
```

---

## 8. CI

`.github/workflows/ci.yml` — one job, matrix over packages:

```yaml
- uses: astral-sh/setup-uv@v5
- run: uv sync --all-packages
- run: uv run ruff check .
- run: uv run pytest
- run: uv run dreams-microscope --sim --selftest    # servers actually start
```

The last line is the one that catches real breakage. A server that imports but won't start is the failure mode that bites during a demo.

---

## 9. Retire the old repos

For each of the three, on its `main`:

1. Replace README with:
   > **Moved.** This code now lives in [uw-loci/dreams](https://github.com/uw-loci/dreams) under `packages/<name>/`. This repo is archived and read-only.
2. Settings → Archive this repository. Do not delete — existing clones, poster links, and any grant text keep resolving.
3. If `uw-loci/dreams-mcp-synapse-datasets` was referenced in a submitted proposal or manuscript, note the redirect in `docs/notes/` for your own record.

---

## Acceptance checklist

- [ ] `uv sync --all-packages` succeeds from a clean clone
- [ ] `uv run dreams-mcp` reproduces the pre-migration supervisor run
- [ ] `uv pip install -e packages/dreams-microscope` in a bare venv works with no LangGraph installed
- [ ] `python -c "import dreams.core, dreams.microscope, dreams.supervisor"` after full sync
- [ ] `dreams doctor` reports green on a machine that has never seen the repo
- [ ] `git log --follow packages/dreams-supervisor/dreams/supervisor/graph.py` shows pre-migration commits
- [ ] Three old repos archived with pointer READMEs
- [ ] No credentials in imported history

## Rollback

Nothing is destructive until step 9. The source repos are untouched through steps 1–8; if the workspace resolution turns out to be a mess, delete `uw-loci/dreams` and keep working in the originals.

## Suggested sequencing

| Session | Steps | Time |
|---|---|---|
| 1 | 0–2 (decisions, subtree imports) | ~1 h |
| 2 | 3–4 (reshape, metadata, first `uv sync`) | ~3 h |
| 3 | 5–6 (registry, config CLI, doctor) | ~2 h |
| 4 | 7–8 (README, CI) | ~2 h |
| 5 | 9 (archive) | ~20 min |
