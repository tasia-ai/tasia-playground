# Tasia Viewer platform builds

This public repository contains build workflows only. The viewer source remains
private in [`tasia-ai/tasia-rust`](https://github.com/tasia-ai/tasia-rust).

## Run a build

1. In **Settings → Secrets and variables → Actions**, add the repository secret
   `TASIA_SOURCE_READ_TOKEN`.
2. Use a fine-grained token with **Contents: read-only** access to the private
   `tasia-ai/tasia-rust` repository only. Do not commit or paste the token.
3. Add a second repository secret, `STORAGE_TO_TOKEN`, using your storage.to
   upload token. Do not reuse or send the source-read token.
4. Open **Actions → Tasia Viewer platform builds → Run workflow**. The workflow
   builds Windows x64 and Linux x64 from `feat/startup-splash`, macOS x64 from
   `build/macos-x86_64`, and macOS arm64 from `build/macos-arm64`.
   Each package and SHA-256 file is uploaded to storage.to; the job summary
   contains the public URL index. No build archives are retained as Actions
   artifacts.

Only manually dispatched builds are enabled. Each job checks out one fixed
private source branch; the private-repository token is used only by checkout
and is not passed to the build or upload steps. The storage.to token is used
only by the uploader, which never prints or writes the token.
