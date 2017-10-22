#!/bin/bash

ansible_user=$1

if which ansible; then
    echo 'Skipping installation'
else
    echo 'Installing dependencies'
    sudo yum install -y python-setuptools python-setuptools-devel
    sudo easy_install pip
    echo 'Installing ansible'
    sudo pip install ansible
fi

su - $ansible_user -c "cd /tmp/provisioning && ansible-playbook --connection=local -i inventories/localhost/hosts.yml main.yml"
