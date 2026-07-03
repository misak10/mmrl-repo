# COPG Spoof Module
#### **Support Group**:
- https://t.me/TheAOSP
#### **Telegram Channel**:
- https://t.me/COPG_module
---
## v5.5.1
### GPU spoofing (per-app) — PRO feature, use at your own risk
*   **GPU spoofing is unlocked with a COPG PRO license.** Every other spoof (CPU, COW props, Android ID, block CPU, tweaks) stays **free** — GPU is the one PRO-gated toggle. On the free tier the GPU row shows a lock; get a license to enable it.
*   **Fake the GPU per app — and it actually reaches the game now.** A **GPU Spoofing** toggle in the package editor lets a game read a *different* graphics chip across **OpenGL ES** (`GL_RENDERER`, `GL_VENDOR`, `GL_VERSION`, GLSL version), **EGL** (`EGL_VERSION`), and **Vulkan** (device name, vendor ID, device ID, API version, driver version, features, and reported VRAM). Games that resolve their graphics calls through the driver dispatcher are now covered — the spoof lands where it did nothing before.
*   **Full profile editor.** It opens a manifest-driven **GPU profile picker** where profiles can be added, **edited**, and deleted. Each profile has the basics (name / renderer / vendor / Vulkan vendor ID) plus a collapsible **Advanced spoofs** section for the GL/EGL/Vulkan extras. The two risky ones — **Fake GL extensions** and **Force all Vulkan features** — sit behind their own warnings, since claiming a capability the real GPU lacks can crash a game.
*   **Gated behind a clear warning — on purpose.** Unlike every other spoof in COPG, GPU spoofing **stays mapped in the game's memory while it runs**, so it *can* be detected. Turning it on pops a red **"use at your own risk"** confirmation with a 5-second cooldown. **Do not enable it for anti-cheat games** — it's meant for benchmarking, compatibility checks, and curiosity, not for getting past bans.
*   **Hidden where it can't work.** The spoof's hook is ARM-only, so the toggle auto-hides on x86 / x86_64 (Intel) devices and emulators where it can't attach.
*   **See your real GPU.** The System tab now shows the device's actual GPU so you know what you're spoofing away from.

### Unified package model — one kind of package, tags for everything
*   **Every package is now a device package.** The old **Device / CPU-Only / Blocked** types are gone. Each app sits on a device profile and you flip exactly the spoofs you want — CPU, GPU, COW props, Android ID, Block CPU — as independent toggles in a tidy **Spoofing** group, with the comfort tweaks (DND / auto-brightness / keep-screen-on / no-log) in a **Tweaks** group.
*   **New "This Device" profile.** A built-in profile that keeps your **real** device identity but still lets you add CPU / GPU / COW / Android-ID spoofs or block CPU per app — handy for apps you don't want to disguise but do want to tweak.
*   **Automatic migration.** Old configs with the global CPU block-list / CPU-only list are converted the moment they load, so existing setups keep working — just reorganized into the new model.
*   **Block CPU anywhere.** Any package on any profile (including This Device) can be set to force the **real** processor. Still mutually exclusive with CPU Spoofing.

### CPU spoof — survives resume and backgrounding
*   **Optional foreground reconcile.** A new opt-in keeps the correct `cpuinfo` mounted as you switch apps, fixing the case where resuming or backgrounding a game could quietly revert it to the real CPU. The Zygisk helper still mounts at launch; this covers everything after.

### Smaller stuff
*   **Dropped 32-bit x86.** The build no longer ships the rarely-used 32-bit x86 library (arm64, arm, and x86_64 are unchanged).
*   **CPU profiles flag missing files.** A CPU profile whose `cpuinfo` file isn't actually present is now clearly marked in the picker instead of silently doing nothing.
*   **Custom profiles are deletable**, and CPU/GPU profiles sync from GitHub by manifest.

### WebUI & polish
*   **Launch a spoofed app from the library.** Installed packages now show a **play** button that force-stops and relaunches the app, so it restarts through a fresh spoof — no need to leave the WebUI and find it yourself.
*   **AMOLED on System theme.** With the theme set to **System**, dark mode now uses **AMOLED black** instead of plain dark (the explicit Dark option is unchanged).
*   **Custom CPU/GPU forms tidied.** The "add profile" fields show their titles as proper labels above each box, matching the device and package editors, and the CPU/GPU add & edit sheets now lift above the on-screen keyboard so nothing hides while you type.
*   **GPU row + fuller Kernel row.** The System tab now shows your real **GPU**, and the **Kernel** row includes the architecture (e.g. `5.10.404R aarch64`) instead of just the release.

---
## v5.4.0
### Per-app CPU spoofing — pick any chip, or load your own
*   **Choose a CPU model per app.** With CPU Spoofing now opens a **CPU profile picker** so each game can pretend to run on a *specific* chip. Ships with **8 profiles** out of the box — Qualcomm Snapdragon 8 Elite, HiSilicon Kirin 9000 / 9000S / 9020 / 9020A / 9030 Pro, and Xiaomi Xring O1 / O3.
*   **Load your own `cpuinfo`.** Tap the **＋** next to the picker's search, choose any `cpuinfo` file from storage, give it a name, and it's saved into the module — **reusable across every app**, not just the one you're editing.
*   **CPU spoof for CPU-Only packages too.** Packages in the CPU-Only list now get the same model picker.
*   **Cleaner tags.** A spoofed app now carries a single `cpu=` tag (with the model baked in) instead of a redundant pair — existing setups keep working and tidy themselves up when you re-save them.

### Mobile Legends (and other multi-process games) fixed
*   **Child processes are now spoofed.** Games that run extra processes (e.g. Mobile Legends' `:UnityKillsMe`) used to leak the **real** device in those processes because COPG only matched the exact process name. It now matches the **base package**, so every process of the game sees the spoof.
*   **Added Mobile Legends variants** (Global, US, VNG, and the Moonton / Samsung / Huawei builds) to the device list.

### Per-app ANDROID_ID
*   **Opt an app into a unique ANDROID_ID.** A new **Spoof Android ID** toggle in the package editor derives a per-app ID from the device profile's seed — so each app gets a *different* ID (matching how real Android 8+ behaves), and the ⓘ previews the exact value the app will read. Still zero-residency: the module unloads before the app runs.

### Stability
*   **Fixed a crash with COW prop spoof on some devices.** On certain phones (e.g. OnePlus / Android 16) a spoofed property was stored in a "long" form that the COW edit corrupted, crashing apps at launch. COPG now detects those and skips them safely — the device is still spoofed via the Build.* fields; nothing crashes.

### WebUI & polish
*   Device editor: the **Serial** field moved into the **Advanced build props** group.
*   Smoother in-app config (background-safe app-icon downloads, tightened security policy).
*   **All 8 languages** brought to full parity.

---
## v5.3.1
### Hotfix — CPU spoof rolled back (was causing bans)
*   **Reverted the new CPU spoof method.** v5.3.0 mounted the fake `cpuinfo` inside each game's own process — but that mount is **visible to the app itself** (`/proc/self/mountinfo`), which some games flagged as tampering and **banned**. v5.3.1 restores the **previous CPU spoof** (system-level mount via the helper) that does not expose the mount to the app.
*   **CPU blocking is opt-in again (like v4.7.3) — no more 50% failures.** The intermediate 5.1.x builds had every non-spoofed app in a profile force a global CPU "unblock", which raced the spoof mounts so it only landed about half the time. Now only **With CPU Spoofing** mounts and only an explicit block unmounts; everything else leaves the mount alone — so CPU spoof applies reliably again.
*   **New per-app "Block CPU" toggle.** A package inside a device profile can now be set to **Block CPU** (forces it to see the real processor) right from the package editor — handy for keeping a banking app on real CPU while games in the same profile are spoofed. It's the opposite of With CPU Spoofing, so only one can be on.
*   **Everything else from v5.3.0 stays:** COW prop spoof, ANDROID_ID spoofing, the extra Build fields, and the tablet navigation-bar fix are all unaffected (none of them mount anything).

> If you installed v5.3.0, **update to v5.3.1** and clear data / force-stop any affected game.

---
## v5.3.0
### New Stealth Spoofing Engine
*   **COW prop spoof replaces GOT hooking.** The old method left a chunk of COPG's code mapped in the game's memory (detectable). The new **`cow` tag** edits device props (`ro.product.*`, fingerprint, and any custom prop) through a per-process copy-on-write page and then **unloads the module before the app runs** — so an anti-cheat scanning memory finds **nothing of COPG mapped**. Same effect, far stealthier. Only your app sees the fake; the system and other apps are untouched.
*   **ANDROID_ID spoofing (no reboot).** Set a per-device `ANDROID_ID` and apps read the fake value with **no reboot and no detectable hook** — the value is planted in the in-process settings cache. New field in the device editor with a **Generate** button.
*   **Serial spoofing.** Optional `Build.SERIAL` + `ro.serialno` per device, also with a Generate button.

### More Build Fields
*   **12 extra Build identifiers** can now be faked per device — `BOARD, HARDWARE, DISPLAY, ID, BOOTLOADER, TAGS, TYPE, SOC_MANUFACTURER, SOC_MODEL, SECURITY_PATCH, INCREMENTAL, CODENAME` — set both as `Build.*` fields **and** their matching `ro.*` props. They live in a collapsible **Advanced build props** group in the device editor, all with example placeholders.

### CPU Spoof — Reliable Every Launch
*   **Fixed the ~50% CPU-spoof failure.** The fake `cpuinfo` is now mounted **inside each game's own process**, in a private mount namespace, instead of through a shared root helper that raced against the per-app block logic. It now lands **every launch**, deterministically. (Per-app only — system and other apps still see the real CPU.)
*   **Removed the Zygisk companion entirely.** CPU spoofing is pure in-process C++ now — one less moving part, nothing extra mapped in the game's memory.

### WebUI & Cleanup
*   **Removed the "Blocked" package type / block list.** Redundant — leaving **With CPU Spoofing** off already blocks the CPU fake (the default). The Type picker is now just **Device** and **CPU Only**.
*   **Keyboard-aware editor sheets** — forms lift above the on-screen keyboard instead of hiding behind it.
*   **Example placeholders** on every device/package field (a coherent Pixel 8 Pro set) so the expected format is obvious.
*   Editing a device now **merges** over the saved profile instead of rebuilding it, preserving advanced keys.
*   Fixed the bottom navigation / ripple rendering off-center on tablets and wide screens.

---
## v5.1.1
### Fully Systemless — no /system mount, no metamodule
*   **No metamodule needed.** COPG no longer touches `/system` at all, so on newer KernelSU you **no longer need the system-overlay metamodule** — it installs and runs as a plain module on KernelSU / Magisk / APatch.
*   **Removed the Google Photos "unlimited backup" spoof.** It worked by overlaying Pixel feature-flag files into `/system`, which forced a system mount (and required that metamodule on newer KernelSU). Dropping it makes COPG **fully systemless** — lighter, cleaner, and free of mount conflicts.
*   **Removed `system.prop`.** The `game_default_frame_rate.disabled` prop meant to lift Android 15's 60fps game cap backfired on some ROMs (read inverted → games **locked** to 60fps). Removed — affected devices now run at full refresh.

### Fixes
*   **Console no longer freezes the UI.** A never-ending command typed in the console (bare `logcat`, `top`, `tail -f`) used to hang the whole WebUI, because the bridge waits for the process to exit. Streaming commands are now guarded: `logcat` auto-runs as `logcat -d`, and other infinite commands are refused with a hint.
*   **Zygisk detection on install.** Fixed two false negatives — Zygisk Next *disabled* + ReZygisk *enabled* no longer aborts install, and Magisk's built-in Zygisk being **ON** is now caught (it silently breaks Zygisk Next / ReZygisk).

---
## v5.1.0
### Faster, Smarter App Icons
*   **No more lag.** Package icons no longer hammer the root bridge one-by-one — a single background task fetches everything, so the Library stays smooth while icons fill in.
*   **Three sources:** Google Play → **APKPure** → F-Droid, so games missing from the Play Store (region-locked and the like) still get a real icon.
*   **Works offline.** Once fetched, icons are cached on-device and load instantly with no network.
*   **Refresh App Icons:** a new action in **Backup & Sync** wipes the icon cache and re-downloads everything — handy when a game changes its icon.

### WebUI Polish
*   **Fullscreen toggle:** an immersive mode that hides the status bar, in Settings.
*   **Device Profile picker:** choosing a device for a package is now a searchable, sortable list instead of a plain dropdown.
*   Fixed the black band under the status bar / notch in fullscreen, plus navigation-bar and sort/filter spacing touch-ups.

### Game List
*   Refreshed the bundled device and game profiles (`COPG.json` / `list.json`).

## v5.0.0
### A Complete Reimagining
*   **Brand-New WebUI:** The entire interface was rebuilt from the ground up with a modern, app-like design — replacing the old single-file UI with a fast, modular one.
*   **Library:** Devices and packages live in one place now, with search, sorting, filters, swipe-between-tabs, and live **Installed** badges.
*   **App Picker:** Add games straight from your installed apps, complete with real names and icons.
*   **Backup & Sync:** Export and restore your config, **Sync from GitHub** to pull the latest game list, and export logs — all saved to `Download/COPG`.
*   **Built-In Console:** Run shell commands, tail logcat, and save logs without ever leaving the app.
*   **Theming & Language:** Dark / Light / AMOLED / Auto themes with one-tap switching and haptic feedback. Now ships in **8 languages** — English, Persian (RTL), Arabic (RTL), German, Spanish, Indonesian, Thai and Chinese.
*   **Fresh app icon** and a cleaner WebUI title.

### Simpler, Safer Spoofing
*   **CPU spoof is now blocked by default.** Every device package is safe out of the box — flip on **With CPU Spoofing** only for the games that need the chipset faked.
*   **Retired the `blocked` and `notweak` tags.** They are no longer needed; a single clear toggle replaces them.
*   **New — GOT Hooking:** an advanced in-memory spoof method for stubborn apps that ignore the normal spoof. Off by default and gated behind a clear risk warning — it can be detected and may even get a game account banned, so only enable it if you know you need it.
*   Plain-language ℹ️ explanations sit next to every toggle, so you always know what each one does.
*   Added support of x84_64 and x86 devices/emulators.

### Per-App Game Tweaks (New)
*   Choose comfort tweaks **per game** — applied only while you are playing and automatically restored when you leave:
    *   **Do Not Disturb**, **Disable Auto-Brightness**, **Keep Screen On**, **Disable Logging**.
*   Smarter switching: hopping between games applies only the tweaks each one asks for — no more notification floods at the wrong moment.
*   Works for both device-spoof and CPU-spoof packages.

### Improvements
*   Rewrote the tweak controller to apply tweaks **per package** with precise apply/restore, dropping the old global toggle file.
*   Allowlist-based tag parsing — unknown or future tags are safely ignored everywhere in the module.
*   Reorganized the whole project (`src/`, `module/`) with a single clean CI workflow and an on-device build script.

### New Devices & Game Profiles
*   **New device:** **Infinix GT 50 Pro** added to the spoof library.
*   **Device refresh:** **RedMagic 10 Pro → RedMagic 11 Pro**, and **HONOR Magic V2 RSR → Sony Xperia 1 III** (old profiles removed, replaced with newer hardware).
*   **PUBG Mobile:** unlocked **HDR + 90+ FPS**.
*   **Free Fire / Free Fire MAX:** unlocked **144 FPS**.
*   **Asphalt 9:** unlocked **120 FPS**.

### Note
*   This is a massive overhaul and still a work in progress — more is on the way. Please report anything unexpected in the support group.
*   **Translations:** going forward only **English** and **Persian** are officially maintained. The other languages are community-driven — contributions and fixes via pull request are very welcome.

### Summary
v5.0.0 is the biggest release yet: a ground-up WebUI rewrite, a simpler and safer spoofing model (block-by-default CPU), brand-new per-app game tweaks, and a cleaner, faster foundation under the hood.
## v4.7.3
- fix version code
## v4.7.2
- Fixed camera/setting some apps were crashing (removed resetprop feature)
- Removed camera apps from black list (COPG.JSON)
- Dropped FIFA mobile support.
## v4.7.1
### HOTFIX Update
- Added blocked tag to all device packages for safety
- Fixed Update Gameslist and action button
### Note: 
- I recommend you add your game always as blocked package expect games those aren't working with device spoof only or they only work with CPU spoof

## v4.7.0
### New Features
*   **Safer Spoof Method:** Enhanced safety and reliability of the spoofing process.
*   **Android/SDK Spoof:** Added optional Android SDK version spoofing capability.
*   **Smart CPU Spoof (Snapdragon 8 Elite):** Introduces intelligent, app-targeted CPU information spoofing via `/proc/cpuinfo`.
*   **Enhanced Configuration (`COPG.json`):**
    *   Configuration file renamed from `config.json` to `COPG.json` (original `config.json` remains for MMRL app settings).
    *   **`blocked` tag:** For apps/games where you want device model spoofing but need to hide/remove CPU spoof.
    *   **`with_cpu` tag:** For apps/games where you want both device model spoofing and CPU spoofing applied together.
    *   **`cpu_only_packages`:** For apps/games where you want **only** CPU spoofing applied (also resets device properties to original via `resetprop`).
    *   **`blocklist`:** To hide/remove CPU spoof and reset properties for sensitive apps (e.g., banking apps, camera apps in Matrix ROM, system settings in some ROMs).
    *   **`notweak` tag:** Significantly improves I/O performance and reduces overhead for specified packages.
*   **Smarter Tweak Controller:** Improved configuration handling logic.
*   **Enhanced WebUI:**
    *   Added sorting and filtering capabilities.
    *   Source code cleanup and full support for all new configuration changes.
*   **Updated Game Support:**
    *   Added support for **Fortnite** and **Farlight 84**.
    *   Removed support for **Mobile Legends: Bang Bang**.

### Improvements
*   **Permission & SELinux:** Better handling during `COPG.json` restoration.
*   **Logging:**
    *   Simplified Zygisk logs.
    *   Changed log tag from `SpoofModule` to `COPGModule`.
*   **Configuration Management:** Removed deprecated `ignorelist.txt` and associated functions from the controller and WebUI.

### Summary
This major release focuses on intelligent, app-specific spoofing with the new Smart CPU feature, a more powerful and granular configuration system via `COPG.json`, a refined WebUI, and significant under-the-hood optimizations for performance and stability.
## v4.6.0
- Added new spoof method with resetprop to zygisk
- Rewrote COPG toggle manager from shell script to C++
- Rewrote config watcher from C to C++ and integrated into COPG toggle manager
- Improved performance for COPG toggle manager
- Fixed toggle persistence issue with smarter toggle management (now DND and screen time turns back to default when you close the game)
- Reduced CPU, RAM, and storage overhead for COPG toggle manager
- Cleaned up installation output logs
- Fixed FIFA max FPS unlock
- Added Galaxy Z Fold 5 support for FIFA
- Removed jq binary dependency
- Removed legacy copg_watcher binary
- Added donation pop-up to WebUI
- Added support pop-up to WebUI
- Changed license from OIL to AGPL-3.0 (now 100% free software)
## v4.5.5
- Fixed config parsing errors when you open a target app/game (e.g. Invalid package list for key PACKAGES_...)
- Fixed font color of save log popup in dark mode 
## v4.5.4
- Fixed config.json parsing for apps/games containing underscore ("_") characters in their package names (Zygisk)
- Optimized CPU usage for the config_watcher binary
- Reduced module file size and binary sizes
- Added Realme 15 Pro 5G device support and migrated Arena of Valor packages from Realme P3 5G
- Compiled all binaries with NDK 27
## v4.5.3 
- Fix config.json parsing issue which causes DND/Timeout and other toggles not working correctly 
## v4.5.2
- Removed the `/proc/cpuinfo` spoofing method due to its reliance on a mount technique that was flagged as suspicious by certain banking applications.
- Removed Fortnite 120 FPS unlock due to its dependency on `/proc/cpuinfo` spoofing.
## v4.5.1
- Spoofed the /proc/cpuinfo file to report the device as a Snapdragon 8 Elite.
   - This workaround tricks games like Fortnite, which rely on a strict CPU model check, into enabling hidden graphics settings (e.g., 120 fps mode).
- Added Fortnite 120 fps
- Updated icon for WebUI-X and mmrl repo Special Thanks to [AmbadeuZ](https://t.me/AmbadeuZ) for the new Icon
- Updated banner for KernelSU-Next and mmrl Thanks to [AmbadeuZ](https://t.me/AmbadeuZ) for the new Banner
## v4.5.0
- Added better spoof method to hide from anticheat (no freefire or delta force ban anymore)
- Added [atexit](https://github.com/5ec1cff/local_cxa_atexit_finalize_impl) by [5ec1cff](https://github.com/5ec1cff) to prevent detection from banking apps/ Anti cheats
- Added better config loading with less overhead and better performance
- Added Backup/Restore feature to WebUI
- Added save logcat file feature to the WebUI
- Added Better logcat output (now only shows errors)
- Added freeFire and freefire max 120 fps
- Added Clash of Titans (India)
- Added Wuthering Waves
- Added Arena of Valor/Honor of Kings all regions
- Removed Fortnite (because spoof doesn't work on it anymore) i will try to add it later with 120 fps support 
- Removed Apex mobile because this game doesn't exist anymore 
## v4.3.6
- Removed freefire
- Added volume control for action script
- Added optional volume control for installing Google photos spoof
- Removed spoofSystemProperties function
## v4.3.5
- Added Next-WebUI package manager
- Removed shortcut button from WebUI (use WebUI-X app to create shortcut)
- added logcat to WebUI (Now you don't need terminal to send me logs)
- added copy button to WebUI console/logs/output
## v4.3.4
- Added FreeFire 120 fps
- Added delta force into game repo
- Added Netflix spoof 
- Cleanup and improving performance and safety
- added KernelSU Next banner
- UI improvement
## v4.3.3
- Fixed root detection by apps because of COPG
- Fixed Mx player, Telegraph and some apps crashing because COPG
- Add version info in installation script 
## v4.3.2
- secure spoofing
- fixed Rezygisk installation 
## v4.3.1
- Added Google photos spoof for unlimited backup and Ai reimagine feature
- Added modern app picker (Use MMRL or WebUI-X)
- Added Game names
- Added TikTok to unlock 1080 streaming
- Added Ignorelist to prevent Apps/Games from general tweaks (e.g. DND, Timeout and ...)
- Fixed some permission peroblems
- Fixed some styles
- Removed useless props (CPU info, Build id, display id)
- Dropped support Zygisk Standard/Native ( Unsafe)
- Fixed crashing on Older devices
- Added swipe snackbar to get rid of it
- Added improvement to snackbar
- Added installed label for installed items
- Added ignore label with explaining popup
- fixed visual bugs and improved packagename error
## v4.0.2
- Improved error logging for SpoofModule and WebUI
- Enhanced permission handling for config files
- Added smoother UI animations and transitions
- Improved device selection UI in the game tab
- Added error popup
- Added prevention for game duplication
- Fixed scroll bar overlapping issues
- Enhanced UI with field highlighting
- Added Delta Force support in config
- Removed reboot requiring with dynamic config check
- Fixed APatch installation issues
- Removed reboot popup
- added snackbar with cooldown animation
- added shortcut button/Support for WebUI-X app
## v3.3.4
- Added apatch support
- Added better architecture detection
- Added Zygisk Next disable detection
- Added better ouput log for installation
- Added multiple root detection
- Added better module deleting 
## v3.3.3
- Updated config and fixed Black Shark device model  
- Changed UI color details and improved dark mode  
- Improved UI/UX and smoothness  
- Enhanced animations  
- Smoother switching between tabs  
- Added logging to the module for better debugging  
## v3.3.2
- fix installation for magisk 
## v3.3.1
- Better installation script 
- removing unused files after installing 
## v3.3
- improved UI
- Added more animations
- added better logging UI
- Added Android version input
- Minor fix when user was adding a new device 
## v3.2.2
- update config
## v3.2.1
### Added
- **New UI Sections**:  
  - Dedicated tabs for *Devices* and *Games* management.  
  - Search bar for quick filtering.  
- **Device/Game Controls**:  
  - Add, edit, or remove devices/games directly from the UI.  
  - Swap devices per-game dynamically.  
- **Quality of Life**:  
  - `KEEP_SCREEN_ON` toggle (timeout: ~83 hours) with auto-reset on exit.  
  - Screen Timeout Toggle to prevent interruptions.  
  - Swipe gestures to navigate between tabs.  
- **Animations**: Smoother MIUI/HyperOS-style transitions.  

### Changed  
- **UI/UX**:  
  - Updated theme and improved visual consistency.  
  - Enhanced smoothness across interactions.  
- **Game Detection**:  
  - Replaced `grep` with `jq` for reliable package parsing (ignores `_DEVICE` keys).  
- **Multi-Game Handling**:  
  - Toggles persist while any game is active; reset only after all close.  

### Fixed  
- **Root Compatibility**: Fixed Magisk integration with Zygisk Next installation.  
- **Stability**: Better console error handling.  
- **Edge Cases**: Split-screen/switching between games no longer breaks settings.  

---  
*For older versions, refer to previous releases.*  

## v3.1.5
### What’s New?
- **UI Upgrades**  
  - Sleeker output log for clearer feedback.  
  - Dark/light theme toggle—your eyes will thank you!  
- **Remove ROM Limits**  
  - New prop kills FPS caps in games like PUBG Mobile.  
- **Saves Your Settings**  
  - Stores DND and brightness settings when you start gaming, restores them after.  
- **Better Handling**  
  - DND and brightness stay consistent during gameplay, reset only when you exit.
## v3.1.0
### What’s New?
- **Enhanced User Interface**: Revamped UI with smoother transitions and a modern vibe for a delightful experience.
- **Clear Console Button**: Added a handy "Clear" button to reset the log output with one tap—no more cluttered console!
- **Auto-Scrolling Logs**: New logs now auto-scroll like a Linux terminal, keeping you on the latest updates without manual effort.
- **Improved Log Animation**: Slicker animation when expanding the log output for a seamless reveal.
- **Smarter DND Backend**: Adjusted "Do Not Disturb" to priority mode when on, toning down its aggressive silence for a balanced feel.
### Removed
- **Reboot Button**: Ditched the reboot option to streamline the interface and keep it simple.
### Under the Hood
- Optimized animations for smoother performance across devices.
- Polished responsiveness for a snappier, more fluid feel.
## v3.0.3
- added webui 
- webui: added disable DND toggle 
- webui: added disable auto brightness  toggle
- webui: added stop logger toggle 
- webui: added update game list button
- webui/action: added game list compare 
- webui: added reboot pop-up question if game list updated
- webui: added reboot button with pop-up question
## v2.8
- trying to fix mid-game crashing
- improve ban spoof system
- **Note**: getting banned at your own risk
## v2.6
- better anti-cheat handling
- **Note**: getting banned at your own risk
## v2.5
- added better spoof for Call of duty anti-cheat
- **Note**: getting banned at your own risk
## v2.3
- added action button for downloading updated config if needed
- added Zygisk check for installing module
- **Note**: getting banned at your own risk 
## v2.2
- Cache JNI Calls for faster app game launch.
- removed logd for even faster launch.
## v2.1.1
- fix s24 ultra in config.json
## v2.1
- now you can add your game to config yourself and you don't need to ask for new update
- config direction: /data/adb/modules/COPG/config.json
## v2
- Added Mobile Legends `com.mobilelegends.mi` support - spoof as ZTE NX769J
- Added Brawl Stars `com.supercell.brawlstars` support - spoof as ZTE NX769J
- Added Diablo Immortal `com.blizzard.diablo.immortal` support - spoof as ZTE NX769J
- Added Arena Breakout `com.netease.newspike` support - spoof as ZTE NX769J
- Added Call of Duty: Warzone Mobile `com.activision.callofduty.warzone` support - spoof as ZTE NX769J
- Added PUBG: New State `com.pubg.newstate` support - spoof as ZTE NX769J
- Added Destiny Warfare `com.gamedevltd.destinywarfare` support - spoof as ZTE NX769J
- Added Drive or Die 2 `com.pikpok.dr2.play` support - spoof as ZTE NX769J
- Added CarX Highway Racing `com.CarXTech.highWay` support - spoof as ZTE NX769J
- Added Shadow Fight 3 `com.nekki.shadowfight3` support - spoof as ZTE NX769J
- Added Shadow Fight Arena `com.nekki.shadowfightarena` support - spoof as ZTE NX769J
- Added Asphalt 8 `com.gameloft.android.ANMP.GloftA8HM` support - spoof as ZTE NX769J
- Added Shadow Fight 2 `com.nekki.shadowfight` support - spoof as ZTE NX769J
- Added Need for Speed No Limits `com.ea.game.nfs14_row` support - spoof as ZTE NX769J
- Added Real Racing 3 `com.ea.games.r3_row` support - spoof as ZTE NX769J
- Added Squad Busters `com.supercell.squad` support - spoof as ZTE NX769J
- Added Battle Prime `com.blitzteam.battleprime` support - spoof as ZTE NX769J

- Added Honor of Kings `com.proximabeta.mf.uamo` support - spoof as Black Shark 4

- Added Apex Legends Mobile `com.ea.gp.apexlegendsmobilefps` support - spoof as Xiaomi Mi 11T PRO
- Added Tower of Fantasy `com.levelinfinite.hotta.gp` support - spoof as Xiaomi Mi 11T PRO
- Added Clash of Clans `com.supercell.clashofclans` support - spoof as Xiaomi Mi 11T PRO
- Added Mobile Legends (Vietnam) `com.vng.mlbbvn` support - spoof as Xiaomi Mi 11T PRO

- Added Arena of Valor (Global) `com.levelinfinite.sgameGlobal` support - spoof as Xiaomi Mi 13 Pro
- Added Arena of Valor (China) `com.tencent.tmgp.sgame` support - spoof as Xiaomi Mi 13 Pro
- Added PUBG Mobile (Korea) `com.pubg.krmobile` support - spoof as Xiaomi Mi 13 Pro
- Added PUBG Mobile (China) `com.rekoo.pubgm` support - spoof as Xiaomi Mi 13 Pro
- Added PUBG Mobile (Taiwan) `com.tencent.tmgp.pubgmhd` support - spoof as Xiaomi Mi 13 Pro
- Added PUBG Mobile (Vietnam) `com.vng.pubgmobile` support - spoof as Xiaomi Mi 13 Pro

- Added Blood Strike `com.netease.lztgglobal` support - spoof as OnePlus 8 PRO
- Added League of Legends: Wild Rift `com.riotgames.league.wildrift` support - spoof as OnePlus 8 PRO
- Added League of Legends: Wild Rift (Taiwan) `com.riotgames.league.wildrifttw` support - spoof as OnePlus 8 PRO
- Added League of Legends: Wild Rift (Vietnam) `com.riotgames.league.wildriftvn` support - spoof as OnePlus 8 PRO

- Added Fortnite `com.epicgames.fortnite` support - spoof as OnePlus 9 PRO
- Added Epic Games Portal `com.epicgames.portal` support - spoof as OnePlus 9 PRO
- Added League of Legends: Wild Rift (China) `com.tencent.lolm` support - spoof as OnePlus 9 PRO

- Added Mobile Legends: Bang Bang `com.mobile.legends` support - spoof as POCO F5

- Added Free Fire `com.dts.freefireth` support - spoof as Asus ROG Phone
- Added Free Fire MAX `com.dts.freefirethmax` support - spoof as Asus ROG Phone

- Added FIFA Mobile `com.ea.gp.fifamobile` support - spoof as Asus ROG Phone 6
- Added Asphalt 9 `com.gameloft.android.ANMP.GloftA9HM` support - spoof as Asus ROG Phone 6
- Added Shadowgun Legends `com.madfingergames.legends` support - spoof as Asus ROG Phone 6
- Added Black Desert Mobile `com.pearlabyss.blackdesertm` support - spoof as Asus ROG Phone 6
- Added Black Desert Mobile (Global) `com.pearlabyss.blackdesertm.gl` support - spoof as Asus ROG Phone 6

- Added Call of Duty: Mobile (Garena) `com.garena.game.codm` support - spoof as Lenovo TB-9707F
- Added Call of Duty: Mobile (Korea) `com.tencent.tmgp.kr.codm` support - spoof as Lenovo TB-9707F
- Added Call of Duty: Mobile (Vietnam) `com.vng.codmvn` support - spoof as Lenovo TB-9707F
---
## v1.0.5
- Added Fortnite support (spoof to s24 ultra)
- added mobile legends support (spoof to s24 ultra)

