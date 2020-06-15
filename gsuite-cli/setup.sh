#!/usr/bin/env bash

docker build -t onboarding-cli:1.0 .
mkdir ~/.onboarding-cli
FILE=$(find ~/Downloads -name 'client_secret_*' -print0 | xargs -0 ls -t | head -1)
cp "$FILE" ~/.onboarding-cli/credentials.json
echo Add the following line to your bashrc or zshrc file: \
alias disqo='"docker run -it --rm -e FRESH_API -v ~/.onboarding-cli:/app/files onboarding-cli:1.0 "$@""'