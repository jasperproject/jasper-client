sudo sysctl net.ipv4.ip_forward=1

sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination 1.2.3.4:80
sudo iptables -t nat -A POSTROUTING -j MASQUERADE
sudo /etc/init.d/networking restart

#sudo iptables -A POSTROUTING -t nat -o wlan0 -j MASQUERADE

#sudo iptables -t mangle -N internet

#sudo iptables -t mangle -A PREROUTING -i wlan0 -p tcp -m tcp --dport 80 -j internet

#sudo iptables -t mangle -A internet -j MARK --set-mark 99

#sudo iptables -t nat -A PREROUTING -i wlan0 -p tcp -m mark --mark 99 -m tcp --dport 80 -j DNAT --to-destination 192.168.3.1

#sudo /etc/init.d/networking restart
