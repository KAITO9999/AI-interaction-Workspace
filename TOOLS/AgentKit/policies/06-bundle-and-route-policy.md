# Tool bundle and download-route policy

- Bundle creation uses an explicit allowlist, deterministic relative paths, SHA-256 manifest, and ZIP output. Never package secrets or the whole home directory by default.
- Route probe is a separate bounded diagnostic. Test HEAD and small Range GET routes independently; record status/content type/redirect/failure without downloading the full artifact.
- A route probe is not the downloader. Do not execute or install downloaded content.
- Use HTTPS only; cap timeout and response bytes. Record that authenticated browser/connector routes are outside URL-level probing.
- Provide a portable ZIP and direct repository/PR links so an AI agent can retrieve files without manual copy-paste where the environment allows it.
