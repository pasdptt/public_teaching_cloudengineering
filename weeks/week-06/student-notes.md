# Week 6 — Storage abstractions

**Quiz 3 this week** (weeks 3–5). **Lab 3 starts.**

---

## Four ways to store bytes

They are not four products. They are four **access patterns**, and picking the wrong one is
one of the more expensive mistakes available to you.

### Block storage
A raw device. The operating system puts a filesystem on it and you use it like a disk,
because it is one. Attached to **one** machine at a time.

*Assumes:* one writer, arbitrary reads and writes at arbitrary offsets, low latency.
*Costs you:* it belongs to a machine. Your Lab 2 boot disk is block storage, which is why
deleting the VM was a question about the disk as well.

### File storage
A filesystem over a network, shared by several machines. POSIX semantics — directories,
permissions, partial writes.

*Assumes:* you genuinely need several machines to see the same filesystem.
*Costs you:* more than the alternatives, and the semantics are harder to make fast over a
network. Usually chosen because existing software demands a filesystem.

### Object storage
A flat namespace of keys and byte-blobs, reached over HTTP. An object is written whole and
read whole. **No partial writes, no appends, no rename.**

*Assumes:* write once, read many, no modification in place.
*Costs you:* the ability to change part of a thing. To "edit" an object you upload a new one.
*Gains you:* effectively unlimited capacity, very high durability, no machine that owns it,
and a price per gigabyte far below the others.

That last property is why object storage changed how applications are built. Before it, "the
files" lived on a server, and that server was special. After it, they live nowhere in
particular, and no server is special. Everything about stateless execution in weeks 8–11
follows from that.

### Databases
Structured records with query, update-in-place and — usually — transactions.

*Assumes:* you need to find things by their contents, change part of a record, or make
several changes atomically.
*Costs you:* per-byte cost far above object storage, size limits per record, and a schema or
index design decision you cannot avoid.

## The question that picks one

Not "what am I storing?" but:

> **How will this be read and written, and by how many things at once?**

Take the course application. Documents are written once, read whole, never modified, and
nobody queries their contents — **object storage**. Job records are small, updated several
times each, looked up by id, listed by recency and searched by key — **a database**.

That is Lab 3 Part 1, and you have to write it down and defend it, including the options you
rejected. Being able to say why job records in object storage would be bad — no query, no
atomic update, and a read-modify-write race every time two things touch one — is worth more
than knowing which service to click.

## Durability, availability, and what a number means

**Durability** is the chance your data still exists later. **Availability** is the chance you
can reach it right now. They are different, and providers quote them separately.

Object storage durability is usually quoted with a lot of nines. Be precise about what that
claims: it is a statement about **hardware and media failure**, produced by writing your
object to several independent places. It is not a claim about:

- you deleting it by mistake,
- your code writing the wrong bytes,
- your credentials being stolen,
- or the provider's billing system closing your account.

**Eleven nines will not protect you from a `for` loop with a bug in it.** Versioning,
retention policies and backups address a different risk from replication, and conflating the
two is how people are surprised.

That also matters for cleanup: if versioning is on, deleting the object you can see leaves a
version behind that still costs money. Lab 3's teardown asks you to check.

## Access control on storage

The single most common cloud data breach is a storage bucket readable by anyone. Not a
sophisticated attack — a configuration.

Two settings in Lab 3 are worth understanding rather than copying:

- **Uniform bucket-level access** — permissions are set on the bucket, not per object. The
  alternative allows per-object ACLs, which sounds flexible and means nobody can state
  confidently who can read what.
- **Public access prevention** — makes it *impossible* to grant public access, rather than
  merely not having granted it yet. A guard rail that survives the next person's mistake.

This is week 1's shared responsibility, made concrete. The provider gives you a correct
permissions system. Configuring it is yours.

## Costs that are not per-gigabyte

Storage pricing has three parts, and beginners see only the first:

1. **Storage** — per GB per month.
2. **Operations** — per request. Cloud Storage splits these into Class A (writes, lists —
   5,000/month free) and Class B (reads — 50,000/month free). Ten times as many free reads
   as writes, which tells you something about their relative cost.
3. **Egress** — per GB leaving the provider's network.

Two consequences you will meet in Lab 3:

- Implementing `exists()` as a download instead of a metadata lookup turns a cheap Class B
  call into an expensive one and burns your scarcer allowance. Both versions pass the tests.
- Many tiny objects can cost more in operations than in storage.

## This week's work (~180 minutes)

| | |
|---|---|
| Read these notes; prepare for Quiz 3 | 30 min |
| Lab 3 Parts 1–2: the decision record, and documents into object storage | 150 min |

## Check yourself

1. For each of block, file, object, database — one access pattern it suits, one it does not.
2. Why can you not append to an object in object storage, and what do you do instead?
3. Durability vs availability. Give a failure each one does *not* protect against.
4. Why would job records in object storage be a bad choice? Give two concrete reasons.
5. What does public access prevention do that simply not granting public access does not?
6. Class A and Class B operations have very different free allowances. What does that
   asymmetry tell you, and where might it bite you?
7. Your bucket has versioning on. You delete every object you can see. Are you still paying?

## Next week

Replication, consistency models, transactions, and how to pick a data service from the
access pattern. You finish Lab 3 — job records move to Firestore, and the application
finally holds no state of its own.
