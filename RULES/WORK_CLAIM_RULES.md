# Work scope / claim rules

Before changing files, state the paths or feature area you intend to modify in the task or PR.

- Avoid overlapping another contributor's active work.
- If overlap is found, coordinate or limit scope rather than overwrite.
- After work, update shared state/task when the result changes project status.
- Do not claim that a coordination mechanism is automated unless it is implemented and verified.
- Every PR changeset must state who authored or materially edited it: ai or human.
- Every PR changeset must state its work route: online, offline or mixed.
- Use TOOLS/AgentKit/agentkit_ext.py record-change to append the path-level record. If both AI and human edits occur, make separate records so paths retain their attribution.
- The PR gate rejects changed files without a corresponding record; it does not verify a person's real-world identity.
