#!/usr/bin/env bash
#shellcheck disable=SC1091
#   SC1091 == unable to follow sourced files

if [[ -z "${1}" ]]; then
    echo "Code Analysis Statistics File is a required parameter"
    exit 1
fi
input_file=${1}

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" 
done

DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
export DIR
pushd "${DIR}" > /dev/null || exit 1
pushd ".." > /dev/null || exit 2
source venv/bin/activate
python -m trendy "${input_file}"
deactivate
popd > /dev/null || exit 3
popd > /dev/null || exit 4
