'''
Please install python 3 and the module that required using pip :
pip install urllib3
pip install requests
pip install argparse
pip install BeautifulSoup

'''

import requests
import argparse
from bs4 import BeautifulSoup
import urllib3


class ServerData:
	def __init__(self, ip_addr_curr,serial):
		self.ip_addr_curr = ip_addr_curr
		self.serial = serial
		self.hostname = ''
		self.mac1=''
		self.mac2=''
	
def get_serial_supermicro(ip_addr):
	"""
	Fungsi untuk membaca Supermicro IPMI serial
	"""
	
	ip_addr_curr = ip_addr
	myserver = None
	try:
		
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
		
		#ini user dan password
		data = {
		'name': 'ADMIN',
		'pwd': 'ADMIN'
		}
		
		s = requests.session()
		
		#tembak api nya IPMI untuk login
		r = s.post('https://'+ip_addr_curr+'/cgi/login.cgi', headers=headers,data=data, verify=False, timeout=5)
		
		#tembal api nya IPMI untu get data serial
		data = {
		'SMBIOS_INFO.XML': '(0,0)',
		'time_stamp': 'Mon Dec 17 2018 18:59:21 GMT+0700 (Indochina Time)',
		'_': ''
		}
		
		r = s.post('https://'+ip_addr_curr+'/cgi/ipmi.cgi', headers=headers, data=data, verify=False, timeout=5)
		#print (r.text)
		
		try:
			mybs=BeautifulSoup(r.text,'xml')
			serial = mybs.find('SYSTEM')['SN']
			myserver = ServerData(ip_addr_curr, serial)
		except:
			print ('Error reading IPMI result -- serial from IP Address : ' + ip_addr_curr)
			pass
		
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
		'Get_PlatformInfo.XML': '(0,0)',
		'time_stamp': 'Fri Feb 22 2019 19:45:19 GMT+0700 (Indochina Time)',
		'_': ''
		}
		r = s.post('https://'+ip_addr_curr+'/cgi/ipmi.cgi', headers=headers, data=data, verify=False, timeout=5)
		
		try:
			mybs=BeautifulSoup(r.text,'xml')
			mac1 = mybs.find('PLATFORM_INFO')['MB_MAC_ADDR1']
			mac2 = mybs.find('PLATFORM_INFO')['MB_MAC_ADDR2']
			myserver.mac1=mac1
			myserver.mac2=mac2
		except:
			print ('Error reading IPMI result -- mac from IP Address : ' + ip_addr_curr)
			pass 

	except:
		print ("could not getting IPMI data from {} something unexpected happen, exit function ..".format(ip_addr_curr))
		pass
		
	return myserver

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
		
if __name__ == "__main__":
	
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file", help="file input consist of IP addresses of Supermicro's IPMI(text file)", required=True)
	parser.add_argument("-o", "--output", help="Save File Output(in csv format)")
	parser.add_argument("-e", "--error", help="Save File Error(text file)")	
	args = parser.parse_args()
	fname = args.file
	list_serverdata = []
	list_error = []
	with open(fname, 'r') as infile:
		for line in infile:
			ip_addr = line.rstrip('\n')
			myserver = get_serial_supermicro(ip_addr)
			if myserver:
				print ("IP Address : {} have Serial : {}".format(ip_addr,myserver.serial))
				list_serverdata.append(myserver)
			else:
				print ("error geeting data")
				list_error.append(ip_addr)
	
	if args.output:
		print ('saving into file: '+args.output)
		fname = open(args.output,'w')
		for item in list_serverdata:
			line = "{},{},{},{},{}\n".format(item.hostname, item.ip_addr_curr, item.serial, item.mac1, item.mac2)
			fname.write(line)
		fname.close()

	if args.error:	
		fname_error = open(args.error,'w')
		for item in list_error:
			print ('error for '+item)
			fname_error.write(item+'\n')
		fname_error.close()
		
	
	print ('Process Done ...')

		
