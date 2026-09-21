# Week 3 — Distributed application basics: state, latency, failure

**Lab 1 is due at the end of this week.**

---

## The moment a call crosses a machine

Last week everything was inside one process. A function call was a function call: it
succeeded, it raised, and it took nanoseconds.

Now put a network in the middle. Three things change, and all three are permanent.

**It got slower, by a lot.** Rough magnitudes worth carrying in your head:

| | Roughly |
|---|---|
| Function call in-process | nanoseconds |
| Read from main memory | ~100 ns |
| Read from a local SSD | tens of microseconds |
| Round trip within one datacentre | under a millisecond |
| Round trip Bangkok ↔ Iowa | ~200 ms |

The last row is not an engineering deficiency; it is the speed of light in fibre plus the
routers along the way, and no amount of optimisation will fix it. It is the reason a chatty
design — twenty small round trips where one would do — can be a hundred times slower than a
talkative one, while looking identical in the source code.

**It can fail in a new way.** A local function call either returns or raises. A remote call
has a third outcome: **you never find out.** The request may have been lost on the way. It
may have arrived, been executed perfectly, and the *response* lost on the way back. From
where you are standing, those two are indistinguishable.

**Parts can fail independently.** In one process, a crash takes everything with it. Across
machines, one component can be dead while everything around it is fine — and the rest of the
system has to decide what to do about that.

## Slow and dead look the same

This is the single most important sentence in distributed systems, so here it is alone:

> **You cannot distinguish a slow component from a dead one.**

You send a request. Nothing comes back. Is the other side down, overloaded, or is the
network dropping packets? You cannot know. All you can do is wait — and eventually decide.

That decision is a **timeout**, and a timeout is always a guess. Too short and you give up on
work that was about to succeed. Too long and your own caller gives up on you. There is no
correct value, only a trade-off you have chosen deliberately or left to a default.

And here is the part that makes it sharp. When you time out, you have two options and both
are wrong:

- **Retry**, and risk doing the work twice — because the first attempt may have succeeded.
- **Do not retry**, and risk not doing it at all — because the first attempt may have failed.

You cannot avoid this. What you *can* do is make doing it twice harmless. That property is
called **idempotency**, and it is why the course application has had an `Idempotency-Key`
since week 2, long before there is a queue to need it.

Try it now:

```bash
# send the same job submission twice with the same key
curl -i -X POST http://127.0.0.1:8080/jobs \
     -H 'Content-Type: application/json' -H 'Idempotency-Key: same-key' \
     -d '{"document_id":"<your doc id>","operation":"wordcount"}'
```

First time: `201 Created`. Second time: `200 OK` and `"deduplicated": true`. Same job, done
once. The client did not have to know whether its first request arrived — and that is the
whole point.

## Where state lives

**State** is anything the system has to remember. It is the hard part of distributed systems,
because execution can be thrown away and recreated while state cannot.

The course application has two kinds, and they behave completely differently:

| | Where it lives | Survives a restart? |
|---|---|---|
| Document bytes | a directory on disk | **yes** |
| Job records | a Python dictionary | **no** |

Lab 1 Part 3 has you watch exactly this. Both feel equally real while the process is
running. Only one of them is.

But there is a second, subtler distinction, and Lab 1 asks you to draw it. Run the
application in a container with no volume, write a document, delete the container, and start
a new one. The document is gone — even though it *was* written to a filesystem.

So there are three levels, not two:

1. **In memory.** Gone when the process ends.
2. **On disposable storage.** Gone when the *container or machine* ends.
3. **On storage that outlives the compute.** Survives both.

Only level 3 is really state. Level 2 feels like durability and is not, which is precisely
why it is dangerous: it works in every test you run on your laptop, and then it does not.

Lab 3 moves the application to level 3. This week is about being able to tell the levels
apart.

## Stateless execution

Once state lives somewhere that outlives execution, the execution can be *stateless*: any
instance can serve any request, because it does not remember anything between them.

That unlocks the properties the rest of the course depends on:

- **Scale horizontally.** Add instances; any of them can take any request.
- **Fail cheaply.** An instance dies, its traffic goes elsewhere, nothing is lost.
- **Deploy without drama.** Stop old instances, start new ones.

None of that works if a request handler remembers something the next request needs. This is
why `Application` in `app.py` holds no per-request state, and why "put it in a variable on
the server" is a decision that quietly forecloses everything in weeks 8–11.

## Failure boundaries and blast radius

A **failure boundary** is a line across which a failure does not propagate. A **blast
radius** is how much stops working when one thing does.

Ask two questions of any design:

1. If this component dies, what else stops?
2. Could it have been less?

In the application as it stands: the process *is* the boundary. Kill it and everything
stops — API, processing, job records. By week 11 the same application will have several
boundaries, and a failure in one of them will be something the rest survives.

Notice that you can only *have* a boundary where there is a real separation. Splitting
things up is what buys you smaller blast radii, and it costs you the network from the top of
this page. That trade is the subject of the rest of the course.

## This week's work (~180 minutes)

| | |
|---|---|
| Read these notes | 25 min |
| Lab 1 Parts 3–5 and the write-up | 155 min |

**Lab 1 is due at the end of this week.** The write-up is part of the work, not an extra:
band B of the rubric — explanation and evidence — is worth 40 marks, more than the
implementation.

## Check yourself

1. You call a remote service and get no reply. Name the three things that could have
   happened.
2. Why is a timeout always a guess?
3. You time out and retry. What have you risked? What if you do not retry?
4. What property makes retrying safe, and where is it in the course application?
5. Name the three levels of state durability, with an example of each.
6. Why can a stateless service scale horizontally when a stateful one cannot?
7. A round trip between Bangkok and Iowa is about 200 ms. Your design makes 20 sequential
   calls. How long, and what would you change?

## Next week

Cloud proper. The resource hierarchy, regions and zones, virtual machines, and identity. You
activate your Google Cloud trial in the session, set up billing alerts, and start Lab 2.

**Do not activate your trial before the session.** Ninety days has to reach week 15.
