import yaml
import os, subprocess

class Wifi:

    access_points = []

    def __init__(self):

        subprocess.call("iwlist wlan0 scan > temp.txt", shell = True)
        output = open("temp.txt")
        lines = output.readlines()

        for index, line in enumerate(lines):

            if "Address" in line:

                name = lines[index + 1].split("\"")[1]
                self.access_points.append(name)

        self.access_points = list(set(self.access_points))

        os.system("rm temp.txt")

    def add_wifi(self, SSID, KEY=""):
        networks = yaml.safe_load(open("networks.yml", "r"))

        # add new network to front of list
        network = {"SSID": SSID, "KEY": KEY}
        networks.insert(0, network)

        with open('networks.yml', 'w') as outputFile:
            output = yaml.dump(networks)
            outputFile.write(output)

    def set_default_wifi(self, SSID, KEY=""):

        text = open("connect.txt", "r").read()
        text = text.replace("{{ SSID }}", SSID)
        text = text.replace("{{ KEY }}", KEY)

        outputFile = open("/etc/network/interfaces", "w")
        outputFile.write(text)
        outputFile.flush()
        outputFile.close()

        subprocess.call(["sudo", "/etc/init.d/networking", "restart"])

    def setup_adhoc(self):

        text = open("broadcast.txt", "r").read()
        outputFile = open("/etc/network/interfaces","w")
        outputFile.write(text)
        outputFile.flush()
        outputFile.close()

        subprocess.call(["sudo", "/etc/init.d/networking", "restart"])
        subprocess.call(['sudo', '/usr/sbin/dhcpd', '-q', '-cf', '/etc/dhcp/dhcpd.conf', '-pf', '/var/run/dhcpd.pid'])
        subprocess.call(["sudo", "/etc/init.d/networking", "restart"])