# Language, platform, and graphics audit policy

## Language coverage
- Python is the coordinator and report format. Keep parsers and platform-specific code in isolated modules only when Python cannot safely or reliably perform the check.
- Initial static coverage includes C, C++, Rust, Java/Kotlin, JavaScript/TypeScript, Android manifests/Gradle, and GLSL/shader source.
- Language detection is not a substitute for a compiler, type checker, linker, sanitizer, GPU validation layer, or device test. Each finding must label heuristic confidence.
- Kotlin UI analysis should distinguish main-thread work, coroutine dispatch, blocking calls, recomposition/layout churn, and lifecycle-sensitive work. Do not claim full call-graph certainty from regex.
- Native ABI inventory includes AArch64/ARM64, x86-64 (Intel/AMD ISA family), and 32-bit x86. ISA, OS, ABI, CPU features, and package availability are separate compatibility gates.

## Baseline policy (initial proposal; adjust for target market)
- Android minimum API: 30 (Android 11), used as a project security/support policy gate. It is not a universal claim that API 29 and older are inherently unsafe.
- OpenGL ES minimum: 3.0. Android officially documents ES 3.0 from API 18 onward, but actual GPU/driver implementation is required. Manifest declarations are static requirements, not live hardware probes.
- Vulkan Android target: minimum API 1.1 for the broad modern baseline; test actual device/driver support and required extensions. Treat Vulkan 1.3 as optional advanced capability unless target fleet is constrained. Vulkan 1.1 is required on new 64-bit Android devices launched with Android 10 or later, but OS version alone does not prove driver support.
- Vulkan 1.0 remains relevant for legacy compatibility checks, but should not be the recommended baseline for new 64-bit Android targets.
- Detect minimum requirements from AndroidManifest.xml, Gradle/NDK ABI filters, build files, source feature calls, and runtime fallback branches where possible. Missing evidence must be reported as unknown, not "supported."

## Sources
- [Android OpenGL ES versions and manifest requirements](https://developer.android.com/develop/ui/views/graphics/opengl/about-opengl)
- [Android Vulkan device/API guidance](https://developer.android.com/games/develop/vulkan/native-engine-support)
- [Vulkan versioning and feature compatibility](https://docs.vulkan.org/guide/latest/versions.html)
