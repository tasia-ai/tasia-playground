# Tasia Viewer platform builds

This public repository contains build workflows only. The viewer source remains
private in [`tasia-ai/tasia-rust`](https://github.com/tasia-ai/tasia-rust).

## Run a build

1. In **Settings → Secrets and variables → Actions**, add the repository secret
   `TASIA_SOURCE_READ_TOKEN`.
2. Use a fine-grained token with **Contents: read-only** access to the private
   `tasia-ai/tasia-rust` repository only. Do not commit or paste the token.
3. Open **Actions → Tasia Viewer platform builds → Run workflow**. The workflow
   builds Windows x64 and Linux x64 from `feat/startup-splash`, macOS x64 from
   `build/macos-x86_64`, and macOS arm64 from `build/macos-arm64`.
4. Download each independent package from that run's artifacts.

Only manually dispatched builds are enabled. Each job checks out one fixed
private source branch; the private-repository token is used only by checkout
and is not passed to the build or artifact steps.
