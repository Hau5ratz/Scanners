#!/usr/bin/python3.6
import os

os.chdir('/home/dc-user/wip/datadbmine')
print('Starting Scans')
from Scanners import apple_scan
from Scanners import damaz_scan
from Scanners import facebook_scan
from Scanners import google_scan
from Scanners import microsoft_scan
from Scanners import samsung_scan
from Scanners import mcscan
from Scanners import amex_scan
from Scanners import visa_scan
from Scanners import uber_scan
from Scanners import Grab_scan
samsung_scan.Scanner().initialize()
apple_scan.Scanner().initialize()
damaz_scan.Scanner().initialize()
facebook_scan.Scanner().initialize()
microsoft_scan.Scanner().initialize()
mcscan.Scanner().initialize()
google_scan.Scanner().initialize()
amex_scan.Scanner().initialize()
visa_scan.Scanner().initialize()
uber_scan.Scanner().initialize()
Grab_scan.Scanner().initialize()
print('\nFinished')

