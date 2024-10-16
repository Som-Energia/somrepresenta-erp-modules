#!/bin/bash
set -eou pipefail

function step() {
    echo -e "\033[34m${*}\033[0m"
}

REPO_PATH="$(dirname "$(dirname "$(realpath "$0")")")"
echo "$REPO_PATH"

cd "$REPO_PATH"

cat scripts/renamed_modules.yaml | while read old new; do
    old=${old:0:-1}
    step "$old -> $new"
    sed -i 's/\<'$old'\>/'$new'/g' $(grep -rIl '\<'$old'\>' somre_* som_ov_signed_documents)
done

