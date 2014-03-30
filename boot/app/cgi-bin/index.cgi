#!/usr/bin/env python

from wifi import *
import os
import cgi
import cgitb; cgitb.enable()  # for troubleshooting

# some housekeeping
print "Content-type: text/html"
print

# get the form input
form = cgi.FieldStorage()
network = form.getvalue("network", "")
password = form.getvalue("password", "")

# if not submitted yet, show them the network selection form
if not network:

    wifi = Wifi()

    networks = [x.replace("\n","") for x in wifi.access_points if x.replace("\n","") != "Jasper"]
    select_code_split = ["<option value=\"%s\">%s</option>" % (network, network) for network in networks]
    select_code = "".join(select_code_split)

    response = open("index-template.html","r").read().replace("{{ select_code }}", select_code)
    print response

# otherwise, show them the password form
elif not password:
    response = open("key-template.html","r").read().replace("{{ network }}", cgi.escape(network))
    print response

# in the final case, process the wifi password and network data
else:
    # show the confirmation page
    response = open("connecting-template.html","r").read()
    print response

    # save the configuration
    wifi = Wifi()
    wifi.add_wifi(network, password)