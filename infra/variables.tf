# Everything that differs between environments arrives through a variable.
#
# That is the whole idea of environment management: ONE configuration, and a variable file
# per environment. If you find yourself copying main.tf to make prod, stop -- whatever you
# change in the copy is a difference nobody declared, and undeclared differences are how
# "it works in dev" happens.

variable "project_id" {
  description = "Google Cloud project id."
  type        = string
}

variable "environment" {
  description = "Environment name. Used to name and label every resource."
  type        = string

  validation {
    # Two environments, by design (decision D-27). A third would double the resources for
    # no new concept -- and would hit the one-free-Firestore-database-per-project limit.
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "environment must be 'dev' or 'prod'."
  }
}

variable "region" {
  description = "Deployment region."
  type        = string
  default     = "us-central1"

  validation {
    # Not a preference. The Always Free allowances exist only in these three regions
    # (course/references.md R-01). Anywhere else, this course starts costing money.
    condition     = contains(["us-west1", "us-central1", "us-east1"], var.region)
    error_message = "region must be us-west1, us-central1 or us-east1 -- the Always Free regions."
  }
}

variable "image" {
  description = "Full container image reference to deploy. Built once, promoted unchanged."
  type        = string
}

variable "max_instances" {
  description = "Upper bound on Cloud Run instances. A cost guard rail, not a capacity plan."
  type        = number
  default     = 2

  validation {
    condition     = var.max_instances >= 1 && var.max_instances <= 10
    error_message = "max_instances must be between 1 and 10. The cap keeps a typo from becoming a bill."
  }
}

variable "processing_delay_ms" {
  description = "Simulated work, in milliseconds. Config, not a secret."
  type        = number
  default     = 250
}

variable "log_level" {
  description = "Application log level."
  type        = string
  default     = "info"
}

# TODO(lab06): add a variable that captures something which SHOULD differ between dev and
# prod, and give it a different value in each tfvars file. Then justify it in your
# submission. A hint about what makes a good answer: it should be something where the right
# value genuinely depends on who is using the environment and what it costs to be wrong.
