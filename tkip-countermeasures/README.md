# Impossible TKIP Countermeasures

## Description

We found a denial-of-service vulnerability in several Access Points (APs). Summarized, these APs accept TKIP MIC failure reports even when the network does not use TKIP. Someone with credentials to the network can abuse this to take make a network unusable, by sending two TKIP MIC failure reports every minute. Normally this should not be possible if the network is only configured to use CCMP.

Background:
- Vulnerable Access Points are Broadcom, Windows 10, and Aerohive.
*Against a Windows 10 hotspot, this results in a permanent denial-of-service attack (requiring a reboot the the AP).*
- The WPA-TKIP countermeasures disallow any clients from connecting to the AP using WPA-TKIP for one minute.
This is to mitigate weaknesses in WPA-TKIP.
- An adversary must posses credentials to connect with the network.
Nevertheless, sometimes a client has the necessary credentials to connect to the network, without being a trusted device.
Examples are public networks such as eduroam, a hotel network, a conference network, etc.

## Proof-of-concept

We created a [PoC patch](tkipdos_poc.patch) that modifies Linux's `wpa_supplicant` to carry out the attck.
It transmits two MIC failure reports after completing the 4-way handshake with the AP.
This triggers the TKIP countermeasure period, even though TKIP is not used by the network.
As a result, clients can no longer connect to the AP.

To execute the attack first patch `wpa_supplicant`:

		git clone git://w1.fi/srv/git/hostap.git -b hostap_2_6 wpasupp-tkipdos
		cd wpasupp-tkipdos
		wget https://raw.githubusercontent.com/vanhoefm/asiaccs2017-pocs/master/tkip-countermeasures/tkipdos_poc.patch
		git apply tkipdos_poc.patch
		cd wpa_supplicant
		cp defconfig .config
		make -j 8

Then edit `network.conf` so it contains the target SSID and password of the network, and run:

		sudo ./wpa_supplicant -D nl80211 -i $INTERFACE -c network.conf

Where `$INTERFACE` is a wireless interface.

