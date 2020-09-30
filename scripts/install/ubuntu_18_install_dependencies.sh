#!/bin/bash

set -e # Fail on error

echo "Installing packages via apt-get"
apt-get update
apt-get install -y git-core python3-dev python3-pip gfortran libopenblas-dev liblapack-dev zlib1g-dev bedtools libbz2-dev liblzma-dev libssl-dev libcurl4-openssl-dev curl
apt-get install -y libblas-dev libatlas-base-dev libpng-dev libjpeg-dev libfreetype6-dev libpq-dev libxft-dev zlib1g-dev libxml2-dev libxslt1-dev rustc
apt-get install -y nginx redis-server rabbitmq-server postgresql pgadmin3 postgresql-contrib libpq-dev
# actually only needed for development
apt-get install -y sassc

# Stuff required to install on shariant server, might just be moving dependencies
apt-get install -y pkg-config

echo "Install python libraries"
# For some reason straight out install of requirements.txt has issues, do some first
python3 -m pip install --upgrade pip
python3 -m pip install django==2.2.10
python3 -m pip install django-registration-redux>=2.1
python3 -m pip install numpy HTSeq Cython 
#python3 -m pip install -r requirements-dev.txt
python3 -m pip install -r requirements.txt
