from testrail import *
from pprint import *
import sys,getopt
import xml.dom.minidom
import ssl
import os
import fnmatch

def parse_uat_result(filename):
	cidstatus = {}
	xmldoc = xml.dom.minidom.parse(filename)
	testlist = xmldoc.getElementsByTagName('test')
	for test in testlist:
		tags = test.getElementsByTagName('tag')
		for tag in tags:
			cid_str = tag.firstChild.nodeValue
			if cid_str[:4] == "CID:":
				cid = cid_str[4:]
				status = test.getElementsByTagName('status')
				cidstatus[cid] = '1' if status[-1].attributes['status'].value=="PASS" else '5'
	return cidstatus

def main():

	ssl._create_default_https_context = ssl._create_unverified_context
	resultxml = "robot_result.xml"
	projectid = 0
	user = "admin"
	pwd = ""
	folder = ""
	testrail_url = "https://172.18.51.100/testrail/"
	try:
		opts, args = getopt.getopt(sys.argv[1:], "",["pid=", "folder=", "user=", "pwd=", "testrail="])
	except getopt.GetoptError as err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		sys.exit(2)
	for o, a in opts:
		if o == "--folder":
			folder = a;
		elif o == "--pid":
			projectid = a;
		elif o == "--user":
			user = a;
		elif o == "--pwd":
			pwd = a;
		elif o == "--testrail":
			testrail_url = a;
		else:
			assert False, "Unknown option" + o
		
	print "User:" + user + ":" + pwd
	print "Project ID:" + str(projectid) + " TestRail URL:" + testrail_url
	client = APIClient(testrail_url)
	client.user = user
	client.password = pwd

	run = client.send_post('add_run/' + str(projectid), 
		{"suite_id": 1,"name": "This is a new test run","assignedto_id": 1,"include_all": 	"1"})

	for root, dirs, files in os.walk(folder):
		for file in files:
			if not fnmatch.fnmatch(file, '*_output.xml'):
				continue
			cidstatus = parse_uat_result(file)		
			for cid in iter(cidstatus):
				print "Updating test result for case:" + str(cid)
				resp = client.send_post('add_result_for_case/' + str(run['id']) + '/' + str(cid),{"status_id":cidstatus[cid]})
		#pprint(resp)
	print "Done!"

main();

