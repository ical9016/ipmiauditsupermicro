'''
This script is to get RAM count in each server.
It is only needed if you setup many nodes.
For few Nodes, yu can always check it manually from IPMI Web gui.
'''

import grequests
import requests
import urllib3
import argparse
from bs4 import BeautifulSoup
import time
import os
import glob

class ServerData:
	def __init__(self):
		self.ip_addr = ''
		self.dimm_count = 0
		self.hostname = ''


		
def get_dimm_supermicro(ip_addr):
	"""
	Fungsi untuk membaca Supermicro IPMI serial
	"""
	
	ip_addr_curr = ip_addr
	myserver = ServerData()
	myserver.ip_addr = ip_addr
	headers = {
		'Connection': 'keep-alive',
		'Cache-Control': 'max-age=0',
		'Upgrade-Insecure-Requests': '1',
		'Content-Type': 'application/x-www-form-urlencoded',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'en-US,en;q=0.9',
	}
	
	#user and password, default please change if needed
	data = {
	'name': 'ADMIN',
	'pwd': 'ADMIN'
	}
	
	s = requests.session()
	
	#API for login
	r = s.post('https://'+ip_addr_curr+'/cgi/login.cgi', headers=headers,data=data, verify=False, timeout=5)
	
	#API to get hostname
	data = {
	'CONFIG_INFO.XML': '(0,0)',
	'time_stamp': 'Tue Feb 19 2019 18:55:41 GMT+0700 (Indochina Time)',
	'_': ''
	}
	r = s.post('https://'+ip_addr_curr+'/cgi/ipmi.cgi', headers=headers, data=data, verify=False)
	try:
		mybs=BeautifulSoup(r.text,'xml')
		hostname = mybs.find('HOSTNAME')['NAME']
		myserver.hostname=hostname
	except:
		print ('Error reading IPMI result -- hostname from IP Address : ' + ip_addr_curr)
		pass
			
	data = {
	'SMBIOS_INFO.XML': '(0,0)',
	'time_stamp': 'Sat May 18 2019 01:30:49 GMT+0700 (Indochina Time)',
	'_': ''
	}
	
	r = s.post('https://'+ip_addr_curr+'/cgi/ipmi.cgi', headers=headers,data=data, verify=False)
	
	mybs=BeautifulSoup(r.text,'xml')
	list_dimm_loc=[]
	list_dimm_size=[]
	elems =  mybs.find_all('DIMM')
	for item in elems: 
		list_dimm_loc.append(item['LOCATION'])
		list_dimm_size.append(item['SIZE'])
	
	myserver.dimm_count = len(elems)
	print ('IP Address : {} have {} pcs RAM'.format(ip_addr_curr, str(len(elems))))
	for i in range(len(list_dimm_loc)):
		print ('{}\t{}'.format(list_dimm_loc[i],list_dimm_size[i]))
		
	return 	myserver
		
fname = 'file_input.txt'  #text file
fout = 'file_output.csv' #output as csv
myserver = None	

foutput = open(fout, 'w')
with open(fname, 'r') as infile:
		for line in infile:
			line=line.rstrip('\n')
			myserver = get_dimm_supermicro(line)
			foutput.write('{},{}\n'.format(myserver.hostname, myserver.dimm_count))

foutput.close()			