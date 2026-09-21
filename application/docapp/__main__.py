"""Entry point: ``python -m docapp``.

Start-up does three things in order, and the order matters. Configuration is validated
first, so a bad environment variable fails immediately with a sentence you can act on
rather than halfway through the first request. The resolved configuration is then logged,
so that the log of any run says what that run was actually doing. Only then does the socket
open.
"""

from __future__ import annotations

import sys

from . import __version__, logs
from .config import Config, ConfigError
from .jobstore import JobStoreError
from .storage import StorageError
from .wiring import build_application


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        print("Configuration is read from the environment. See application/README.md.")
        return 0
    if argv and argv[0] in ("-V", "--version"):
        print(f"docapp {__version__}")
        return 0

    try:
        config = Config.from_env()
    except ConfigError as exc:
        # Deliberately not a traceback. The reader is a student with a typo, and a stack
        # trace would tell them about our code rather than about their mistake.
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    logs.configure(config.log_level)

    try:
        application = build_application(config)
    except (StorageError, JobStoreError, NotImplementedError) as exc:
        print(f"Startup failed: {exc}", file=sys.stderr)
        return 2

    from .app import make_server
    try:
        server = make_server(config, application)
    except OSError as exc:
        print(
            f"Could not listen on {config.host}:{config.port}: {exc}\n"
            f"If the port is already in use, either stop the other process or set "
            f"PORT to a different value.",
            file=sys.stderr,
        )
        return 2

    logs.info("docapp starting", version=__version__, **config.describe())
    print(
        f"docapp {__version__} listening on http://{config.host}:{config.port}  "
        f"(try: curl http://{config.host}:{config.port}/healthz)",
        file=sys.stderr,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logs.info("docapp stopping")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
