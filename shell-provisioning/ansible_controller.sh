#!/bin/bash

useradd baseuser -G wheel
mkdir -p /home/baseuser/.ssh
chown -R baseuser:baseuser /home/baseuser
chmod 0755 /home/baseuser
chmod 0700 /home/baseuser/.ssh
cp /tmp/all-ssh/baseuser_generic* /home/baseuser/.ssh
chmod 0600 /home/baseuser/.ssh/*
chmod 0644 /home/baseuser/.ssh/*.pub
