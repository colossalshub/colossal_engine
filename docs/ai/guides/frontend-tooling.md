# Frontend Tooling Guide

Read this guide only when a task touches Lightweight Charts, AG Grid, or
their frontend test setup.

## Lightweight Charts v5.2.1

- **Series marker API:** use `createSeriesMarkers(series, markers)` from
  `'lightweight-charts'`. The series object does **not** have a
  `setMarkers` method in v5 — that moved to a plugin API. It returns
  `ISeriesMarkersPluginApi` with `.setMarkers()`, `.markers()`, `.detach()`.
  Chart disposal (`chart.remove()`) handles plugin cleanup; no manual
  `detach()` call is needed for a chart that lives for the component's
  lifetime. Discovered in Phase 6.1 — the original task spec assumed the
  v4 API (`series.setMarkers(...)`), which doesn't exist in v5.

## AG Grid v33+ module registration

- **AG Grid v33+ requires `ModuleRegistry.registerModules([AllCommunityModule])`
  at app initialization (`main.tsx`).** Without it, `AgGridReact` still
  renders rows/columns/sorting/`valueFormatter`/theme CSS variables, but
  features backed by an unregistered module — e.g. `cellStyle` (needs
  `CellStyleModule`, bundled inside `AllCommunityModule`) — **silently
  no-op with no console warning or error**. Discovered in Phase 6.3:
  `TradeLedger.tsx`'s conditional PnL coloring rendered gray instead of
  red/green because this registration call was missing since Phase 4.5
  first wired up AG Grid. Fixed in Phase 6.3.1.

- AG Grid modules must be registered in `frontend/src/setupTests.ts`,
  not just `main.tsx`. Vitest runs each test file in an isolated worker
  process; only `setupTests.ts` runs in every worker.

- `vitest.config.ts` has `retry: 2` to absorb AG Grid's jsdom layout
  flakiness under parallel workers. Do not remove without verifying all
  AG Grid tests pass 10 consecutive full-suite runs in parallel.
