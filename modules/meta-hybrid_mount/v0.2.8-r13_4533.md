## v0.2.8-r13

Changes since v0.2.8-r12:
* Revert "build(deps): bump rustix from 0.38.44 to 1.1.2"
* Revert "build(deps): bump procfs from 0.17.0 to 0.18.0"
* fix(xtask): resolve duplicate function and generic type errors
* Merge pull request #25 from YuzakiKokuban/dependabot/cargo/android_logger-0.15.1
* Merge pull request #26 from YuzakiKokuban/dependabot/cargo/procfs-0.18.0
* build(deps): bump procfs from 0.17.0 to 0.18.0
* Merge pull request #27 from YuzakiKokuban/dependabot/cargo/zip-6.0.0
* Merge pull request #28 from YuzakiKokuban/dependabot/cargo/rustix-1.1.2
* 	modified:   xtask/src/main.rs
* build(deps): bump rustix from 0.38.44 to 1.1.2
* build(deps): bump zip from 0.6.6 to 6.0.0
* feat(build): centralize build logic in xtask
* build(deps): bump android_logger from 0.13.3 to 0.15.1
* 	modified:   .github/workflows/build.yml 	modified:   .github/workflows/release.yml
* 	modified:   .github/workflows/build.yml 	modified:   .github/workflows/release.yml 	modified:   .gitignore 	deleted:    webui/src/lib/constants_gen.js
* 	modified:   .gitignore 	new file:   webui/src/lib/constants_gen.js
* 	modified:   .github/workflows/build.yml 	modified:   .github/workflows/release.yml
* Merge pull request #21 from YuzakiKokuban/dependabot/github_actions/actions/setup-node-6
* [skip ci]Merge pull request #22 from YuzakiKokuban/dependabot/github_actions/actions/setup-java-5
* [skip ci]Merge pull request #23 from YuzakiKokuban/dependabot/github_actions/actions/checkout-6
* [skip ci]Merge pull request #24 from YuzakiKokuban/dependabot/github_actions/actions/upload-artifact-5
* fix(xtask): correctly setup NDK linker environment
* feat(installer): implement universal architecture support
* build(deps): bump actions/upload-artifact from 4 to 5
* build(deps): bump actions/checkout from 4 to 6
* build(deps): bump actions/setup-java from 4 to 5
* build(deps): bump actions/setup-node from 4 to 6
* fix(build): replace cargo-ndk with manual env setup
* chore(xtask): remove unused Path import
* [skip ci]Merge pull request #17 from YuzakiKokuban/dependabot/github_actions/actions/setup-node-6
* [skip ci]Merge pull request #18 from YuzakiKokuban/dependabot/github_actions/actions/upload-artifact-5
* [skip ci]Merge pull request #19 from YuzakiKokuban/dependabot/github_actions/actions/setup-java-5
* [skip ci]Merge pull request #20 from YuzakiKokuban/dependabot/github_actions/actions/checkout-6
* fix(xtask): restore artifact copy logic and fix warnings
* build(deps): bump actions/checkout from 4 to 6
* build(deps): bump actions/setup-java from 4 to 5
* build(deps): bump actions/upload-artifact from 4 to 5
* build(deps): bump actions/setup-node from 4 to 6
* fix(xtask): use cargo-ndk to wrap build command
* Merge pull request #15 from YuzakiKokuban/dependabot/cargo/libc-0.2.178
* Merge pull request #16 from YuzakiKokuban/dependabot/cargo/log-0.4.29
* build(deps): bump log from 0.4.28 to 0.4.29
* build(deps): bump libc from 0.2.177 to 0.2.178
* ci: add dependabot configuration
* fix(ci): enable build-std for riscv64 target
* workflow: switch rust toolchain to stable
* feat(build): add x86_64 and riscv64 architecture support
* style(webui): fix text overflow overlap in module list
* config: unify default mount source to "KSU"
* webui: add mock for webui debug
* 	modified:   .gitignore
* 	modified:   .gitignore 	modified:   webui/.gitignore
* 	修改：     .gitignore 	修改：     webui/.gitignore 	修改：     webui/package-lock.json
* 	modified:   README.md 	modified:   README_ZH.md
* style(webui): double logo size and apply monet theming fix(mount): move magic mount tree logs to debug level
* webui:add hybrid-mount logo
* feat(log): overhaul logging system with otaku-style visualization
* [skip ci] Update KernelSU json and changelog for v0.2.8-r12