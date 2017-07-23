#!/bin/bash
set -e

# When running this manually outside the git repo first execute:
#   wget https://raw.githubusercontent.com/vanhoefm/asiaccs2017-pocs/master/openbsd/mitm_poc.patch
git clone git://w1.fi/srv/git/hostap.git -b hostap_2_6 openbsd-mitm
cd openbsd-mitm
git apply ../mitm_poc.patch
cd hostapd
cp defconfig .config
make
