# Runtime profile and workload model policy

## Required behavior
- Never inspect the host to infer the user's target device. Hardware figures are profile inputs, not host facts.
- Default execution evaluates all profiles in parallel/sequential batch mode and writes one report per profile. "Parallel" here means independent profile runs in one invocation; no unbounded process fan-out.
- Profiles are named `low`, `mid`, `mid-high`, and `high-end`. Default clock/core/RAM/bandwidth figures are explicit, versioned reference assumptions and must be editable.
- Do not convert clock rate or core count directly into a universal JS throughput multiplier. Core count only matters when the workload explicitly models worker/native parallelism.
- Runtime estimates require a bounded workload scenario and measured target-runtime calibration ranges. If missing, return `INSUFFICIENT_DATA`, not a guessed number.
- Report a range and confidence, list assumptions, input hashes, calibration method and source URLs. Source URLs are metadata, not independently verified evidence.
- Network/API latency is a separate measured range. Account for concurrency, batches, rate limits, and ordering; do not assume parallelization is semantically safe.
- Keep per-profile reports and append-only logs separate. Prevent output paths from overwriting source or input files.
- User can choose a single profile for debugging, but default is all four.

## Evidence policy
Use representative measurements and official benchmark methodologies. Aggregate scores are not universal operations-per-second. See [V8 real-world performance](https://v8.dev/blog/real-world-performance), [JetStream 3](https://webkit.org/blog/17899/introducing-the-jetstream-3-benchmark-suite/), and [Speedometer](https://github.com/WebKit/Speedometer).
