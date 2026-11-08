#!/usr/bin/env bash
set -euo pipefail

target="$1"
arch="$2"
binary="source/target/$target/release/tasia-viewer"
if [[ ! -x "$binary" ]]; then
  echo "::error::Expected built executable missing or not executable: $binary" >&2
  exit 1
fi
app="Tasia Viewer.app"
contents="$app/Contents"
version="$("$binary" --version)"
version="${version#Tasia Viewer }"
mkdir -p "$contents/MacOS" "$contents/Resources/assets/emoji" "$contents/Resources/assets/dictionaries"
install -m 755 "$binary" "$contents/MacOS/tasia-viewer"
cp source/assets/emoji/LICENSE-OFL.txt "$contents/Resources/assets/emoji/"
cp source/crates/aurora-viewer/assets/dictionaries/README.md "$contents/Resources/assets/dictionaries/"
find source/crates/aurora-viewer/assets/dictionaries -name LICENSE.txt -print0 | while IFS= read -r -d '' license; do
  name="$(basename "$(dirname "$license")")"
  cp "$license" "$contents/Resources/assets/dictionaries/${name}-LICENSE.txt"
done
cp source/LICENSE source/NOTICE.md source/README.md "$contents/Resources/"
cat > "$contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleExecutable</key><string>tasia-viewer</string>
  <key>CFBundleIdentifier</key><string>work.tasiaviewer.viewer</string>
  <key>CFBundleName</key><string>Tasia Viewer</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleInfoDictionaryVersion</key><string>6.0</string>
  <key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST
APP_CONTENTS="$contents" VERSION="$version" python3 -c 'import json,os; path=os.path.join(os.environ["APP_CONTENTS"],"Resources","version.json"); open(path,"w",encoding="utf-8").write(json.dumps({"schema":1,"version":os.environ["VERSION"]},indent=2)+"\n")'
plutil -lint "$contents/Info.plist"
codesign --force --sign - "$app"
codesign --verify --strict "$app"
ditto -c -k --sequesterRsrc --keepParent "$app" "Tasia-Viewer-macos-${arch}.zip"
