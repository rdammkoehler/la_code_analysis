#!/usr/bin/env bash
#shellcheck disable=SC1091
#   SC1091 == unable to follow sourced files

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" 
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
export DIR
pushd "${DIR}" > /dev/null || exit 1


if [[ "${#}" -ne 2 ]]; then
    echo "Bad argument count (${#})"
    echo "usage: run_analysis.sh \${CODE_ANALYSIS_LOCATION} \${PRODUCT_CODE_ROOT}"
    echo "You ran: ${*}"
    exit 1
fi

if [[ ! -d "${1}" ]]; then
    echo "Code Analysis Location folder does not exist"
    exit 2
fi

if [[ ! -d "${2}" ]]; then
    echo "Product Code Root folder does not exist"
    exit 3
fi

CODE_ANALYSIS_LOCATION=${1}
PRODUCT_CODE_ROOT=${2}

# NOTE: the following line assumes we are at the root of the folder structure
# TODO this now picks up the .git, venv, and .pytest_cache folder; we should exclude those
ALL_TOP_LEVEL_FOLDERS=$(find ${PRODUCT_CODE_ROOT}/. -type d -depth 2)

# setup/configure code analysis tool(s)
pushd ${CODE_ANALYSIS_LOCATION} > /dev/null || exit 1
if [[ -z "${NO_RE_VENV}" ]]; then
    rm -Rf venv && python -m venv venv && source venv/bin/activate && pip install --upgrade pip setuptools && deactivate
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
fi
source venv/bin/activate
popd > /dev/null || exit 1

# main run loop; repeatedly execute the analysis command!
pushd "${DIR}" > /dev/null  || exit 1
for code_dir in ${ALL_TOP_LEVEL_FOLDERS}; do
    if [[ ! ${code_dir} =~  .*(\.git|venv|\.pytest_cache).*$ ]]; then
      echo "starting: ./run_analysis.sh \"${CODE_ANALYSIS_LOCATION}\" \"${PRODUCT_CODE_ROOT}\" \"${code_dir}\" &"
      ./run_analysis.sh "${CODE_ANALYSIS_LOCATION}" "${PRODUCT_CODE_ROOT}" "${code_dir}" >> analysis.log 2>&1  &
      if [[ -z "${SLEEP_NOT}" ]]; then
        sleep 2
      fi
    else
      echo "Ignoring ${code_dir}"
    fi
done

popd > /dev/null  || exit 1

popd > /dev/null  || exit 1
