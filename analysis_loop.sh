#!/usr/bin/env bash
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" 
done
export DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
pushd ${DIR} > /dev/null

# TODO parameterize some of this stuff
CODE_ANALYSIS_LOCATION=/Users/rpd/projects/la/code-analysis
PRODUCT_CODE_ROOT=/Users/rpd/projects/la/ford/ford-digital/enrollment

# NOTE: the following line assumes we are at the root of the folder structure
ALL_TOP_LEVEL_FOLDERS=`find ${PRODUCT_CODE_ROOT}/. -type d -depth 2`

# setup/configure code analysis tool(s)
pushd ${CODE_ANALYSIS_LOCATION} > /dev/null
if [[ -z NO_RE_VENV ]]; then
    rm -Rf venv && python -m venv venv && source venv/bin/activate && pip install --upgrade pip setuptools && deactivate
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
fi
source venv/bin/activate
popd > /dev/null

# main run loop; repeatedly execute the analysis command!
pushd ${DIR} > /dev/null
for code_dir in ${ALL_TOP_LEVEL_FOLDERS}; do
    echo "starting: ./run_analysis.sh \"${CODE_ANALYSIS_LOCATION}\" \"${PRODUCT_CODE_ROOT}\" \"${code_dir}\" &"
    ./run_analysis.sh "${CODE_ANALYSIS_LOCATION}" "${PRODUCT_CODE_ROOT}" "${code_dir}" >> analysis.log 2>&1  &
    sleep 2
done

popd > /dev/null

popd > /dev/null
