#!/usr/bin/env bash
# Create the VM that will run the application.
#
# Read this before running it. Every flag below is a decision, and Part 1 of the lab asks
# you to be able to explain three of them.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud
require_free_tier_region

say "Creating ${INSTANCE_NAME} in ${ZONE}"

gcloud compute instances create "$INSTANCE_NAME" \
  --project="$PROJECT_ID" \
  --zone="$ZONE" \
  --machine-type="$MACHINE_TYPE" \
  --boot-disk-size="$BOOT_DISK_SIZE" \
  --boot-disk-type="pd-standard" \
  --image-family="debian-12" \
  --image-project="debian-cloud" \
  --tags="docapp" \
  `# --boot-disk-auto-delete is the DEFAULT, and it is what stops the disk` \
  `# outliving the instance and quietly billing. Lab 2 Part 6 asks you to verify` \
  `# that it actually did what it claims.` \
  --boot-disk-auto-delete \
  `# TODO(lab02): this creates an EPHEMERAL external IP, because no address is named.` \
  `# Find the flag that would give the instance NO external address at all, and the flag` \
  `# that would attach a reserved static one. Do not use either -- write down, in your` \
  `# submission, what each would change about reachability and about cost.` \
  --scopes="https://www.googleapis.com/auth/logging.write" \
  --metadata="enable-oslogin=TRUE"

say "Done"
gcloud compute instances list --project="$PROJECT_ID" \
  --filter="name=$INSTANCE_NAME" \
  --format="table(name, zone, machineType.basename(), status, networkInterfaces[0].accessConfigs[0].natIP:label=EXTERNAL_IP)"

note "The EXTERNAL_IP above is ephemeral: it is released when this instance is deleted,"
note "and you will get a different one next time. That is deliberate -- see Part 6."
