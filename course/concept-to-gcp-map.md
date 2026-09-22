# Concept → GCP map

**How to read this file.** The left column is what the course teaches. The right columns
are how one provider happens to implement it. The order matters: students meet the generic
abstraction first, then the product name, then a short note on what actually differs
elsewhere.

Two warnings this file exists to prevent:

1. **Similar names do not mean interchangeable services.** "Object storage" is a genuine
   shared abstraction with shared semantics. "Managed container platform" is not — Cloud
   Run, AWS App Runner, Azure Container Apps and Fly.io differ in concurrency model,
   scaling behaviour and lifecycle in ways that change how you design.
2. **Vendor documentation is not independent evidence of comparative superiority.** Where
   this file compares, it compares mechanisms, not marketing.

---

## Compute and execution

| Concept taught | Mechanism | GCP service | What transfers | What is provider-specific |
|---|---|---|---|---|
| Virtual machine | Hardware virtualization; guest OS you operate | Compute Engine | The model is near-identical everywhere: you get an OS, you patch it, you pay while it exists | Machine family naming, metadata service details, default images |
| Machine sizing | vCPU/memory as separate billable dimensions | E2 / N-series machine types | Right-sizing reasoning | Family names, custom-type rules, discount structures |
| Container image | Layered filesystem + process isolation | Artifact Registry (storage), OCI images | Fully portable. An OCI image runs anywhere | Registry auth and naming |
| Managed container execution | Provider runs the scheduler; you supply an image and a port | Cloud Run | Statelessness requirement, request-scoped lifecycle, cold start as a concept | **Concurrency-per-instance is unusually explicit here.** Scaling triggers and min-instance semantics differ substantially between providers |
| Orchestration (conceptual only) | Declarative desired state, reconciliation loop | GKE | Kubernetes API objects are genuinely portable | Managed control-plane behaviour, autopilot modes, networking plugins |
| Function-as-a-service (mentioned, not required) | Event-triggered short-lived execution | Cloud Run functions | Event-driven model | Trigger types, runtime limits, cold-start characteristics |

## Networking and access

| Concept taught | Mechanism | GCP service | What transfers | What is provider-specific |
|---|---|---|---|---|
| Virtual network | Software-defined L3 isolation | VPC network | Subnets, routes, private vs public addressing | **GCP VPCs are global with regional subnets** — this genuinely differs from the regional-VPC model elsewhere, and is worth one slide |
| Firewall | Stateful allow-list on a network path | VPC firewall rules | Default-deny thinking, least-exposure design | Rule priority, target tags, hierarchical policies |
| Public entry point | Stable address + name resolution | External IP, Cloud DNS | DNS and addressing fundamentals | Address types, whether an unattached address bills |
| Load distribution | Health-checked distribution across backends | Cloud Load Balancing | L4 vs L7, health checks, backend pools | Global anycast L7 load balancing is architecturally distinctive |
| Private service access | Reaching a managed service without traversing the public internet | Private Google Access, VPC connectors | The principle | Implementation differs a lot; don't over-generalise |

## Identity

| Concept taught | Mechanism | GCP service | What transfers | What is provider-specific |
|---|---|---|---|---|
| Principal, role, policy | Who may do what to which resource | Cloud IAM | The triple, and least privilege as a default | **Policy inheritance down the resource hierarchy is a real structural difference** from a flat account model |
| Workload identity | Non-human identity for code | Service accounts | Never embed keys; attach an identity to the workload | Attachment mechanism, key-less patterns |
| Resource hierarchy | Where policy and billing attach | Organisation → Folder → Project → Resource | Billing boundaries as a design decision | The project abstraction is specific to GCP; the nearest analogue elsewhere is an account or subscription, and it is not an exact match |

## Storage and data

| Concept taught | Mechanism | GCP service | What transfers | What is provider-specific |
|---|---|---|---|---|
| Block storage | Raw device attached to one instance | Persistent Disk | Attachment model, why it outlives a VM and keeps billing | Disk types, snapshot semantics |
| Object storage | Flat namespace, HTTP API, immutable-object semantics | Cloud Storage | **Strong transfer.** The abstraction is genuinely similar across providers | Storage classes, consistency guarantees (read the current docs — these have changed), lifecycle rule syntax |
| File storage | Shared POSIX filesystem over a network | Filestore | Semantics and when you actually need it | Performance tiers, minimum sizes |
| Relational managed database | Provider operates the engine; you own the schema | Cloud SQL | Everything about schema, transactions, indexing | Backup/HA/maintenance-window behaviour, and **whether an idle instance keeps billing** |
| Document / key-value store | Schema-flexible, query by key or index | Firestore | Access-pattern-first design | Query limitations and index requirements differ sharply between document stores |
| Managed cache | In-memory store, evictable by design | Memorystore | Cache invalidation reasoning | Engine versions and failover behaviour |

*Lab 3 uses **Firestore**, the project's single free `(default)` database (decision D-20).
Chosen on idle cost: Firestore charges nothing when unused, while Cloud SQL bills per hour
whether or not anything connects. Worth saying to students explicitly — the course picked its
database the way a cost-conscious engineer would, and the reasoning is the lesson.*

## Asynchrony

| Concept taught | Mechanism | GCP service | What transfers | What is provider-specific |
|---|---|---|---|---|
| Queue / topic | Durable decoupling of producer and consumer | Pub/Sub | **Strong transfer:** at-least-once delivery, therefore duplicates, therefore idempotency | Push vs pull subscriptions, ack deadline semantics, ordering keys |
| Retry and backoff | Bounded re-attempts with growing delay | Subscription retry policy | The whole retry-storm and backoff discussion | Default policies and configurability |
| Dead-letter handling | Quarantine for messages that keep failing | Dead-letter topics | The pattern | Configuration and required permissions |
| Scheduled work | Time-triggered execution | Cloud Scheduler | Cron semantics | Timezone and retry behaviour |

## Observability

| Concept taught | Mechanism | GCP service | What transfers | What is provider-specific |
|---|---|---|---|---|
| Structured logs | Machine-readable events with severity and correlation | Cloud Logging | **Strong transfer.** Structured logging is a discipline, not a product | Query language, retention and export |
| Metrics | Aggregated numeric time series | Cloud Monitoring | Counters vs gauges vs histograms; percentiles over averages | Metric naming, alerting policy model |
| Tracing (introduced only) | Causal span tree across services | Cloud Trace | The concept, and OpenTelemetry instrumentation | Backend integration |
| SLO / error budget | Target on a measurable indicator | Monitoring SLOs | The reasoning; it is vendor-independent | Tooling |

## Delivery and environments

| Concept taught | Mechanism | Tool / GCP service | What transfers | What is provider-specific |
|---|---|---|---|---|
| Continuous integration | Every change runs the tests before it can merge | **GitHub Actions** (free on public repos) | **Everything.** CI is a discipline; the YAML dialect is the only vendor-specific part | Workflow syntax. GitLab CI, Cloud Build and Jenkins express the same idea differently |
| Build once, promote the artefact | The *same* image is deployed to each environment in turn | Artifact Registry + Cloud Run revisions | **Strong transfer**, and the single most-violated rule in practice — rebuilding per environment means you never tested what you shipped | Registry and revision mechanics |
| Pipeline identity | The pipeline is a principal and needs permissions of its own | **Workload Identity Federation** (OIDC) | **Strong transfer.** Every major provider now offers OIDC federation from CI, precisely so that no key has to exist | Pool/provider configuration, and the exact trust-condition syntax |
| Environment management | One configuration, parameterised per environment | Terraform variable files + separate resource names | The parameterisation discipline, and the rule that undeclared differences are bugs | Whether environments are separate projects, folders, or prefixes within one |
| Deployment gate | A stage that must pass before the next one runs | Branch protection + workflow job dependencies | The reasoning about **what each gate protects** | Configuration surface |
| Managed build service | Provider-hosted build runners | Cloud Build (2,500 free min/month) | The build-service model | Triggers, substitutions, and IAM integration |

*Why GitHub Actions rather than Cloud Build (D-26):* Actions minutes are free on public
repositories, and keyless federation to Google Cloud means students implement the course's
"never embed credentials" rule instead of reciting it. Cloud Build is discussed as the
in-platform alternative and is a perfectly good choice; it is simply not the taught path.

## Automation and cost

| Concept taught | Mechanism | GCP service / tool | What transfers | What is provider-specific |
|---|---|---|---|---|
| Declarative infrastructure | Desired state + state file + plan/apply | **Terraform** with `hashicorp/google` provider (D-03) | The declarative model, state, drift, plan-before-apply — this is the transferable lesson | Resource schemas and provider arguments. Syntax is not the objective |
| Secret handling | Secrets out of code and out of images | Secret Manager | Never commit a secret; a committed secret is permanent | Access model and versioning |
| Config vs secret | Config varies per environment and may be read; a secret varies and must not be | Terraform variables vs Secret Manager | The distinction, and that "it's only a test key" is how keys leak | Where each is stored and injected |
| Cost model | Metered resources, billed per unit time or operation | Cloud Billing, budgets | Estimate-before-deploy; know what accrues when idle | SKU structure, free tiers, sustained-use discounts |
| Cost guardrails | Notification on threshold | Budget alerts | **A budget alert is a notification, not a cap.** True everywhere and always worth saying twice | Alert configuration and quota mechanisms |
| Free tier | A recurring allowance, not a spending limit | Always Free | **Every major provider has one, and on every one it is a discount rather than a cap** — exceeding it bills silently. Reasoning about allowances transfers directly | Which services, which regions, and how the allowance is counted (GCP counts per *billing account*, not per project) |
| Idle cost | Paying for provisioned capacity nobody is using | — | **The most transferable cost lesson there is.** A reserved-but-unattached IP costs twice an attached one; a min-instance kept warm bills like a running server | Which specific resources bill when idle differs by provider — the *habit of asking* does not |

---

## What we do not claim

- That any two services with similar descriptions are drop-in replacements.
- That portability is free, or that avoiding managed services is automatically wiser. The
  course teaches students to **name the dependency and price the exit**, not to avoid
  dependencies.
- That this table is complete. It covers what the course teaches.

## Maintenance

Cloud services are renamed, merged and repriced. Re-verify this table against official
documentation before each offering, and update `course/references.md` with the dates. A
stale mapping table is worse than none, because students will trust it.

Last verified against official sources: **2026-09-21** (trial terms and free-tier limits
only — the service mappings above are structural and were not individually re-fetched).
