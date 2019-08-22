#!/bin/bash

set -e -x
    
CHANGED_FILES=($(git diff --name-only $TRAVIS_COMMIT_RANGE))
ADDONS_CHANGED=
SCHEMA_CHANGED=0
CHECKER_CHANGED=0

echo "Changed:" "${CHANGED_FILES[@]}"
echo

for file in ${CHANGED_FILES[@]}; do
    if [[ "$file" =~ ^addons/([^/]+).json ]]; then
        ADDONS_CHANGED="$ADDONS_CHANGED ${BASH_REMATCH[1]}"
    elif [ "$file" = "schema.json" ]; then
        SCHEMA_CHANGED=1
    elif [ "$file" = "tools/check-list.py" ]; then
        CHECKER_CHANGED=1
    fi
done

if [[ $SCHEMA_CHANGED == 1 || $CHECKER_CHANGED == 1 ]]; then
    ./tools/check-list.py
elif [ -n "$ADDONS_CHANGED" ]; then
    ./tools/check-list.py $ADDONS_CHANGED
fi
