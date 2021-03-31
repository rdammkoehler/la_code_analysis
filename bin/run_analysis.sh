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

if [[ "${#}" -ne 3 ]]; then
    echo "Bad argument count (${#})"
    echo "usage: run_analysis.sh \${CODE_ANALYSIS_LOCATION} \${PRODUCT_CODE_ROOT} \${ANALYSIS_TARGET}"
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

if [[ ! -d "${3}" ]]; then
    echo "Analysis Target folder does not exist"
    exit 4
fi

CODE_ANALYSIS_LOCATION=${1}
PRODUCT_CODE_ROOT=${2}
code_dir=${3}

# setup/configure code analysis tool(s)
pushd "${CODE_ANALYSIS_LOCATION}" > /dev/null || exit 10
source venv/bin/activate
popd > /dev/null || exit 10

# create the analysis command
# TODO parameterize the following
steps=52
ANALYSIS_CMD="python -m metrics.gather --generate-graphs --language java -m method_lines balance complexity fan_out -t ${steps}"

echo "***** processing: ${code_dir}"

# make sure we're as clean as we can be before starting
pushd "${code_dir}" > /dev/null || exit 10
trunk_branch_name=$(git branch --show-current)
git reset --hard
git checkout "${trunk_branch_name}"
git pull
rm checkstyle-config.xml
git reset --hard
git checkout "${trunk_branch_name}"
popd > /dev/null || exit 10

# create a viable filename prefix
repo_name=${code_dir/${PRODUCT_CODE_ROOT}/}
repo_name=${repo_name/\/\.\//}
repo_name=${repo_name//\//-}

# run the actual analysis 
pushd "${CODE_ANALYSIS_LOCATION}" > /dev/null || exit 10
${ANALYSIS_CMD} -D "${code_dir}" --filename "${repo_name}" 
popd > /dev/null || exit 10

# clean up after the run
pushd "${code_dir}" > /dev/null  || exit 10
git checkout "${trunk_branch_name}"
git reset --hard
popd  > /dev/null  || exit 10

# move the results to the folder 
mkdir -p "${code_dir}/../analysis_results"
# don't quote my globs
mv ${CODE_ANALYSIS_LOCATION}/full_results/${repo_name}* "${code_dir}/../analysis_results"


popd > /dev/null || exit 10
