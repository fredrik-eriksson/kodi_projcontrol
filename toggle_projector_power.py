#!/usr/bin/python2

# -*- coding: utf-8 -*-
# Copyright (c) 2015 Fredrik Eriksson <git@wb9.se>
# This file is covered by the MIT license, read LICENSE for details.

import simplejson
import urllib2

url = "http://localhost:6661/power"
data = simplejson.dumps("toggle")
headers = {'Content-Type': 'application/json'}

req = urllib2.Request(url, data, headers)
res = urllib2.urlopen(req)

print(res.read())
