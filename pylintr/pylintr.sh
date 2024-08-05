#!/usr/bin/env bash
#-----------------------------------------------------------------------
# Prog:     pylintr.sh
# Version:  0.4.1
# Desc:     This script walks down a project tree searching for all
#           *.py files and runs pylint over each file, using the default
#           pylint config file and stores the report to the defined
#           ${OUTPUT} location.
#
#           Once complete, the score from each report is written to a
#           summary file, which is printed at the end of the script.
#
# Platform: Linux / Windows*
#           *The script has been designed to run on both Linux and
#           Windows, providing Windows has git bash, cygwin, or the
#           like installed.
#
# Deploymt: This script (and its parent directory) should be placed at
#           the top level of a project.
#
# UPDATES:
# 11.01.19  J. Berendt  0.1.0  Written.
# 14.01.19  J. Berendt  0.1.1  Updated regex for accuracy.
#                              Moved script and output into same dir.
#                              Added date run to summary.
# 17.01.19  J. Berendt  0.1.2  Converted line endings to Unix format.
# 10.06.20  J. Berendt  0.2.0  Updated to use the local .pylintrc file
#                              if available.
# 30.04.21  J. Berendt  0.2.1  1) Updated the output files to contain 
#                              the parent directory's name 
#                              (if applicable)to prevent modules with 
#                              the same name from being overwritten.
#                              2) Updated the filename filter to allow
#                              files with an underscore after the first
#                              character. For example: test_thing1.py
# 26.05.21  J. Berendt  0.3.0  Updated to print a second summary; 
#                              showing pylintr scores less than 10;
# 27.08.21  J. Berendt  0.3.1  Updated to allow *.py files with two or
#                              more characters (including numbers) in the 
#                              filename to be linted. 
#                              Previously, numbers were not allowed.
# 20.01.23  J. Berendt  0.4.0  Updated generate rcfile script to include
#                              regex patterns for arguments and variable
#                              names, as a later version of pylint 
#                              (2.14+)? has changed the way names are 
#                              validated.
#                              Also updated to include more arguments
#                              which are passed into pylint.
#                              ** NOTE: This version of the rcfile works 
#                              with pylint 2.14+. ** 
# 20.03.24  J. Berendt  0.4.1  Added README.md and LICENSE files in 
#                              preparation for uploading to GitHub.
#-----------------------------------------------------------------------

EXT=".plr"
OUTPUT="./results"
SUMMARY="${OUTPUT}/summary${EXT}"

# TEST FOR OUTPUT DIRECTORY
if [ ! -d ${OUTPUT} ]; then
    echo
    echo Creating output directory ...
    mkdir ${OUTPUT}
    printf "Done.\n\n"
else
    echo
    echo Removing current results ...
    rm ${OUTPUT}/*${EXT}
    printf "Done.\n\n"
fi

# Determine which .pylintrc file to use.
[ -f "../.pylintrc" ] && rcfile='--rcfile=../.pylintrc' || rcfile=""

# RUN PYLINT OVER ALL *.PY FILES (EXCLUDE docs DIRECTORY)
for f in $( /usr/bin/find ../ -name "*.py" | grep -v "docs" ); do
    bname=$( basename ${f} )
    dname=$( basename $( dirname ${f} ) )_
    [ $dname = ".._" ] && dname=""
    if [[ ${bname} =~ ^[a-z][a-z0-9_]+\.py ]]; then
        echo Processing: ${f}
        outname=${dname}$( echo ${bname} | sed s/.py// )${EXT}
        pylint "${rcfile}" ${f} > "${OUTPUT}/${outname}"
    fi
done

# READ EACH REPORT AND POPULATE RESULTS TO SUMMARY
echo Pylint Summary: > ${SUMMARY}
echo ------------------------ >> ${SUMMARY}
for f in ${OUTPUT}/*; do
    if [ ${f} != ${SUMMARY} ]; then
	score=$( cat ${f} | grep -Eo "^Your.*at\s([0-9]+\.[0-9]+\/[0-9]+)" | awk '{ print $NF }' )
        echo $( basename ${f} ): ${score} >> ${SUMMARY}
    fi
done
echo ------------------------ >> ${SUMMARY}
echo
echo Run date: $( date ) >> ${SUMMARY}

# PRINT SUMMARY
cat ${SUMMARY}
printf "\n"

# PRINT SUMMARY 2
printf "Scores < 10 Summary:\n"
echo "---------------------"
grep ".plr:" ${SUMMARY} | grep -v "10.00/10"
echo "---------------------"
printf "\nDone.\n\n"

