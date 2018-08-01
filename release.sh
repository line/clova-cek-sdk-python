#!/bin/bash

# Script for Pypi release
# 0. Make sure you are on git tag
# 1. Run the script
# 2. Upload sdist

set -e

script_dir=$(cd $(dirname ${BASH_SOURCE:-$0}); pwd)
cd $script_dir

TAG=$(git describe --exact-match --tags HEAD)

VERSION=${TAG/v/}

python setup.py develop sdist
sdist_tar=dist/clova-cek-sdk-${VERSION}.tar.gz
if [ ! -e ${sdist_tar} ]; then
  echo "${sdist_tar} doesn't exist. You may be trying to release wrong version of SDK."
  exit 1
fi

echo "*** Ready to release! clova-cek-sdk $TAG ***"
echo "To test, please run the following command manually:"
echo twine upload ${sdist_tar} --repository-url https://test.pypi.org/legacy/
echo "If it runs successfully, then please run the following command to release the package on PyPi:"
echo twine upload ${sdist_tar} --repository-url https://upload.pypi.org/legacy/
