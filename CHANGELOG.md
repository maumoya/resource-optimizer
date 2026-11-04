# Changelog

## Unreleased

- README: latest real-machine numbers (21% of the disk freed, 103.8 GB, free space 4% → 25%) and an animated
  before/after card; header and cards updated to match.

## 0.3.0

- GitHub Action `maumoya/resource-optimizer@v0.3.0`: read-only disk, RAM and load snapshot of the runner, with a
  `min-free-percent` gate and a summary table. CI self-tests it on a passing and a failing input.

## 0.2.0

- Covers 9 more targets found by comparing 7 other cleanup tools: Electron app caches, language caches (Gradle,
  Cargo, Go, Maven, CocoaPods, Yarn, pnpm, Bun), Xcode DeviceSupport, installers, logs, build output beyond
  node_modules, old toolchains, uninstall leftovers by bundle ID, Docker by exact ID.
- Every row now carries one checked fact as evidence; caches in use are skipped; approved paths are re-checked right
  before the command; an optional `~/.resource-optimizer/keep.txt` keep list.
- Backups get no action at all (no "prune it" advice); old `node_modules` and `.venv` are offered with the rebuild
  command.
- New sandbox test `evals/sandbox-full-disk` (fake home folder, with vs without the skill).

## 0.1.0

- First version.
