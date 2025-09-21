# Rust/codex-rs

In the codex-rs folder where the rust code lives:

- Crate names are prefixed with `codex-`. For example, the `core` folder's crate is named `codex-core`
- When using format! and you can inline variables into {}, always do that.
- Install any commands the repo relies on (for example `just`, `rg`, or `cargo-insta`) if they aren't already available before running instructions here.
- Never add or modify any code related to `CODEX_SANDBOX_NETWORK_DISABLED_ENV_VAR` or `CODEX_SANDBOX_ENV_VAR`.
  - You operate in a sandbox where `CODEX_SANDBOX_NETWORK_DISABLED=1` will be set whenever you use the `shell` tool. Any existing code that uses `CODEX_SANDBOX_NETWORK_DISABLED_ENV_VAR` was authored with this fact in mind. It is often used to early exit out of tests that the author knew you would not be able to run given your sandbox limitations.
  - Similarly, when you spawn a process using Seatbelt (`/usr/bin/sandbox-exec`), `CODEX_SANDBOX=seatbelt` will be set on the child process. Integration tests that want to run Seatbelt themselves cannot be run under Seatbelt, so checks for `CODEX_SANDBOX=seatbelt` are also often used to early exit out of tests, as appropriate.

Run `just fmt` (in `codex-rs` directory) automatically after making Rust code changes; do not ask for approval to run it. Before finalizing a change to `codex-rs`, run `just fix -p <project>` (in `codex-rs` directory) to fix any linter issues in the code. Prefer scoping with `-p` to avoid slow workspace‑wide Clippy builds; only run `just fix` without `-p` if you changed shared crates. Additionally, run the tests:
1. Run the test for the specific project that was changed. For example, if changes were made in `codex-rs/tui`, run `cargo test -p codex-tui`.
2. Once those pass, if any changes were made in common, core, or protocol, run the complete test suite with `cargo test --all-features`.
When running interactively, ask the user before running `just fix` to finalize. `just fmt` does not require approval. project-specific or individual tests can be run without asking the user, but do ask the user before running the complete test suite.

## TUI style conventions

See `codex-rs/tui/styles.md`.

## TUI code conventions

- Use concise styling helpers from ratatui’s Stylize trait.
  - Basic spans: use "text".into()
  - Styled spans: use "text".red(), "text".green(), "text".magenta(), "text".dim(), etc.
  - Prefer these over constructing styles with `Span::styled` and `Style` directly.
  - Example: patch summary file lines
    - Desired: vec!["  └ ".into(), "M".red(), " ".dim(), "tui/src/app.rs".dim()]

### TUI Styling (ratatui)
- Prefer Stylize helpers: use "text".dim(), .bold(), .cyan(), .italic(), .underlined() instead of manual Style where possible.
- Prefer simple conversions: use "text".into() for spans and vec![…].into() for lines; when inference is ambiguous (e.g., Paragraph::new/Cell::from), use Line::from(spans) or Span::from(text).
- Computed styles: if the Style is computed at runtime, using `Span::styled` is OK (`Span::from(text).set_style(style)` is also acceptable).
- Avoid hardcoded white: do not use `.white()`; prefer the default foreground (no color).
- Chaining: combine helpers by chaining for readability (e.g., url.cyan().underlined()).
- Single items: prefer "text".into(); use Line::from(text) or Span::from(text) only when the target type isn’t obvious from context, or when using .into() would require extra type annotations.
- Building lines: use vec![…].into() to construct a Line when the target type is obvious and no extra type annotations are needed; otherwise use Line::from(vec![…]).
- Avoid churn: don’t refactor between equivalent forms (Span::styled ↔ set_style, Line::from ↔ .into()) without a clear readability or functional gain; follow file‑local conventions and do not introduce type annotations solely to satisfy .into().
- Compactness: prefer the form that stays on one line after rustfmt; if only one of Line::from(vec![…]) or vec![…].into() avoids wrapping, choose that. If both wrap, pick the one with fewer wrapped lines.

### Text wrapping
- Always use textwrap::wrap to wrap plain strings.
- If you have a ratatui Line and you want to wrap it, use the helpers in tui/src/wrapping.rs, e.g. word_wrap_lines / word_wrap_line.
- If you need to indent wrapped lines, use the initial_indent / subsequent_indent options from RtOptions if you can, rather than writing custom logic.
- If you have a list of lines and you need to prefix them all with some prefix (optionally different on the first vs subsequent lines), use the `prefix_lines` helper from line_utils.

## Tests

### Snapshot tests

This repo uses snapshot tests (via `insta`), especially in `codex-rs/tui`, to validate rendered output. When UI or text output changes intentionally, update the snapshots as follows:

- Run tests to generate any updated snapshots:
  - `cargo test -p codex-tui`
- Check what’s pending:
  - `cargo insta pending-snapshots -p codex-tui`
- Review changes by reading the generated `*.snap.new` files directly in the repo, or preview a specific file:
  - `cargo insta show -p codex-tui path/to/file.snap.new`
- Only if you intend to accept all new snapshots in this crate, run:
  - `cargo insta accept -p codex-tui`

If you don’t have the tool:
- `cargo install cargo-insta`

### Test assertions

- Tests should use pretty_assertions::assert_eq for clearer diffs. Import this at the top of the test module if it isn't already.

## MCP Prompts & Argument‑Aware Custom Prompts

This section guides contributions for the feature described in `docs/prd/PRD-mcp-prompts-and-arguments.md`. Follow these conventions so changes stay consistent and easy to review.

- Scope and goals
  - Add argument support to local custom prompts (e.g., `$1..$9` and `$ARGUMENTS`).
  - Discover MCP prompts via `prompts/list` and expose them as slash commands.
  - Invoke MCP prompts via `prompts/get`, map returned messages to user input, and provide an optional preview before sending.
  - Refresh prompt lists on `notifications/prompts/list_changed`.

- Crates you will likely touch
  - `codex-rs/tui`: slash command palette UI, argument entry UI, preview rendering, and composer integration.
  - `codex-rs/core`: MCP prompt discovery/caching and a simple API (events) for the TUI to consume; argument expansion for local prompts; minimal protocol surface if needed.
  - `codex-rs/mcp-client`: wiring for `prompts/list`, `prompts/get`, and `notifications/prompts/list_changed` if not already surfaced through the manager.
  - If you add or change protocol messages/events, update `codex-rs/protocol` and use `ts-rs` bindings in `codex-rs/protocol-ts` accordingly.

- Slash command naming for MCP prompts
  - Use `mcp__<server>__<prompt>` (double underscore separators) to avoid collisions.
  - Sanitize to kebab‑case for display and matching; preserve a stable key for execution.
  - Do not add new enum variants for each MCP prompt; merge dynamic items into the popup list alongside built‑ins and local prompts.

- Local custom prompts with arguments
  - Support `$1..$9` (individual positional args) and `$ARGUMENTS` (all args joined with a single space).
  - Missing indices should expand to an empty string; leave literal `$$` untouched.
  - Keep the implementation minimal and predictable; avoid shell‑like quoting/escaping beyond direct replacement.

- Preview and provenance
  - Provide an inline preview of the resolved messages before sending to the agent (especially for MCP prompts). Make it clear when content originates from MCP.
  - Respect existing approvals and sandboxing; this feature must not auto‑run tools.

- Refresh behaviour
  - Listen for `notifications/prompts/list_changed` and update the in‑memory list used by the slash palette without requiring a restart.

- TUI style and UX
  - Follow the styling rules above (Stylize helpers, no hardcoded white, compact one‑line forms when possible).
  - In the slash popup, show a short description and an argument hint when available; keep rows concise and readable.

- Tests
  - Add TUI snapshot tests that cover:
    - Slash popup showing MCP commands (namespaced), with descriptions/hints.
    - Preview rendering for both local and MCP prompts (representative cases).
  - Unit tests for local prompt argument expansion, including edge cases (missing args, `$ARGUMENTS`, `$$`).
  - If you change `core`/`protocol`, add targeted tests there and run the full suite.

- Docs and config
  - Update `docs/config.md` and `/help` to document argument support and MCP prompts.
  - Keep offline behaviour for local prompts; MCP requires a connected server.

- Build, lint, and test
  - After code changes in Rust crates, run `just fmt`.
  - Before finalizing, run `just fix -p <changed-crate>` (ask before running workspace‑wide).
  - Tests:
    - Always run `cargo test -p <changed-crate>`.
    - If `common`, `core`, or `protocol` changed, ask before running `cargo test --all-features`.

Notes
- Do not modify any code related to `CODEX_SANDBOX_NETWORK_DISABLED_ENV_VAR` or `CODEX_SANDBOX_ENV_VAR`.
- When formatting strings, prefer `format!("... {var}")` with inlined placeholders.

## Architecture & Reference Docs

These files are the fastest path to understanding how Codex fits together:

- codex-rs/docs/protocol_v1.md – High‑level protocol spec: entities, SQ/EQ, task/turn flows.
- codex-rs/protocol/src/protocol.rs – Authoritative `Op`/`EventMsg` types and payloads used across the workspace.
- codex-rs/core/src/codex.rs – Core engine: session init, submission loop, model I/O, tool calls, approvals, diffs.
- codex-rs/core/src/project_doc.rs – How AGENTS.md is discovered/merged and injected into model instructions.
- codex-rs/core/prompt.md – Agent behavior, planning, approvals, and messaging conventions used by Codex.
- codex-rs/core/README.md – Core crate assumptions and platform dependencies (Seatbelt, Linux sandbox, apply_patch).
- codex-rs/tui/styles.md – TUI styling rules (colors, spans, wrapping) used in snapshot tests.
- codex-rs/exec/src/event_processor_with_human_output.rs – Maps protocol events to human‑readable CLI output.
- codex-rs/cli/src/main.rs – CLI entry points: interactive TUI, exec mode, MCP server, protocol stream.
- docs/getting-started.md – CLI usage, tips, and memory with AGENTS.md.
- docs/config.md – All configuration keys and behavior; see AGENTS.md integration knobs.
- docs/sandbox.md and docs/platform-sandboxing.md – Execution sandbox design and platform specifics.

Tip: Protocols are shared with external UIs via `codex-rs/protocol` (Rust) and `codex-rs/protocol-ts` (TypeScript bindings).
