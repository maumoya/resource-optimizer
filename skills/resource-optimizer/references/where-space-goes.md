# Where space usually goes

Sizes vary. Measure each with `du -sh PATH`, one explicit path at a time.

## Group A: regenerable (safe)

| Item | macOS path | Linux path | Clean command (user runs it) |
|---|---|---|---|
| npm cache | `~/.npm` | `~/.npm` | `npm cache clean --force` |
| pip cache | `~/Library/Caches/pip` | `~/.cache/pip` | `pip cache purge` |
| uv cache | `~/.cache/uv` | `~/.cache/uv` | `uv cache prune` |
| Homebrew | `~/Library/Caches/Homebrew` | `~/.cache/Homebrew` | `brew cleanup --prune=all` |
| Playwright browsers | `~/Library/Caches/ms-playwright` | `~/.cache/ms-playwright` | `npx playwright uninstall --all` |
| iOS simulators | `~/Library/Developer/CoreSimulator` | n/a | `xcrun simctl delete unavailable` first; if that frees nothing, `xcrun simctl delete all` (Xcode re-downloads on demand) |
| Xcode build output | `~/Library/Developer/Xcode/DerivedData` | n/a | Xcode › Settings › Locations › delete, or move the folder to the Trash |
| Docker images | inside the VM disk | `/var/lib/docker` | `docker system prune` (shows what it removes first) |
| Browser caches | `~/Library/Caches/Google`, `Firefox` | `~/.cache/google-chrome` | clear from the browser's settings with the browser closed |
| apt / dnf caches | n/a | `/var/cache/apt` | needs admin: explain, let the user decide |
| journal logs | n/a | `/var/log/journal` | needs admin: explain, let the user decide |
| Electron app caches (Slack, VS Code, Discord, Claude) | `~/Library/Application Support/APP/Cache`, `Code Cache`, `GPUCache` only | `~/.config/APP/Cache` | quit the app first, then Trash those 3 subfolders only, never the app's whole folder |
| Language caches | `~/.gradle/caches`, `~/.cargo/registry`, `~/go/pkg/mod`, `~/.m2/repository`, `~/Library/Caches/CocoaPods`, `~/Library/Caches/Yarn`, `~/Library/pnpm/store`, `~/.bun/install/cache` | same under `~` or `~/.cache` | the tool's own command: `go clean -modcache`, `pnpm store prune`, `yarn cache clean`, `pod cache clean --all`, `cargo cache -a` if installed; else Trash the cache folder |
| Xcode extras | `~/Library/Developer/Xcode/iOS DeviceSupport`, `DocumentationCache`, `~/Library/Developer/XCTestDevices` | n/a | Trash versions for iOS releases no longer on any device; Xcode re-downloads on connect |
| Installer files | `.dmg`, `.pkg`, `.xip` in `~/Downloads`; `Install macOS *.app`; `~/Library/iTunes/iPhone Software Updates/*.ipsw` | `.deb`, `.AppImage` in `~/Downloads` | Trash once the app is installed |
| Logs and crash reports | `~/Library/Logs`, `~/Library/Logs/DiagnosticReports` | `~/.local/state/*/log` | Trash files older than 30 days |

## Group B: you decide

| Item | Where | How to check if it is used | Action |
|---|---|---|---|
| Ollama models | `~/.ollama/models` | `ollama list`, then search the user's code and config for each name | `ollama rm NAME`, one per line |
| MLX / Hugging Face models | `~/MLXModels`, `~/.cache/huggingface` | which app loads them; is that app still installed | app gone: Trash; else external disk |
| VM disks (Colima, Docker Desktop, UTM) | `~/.colima`, `~/Library/Containers/com.docker.docker` | is the VM running, is it needed soon | stop it, then archive to an external disk |
| Old app support folders | `~/Library/Application Support/APP` | is the app still installed and used | uninstall the app the official way, then Trash the folder |
| `node_modules` in old projects | project folders | repo committed and pushed, not opened lately | Trash; `npm install` brings it back |
| Downloads, Movies | `~/Downloads`, `~/Movies` | last opened date | Trash or external disk |
| Build output beyond node_modules | `target`, `.build`, `dist`, `.next`, `Pods`, `.venv` in project folders | project untouched 6+ months (`stat` mtime) | Trash; the build or `pip install` brings it back |
| Old toolchain versions | `~/.rustup/toolchains`, `~/.nvm/versions/node`, `~/.pyenv/versions`, old `/Applications/Xcode-*.app` | which version the projects pin (`.nvmrc`, `rust-toolchain`, `.python-version`) | the version manager's own uninstall (`nvm uninstall`, `rustup toolchain uninstall`, `pyenv uninstall`) |
| Uninstall leftovers | `~/Library/Containers/BUNDLE_ID`, `Group Containers`, `HTTPStorages`, `WebKit`, `Saved Application State` named by the bundle ID | `mdfind "kMDItemCFBundleIdentifier == 'BUNDLE_ID'"` finds no app | Trash those folders, one path per line |
| Docker data | `docker system df -v` | which images and volumes running containers use | `docker image rm ID`, `docker volume rm NAME` by exact ID, never `system prune --volumes` |

**Report only, never offered:** Xcode Archives (they hold the dSYMs needed to read crash reports), iOS device backups in
`~/Library/Application Support/MobileSync/Backup`, Mail Downloads, and Chromium `*.code_sign_clone` folders.

## What freed the most in a real run

16 GB Mac mini, 29 → 92 GiB free in four user-run rounds: emptying the Trash (+23 GiB, nothing is freed until then),
unused Ollama models (checked against code first), iOS simulators, models whose app was gone, and `node_modules` in
pushed repos. Package caches gave about 7 GiB. A later round took it to 115 GiB: old simulator runtimes (14.8 GB) and
unused or duplicate apps, then the Trash emptied again. Whole run by macOS Storage: 19.6 → 123.3 GB free (103.8 GB,
21% of the disk). Start with the Trash size, the model folders and simulator runtimes.

## Unused apps

| Check | How |
|---|---|
| Size and last use | System Settings › General › Storage › Applications (Last Accessed column), or `mdls -name kMDItemLastUsedDate -name kMDItemAppStoreHasReceipt /Applications/NAME.app` |
| Re-downloadable? | `kMDItemAppStoreHasReceipt = 1` means the App Store gives it back free |
| Leftover data | `du -sh ~/Library/Containers/BUNDLE_ID` and `~/Library/Application Support/NAME`; GarageBand sounds in `/Library/Application Support/GarageBand` |

Rank apps unused for 90+ days, largest first. Action: the app's own uninstaller if it has one, else SKILL.md step 7
(`trash`, then Finder by `osascript` for root-owned App Store apps, then computer use). `trash` fails with
`afpAccessDenied` on root-owned apps; that is the cue for the Finder route. Data the app made (iMovie libraries, GarageBand projects) is user data: Group B,
archive first. Paid apps: deleting the app does not cancel the plan; tell the user to cancel it in their account.
Duplicates: group `.app` bundles by `CFBundleIdentifier` (`mdfind "kMDItemContentType == com.apple.application-bundle"`,
skip `/System`, paths inside `/Contents/`, the Trash and Developer folders). Same id twice = an old copy or a `-backup` app
beside the current one; offer the older one. Ignore versioned bundles that an app manages itself (claude-code versions,
GoogleUpdater).
System Settings › Storage keeps a cached list: quit System Settings and reopen it on Storage
(`open "x-apple.systempreferences:com.apple.settings.Storage"`) to see the change.
Never offer system apps (Safari, Mail) or apps with a running login item or helper.

## Why "System Data" is huge on macOS

| Item | Check (read-only) | Action |
|---|---|---|
| Simulator runtimes (often 8 GB each) | `xcrun simctl runtime list -v` (size, last used) | keep the newest one in use; `xcrun simctl runtime delete ID` for the rest |
| Temp and cache (`/private/var/folders`) | `du -sh "$(getconf DARWIN_USER_TEMP_DIR)"` | a restart clears most of it; never Trash it by hand while apps run |
| Time Machine local snapshots | `tmutil listlocalsnapshots /` | macOS thins them when space is low |
| App VM bundles (Claude, Docker) | `du -sh` on the app's support folder | keep while the app is used |
| Purgeable space | `diskutil info /` Container Free Space | Settings counts it as used; it frees by itself |

## Group C: in an app's own settings

Messages and WhatsApp attachments, iCloud "Optimize Mac Storage", photo libraries, mail downloads, a pending OS update.

## Extra read-only checks

| Check | macOS | Linux |
|---|---|---|
| Time Machine local snapshots (hidden "System Data") | `tmutil listlocalsnapshots /`; user can run `tmutil thinlocalsnapshots / 1000000000 4` | n/a |
| Purgeable vs real free | `diskutil info /` (Container Free Space) vs `df -h /` | `df -h /` |
| Docker / Colima / Podman | `docker system df`, `colima status`, `podman system df` | same |
| node_modules and build output | `find ~/Projects -maxdepth 6 -name node_modules -type d -prune -exec du -sh {} +` | same |
| Stale large files (approx. last use) | `find ~/Downloads ~/Movies ~/Desktop -type f -size +500M -atime +180` | same |
| Trash | `du -sh ~/.Trash` (needs Full Disk Access; else read the Finder size) | `du -sh ~/.local/share/Trash` |
| Homebrew dry run | `brew cleanup -n` | `brew cleanup -n` |
| Login items | `osascript -e 'tell application "System Events" to get the name of every login item'`, `ls ~/Library/LaunchAgents` | `systemctl --user list-unit-files --state=enabled` |
| Package caches, logs | n/a | `du -sh /var/cache`, `journalctl --disk-usage`, `snap list --all` |

Name the search roots explicitly. Never `find ~` over the whole home on a large disk: it can run for minutes.

## Why "Documents" is huge on macOS

System Settings › Storage shows "Documents" as every user file that fits no other category: models, VM disks, caches,
app support folders, and hidden folders such as `~/.ollama`, `~/.colima` or an app's VM bundle (`vm_bundles` under Application Support). The `~/Documents`
folder itself is often tiny. Measure the home folder's top level, hidden folders included, and show the user those
names instead of saying "Documents is heavy".

## Keep, never clean

Agent threads and sessions (active or archived), their git worktrees and merged git branches. They are the record of
why things were done. If they are in the way, archive them; report their size only.

## RAM and CPU

- `top -l 1 -o mem -n 15` (macOS) or `ps aux --sort=-%mem | head -16` (Linux): the 15 heaviest processes.
- Login items: System Settings › General › Login Items (macOS), `systemctl --user list-unit-files --state=enabled` (Linux).
- Local AI models: one loaded model can hold several GB of RAM. Keep the defaults under about a third of total RAM.
- A disk over about 90% full slows everything: swap and caches have no room.
