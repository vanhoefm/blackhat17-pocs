# OpenBSD Access Point Denial-of-Service

## Description

This attack exploits two vulnerabilities in the OpenBSD Access Point:

1. It does not terminate the TKIP countermeasures after one minute, meaning the AP will permanently be unusable after our attack.
2. It accepts TKIP MIC failure reports at any time during the handshake, even before the client is authenticated.
Moreover, the AP will use an
an all-zero KCK key to verify the authenticity of this frame.

Background:
- The WPA-TKIP countermeasures disallow any clients from connecting to the AP using WPA-TKIP for one minute.
This is to mitigate weaknesses in WPA-TKIP.
However, OpenBSD permanently blocks clients from connecting.
- This attack works as long as the target network supports WPA-TKIP.


## Proof-of-concept

We created a PoC by patching Linux's `wpa_supplicant` client.
It transmits two MIC failure reports after receiving message 1 from the AP,
and uses an all-zero KCK to authenticate the frame.
This triggers the permanent TKIP countermeasure period, meaning clients can no longer connect to the AP.

To execute the attack first patch `wpa_supplicant`:

		git clone git://w1.fi/srv/git/hostap.git -b hostap_2_6 openbsd-dos
		cd openbsd-dos
		patch -p1 < attack_ap_dos.patch
		cd wpa_supplicant
		cp defconfig .config
		make -j 8

Then edit `network.conf` so it contains the target SSID and run:

		sudo ./wpa_supplicant -D nl80211 -i $INTERFACE -c network.conf

Where `$INTERFACE` is a wireless interface.

