#!/bin/bash
#
# Storing passphrases in the clear (either in a script or in your history) is
# never a good idea. Don't script generating your passphrase.

rm -f ./*_rsa*

common_opts="-P password -b 2048 -t rsa"

ssh-keygen $common_opts -f baseuser_generic_rsa -C baseuser@generic
