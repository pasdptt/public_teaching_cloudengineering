# Course application

**STATUS: not yet authored — scheduled for Stage B.**

This file is a placeholder so the repository structure is visible and reviewable. It is
not content, and it is not a summary of content that exists elsewhere.

A small Python document/job-processing service (decision D-13): submit a synthetic input,
store it, request processing, poll status, read the result. It starts fully local and
synchronous; object storage arrives in Lab 3, managed execution in Lab 4, and a queue in
Lab 5 — each only once the concept has been taught.

Constraints already fixed: minimal dependencies, pinned versions, no AI APIs, no
complicated frontend, small non-sensitive synthetic data, bounded resource use, actionable
setup errors, and tests that check meaningful behaviour (especially retry/idempotency and
cleanup logic) rather than mirroring the implementation.

**This is the next thing to build.**

See `planning/progress.md` for the authoring order and the current next action.
