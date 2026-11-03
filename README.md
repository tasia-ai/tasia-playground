# Tasia Playground

The manual **Tasia Viewer platform builds** workflow checks out the private
`tasia-rust` source using `TASIA_SOURCE_READ_TOKEN`, builds Windows x64, Linux
x64, macOS x64 and macOS arm64, and uploads each package plus its SHA-256 file
to FileDitch. The public package URLs are written to each GitHub Actions run
summary. FileDitch's public upload API needs no upload credential; source access
still uses the repository secret. Uploads are subject to FileDitch's published
retention and size limits.
