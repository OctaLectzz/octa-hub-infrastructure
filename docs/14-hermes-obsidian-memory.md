# 14 — Hermes Obsidian Memory Plugin Operations

**Status:** Runtime customization tested; repository documentation pending review and commit
**Last updated:** 2026-10-13

## 1. Scope and Official References

This document records the `obsidian-memory` community plugin installed in the Hermes Agent dashboard. It is distinct from the separately planned Obsidian Web service at `https://obsidian.octalectzz.my.id`.

- Hermes Agent repository: https://github.com/NousResearch/hermes-agent
- Hermes plugin documentation: https://hermes-agent.nousresearch.com/docs/zh-Hans/plugins/obsidian-memory
- Community plugin repository: https://github.com/kyssta-exe/hermes-obsidian-memory

Check the plugin repository and the deployed Hermes release's official documentation before changing plugin behavior or updating it.

## 2. Observed Runtime Configuration

| Item | Observed value |
|---|---|
| Hermes container | `hermes` |
| Plugin directory inside container | `/opt/data/plugins/obsidian-memory` |
| Dashboard frontend | `/opt/data/plugins/obsidian-memory/dashboard/plugin.js` |
| Plugin API module | `/opt/data/plugins/obsidian-memory/dashboard/plugin_api.py` |
| Vault path inside container | `/opt/data/obsidian-vault` |
| Vault configuration | `OBSIDIAN_VAULT_PATH=/opt/data/obsidian-vault` |
| Dashboard URL | `https://hermes.octalectzz.my.id/obsidian?profile=default` |

The Hermes persistent host directory `/opt/octa/data/hermes` is mounted at `/opt/data` in the container. Therefore, the plugin and vault files live in persistent runtime data, not in this infrastructure repository. Confirm the active mount and configured path on the VPS before relying on these paths.

Do not commit the vault, runtime plugin directory, authentication data, or other private application data to this public repository.

## 3. Runtime Customizations

Two changes were made directly in the installed plugin's persistent runtime files.

### 3.1 Backend cache refresh

In `dashboard/plugin_api.py`:

- `_VAULT_CACHE_TTL_SECONDS` is set to `5.0`.
- `_get_vault()` rescans the vault when its cached note index is absent or at least five seconds old.
- `_vault_cache_scanned_at` records the last scan time using `time.monotonic()`.

This allows filesystem changes made outside the dashboard to be discovered without requiring a manual plugin refresh. Python syntax was checked with `py_compile`, and the backend was activated by restarting the Hermes container.

### 3.2 Frontend polling and graph labels

In `dashboard/plugin.js`:

- The notes/folders/tags/graph data loader is called immediately and then polled with a configured 10-second interval while the browser tab is visible and the user is not editing a note.
- The interval is cleaned up when the effect is disposed.
- Graph labels are drawn for every node rather than only for hovered, selected, or sufficiently large nodes.

The graph-label condition was changed from `if (hov || sel || r > 7)` to `if (true)`. This is functionally verified but is a simple runtime patch; consider replacing it with a clearer unconditional label-rendering block when the graph UI is next improved.

The polling interval is configured for 10 seconds. Browser scheduling and React effect lifecycle may make observed request timing longer; do not promise a strict update-time guarantee.

## 4. Verification Performed

The following checks were observed on 2026-10-13:

- The plugin vault endpoint returned HTTP `200` and listed `obsidian-vault`.
- The notes endpoint returned HTTP `200` and included newly created test notes.
- A new note created directly in `/opt/data/obsidian-vault` appeared in the dashboard without manually refreshing the browser after the polling and backend cache changes were activated.
- Graph labels became visible for the five test notes after reloading the dashboard.
- `python -m py_compile` succeeded for `plugin_api.py`.
- The Hermes container returned to `running` after restart.

These tests verify the specific behavior described above; they are not a full plugin security audit or an end-to-end regression test.

Temporary test notes created during validation include `Auto-Refresh-Test.md` and `Live-Polling-Test.md`. Decide whether to keep or remove them manually after confirming they are no longer needed. Do not delete notes automatically.

## 5. Backups on the VPS

Runtime backups created during the change:

- `/opt/data/plugins/obsidian-memory/dashboard/plugin_api.py.bak-20261012-193719`
- `/opt/data/plugins/obsidian-memory/dashboard/plugin.js.bak-20261013-polling`
- `/opt/data/plugins/obsidian-memory/dashboard/plugin.js.bak-20261013-graph-labels`

These are runtime recovery artifacts, not repository files. Confirm their presence on the VPS before restoring. Do not assume a backup is available just because it is listed here.

## 6. Maintenance and Rollback

Before updating the community plugin or changing its runtime files:

1. Read the current official plugin and Hermes release documentation.
2. Confirm the persistent mount and active vault path.
3. Make a new timestamped backup of each file to be changed.
4. Apply one change at a time and validate Python/JavaScript syntax where applicable.
5. Verify the vault endpoint, notes endpoint, automatic refresh, note editing, and graph behavior.
6. If a rollback is needed, stop and inspect the current files, then restore the matching backup deliberately. Avoid overwriting newer user changes.

The runtime customizations are not yet represented as a reproducible patch in this repository. Until that is addressed, reinstalling or upgrading the community plugin may overwrite these changes. Review the upstream plugin's update behavior before upgrading.

## 7. Remaining Work

- [ ] Decide whether to maintain the changes as a documented patch file in this repository or keep them as runtime-only modifications.
- [ ] Review graph label density and readability later; this was explicitly deferred.
- [ ] Decide whether to remove the temporary test notes.
- [ ] Review the community plugin's update/upgrade procedure before the next plugin update.
- [ ] Keep the separately planned Obsidian Web service status independent from this Hermes plugin.
