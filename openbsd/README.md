# OpenBSD Client Man-in-the-Middle

[You can watch a demonstration of the attack!](https://www.youtube.com/watch?v=t4fvgLPOYOw)

## Description

Due to insufficient state checks in the Wi-Fi handshake, clients that use WPA1 or WPA2 are vulnerable to a man-in-the-middle attack.
Summarized, it's not checked whether incoming EAPOL-Key messages are in order.
In particular, a rogue access point can skip the 4-way handshake, meaning the client will never authenticate the AP.


## Proof-of-concept

We created a [PoC patch](mitm_poc.patch) that modifies Linux's `hostapd` to carry out the man-in-the-middle attck.
When an OpenBSD client connects to the rogue AP, it will send message 1 of the group key handshake, instead of starting the 4-way handshake.
The client wrongly accepts this message, replies with message 2 of the group key handshake, and starts receiving and sending *unencrypted* data frames.
To execute the attack first install required dependencies, then download and patch `hostapd`:

		sudo apt-get install libnl-3-dev libnl-genl-3-dev pkg-config libssl-dev rfkill
		./get-and-compile-mitm.sh
		cd openbsd-mitm/hostapd/

Then edit `hostapd.conf` and configure options of the rogue AP to mimic the network you are targetting.
**Disable Wi-Fi in your network manager,** and then start the rogue AP:

		sudo rfkill unblock wifi
		sudo ./hostapd hostapd.conf

The network trace [example-mitm-attack.pcapng](example-mitm-attack.pcapng) contains an example network trace of a successfull man-in-the-middle attack against an OpenBSD client.

## Details

The AP does perform some state checks during the handshake (though not for EAPOL-Key Request frames).
For example, in `ieee80211_recv_group_msg2` it checks that `ni->ni_rsn_gstate != RSNA_REKEYNEGOTIATING`, assuring handshake frames are processed in order.
However, the following functions are missing similar checks:
- `ieee80211_recv_4way_msg1`
- `ieee80211_recv_4way_msg3`
- `ieee80211_recv_wpa_group_msg1`
- `ieee80211_recv_rsn_group_msg1`
- `ieee80211_recv_eapol_key_req`
These functions will process incoming frames, regardless of which handshake frames have already been received.

This bug is exploitable in `ieee80211_recv_rsn_group_msg1`.
Summarized, in the function the client will use an uninitialized all-zero key to validate the frame, after which it thinks the (group) handshake was successfully completed.
In more detail, this function handles group handshake message 1 (`group_msg1`).
This message is used to configure/update the group key, and it should only be processed after the 4-way handshake is completed.
However, the function does not check this.
Therefore, a rogue AP can send `group_msg1` before initiating the 4-way handshake.
On receipt, the function checks that the replay counter is valid, and then verifies the message integrity code (MIC) using the key `ni->ni_ptk`.
Unfortunately, this key has not yet been initialized and is all-zeros, because no 4-way handshake occurred.
Since the key is predictable, an attacker can pass the MIC check.
Eventually the function will execute `ni->ni_port_valid = 1;`, which means the client will now accept incoming data frames, and will start sending data.
Note that, because the flag `IEEE80211_NODE_TXRXPROT` was not set in the `ni->ni_flags` field (this is normally done when receiving message 3), the client transmits (and will receive/accept) plaintext frames.


# OpenBSD Access Point Denial-of-Service

[You can watch a demonstration of the attack!](https://www.youtube.com/watch?v=XLvXL7HabYM)

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

We created a [PoC patch](attack_ap_dos.patch) that modifies Linux's `wpa_supplicant` to carry out the attck.
It transmits two MIC failure reports after receiving message 1 of the 4-way handshake from the AP,
and uses an all-zero KCK to authenticate the frame.
This triggers the permanent TKIP countermeasure period, meaning clients can no longer connect to the AP.

To execute the attack first patch `wpa_supplicant`:

		sudo apt-get install libnl-3-dev libnl-genl-3-dev pkg-config libssl-dev rfkill
		./get-and-compile-dos.sh
		cd openbsd-dos/wpa_supplicant/

Then edit `network.conf` so it contains the target SSID, **disable Wi-Fi in your network manager**, and run:

		sudo rfkill unblock wifi
		sudo ./wpa_supplicant -D nl80211 -i $INTERFACE -c network.conf

Where `$INTERFACE` is a wireless interface.

