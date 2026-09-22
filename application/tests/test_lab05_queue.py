"""ACCEPTANCE TESTS — Lab 5, the Pub/Sub backend and the push envelope.

    pytest -m lab05                                    # the envelope. No cloud. No cost.
    DOCAPP_TEST_PROJECT=p DOCAPP_TEST_TOPIC=t \
        pytest -m lab05                                # ...and the publisher, for real

Two halves, deliberately split, because the halves are not equally expensive to get wrong.

**The envelope tests need no account and no network.** They are pure functions over bytes,
they run in milliseconds, and the base64 bug in question 1 of the stub docstring is the one
that costs students an afternoon when they find it against a real broker instead of here.
Do these first.

**The publisher tests touch real Pub/Sub** and are skipped unless you point them at a topic,
so nobody is billed by surprise. At these volumes -- a handful of messages of a few dozen
bytes -- the cost is nothing against a 10 GiB monthly allowance. They clean up the
subscription they create; read the fixture and satisfy yourself that they do.
"""

from __future__ import annotations

import base64
import json
import os
import threading
import uuid

import pytest

from conftest import SAMPLE, make_config

pytestmark = pytest.mark.lab05

TEST_PROJECT = os.environ.get("DOCAPP_TEST_PROJECT", "").strip()
TEST_TOPIC = os.environ.get("DOCAPP_TEST_TOPIC", "").strip()


def envelope(job_id: str, **overrides) -> bytes:
    """Build a push body the way Pub/Sub does, so the tests are not guessing at the shape."""
    message = {
        "data": base64.b64encode(job_id.encode("utf-8")).decode("ascii"),
        "messageId": "2070443601311540",
        "publishTime": "2026-09-22T08:00:00.000Z",
    }
    message.update(overrides)
    return json.dumps({"message": message,
                       "subscription": "projects/p/subscriptions/s"}).encode("utf-8")


# ------------------------------------------------------------------ the envelope, offline

class TestDecodePushEnvelope:
    """What ``decode_push_envelope`` must do. No cloud account needed for any of it."""

    def decode(self, body: bytes) -> str:
        from docapp.pubsub_queue import decode_push_envelope

        return decode_push_envelope(body)

    def test_returns_the_job_id(self):
        assert self.decode(envelope("job_abc123")) == "job_abc123"

    def test_the_data_field_is_base64(self):
        """The test that catches the mistake everybody makes once.

        A body whose ``data`` is NOT encoded must not quietly succeed. Rejecting it and
        decoding it to something else are both fine; **passing it straight through is not**.
        If your implementation does that, it will also appear to "work" against the real
        broker -- by returning the base64 of the real job id, producing a 404 for a job that
        definitely exists, which is a genuinely horrible afternoon.
        """
        from docapp.queue import QueueError

        raw = json.dumps({"message": {"data": "job_abc123", "messageId": "1"},
                          "subscription": "projects/p/subscriptions/s"}).encode()
        try:
            decoded = self.decode(raw)
        except QueueError:
            return  # refusing to read it is a perfectly good answer
        assert decoded != "job_abc123", (
            "the data field was not base64-decoded: a plain job id must not pass through"
        )

    def test_ignores_the_fields_it_does_not_need(self):
        """Extra attributes and a different messageId must not change the answer."""
        body = envelope("job_abc123", attributes={"origin": "nowhere"},
                        messageId="99999999", orderingKey="k")
        assert self.decode(body) == "job_abc123"

    @pytest.mark.parametrize("body, why", [
        (b"", "an empty body"),
        (b"not json at all", "a body that is not JSON"),
        (b"[]", "JSON that is not an object"),
        (json.dumps({"subscription": "s"}).encode(), "an envelope with no message"),
        (json.dumps({"message": {}}).encode(), "a message with no data"),
        (json.dumps({"message": {"data": "!!!not base64!!!"}}).encode(), "undecodable data"),
    ])
    def test_rejects_what_it_cannot_read(self, body, why):
        """Every one of these must raise QueueError, not return something plausible.

        A decoder that guesses turns a malformed message into a mystery 404 in a different
        part of the system, hours later. Failing here, loudly, with a message naming the
        problem, is the whole job.
        """
        from docapp.queue import QueueError

        with pytest.raises(QueueError):
            self.decode(body)

    def test_the_error_says_something_useful(self):
        """A student debugging this at 11 p.m. is the reader. Write for them."""
        from docapp.queue import QueueError

        with pytest.raises(QueueError) as exc:
            self.decode(b"not json at all")
        assert len(str(exc.value)) > 20, "an error message of five words helps nobody"


# ------------------------------------------------- the consumer end, over real HTTP, offline

class TestPushEndpoint:
    """``POST /tasks/process`` with your decoder behind it. Still no cloud account.

    The status codes are supplied and are not the exercise; what they mean to a broker is.
    Lab 5 Part 4 asks you to argue with two of them.
    """

    @pytest.fixture
    def server(self, tmp_path):
        from docapp.app import make_server
        from docapp.wiring import build_application

        class NeverDelivers:
            """Accepts work and never does it -- which is exactly what a producer sees.

            With a real broker the application's own process has no consumer in it at all:
            the messages leave, and something else brings them back over HTTP. This stands
            in for that, and it means the ONLY way a job can be processed in these tests is
            the push endpoint -- so they test the endpoint rather than a worker thread.
            """

            def __init__(self) -> None:
                self.submitted: list[str] = []

            def submit(self, job_id: str) -> None:
                self.submitted.append(job_id)

        config = make_config(tmp_path)
        app = build_application(config)
        app.service.attach_queue(NeverDelivers())
        httpd = make_server(config, app)
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{port}", app.service
        finally:
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=5)

    def post(self, base, path, body):
        import json as _json
        from urllib import error, request

        req = request.Request(base + path, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        try:
            with request.urlopen(req, timeout=10) as resp:
                return resp.status, _json.loads(resp.read().decode())
        except error.HTTPError as exc:
            return exc.code, _json.loads(exc.read().decode())

    def test_a_pushed_message_processes_the_job(self, server):
        base, service = server
        doc = service.create_document("notes.txt", SAMPLE)
        job, _ = service.create_job(doc.id, "wordcount")
        assert service.get_job(job.id).status == "pending"

        status, body = self.post(base, "/tasks/process", envelope(job.id))
        assert status == 200
        assert body["status"] == "succeeded"
        assert service.get_job(job.id).status == "succeeded"

    def test_a_redelivered_message_does_not_redo_the_work(self, server):
        """At-least-once, arriving over HTTP. The second push must change nothing."""
        base, service = server
        doc = service.create_document("notes.txt", SAMPLE)
        job, _ = service.create_job(doc.id, "wordcount")

        self.post(base, "/tasks/process", envelope(job.id))
        first = service.get_job(job.id)

        status, body = self.post(base, "/tasks/process", envelope(job.id))
        assert status == 200

        second = service.get_job(job.id)
        assert second.attempts == first.attempts == 1
        assert second.completed_ms == first.completed_ms
        assert service.counters.jobs_processed == 1
        assert service.counters.duplicate_deliveries_skipped == 1

    def test_a_message_for_a_missing_job_is_acknowledged(self, server):
        """200, not 404. There is nothing a redelivery could fix."""
        base, _ = server
        status, body = self.post(base, "/tasks/process", envelope("job_does_not_exist"))
        assert status == 200
        assert body["status"] == "dropped"

    def test_an_undecodable_message_is_rejected_not_retried(self, server):
        """400. The same malformed bytes will be just as malformed in thirty seconds."""
        base, _ = server
        status, _body = self.post(base, "/tasks/process", b"not an envelope")
        assert status == 400


# ---------------------------------------------------------------- the publisher, for real

@pytest.mark.skipif(not (TEST_PROJECT and TEST_TOPIC),
                    reason="set DOCAPP_TEST_PROJECT and DOCAPP_TEST_TOPIC to run these")
class TestPubSubQueue:
    """``PubSubQueue.submit`` against a real topic.

    The test subscribes to the topic, publishes, and pulls the message back, because the
    only honest way to check that you published something readable is to read it.
    """

    @pytest.fixture
    def subscription(self):
        from google.cloud import pubsub_v1  # type: ignore

        subscriber = pubsub_v1.SubscriberClient()
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(TEST_PROJECT, TEST_TOPIC)
        name = f"lab05-test-{uuid.uuid4().hex[:12]}"
        path = subscriber.subscription_path(TEST_PROJECT, name)
        subscriber.create_subscription(request={"name": path, "topic": topic_path})
        try:
            yield subscriber, path
        finally:
            # A subscription with no consumer retains messages and bills for the storage.
            # Leaving one behind is the single way this test could cost anybody money.
            subscriber.delete_subscription(request={"subscription": path})
            subscriber.close()

    def test_submit_publishes_a_readable_job_id(self, subscription):
        from docapp.pubsub_queue import PubSubQueue

        subscriber, path = subscription
        queue = PubSubQueue(TEST_PROJECT, TEST_TOPIC)
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        queue.submit(job_id)

        response = subscriber.pull(request={"subscription": path, "max_messages": 10},
                                   timeout=30)
        received = [m.message.data.decode("utf-8") for m in response.received_messages]
        subscriber.acknowledge(request={
            "subscription": path,
            "ack_ids": [m.ack_id for m in response.received_messages],
        })
        assert job_id in received, (
            "the published message did not carry the job id in a readable form"
        )

    def test_submit_raises_queue_error_for_a_topic_that_does_not_exist(self):
        """Library exceptions must not escape the seam. Work out why before you fix it."""
        from docapp.pubsub_queue import PubSubQueue
        from docapp.queue import QueueError

        queue = PubSubQueue(TEST_PROJECT, f"no-such-topic-{uuid.uuid4().hex[:8]}")
        with pytest.raises(QueueError):
            queue.submit("job_whatever")
