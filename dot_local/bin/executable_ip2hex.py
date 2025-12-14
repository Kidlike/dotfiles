#!/usr/bin/python
import sys
import re

def iptohex(ip):
        octets = ip.split('.')
        hex_octets = []
        for octet in octets:
                if int(octet) < 16:
                        hex_octets.append('0' + hex(int(octet))[2:])
                else:
                        hex_octets.append(hex(int(octet))[2:])
        hex_octets = ''.join(hex_octets)
        return hex_octets

def main():
        if (len(sys.argv) != 2):
                print 'Usage: ./iptohex.py x.x.x.x'
                sys.exit(1)
        ip = sys.argv[1]

        invalidInput = re.search(r'[^0-9\.]', ip)
        if invalidInput:
                print 'Usage: ./iptohex.py x.x.x.x'
        hex_ip = iptohex(ip)
        print "Hex IP: %s " % (hex_ip)
        print "Decimal IP: %s" % (ip)

if __name__ == '__main__':
        main()
