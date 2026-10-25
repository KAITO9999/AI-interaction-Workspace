# Android APK build policy

## Hard default: do not compile Android packages on the phone

Do not run Android APK/AAB build or compilation workloads on the user's Android/Termux device. This is a deliberate resource-protection policy, not a suggestion. If asked to compile locally, refuse that execution path and continue with the remote-build route.

This prohibition includes, but is not limited to:
- Gradle/Android Gradle Plugin tasks such as `assembleDebug`, `assembleRelease`, `bundleDebug`, and `bundleRelease`, whether invoked through `gradle`, `./gradlew`, an IDE, or a wrapper script.
- Android native compilation/build pipelines using NDK/CMake/Ninja, Kotlin/Java compilation as part of an Android app build, and packaging/signing stages such as `aapt`, `d8`, `dx`, `zipalign`, or `apksigner` when they form part of an APK/AAB build.
- Starting, resuming, or retrying an on-device build indirectly through a shell, background task, script, MCP tool, or AgentKit.

Reading build files, reviewing source, editing code, checking workflow YAML, inspecting an existing APK, running lightweight static checks, and deleting confirmed generated build outputs are allowed. Do not confuse those activities with compiling an APK.

## Preferred path: GitHub-hosted build

1. Identify the Android repository and inspect its existing GitHub Actions workflows before creating a substitute.
2. Prefer the repository's existing hosted build workflow. For a project with a working build-check workflow, use a branch/PR or the workflow's supported trigger and inspect the actual run result.
3. If no hosted build workflow exists, add a project-specific GitHub Actions workflow in a focused branch/PR. Use a GitHub-hosted runner, pin/configure the required JDK and Gradle versions, and upload the APK as an artifact when the user needs to install or inspect it.
4. Never commit generated APK/AAB files, keystores, signing credentials, or local build caches. Release signing must use repository secrets and an explicitly requested release workflow; do not trigger a release merely to test compilation.
5. Report the workflow URL and actual job result. A workflow file existing, a build being queued, or source-level checks passing is not evidence that an APK was successfully built.

## Failure and fallback

If GitHub Actions cannot run because of repository permissions, missing secrets, runner limits, or workflow failure, report the concrete blocker and offer a reviewable workflow fix. Do not fall back to compiling on the phone. Do not silently download dependencies, alter the Android SDK/NDK installation, clear the global Gradle cache, or delete signing keys as a workaround.

## Build-output cleanup

Only delete generated outputs whose role is verified (for example, project `build/` directories, APK/AAB outputs, DEX/class intermediates, and APK signature sidecars). Preserve source files, manifests, keystores/JKS files, downloaded APKs, and the global Gradle cache unless separately requested and confirmed.
