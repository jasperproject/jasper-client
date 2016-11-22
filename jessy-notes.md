# Updated URLs

OpenFST:
https://github.com/AdolfVonKleist/Phonetisaurus/tree/openfst-1.5.3

MITLM:
https://github.com/mitlm/mitlm

sudo wget https://m2m-aligner.googlecode.com/files/m2m-aligner-1.2.tar.gz
sudo wget https://www.dropbox.com/s/154q9yt3xenj2gr/phonetisaurus-0.8a.tgz
sudo wget https://phonetisaurus.googlecode.com/files/is2013-conversion.tgz


Installing stuff:
-----------------------------------------
1. sudo su -c "echo 'deb http://cognomen.co.uk/apt/debian jessie main' > /etc/apt/sources.list.d/cognomen.list"

2. gpg --keyserver keyserver.ubuntu.com --recv  FC88E181D61C9391C4A49682CF36B219807AA92B && gpg --export --armor keymaster@cognomen.co.uk | sudo apt-key add -

3. sudo apt-get update

4. sudo apt-get install phonetisaurus m2m-aligner mitlm libfst-tools libfst1-plugins-base libfst-dev

5. sudo apt-get install pocketsphinx-hmm-en-hub4wsj



Configure: .jasper/profile.yml:

stt_passive_engine: sphinx
pocketsphinx:
  hmm_dir: /usr/share/pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k

--------------------------
