# References

Dated, with an explicit verification status for each entry. Readings are chosen to be
**free to access** and short enough to fit the 30-minute weekly reading budget.

## Verification status key

| Status | Meaning |
|---|---|
| **FETCHED 2026-09-21** | The page was retrieved during authoring and its content confirmed the claim made here |
| **SEARCH-CONFIRMED 2026-09-21** | Existence and bibliographic details confirmed via search results; full text not retrieved in this session |
| **NOT VERIFIED** | Cited from general knowledge — **must be checked before being given to students** |

Nothing in this repository may cite a source that has not reached at least
SEARCH-CONFIRMED before it is put in front of a class.

---

## R-01 · Google Cloud Free Trial and Free Tier
<https://cloud.google.com/free/docs/free-cloud-features>
**FETCHED 2026-09-21** (served from `docs.cloud.google.com`).

Confirmed: $300 Welcome credit over 90 days; eligibility limited to users who have never
been paying customers of Google Cloud, Google Maps Platform or Firebase and have not
previously signed up for the trial; a payment method is required for identity verification
(a temporary authorisation, not a charge); at trial end the billing account closes and
associated projects and resources are **stopped**, with a 30-day grace period for recovery
by upgrading; upgrading to paid billing is **manual**.

Always Free limits confirmed on the same page, relevant to this course:
1 non-preemptible `e2-micro` instance per month in `us-west1`, `us-central1` or `us-east1`,
plus 30 GB-months standard persistent disk and 1 GB egress · Cloud Storage 5 GB-months
regional in those US regions, 5,000 Class A and 50,000 Class B operations/month ·
Cloud Run 2M requests, 360,000 GB-seconds, 180,000 vCPU-seconds/month · Pub/Sub 10 GiB
messages/month · Cloud Logging first 50 GiB per project/month · Cloud Build 2,500
build-minutes/month.

*Used by:* `operations/cloud-access-and-fallback.md`, `operations/cost-model.md`, D-18.

## R-02 · Google Cloud Free Trial FAQs
<https://cloud.google.com/signup-faqs>
**FETCHED 2026-09-21.**

Confirmed additionally: multiple users at the same organisation may each sign up and each
receive their own credit; a personal credit card is acceptable (a corporate card is not
required); a pending authorisation may appear for 1–14 business days; **no charges occur
unless the user manually upgrades**; after the trial and grace period the account closes
and workloads are deleted with no charge.

*Used by:* the cost and access sections of the syllabus, and the pair-billing rules in
`assessment-plan.md`.

## R-03 · Terraform provider for Google Cloud — releases
<https://github.com/hashicorp/terraform-provider-google/releases>
**FETCHED 2026-09-21.** The provider is on the 8.x line (8.x releases dated late August /
early September 2026; a 7.46.1 maintenance release dated 2026-09-04 also present).

*Used by:* D-03. `infra/` pins `hashicorp/google ~> 8.0`. Re-check before each offering, and
note that v8.0.0 contained breaking changes — configurations written against 7.x are not
guaranteed to apply.

## R-04 · Google Cloud pricing
<https://cloud.google.com/pricing/list>
**NOT VERIFIED for specific rates.** Two pricing pages were fetched on 2026-09-21
(`/compute/all-pricing` and `/products/compute/pricing/general-purpose`) and **neither
returned usable E2-family figures**.

**Therefore no per-service dollar rate appears anywhere in this repository.** Fabricating a
plausible-looking price would be worse than leaving the field empty, because a student
would believe it. `operations/cost-model.md` states the method, the quantities and the
region, and leaves the rate cells blank with the retrieval procedure attached. Rates are
filled in during Stage C, each stamped with its retrieval date.

## R-05 · NIST SP 800-145, *The NIST Definition of Cloud Computing*
Mell, P. and Grance, T., NIST, September 2011.
<https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-145.pdf>
**FETCHED 2026-09-21.** Authors, date, the five essential characteristics (on-demand
self-service, broad network access, resource pooling, rapid elasticity, measured service)
and the three service models (SaaS, PaaS, IaaS) all confirmed.

*Assigned in:* Week 1. Three pages, free, and the canonical definition — which is exactly
why it is used rather than a vendor's marketing page. Worth telling students that this
definition is from 2011 and predates serverless, so the gaps are informative.

## R-06 · *Site Reliability Engineering* (the Google SRE Book), free online edition
<https://sre.google/sre-book/table-of-contents/>
**FETCHED 2026-09-21.** Free to read online under CC BY-NC-ND 4.0. Chapters confirmed:
**Ch. 4 Service Level Objectives**, **Ch. 6 Monitoring Distributed Systems**,
**Ch. 21 Handling Overload**, **Ch. 22 Addressing Cascading Failures**.

*Assigned in:* Week 11 (Ch. 4 and selected parts of Ch. 6). Chapters 21–22 are offered as
optional enrichment — they are excellent and too long for the budget.

## R-07 · Armbrust, M. et al., "A View of Cloud Computing"
*Communications of the ACM*, 2010, 53(4), pp. 50–58. DOI 10.1145/1721654.1721672
**SEARCH-CONFIRMED 2026-09-21.** Bibliographic details confirmed; the CACM page returned
403 to automated retrieval in this session, so **check student access before assigning**.
Institutional ACM access or an open-access mirror may be needed.

*Candidate for:* Week 1 enrichment. Historically important framing of elasticity,
statistical multiplexing and the obstacles to adoption. If access proves awkward, R-05
alone is sufficient for the required reading.

## R-08 · "Exponential Backoff And Jitter", AWS Architecture Blog
<https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/>
**SEARCH-CONFIRMED 2026-09-21.** Not fetched. The related Amazon Builders' Library article
"Timeouts, Retries, and Backoff with Jitter" has **moved** — the `aws.amazon.com/builders-library/`
URL now redirects to `builder.aws.com`, and the new location did not return article content
to automated retrieval. Verify the working URL before assigning either.

*Candidate for:* Week 10. Deliberately chosen from a **different** provider to a GCP course,
so students see that retry and jitter reasoning is not GCP-specific. Note for the teaching
guide: a vendor engineering blog is a good source for a mechanism and a poor source for a
comparative claim.

---

## Deliberately not used

- **Vendor comparison tables** ("GCP service X = AWS service Y"). They encourage exactly
  the interchangeability error `concept-to-gcp-map.md` exists to prevent.
- **Certification study guides.** Wrong objective (A-10, non-goals).
- **Paywalled textbooks as required reading.** Required readings must be free to access.
  *Release It!* (Nygard) and *Designing Data-Intensive Applications* (Kleppmann) are
  excellent and are mentioned as optional purchases only — neither is required, and
  neither has been verified as available through the institution.
- **Any source cited from memory without a check.** See the status key above.

---

## Maintenance

| Task | When |
|---|---|
| Re-fetch R-01 and R-02 (trial terms) | Before each offering, and before finalising setup instructions |
| Re-fetch R-03 (provider version) and re-test `infra/` | Before each offering |
| Fill R-04 rates and stamp the date | Stage C, per lab |
| Re-check R-07 and R-08 access | Before assigning them |

Every claim about current GCP behaviour, pricing, quotas or trial limits in this repository
traces to an entry above. If a claim has no reference, it is a bug.
