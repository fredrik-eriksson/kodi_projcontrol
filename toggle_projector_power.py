#!/usr/bin/python2
import simplejson
import urllib2

url = "http://localhost:6661/power"
data = simplejson.dumps("toggle")
headers = {'Content-Type': 'application/json'}

req = urllib2.Request(url, data, headers)
res = urllib2.urlopen(req)

print(res.read())
