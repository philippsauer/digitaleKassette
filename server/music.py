#!/usr/bin/env python
print "Content-type: text/html"
print

import cgi
import cgitb; cgitb.enable() 

head_html = open("html/head.html","r")
nav_html = open("html/nav.html","r")

print head_html.read()
print nav_html.read()

print "<br>Hello World!<br>"
