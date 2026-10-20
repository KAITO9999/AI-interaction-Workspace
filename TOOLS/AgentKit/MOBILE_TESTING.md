# AgentKit smartphone test profiles

This feature assigns smartphone-oriented resource budgets and performs a static Android compatibility preflight. It does **not** emulate a phone, install an APK, run the application, or benchmark CPU/GPU, frame rate, battery, thermals, or memory pressure.

## Profiles

| Profile | Configured RAM budget | Default Android gate |
|---|---:|---|
| Low-end | 4 GB | Android 11 (API 30) |
| Mid-end | 8 GB | Android 15 (API 35) |
| Mid-high | 12 GB | No default Android version |
| High-end | 16 GB | No default Android version |

The RAM values are test-budget settings, not assertions that every phone in a marketing tier has exactly that much usable RAM. No CPU core-count, clock-rate, GPU, storage-speed, or thermal limits are invented: the current AgentKit source did not contain an existing smartphone hardware profile to tune.

## Run

From the repository root:

```sh
python3 TOOLS/AgentKit/mobile_test.py --root path/to/android-project
python3 TOOLS/AgentKit/mobile_test.py --root path/to/android-project --profile low-end
python3 TOOLS/AgentKit/mobile_test.py --root path/to/android-project --profile low-end --profile mid-end
python3 TOOLS/AgentKit/mobile_test.py --root path/to/android-project --android-version 11
python3 TOOLS/AgentKit/mobile_test.py --root path/to/android-project --min-sdk 23 --json /tmp/mobile-test-plan.json
```

If `--profile` is omitted, all four profiles are assigned automatically. If `--android-version` is specified, it overrides each selected profile's default Android target. `--min-sdk` is an explicit override for projects where Gradle variables, version catalogs, convention plugins, or generated manifests prevent literal detection.

## Automatic compatibility gate

- A literal `minSdkVersion` is read from common Android manifest or Gradle locations.
- If the app's `minSdkVersion` is higher than the selected Android target's API level, that profile is marked `rejected_incompatible` and the preflight exits non-zero.
- For the default low-end profile, an app requiring API 31 or newer is therefore rejected for Android 11 (API 30).
- If the minimum SDK cannot be determined, a version-gated profile is marked `needs_review_min_sdk_unknown` and blocked rather than being assumed compatible. Supply `--min-sdk` after verifying the effective Gradle configuration.
- Mid-high and high-end profiles have no default Android-version target. They receive a resource profile, but Android compatibility is not asserted unless `--android-version` is supplied.
- Non-Android projects are reported as such; the tool does not claim Android compatibility was checked.

The current gate compares Android's minimum supported API level with the requested target. It does not prove that an app works on that OS release. Actual compatibility still requires a matching emulator or physical-device test.
