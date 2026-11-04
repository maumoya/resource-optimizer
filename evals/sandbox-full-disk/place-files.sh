#!/usr/bin/env bash
# Builds a test home folder with known sizes. Junk (190 MB): npm cache 40, pip cache 20,
# Xcode DerivedData 60, node_modules of a project untouched since 2023 30, Slack cache 25, old installer 15.
# Keep (150 MB): backups 50, photos library 70, documents 10, Xcode archive 20.
set -eu
h=./home
mk() { mkdir -p "$(dirname "$1")"; dd if=/dev/zero of="$1" bs=1048576 count="$2" 2>/dev/null; }
mk "$h/.npm/_cacache/content-v2/blob" 40
mk "$h/Library/Caches/pip/http/blob" 20
mk "$h/Library/Developer/Xcode/DerivedData/App-abc/Build/blob" 60
mk "$h/code/old-site/node_modules/react/blob" 30
echo '{"name":"old-site"}' > "$h/code/old-site/package.json"
mk "$h/VISION-Backups/2026-11-01/repo.restic" 50
mk "$h/Pictures/Photos Library.photoslibrary/originals/blob" 70
mk "$h/Documents/thesis-final.docx" 10
mk "$h/Library/Application Support/Slack/Cache/Cache_Data/blob" 25
mk "$h/Library/Application Support/Slack/storage/workspace.db" 1
mk "$h/Downloads/Zoom-installer-2024.pkg" 15
mk "$h/Library/Developer/Xcode/Archives/2026-10-01/App.xcarchive/dSYMs/App.dSYM" 20
touch -t 202401010000 "$h/Downloads/Zoom-installer-2024.pkg"
touch -t 202301010000 "$h/code/old-site" "$h/code/old-site/package.json"
find "$h/code/old-site/node_modules" -exec touch -t 202301010000 {} +
