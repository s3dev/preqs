#!/usr/bin/env bash 

disables=''
disable=(
    "broad-except"
    "fixme"
    "invalid-name"
    "not-callable"
    "too-few-public-methods"
    "too-many-arguments"
    "too-many-instance-attributes"
    "too-many-lines"
    "too-many-locals"
    "too-many-public-methods"
    "too-many-statements"
)

# Build string of items to disable.
for i in ${disable[@]}; do disables+="${i},"; done

# Generate a custom, project-specific config file.
pylint --reports=yes --disable="${disables}" --generate-rcfile > ../.pylintrc

# Removing lines.
sed -E /use\-implicit\-booleaness\-not\-comparison[\-a-z\=]+/d -i ../.pylintrc
sed -E /prefer\-stubs[\-a-z\=]+/d -i ../.pylintrc
sed -E /suggest\-join[\-a-z\=]+/d -i ../.pylintrc

