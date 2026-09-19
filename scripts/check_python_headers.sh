#!/usr/bin/env bash

set -u

errors=0

for root in src tests; do
    while IFS= read -r -d '' file; do
        relative="${file#./}"
        expected="# ${relative}"

        IFS= read -r first_line < "$file" || first_line=""
        first_line="${first_line%$'\r'}"

        if [[ "$first_line" != "$expected" ]]; then
            printf 'ERROR: %s\n' "$relative"
            printf '       expected: %s\n' "$expected"
            printf '       found:\t %s\n' "$first_line"
            errors=$((errors + 1))
        fi
    done < <(
        find "$root" \
            -type f \
            -name '*.py' \
            ! -name '__init__.py' \
            -print0
    )
done

if (( errors > 0 )); then
    printf '\n%d Python file(s) with an invalid header.\n' "$errors"
    exit 1
fi

printf 'All Python files have the correct path header.\n'
exit 0
