sudo apt-get update
sudo apt-get -y install python-dev git
#wget https://pypi.python.org/packages/source/T/Twisted/Twisted-12.3.0.tar.bz2#md5=6e289825f3bf5591cfd670874cc0862d
wget https://pypi.python.org/packages/source/T/Twisted/Twisted-13.1.0.tar.bz2#md5=5609c91ed465f5a7da48d30a0e7b6960
bunzip2 Twisted-13.1.0.tar.bz2
tar -xf Twisted-13.1.0.tar
cd Twisted-13.1.0
sudo python setup.py install