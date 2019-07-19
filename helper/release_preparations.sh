#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"




#nosetests3 -v -w "../tests"  \
#    --with-coverage  --cover-erase  --cover-package=qplotutils --cover-html \
#    --cover-html-dir "$DIR/../coverage_report"

cd $DIR/..
source ~/venvs/sample/bin/activate

pytest --cov=qplotutils --cov-report html:coverage $DIR/../tests
deactivate

#cd "$DIR/../docs"
#make html