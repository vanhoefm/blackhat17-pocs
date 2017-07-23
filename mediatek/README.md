# MediaTek Client Downgrade

The network capture [mediatek-downgrade.pcapng](mediatek-downgrade.pcapng) contains a network trace where the MediaTek client is downgraded to WPA-TKIP.
Notice that the beacons and probe responses only advertise support of WPA-TKIP, but the information element in message 3 of the 4-way handshake contains both WPA-TKIP and AES-CCMP.
The client should have detected this mismatch, and aborted the handshake.
However, the MediaTek client continues with the handshake, and is thereby downgraded into using WPA-TKIP.

A public proof-of-concept of this attack is not available.
The above network trace is a simulated attack to test whether the client verifies the information elements received in message 3 of the 4-way handshake.
