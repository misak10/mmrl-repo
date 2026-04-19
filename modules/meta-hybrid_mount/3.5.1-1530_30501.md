
## v3.5.1


### <!-- 1 --> Features

- Implement SELinux context and ownership cloning for file operations




## v3.5.0


### <!-- 1 --> Features

- `lkm` Fallback to ksud insmod when finit_module fails on KernelSU When finit_module fails and the runtime environment is KernelSU, retry loading the HymoFS LKM via `ksud debug insmod`. Falls back through /data/adb/ksud then $PATH, and surfaces both failures on error.

- `nuke` Add strict verification for apatch nuke execution

- `xattr` Add support for legacy system file context in firmware paths

- `xattr` Refactor path resolution and context handling for managed partitions

- `xattr` Add function to determine if live context should apply to managed partitions



### <!-- 2 --> Fixes

- `lkm` Use 'ksud insmod' instead of 'ksud debug insmod'

- Improve live SELinux context application

- Collapse xattr let-chains for clippy

- Try fix GPU driver selinux is error

- Fix xattr



### <!-- 4 --> Refactors

- `xattr` Clean up formatting and improve readability in path resolution functions

- Improve code formatting and readability across multiple files

- Separate domain models and hymofs orchestration

- Enhance cleanup logic and add mounted path check

- Remove unused LiveContextCache and related functions

- `core` Simplify runtime state finalization

- `xattr` Remove unused lgetxattr import



### <!-- 8 --> Maintenance

- Remove unused test modules and associated test cases across various files - Deleted test modules and their corresponding tests from `user_hide_rules.rs`, `mod.rs`, `compile.rs`, `mod.rs`, `runtime.rs`, `tests.rs`, `utils.rs`, `file.rs`, `hymofs.rs`, `lkm.rs`, and `node.rs`. - Cleaned up code by removing commented-out test code and unnecessary imports. - This cleanup improves code readability and maintainability by eliminating redundant test cases that are no longer needed.

- Revert "Speed up CI by skipping hymofs LKM builds by default" This reverts commit 58e8b20423a6c1cdf5e344dd7686f300b9c06ca3.



### <!-- 9 --> Other

- Switch to GPLv2 licence

- Using hawkeye to manage licence

- Refactor sync and runtime finalization logic - Updated `perform_sync` to use `defs::managed_partition_names` for managed partitions. - Removed the `build_managed_partitions` function from `sync.rs` and replaced its usage. - Modified `build_runtime_state` to accept `ExecutionResult` instead of `MountPlan`. - Changed `collect_active_mounts` to use `ExecutionResult` for active mounts collection. - Introduced `managed_partition_names` and `managed_partition_set` in `defs.rs` for better partition management. - Refactored `build_managed_partitions` in `hymofs/common.rs` to utilize the new `managed_partition_set`. - Enhanced `collect_module_files` in `magic_mount/utils.rs` to accept `magic_modules` and `use_hymofs` parameters. - Implemented path normalization functions in `hymofs/compile.rs` for better path handling. - Updated `sync_dir` in `file.rs` to use a live context cache for improved performance. - Refined extended attribute handling in `xattr.rs` with better error logging and caching. - Removed deprecated functions in `hymofs.rs` to streamline the codebase.

- Simplify LiveContextSourceKind display

- Opt TMPFS_XATTR_SUPPORTED lock using AtomicBool, instead of OnceLock

- Refactor CLI handlers and remove legacy hymofs compatibility

- Split core API payload builders by domain

- Speed up CI by skipping hymofs LKM builds by default




## v3.4.7


### <!-- 1 --> Features

- `hymofs` Integrate HymoFS as third mount mode - New hymofs executor that drives the HymoFS LKM via ioctl rules (ADD_RULE / ADD_MERGE_RULE / HIDE_RULE / ADD_MAPS_RULE / HIDE_OVERLAY_XATTRS), with bidirectional src/resolved_src matching to keep module-side paths like /system/product working alongside the kernel's canonical form. - LKM lifecycle management: autoload/unload, KMI override, runtime probe via /proc/modules, and packaging of per-KMI hymofs_lkm.ko under module/hymofs_lkm/ via xtask (HYBRID_MOUNT_HYMOFS_LKM_DIR). - New CLI surface: hybrid-mount hymofs {status,list,enable,disable, stealth,hidexattr,maps,hide-uids,mount-hide,statfs-spoof,uname, cmdline,fix-mounts,clear,release-connection,invalidate-cache} and hybrid-mount lkm {status,load,unload,set-autoload,set-kmi, clear-kmi}, plus user-hide persistence (hide add/remove/list/apply). - Planner / controller / runtime-state / finalization updated to treat hymofs as a first-class mount mode alongside overlay/magic. - Config schema extends with HymofsConfig (flags, uname/cmdline spoof, hide_uids, maps_rules, kstat_rules, mount_hide, statfs_spoof) and persists to /data/adb/hybrid-mount/hymofs.toml. - WebUI: new HymoFS tab with LKM card, runtime toggles, identity spoof, user-hide list, maps rules, and capability summary. Bottom-nav snowflake icon. hymofsStore uses /proc/modules as a fast probe: on LKM unloaded it synthesizes a fallback status that preserves the previous real config so the master toggle never flips off on unload. - CI: build.yml and release.yml now call build-hymofs-lkm.yml (matrix: 7 KMIs x arm64), download the .ko artifacts, and stage them via HYBRID_MOUNT_HYMOFS_LKM_DIR before xtask build. - scripts/build-local.sh: local build helper with --hymofs-lkm-dir for dev iterations.



### <!-- 2 --> Fixes

- `hymofs` Drop redundant u64 casts in statvfs math to satisfy clippy

- `hymofs` Stabilise statvfs and default-config unit tests - statvfs_usage: widen via u64::from and silence the per-platform unnecessary_cast / useless_conversion lints instead of carrying target-gated code just for this helper. - hymofs_runtime_requires_mapping_or_explicit_feature: Config::default() turns stealth on; clear all auxiliary feature flags in the test so it actually exercises the 'no mapping, no feature' path.

- `hymofs` Remove redundant imports in compile and runtime modules

- `action` Update download-artifact action to v8

- `planner` Handle symlinks and improve error logging in generate_with_root function feat(utils): enhance collect_module_files to maintain partition structure fix(node): update symlink handling in Node implementation and add tests

- `module_status` Improve status description formatting in update_description function

- `hymofs` Align cmdline sync/clear behavior with upstream semantics

- `hymofs` Isolate runtime sync and harden compat

- `storage` Align tmpfs and ext4 selinux context



### <!-- 4 --> Refactors

- `hymofs` Unify config and tighten runtime behavior

- `hymofs` Reorganize use statements for better readability

- `build` Remove setup-build-env action and integrate KPM setup directly in workflows



### <!-- 9 --> Other

- Add HymoFS module with runtime and status management - Introduced a new HymoFS module in `src/mount/hymofs/mod.rs` to encapsulate functionality related to the HymoFS file system. - Implemented runtime management in `src/mount/hymofs/runtime.rs`, including feature toggles, runtime configuration synchronization, and application of mount rules. - Created a status management module in `src/mount/hymofs/status.rs` to handle operational checks and runtime information collection. - Added comprehensive tests in `src/mount/hymofs/tests.rs` to validate runtime behavior, feature toggles, and rule compilation. - Ensured proper logging and error handling throughout the module for better debugging and operational visibility.




## v3.4.6


### <!-- 1 --> Features

- `xtask` Call notify crate directly



### <!-- 8 --> Maintenance

- Split notify into separate repository




## v3.4.5


### <!-- 1 --> Features

- Add ext4 probe and post-check for APatch nuke flow

- Finalize APatch nuke KPM support

- Enhance ext4 sysfs handling by using function pointers for dynamic symbol resolution



### <!-- 2 --> Fixes

- Fix late mode check Signed-off-by: Tools-app <localhost.hutao@gmail.com>

- Fix panic

- Make kpm module compile in CI toolchain headers

- Collapse nested if to satisfy clippy

- Use APatch kptools for kpm nuke calls

- Only extract kpm assets on APatch



### <!-- 3 --> Performance

- `sync` Reduce repeated module tree traversal



### <!-- 8 --> Maintenance

- Remove extra kpm README and related doc entries




## v3.4.2


### <!-- 9 --> Other

- Fix installer notice confirmation blocking

- Improve mount planning diagnostics

- Refactor magic mount stats into context

- Make node traversal deterministic

- Polish executor naming and diagnostics text

- Unify logging format across runtime




## v3.4.1


### <!-- 2 --> Fixes

- `core` Resolve naming refactor build errors

- `recovery` Avoid state borrow conflict

- `planner` Split configured extra partitions

- `planner` Preserve real partition names for symlink targets

- `umount` Restore queued try-umount commit



### <!-- 4 --> Refactors

- `core` Split boot and command entrypoints

- `executor` Split overlay and magic handlers

- `storage` Split backends and ext4 setup

- `recovery` Split retry state and markers

- `core` Extract finalization workflow

- `core` Separate module description updates

- `inventory` Separate module presentation

- `core` Clarify controller and runtime names

- `startup` Rename boot recovery modules

- `naming` Rename entry, inventory, and fallback modules

- `naming` Rename status and finalization modules

- `umount` Drop extra /mnt cleanup and unify wording



### <!-- 6 --> Tests

- `planner` Add mount plan scenarios



### <!-- 7 --> CI / Tooling

- `submodule` Track webui on configured branch

- `release` Generate changelog with git-cliff



### <!-- 9 --> Other

- .github/workflows/update_webui_submodule.yml



## v3.4.0

Changes since v3.3.1:
* chore(submodule): update webui
* docs: add policy behavior matrix to Chinese README
* fix: complete P2 recovery retry and magic mount counter reset
* feat: complete P1 observability and tighten overlay fallback gate
* fix: narrow auto skip_mount attribution for magic mount failures
* workflow: update pnpm version
* adj: Add checks for unsupported root platform and late load
* fix: resolve clippy warning and update lockfile in release sync
* chore: clarify ELOOP fallback logging by condition
* feat: fallback symlink-loop overlay failures to magic mount
* chore(submodule): update webui
* chore: update cargo package
* chore(installer): switch notice prompt to English and add feedback channels
* chore: update license headers [skip ci]
* chore(release): sync version v3.3.1 [skip ci]## v3.3.1

Changes since v3.3.0:
* ci(release): install armv7 android rust target## v3.2.2

Changes since v3.2.1:
* build: pin nightly toolchain for rustfmt consistency
* chore(submodule): update webui [skip ci]
* ci: restrict webui updater workflow to dev branch
* fix: make cargo clippy happy
* metainstall: add support for hot install
* feat(core): auto detect manual mount scripts to prevent conflicts
* chore: update license headers [skip ci]
* chore(release): sync version v3.2.1 [skip ci]## v3.2.1

Changes since v3.2.0:
* chore: remove unused update_desc
* Revert "ci: promote only latest prereleases"
* Revert "ci(workflow): fix unrecognized 'secrets' context in if conditions"
* sync: sync magic mount updates from upstream
* adj: removed normalize_module_layout
* chore(deps): bump the crates group with 2 updates
* chore(tools): update notify binary [skip ci]
* chore(deps): bump rustls-webpki
* chore: bump webui submodule
* Update dependabot.yml
* Remove leftover EROFS module tool
* refactor: Fixed the issue with the size of the statistics
* BREAKING CHANGE: feat: The erofs is marked as deprecated
* ci: add caches to compilation workflows
* xtask: adj: adj target platform(https://github.com/Tools-cx-app/meta-magic_mount-rs/pull/31)
* Fix EROFS magic fallback and logging
* Fix EROFS empty remount handling
* ci(workflow): fix unrecognized 'secrets' context in if conditions## v3.1.6

Changes since v3.1.5:
* chore: fmt
* adj: Adjusting loop logic
* chore: make cargo clippy
* fix: Fixing layout errors
* chore: fmt
* feat: removed trait MountDriver in backend
* fix: fix glob rules again
* fix: make clippy happy
* fix: restore missing utils module and logging statements
* perf: eliminate O(N^2) tree cloning in magic mount and fix I/O safety
* fix: resolve critical mount bugs, ext4 inode exhaustion, and strict sync limits
* fix: fix error glob rules
* improve: Delete all imgs before mounting img.
* chore(deps): bump quinn-proto from 0.11.13 to 0.11.14 in /tools/notify in the cargo group across 1 directory (#249)
* feat(issue): add kernel version & hook type fields with auto-labeling
* chore: update license headers [skip ci]
* ci: delete unused workflow i18n
* ci: fix webui submodule path
* chore: add hybrid-mount-webui-md3 as webui submodule
* chore: remove webui folder for submodule migration
* chore(tools): update notify binary [skip ci]
* chore(deps): update dependencies in Cargo.lock
* chore(deps-dev): bump eslint in /webui in the crates group
* chore(deps): bump the crates group with 2 updates
* fix: make clippy happy
* refactor: remove random kworker camouflage feature
* feat: refactor logger system
* feat: add const_format dependency and refactor path constants
* feat: normalize module directory layout during sync
* chore(logging):logger tag to "Hybrid_Logger"
* ci: Simplify commit and push steps in workflow (#242)
* chore(tools): update notify binary [skip ci]
* chore(deps): bump aws-lc-sys
* chore(tools): update notify binary [skip ci]
* chore(deps): bump the crates group in /tools/notify with 2 updates
* chore(deps): bump zip from 8.1.0 to 8.2.0 in the crates group
* chore(release): sync version v3.1.5 [skip ci]## v3.1.5

Changes since v3.1.4:
* fix(core): expose full anyhow error chain and sanitize newlines for module.prop
* feat(core): catch daemon startup errors and display crash reason in module description
* feat(i18n): add step to delete old translation branch in workflow
* chore(deps-dev): bump globals from 17.3.0 to 17.4.0 in /webui in the crates group (#234)
* [skip ci]fix: update image source and correct binary name in README files
* chore(deps): bump actions/upload-artifact in the crates group
* New Crowdin translations by GitHub Action
* refactor: remove unused import of Show from ConfigTab component
* refactor: remove umount coexistence option and optimize ModulesTab performance
* Refactor store usage to uiStore and moduleStore across components
* feat: refactor application structure and implement new store management for configuration, modules, and system state
* fix(webui): resolve swipe stuck issue caused by requestAnimationFrame race condition
* feat: add Vietnamese translation for Hybrid Mount (#229)
* fix: fix error handling when scan modules (#228)
* feat(perf): implement UI performance optimizations
* chore(release): sync version v3.1.4 [skip ci]## v3.1.4

Changes since v3.1.3:
* fix(planner): correct module partition directory detection logic
* chore(deps): bump rollup## v3.1.2

Changes since v3.1.1:
* feat: add remote release step for KernelSU-Repo in workflow
* fix: correct typo in module summary
* chore(release): sync version v3.1.1 [skip ci]## v3.1.1

Changes since v3.1.0:
* daemon: using ksu's override.description api for description overriding
* chore(deps): bump ajv
* chore: remove unused fs import from mount.rs
* chore(tools): update notify binary [skip ci]
* feat: add branch name to Telegram notification and improve zip file detection
* feat: add webuiIcon parameter to module.prop generation
* feat: update launcher icon
* feat: add webui shortcut button
* chore(deps): update webui deps
* feat: removed useless read self mounts
* fix: fix typo
* chore: make cargo clippy happy
* docs: moved README to docs/
* refactor: abstract mount backend and storage implementations using traits
* fix: update refactored `fs` utility imports and function calls
* chore(deps): bump the crates group with 3 updates
* refactor: move fs module from utils to sys
* chore(release): sync version v3.1.0 [skip ci]## v3.1.0

Changes since v3.0.2:
* chore: add module.prop to gitignore
* fix: fix error handle logic
* feat: dropped folder check when umount
* chore: fmt
* feat: dropped zygisk check
* chore: removed module.prop
* feat: only use MNT_DETACH to umount
* workflow: fix workflow fmt
* refactor: ci&release logic
* feat: add overlay supported check
* chore: fmt && make cargo clippy happy (#215)
* fix: cargo fmt
* chore: fmt && make cargo clippy happy
* fix: fix nuke failed && fix ap no hidden ext4 loop
* feat(deps): bump && removed useless deps
* refactor: refactor mount_ext4
* fix: fix build
* feat: dropped poaceae subcommand
* chore(tools): update notify binary [skip ci]
* fix: fix build
* notify: make binary size less
* chore: fix gitignore
* refactor: refactor ignore partitions logic
* Change build command to use CI configuration
* Refactor:build_full function to handle CI and archs
* fix: fix error handling methods
* feat: dropped tmpfs setting
* opt: Optimize the logic of donnot umount
* feat: add ignore paths in umount
* feat: Make the errors of the fsopen operation more detailed
* fix: fix try umount flags
* feat: add umount successful log
* fix: correct modules name in some pathes
* chore(tools): update notify binary [skip ci]
* build: unify project naming to Hybrid-Mount and fix xtask syntax
* Revert "chore: rename package name in Cargo.toml"
* workflow: rename build.yml
* chore: rename package name in Cargo.toml
* xtask: refactor generate the module.prop
* chore(deps): bump tgbot from 0.41.0 to 0.42.0 in /tools/notify in the crates group (#212)
* chore(deps): update toml requirement from 0.9 to 1.0 in the crates group (#211)
* chore(release): bump version to v3.0.2 [skip ci]## v3.0.2

Changes since v3.0.14:
* chore: bump to v3.0.2
* build: inject release flag into webui constants and use it for logo display
* chore: fmt
* chore(release): bump version to v3.0.14 [skip ci]