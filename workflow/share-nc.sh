#!/usr/bin/env bash
# AUTHOR: Violet (violet@def.au)
VERSION=0.2
RETRY=15
RETRY_TIME=5
ERR_STRING="Error: api request: failure (404): Wrong path, file/folder does not exist"

necPath="$(which nec)"
direct=false
stable=false
while [ "$#" -gt 0 ]; do
    case $1 in
        -dl|--direct) direct=true; shift ;;
        -d|--dest) ncRoot="$2"; shift 2;;
        -s|--script|--stable) stable=true; shift ;;
        --nec) necPath=$(realpath "$2"); shift 2;;
        -v|--version) echo "$VERSION"; exit 0 ;;
        *) srcPath=$(realpath "$1"); shift ;; # works for files or folders at srcPath
    esac
done 
fileName=$(basename "$srcPath")

if [ -z "$srcPath" ]; then 
    echo "No path given"
    exit 1
fi

if [ -d "$srcPath" ]; then 
    # always use indirect links for folder upload.
    direct=false
fi

# add slug to dest filename if necessary to avoid collisions.
cnt=1
propfileName="$fileName"
while [ -e "${ncRoot}/${propfileName}" ]; do 
    propfileName="${fileName%%.*}-${cnt}.${fileName#*.}"
    (( cnt+=1 ))
done
fileName="$propfileName"

cp -r "$srcPath" "${ncRoot}/${fileName}"

# retry based on vars while waiting for nextcloud to sync
out=$("$necPath" share --expire 'in 6 weeks' "${ncRoot}/${fileName}" 2>&1)
cnt=0
while [ "$out" == "$ERR_STRING" ] && [  $cnt -lt "$RETRY" ]; do
    if [ "$stable" != true ]; then 
        echo "File not synced to cloud; retrying"
    fi
    sleep "$RETRY_TIME"
    out=$("$necPath" share --expire 'in 6 weeks' "${ncRoot}/${fileName}" 2>&1)
    (( cnt+=1 ))
done 

# Stable output format for last 2 lines of stdout:
# <Status string describing success/failure with time> \n <Link URL if success>
at=$(date +"%Y-%m-%d %H:%M")
if [ "$out" == "$ERR_STRING" ]; then
    printf "Failure to upload %s after %s retries at %s" "$srcPath" "$cnt" "$at"
    printf "
    "
    exit 1
else
    out=$(tail -n 1 <<< "$out")
    if [ "$direct" = true ]; then
        out="${out}/download/${fileName}"
    fi 
    printf "Success uploading %s at %s" "$srcPath" "$at"
    printf "
    %s" "$out"
    pbcopy <<< "$out"
    exit 0
fi
