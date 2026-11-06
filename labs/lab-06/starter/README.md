# Lab 6 starter

| File | Part | What it does |
|---|---|---|
| `config.env.example` | 2 | Copy to `config.env` (gitignored). Project id and `owner/name` of your repository |
| `00-registry-and-image.sh` | 2 | Creates the Artifact Registry repository Labs 4 and 5 deleted, builds one image from your tree, and prints it **by digest** |
| `01-bootstrap-pipeline.sh` | 4 | Federation pool and provider, deployer account and roles, state bucket. Prints the values `deploy.yml` needs |
| `02-teardown-pipeline.sh` | **week 15** | Removes the above, state bucket last. **Not run in Lab 6**: the project deploys through this pipeline in weeks 14–15, and a deleted pool's id cannot be reused for 30 days |

**Supplied since Lab 6 became a one-week lab** (`planning/decisions.md` D-67). Until then
students set up federation themselves from the documentation; the time that took went on
debugging an attribute condition rather than on what Part 4 marks.

**Status: not yet run against a real project.** The commands follow Google's documented
Workload Identity Federation setup for GitHub Actions. Like everything else in this course
that touches Google Cloud, they have not been executed against a live project
(`planning/progress.md`). Read each block before running it; where a command fails, its error
and the current documentation decide.
