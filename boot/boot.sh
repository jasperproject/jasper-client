cd /home/pi/jasper/boot/
LD_LIBRARY_PATH="/usr/local/lib"
export LD_LIBRARY_PATH
PATH=$PATH:/usr/local/lib/:/usr/local/bin
export PATH
python boot.py &