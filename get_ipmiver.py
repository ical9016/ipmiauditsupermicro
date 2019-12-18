'''
This script is used to gather ipmi version of supermicro Nodes.
After doing upgrade for a lot of Nodes, some times we have to check all of them.
Using this script we could easily checking whether all Servers already upgraded.
'''
import grequests
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import argparse
from bs4 import BeautifulSoup
import time
import os
import glob

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class ServerData:
	def __init__(self):
		self.ip_addr = ''
		self.ipmiver = ''
		self.hostname = ''
		
def get_ipmiver_supermicro(ip_addr):
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
	
	#user and password, change if needed
	data = {
	'name': 'ADMIN',
	'pwd': 'ADMIN'
	}
	
	s = requests.session()
	
	#API IPMI to login
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
	
	#API to IPMI ver	
	data = {
	'GENERIC_INFO.XML': '(0,0)',
	'time_stamp': 'Fri Jun 14 2019 15:42:51 GMT+0700 (Indochina Time)',
	'_': ''
	}

	r = s.post('https://'+ip_addr_curr+'/cgi/ipmi.cgi', headers=headers,data=data, verify=False)
	
	mybs=BeautifulSoup(r.text,'xml')
	list_IPMIVER=[]

	elems =  mybs.find('GENERIC')
	ipmiver = elems['IPMIFW_VERSION']
	myserver.ipmiver = ipmiver
	
	#print ('IP Address : {} have IP ver :{}'.format(ip_addr_curr, str(item['IPMIFW_VERSION'])))
	return myserver

	
fname = 'file_input.txt' #input file, consist of IP address of IPMI
fout = 'file_output.csv' #output as csv formal
foutput = open(fout, 'w')
with open(fname, 'r') as infile:
		for line in infile:
			line=line.rstrip('\n')
			myserver=get_ipmiver_supermicro(line)
			print('{},{}\n'.format(myserver.hostname, myserver.ipmiver))
			foutput.write('{},{}\n'.format(myserver.hostname, myserver.ipmiver))
			