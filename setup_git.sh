#!/usr/bin/env bash
# Run once after cloning the fresh repo to pin the git identity to mike-datacore.
set -euo pipefail

git config user.name  "mike-datacore"
git config user.email "mike@datacore.vn"

echo "Git identity set:"
git config user.name
git config user.email

# Optional: configure commit signing if you have a GPG key
# git config commit.gpgsign true
# git config user.signingkey <YOUR_KEY_ID>
