sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update
sudo apt install python3.8 -y
sudo apt install python3.8-distutils -y

sudo apt install python3-virtualenv -y
virtualenv --python="/usr/bin/python3.8" sandbox
source sandbox/bin/activate

mkdir -p aws-layer/python/lib/python3.8/site-packages
pip3 install --no-cache-dir -r requirements.txt --target aws-layer/python/lib/python3.8/site-packages
cd aws-layer
zip -r9 lambda-layer.zip .

deactivate