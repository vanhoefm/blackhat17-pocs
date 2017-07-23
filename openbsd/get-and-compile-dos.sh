#!/bin/bash
set -e

# When running this manually outside the git repo first execute:
#   wget https://raw.githubusercontent.com/vanhoefm/asiaccs2017-pocs/master/openbsd/attack_ap_dos.patch
git clone git://w1.fi/srv/git/hostap.git -b hostap_2_6 openbsd-dos
cd openbsd-dos
git apply ../attack_ap_dos.patch
cd wpa_supplicant
cp defconfig .config
make

