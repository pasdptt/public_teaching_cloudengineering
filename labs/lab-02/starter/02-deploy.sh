#!/usr/bin/env bash
# Put the application on the instance and start it.
#
# This is deliberately crude: copy the files, run it under systemd, done. It is the kind of
# deployment script people really do write first, and keeping it by hand for eight weeks is
# what makes Terraform in Lab 6 feel like an answer rather than a new tool to learn.
source "$(dirname "$0")/lib.sh"
load_config
require_gcloud

APP_SRC="$(cd "$(dirname "$0")/../../../application" && pwd)"
[[ -d "$APP_SRC" ]] || { echo "ERROR: cannot find application/ at $APP_SRC" >&2; exit 1; }

say "Copying the application to ${INSTANCE_NAME}"
gcloud compute scp --recurse "$APP_SRC" "${INSTANCE_NAME}:~/application" \
  --project="$PROJECT_ID" --zone="$ZONE"

say "Installing and starting"
gcloud compute ssh "$INSTANCE_NAME" --project="$PROJECT_ID" --zone="$ZONE" --command "
  set -euo pipefail
  sudo mkdir -p /opt/docapp
  sudo cp -r ~/application /opt/docapp/
  sudo tee /etc/systemd/system/docapp.service >/dev/null <<'UNIT'
[Unit]
Description=docapp
After=network.target

[Service]
# TODO(lab02): DOCAPP_HOST is 0.0.0.0 here and 127.0.0.1 on your laptop.
# Part 2 asks you to explain why this machine needs the different value, and what that
# value means on a host that has a public address.
Environment=DOCAPP_HOST=0.0.0.0
Environment=PORT=8080
Environment=DOCAPP_DATA_DIR=/var/lib/docapp
Environment=DOCAPP_LOG_LEVEL=info
ExecStart=/usr/bin/python3 -m docapp
WorkingDirectory=/opt/docapp/application
Restart=on-failure
# Not root. The application needs no privileges, and week 1's shared-responsibility
# discussion is about exactly this kind of choice being yours rather than the provider's.
User=nobody
StateDirectory=docapp

[Install]
WantedBy=multi-user.target
UNIT
  sudo systemctl daemon-reload
  sudo systemctl enable --now docapp
  sleep 2
  systemctl is-active docapp
  curl -sS http://127.0.0.1:8080/healthz
"

say "The application is healthy ON THE INSTANCE."
note "Now try it from your laptop using the external IP. Predict the result first."
