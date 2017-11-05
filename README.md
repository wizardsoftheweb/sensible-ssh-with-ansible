[![Build Status](https://travis-ci.org/wizardsoftheweb/sensible-ssh-with-ansible.svg?branch=master)](https://travis-ci.org/wizardsoftheweb/sensible-ssh-with-ansible)

This is the code behind a longer blog post. Cool things currently in the repo include

* A broken [networking script](powershell) because I apparently can't follow instructions
* A [multimachine `Vagrantfile`](Vagrantfile) to simulate a network with `ssh` boxes
* Ansible roles to [build simple users](provisioning/roles/build_user) and [attach them](provisioning/roles/add_user) to generic boxes
* Very simple [playbook tests](.travis.yml)

Cool things that will eventually be in this repo (or a continuation) include

* Code write-ups (that's why I'm pushing now; I keep getting distracted by interesting things instead of documenting)
* Better Ansible tests
* A decent `ssh` shakedown (I am not a pentester; Google and past mistakes taught me everything I know)
* `ssh` config and all that jazz
* What I (plan to) use to keep my keys ship-shape

## Why Vagrant over Docker?

The whole point of containers is slim isolation. Unless your app depends on `ssh`, there's absolutely no reason to install it in the container. On top of that, Vagrant is a bit easier to demo. This is intended to be useful on the boxes that run your containers and might not work in your containers.
