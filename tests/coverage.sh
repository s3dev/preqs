#!/usr/bin/env bash

path="./htmlcov/index.html"

# Parse HTML results to get total coverage result.
function get_coverage() {
    if [ -f ${path} ]; then
        cov=$( grep "</tfoot>" -B3 ${path} | grep "data-ratio" | grep -Eo ">[0-9]{1,3}%<" | grep -Eo "[^><]+" )
        echo $cov
    fi
}

printf "\nRunning unit tests under coverage ..."
coverage run -m unittest discover

printf "\nGenerating HTML report ...\n- "
coverage html
printf "Done.\n"

total=$( get_coverage )
printf "\nTotal coverage: %s\n\n" $total

