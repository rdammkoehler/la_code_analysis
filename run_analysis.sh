#!/usr/bin/env bash
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" 
done
export DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
pushd ${DIR} > /dev/null

if [[ ! "${#}" -ge 3 ]]; then
    echo "Not enough arguments supplied (${#})"
    echo 'usage: run_analysis.sh $CODE_ANALYSIS_LOCATION $PRODUCT_CODE_ROOT $ANALYSIS_TARGET'
    echo "You ran: ${@}"
    exit -1
fi

if [[ -z "${1}" ]]; then
    echo "Code Analysis Location is a required parameter"
    exit -2
fi

if [[ -z "${2}" ]]; then
    echo "Product Code Root folder is a required parameter"
    exit -3
fi

if [[ -z "${3}" ]]; then
    echo "Analysis Target folder is a required parameter"
    exit -4
fi

CODE_ANALYSIS_LOCATION=${1}
PRODUCT_CODE_ROOT=${2}
code_dir=${3}

# NOTE: the following line assumes we are at the root of the folder structure
ALL_TOP_LEVEL_FOLDERS=`find ${PRODUCT_CODE_ROOT}/. -type d -depth 2`

# setup/configure code analysis tool(s)
pushd ${CODE_ANALYSIS_LOCATION} > /dev/null
source venv/bin/activate
popd > /dev/null

# create the analysis command
# TODO parameterize the following
steps=52
ANALYSIS_CMD="python -m metrics.gather --language java -m method_lines balance complexity fan_out -t ${steps}"

echo "***** processing: ${code_dir}"

# make sure we're as clean as we can be before starting
pushd ${code_dir} > /dev/null
trunk_branch_name=`git branch --show-current`
git reset --hard
git checkout ${trunk_branch_name}
git pull
rm checkstyle-config.xml
git reset --hard
git checkout ${trunk_branch_name}
popd > /dev/null

# create a viable filename prefix
repo_name=${code_dir/${PRODUCT_CODE_ROOT}/}
repo_name=${repo_name/\/\.\//}
repo_name=${repo_name//\//-}

# run the actual analysis 
pushd ${CODE_ANALYSIS_LOCATION} > /dev/null
${ANALYSIS_CMD} -D ${code_dir} --filename ${repo_name} 
popd > /dev/null

# clean up after the run
pushd ${code_dir} > /dev/null
git checkout ${trunk_branch_name}
git reset --hard
popd  > /dev/null

# move the results to the folder 
mkdir -p ${code_dir}/../analysis_results
mv ${CODE_ANALYSIS_LOCATION}/full_results/${repo_name}* ${code_dir}/../analysis_results/.


popd > /dev/null
