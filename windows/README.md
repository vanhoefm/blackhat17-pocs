# Windows 7 DoS: win7_dos_attack.py

[You can watch a demonstration of the attack!](https://www.youtube.com/watch?v=goPWTvOjhEM)

## Description

A windows 7 hotspot is vulnerable to an unauthenticated targeted DoS attack that permanently prevents a specific client from connecting to the network. This attack does not require knowledge of credentials, and can be executed by anyone within range of the AP. The attack works by sending two association requests after one another, after first sending an authentication request. The sender MAC address is set the the MAC address of the victim. After this, the victim can no longer connect to the network. This allows an adversary to permanently block specific MAC addresses from connecting to the network.

When the client now tries to connect to the wireless network, the Windows 7 AP will reply using an Association Response with status code 12. This status code means "association denied due to reason outside the scope of this standard.

## Proof-of-concept

The script `win7_dos_attack.py` uses scapy to execute the attack. To use this script, first edit in the `main` function: (1) the BSSID; (2) the MAC address of the victim; (3) the channel; and (4) and SSID of the target network the `main` function. Also set the correct interface to inject frames on, and put this interface in monitor mode. Then you can execute the script on a Linux machine. On my device the set of commands were:

		$ sudo iw wlp0s20u1 set type monitor
		$ sudo ifconfig wlp0s20u1 up
		$ sudo ./win7_dos_attack.py

You can [view a demo of this attack on YouTube](https://www.youtube.com/watch?v=goPWTvOjhEM).

## Notes

This was tested against Windows 7 Professional 64-bit (Service Pack 1 - build 7601), with windows using a TL-WN722N Wi-Fi dongle as AP. This attack assumes the vulnerability is in the Windows Wi-Fi stack instead of in the Atheros driver (but we are not yet 100% sure of this).


# Windows 10 DoS: win10_tkipdos_poc.patch

## Description

A Windows 10 hotspot accepts TKIP MIC failure reports even when the network does not use TKIP. Someone that knows the credentials to the network can abuse this as a denail-of-service, by sending two TKIP MIC failure reports. The hotspot will become unusable until it is restarted. Normally, these MIC failure reports should be ignored.

An adversary must posses the necessary credentials in order to connect with the network, to then send the TKIP MIC failure reports. This significantly lowers the impact of the attack. Nevertheless, in certain scenarios a client may have the necessary credentials to connect to the network, without being a fully trusted device. For example, when hosting a network for a conference where (not fully trusted) people are given the passphrase.

## Proof-of-concept

Our proof-of-concept is a patch to Linux's wpa_supplicant. The patch transmits two MIC failure reports after connecting to the network. This triggers the TKIP countermeasure period. After this, clients can no longer connect to the Windows 10 AP for one minute. Repeating this every minute makes the network unusable. To apply the patche, execute the following commands (on a Linux machine):

		$ git clone git://w1.fi/srv/git/hostap.git -b hostap_2_6 wpasupp
		$ cd wpasupp
		$ patch -p1 < win10_tkipdos_poc.patch

Now compile wpa_supplicant and use it to connect to a CCMP-only network hosted by Windows 10.

## Background

When a connected Wi-Fi client sends two MIC failure reports within a minute, the TKIP countermeasures are started. These countermeasures kick all clients that use TKIP from the network, clear all TKIP keys, and then disallow any clients from connecting to the AP using TKIP for one minute. Note that (normally!) only clients using TKIP can send MIC failure reports, and hence only networks with TKIP enabled are affected by this DoS attack. However, due to a bug in Windows 10, a client can send MIC failure reports even if the network does not use TKIP, i.e., if the network only supports CCMP. Morever, it permanently makes the network unusable, instead of only for one minute.

## Notes

This was tested against Windows 10 Education 64-bit (build 10240), with windows using a TL-WN722N Wi-Fi dongle as AP. This attack assumes the vulnerability is in the Windows Wi-Fi stack instead of in the Atheros driver (but we are not yet 100% sure of this).

