AgentKit — AI-first Environment Probe & Workflow Helpers

Status: prototype / review required. Version 0.1.0. Python 3.9+ standard library only.

Safety: no privilege escalation, restriction bypass, or credential discovery. probe is heuristic. fetch-probe runs exactly one read-only git ls-remote attempt and stops on first error/timeout; it does not clone. Linux scripts cannot assume access to ChatGPT history. ingest reads only explicitly supplied file/stdin. Review reports before sharing.

Quick start:

    python3 TOOLS/AgentKit/agentkit.py --help
    python3 TOOLS/AgentKit/agentkit.py probe --root . --json agentkit-report.json
    python3 TOOLS/AgentKit/agentkit.py probe --root . --list-files
    python3 TOOLS/AgentKit/agentkit.py locate src/example.py --start 20 --end 50
    python3 TOOLS/AgentKit/agentkit.py note "Investigate syscall tracing fallback" --name syscall
    python3 TOOLS/AgentKit/agentkit.py ingest conversation.txt --query timeout --save
    python3 TOOLS/AgentKit/agentkit.py timer 300 --prompt
    python3 TOOLS/AgentKit/agentkit.py versions --root . --output VERSIONS.md
    python3 TOOLS/AgentKit/agentkit.py fetch-probe https://github.com/OWNER/REPOSITORY.git --timeout 5

Probe: root is explicit with --root; default is current working directory. At most 49 files skips page selection; 50+ offers 50/100/200/500/MAX. Hidden build/dependency directories are excluded. Capability presence is not a guarantee that target code works. Timer prints local and UTC end times, but a killed process cannot notify later. fetch-probe tests remote refs only.

Tests from repository root: python3 -m unittest discover -s TOOLS/AgentKit/tests -v


## Runtime selection / reduced fallback

Use the launcher at TOOLS/AgentKit/agentkit. It selects Python when available and otherwise uses the POSIX shell fallback. Set AGENTKIT_FORCE_SH=1 to test the fallback deliberately:

    sh TOOLS/AgentKit/agentkit --help
    AGENTKIT_FORCE_SH=1 sh TOOLS/AgentKit/agentkit probe --root . --list-files

The shell fallback only supports command inventory and file listing. It is not feature-equivalent to the Python version. This is intentional: the fallback should be small and auditable, not a second full implementation.
