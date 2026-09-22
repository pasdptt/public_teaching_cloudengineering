"""The queue, on a real broker outside this process.

------------------------------------------------------------------------------------------
STUDENT WORK — Lab 5, Parts 2 and 3. Two things here are deliberately unimplemented.
------------------------------------------------------------------------------------------

``ThreadQueue`` already gave you asynchronous processing and duplicate delivery. So why
bother with this at all? Answer that before you write any code — Lab 5 Part 1 asks, and the
answer is not "because it is the cloud one". Both deliver at least once. Both retry. The
difference is what survives when the process does not.

There are two pieces, because a queue has two ends:

  ``PubSubQueue.submit``     the producer. Publishes a job id and returns immediately.
  ``decode_push_envelope``   the consumer. Pub/Sub delivers a message by POSTing a JSON
                             envelope to your service; this turns that envelope back into
                             a job id. ``app.py`` calls it for you and then calls
                             ``service.run_job``.

The acceptance tests are written, and they split the same way:

    pytest -m lab05                              # the envelope tests: no cloud, no cost
    DOCAPP_TEST_TOPIC=... pytest -m lab05        # the publish tests: real Pub/Sub

Do the envelope first. It needs no account, it is where the subtle bug lives, and half the
marks for this part are in the questions below rather than in the code.

Things to decide before you write code:

  1. The envelope's ``data`` field is **base64-encoded**. What happens if you forget to
     decode it? Be precise: does it fail loudly, or does it fail quietly by looking up a
     job id that cannot exist?
  2. Every push message carries a ``messageId`` that is stable across redeliveries, and a
     ``publishTime`` that is not. Which one would you use to detect a duplicate, and why
     is the application not using either?
  3. ``submit`` returns as soon as the broker has the message. What has it NOT promised at
     that moment? List everything, then look at what ``create_job`` returns to the caller
     and say what the API should tell a client that has just submitted.
  4. Publishing is a network call and can fail. If it raises after the job record has
     already been written, what state is the system in, and what would the user see? This
     one has no clean answer with the design as it stands — say what you would change.
  5. The push endpoint is a URL on the public internet that causes work to happen. What
     stops anyone else calling it? Find out what Pub/Sub can attach to a push request, and
     say what your subscription is configured to send.
"""

from __future__ import annotations

import base64
import json
from typing import Any

from .queue import QueueError


def decode_push_envelope(body: bytes) -> str:
    """Turn a Pub/Sub push request body into the job id it carries.

    A push envelope looks like this, with the interesting part nested and encoded::

        {
          "message": {
            "data": "<base64>",
            "messageId": "123456789",
            "publishTime": "2026-09-22T08:00:00Z",
            "attributes": {"...": "..."}
          },
          "subscription": "projects/p/subscriptions/s"
        }

    Raise :class:`QueueError` with a message a human can act on if the body is not a valid
    envelope. Returning a wrong-but-plausible job id instead would turn a malformed message
    into a 404 somewhere else entirely, which is a much worse afternoon.

    TODO(lab05): implement this.
    """
    raise NotImplementedError(
        "decode_push_envelope is your Lab 5 exercise and is not implemented yet.\n"
        "Run `pytest -m lab05` to see what it must do. These tests need no cloud account."
    )


class PubSubQueue:
    """Publishes job ids to a Pub/Sub topic.

    Note what this class does *not* contain: any consumer. With a push subscription the
    broker calls your service, so the consumer is an HTTP route in ``app.py`` rather than a
    loop in here. Part 1 asks you to say what you would have needed instead if you had
    chosen a pull subscription, and what that would have cost you on managed execution.
    """

    def __init__(self, project_id: str, topic: str) -> None:
        if not project_id:
            raise QueueError(
                "DOCAPP_PROJECT_ID is not set. The Pub/Sub backend needs a project. "
                "Either set it, or run with DOCAPP_QUEUE=thread."
            )
        if not topic:
            raise QueueError(
                "DOCAPP_QUEUE_TOPIC is not set. The Pub/Sub backend needs a topic name. "
                "Either set it, or run with DOCAPP_QUEUE=thread."
            )
        self.project_id = project_id
        self.topic = topic

        # Imported here rather than at module top level, for the same reason as the Lab 3
        # backends: a student on the local or fallback path never needs this library
        # installed, and the application keeps its zero-dependency start-up.
        try:
            from google.cloud import pubsub_v1  # type: ignore
        except ImportError as exc:
            raise QueueError(
                "google-cloud-pubsub is not installed, but DOCAPP_QUEUE=pubsub.\n"
                "  pip3 install -r application/requirements.txt\n"
                "Or run with DOCAPP_QUEUE=thread."
            ) from exc

        self._publisher: Any = pubsub_v1.PublisherClient()
        self._topic_path: str = self._publisher.topic_path(project_id, topic)

        raise NotImplementedError(
            "PubSubQueue is your Lab 5 exercise and is not implemented yet.\n"
            "Run `DOCAPP_TEST_TOPIC=<topic> DOCAPP_TEST_PROJECT=<project> pytest -m lab05` "
            "to see what it must do. Until then, run with DOCAPP_QUEUE=thread."
        )

    # TODO(lab05): implement submit(self, job_id: str) -> None
    #
    # It must publish the job id in a form decode_push_envelope can read back, and it must
    # raise QueueError -- not the library's own exception -- if publishing fails. The
    # second half of that sentence is a design decision, not a formality: work out what the
    # rest of the application would have to know in order to catch anything else.


__all__ = ["PubSubQueue", "decode_push_envelope"]
