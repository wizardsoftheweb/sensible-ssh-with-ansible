This is the first in a series of several posts on how to manage `ssh` via Ansible. It was inspired by [a warning from Venafi](https://www.venafi.com/blog/ssh-keys-lowest-cost-highest-risk-security-tool) that gained traction in the blogosphere (read: my Google feed for two weeks). I don't know many people that observe good `ssh` security, so my goal is to make it more accessible and (somewhat) streamlined.

As the first post in the series, this will provide a roadmap for the series and a brief overview of the tools involved. If you're familiar with `ssh`, have a pretty good idea what Ansible is, and have either seen Vagrant before or have your own virtualization solution to use, you can probably skip this post.

<p class="nav-p"><a id="post-nav"></a></p>
<!-- MarkdownTOC -->

- [The Series so Far](#theseriessofar)
- [Code](#code)
- [Executive Summary](#executivesummary)
- [Note](#note)
- [Software](#software)
    - [Main](#main)
    - [Windows](#windows)
    - [My Environment](#myenvironment)
- [Tool Overview](#tooloverview)
    - [`ssh`](#ssh)
    - [Ansible](#ansible)
    - [Optional: Vagrant](#optionalvagrant)

<!-- /MarkdownTOC -->

<!--  wotw-series-toc -->
## The Series so Far

1. [Overview](//blog.wizardsoftheweb.pro/sensible-ssh-with-ansible-overview)
2. [Creating the Status Quo](//blog.wizardsoftheweb.pro/sensible-ssh-with-ansible-vagrant-setup)
3. [Populating the Status Quo](//blog.wizardsoftheweb.pro/sensible-ssh-with-ansible-ansible-setup)
<!-- /wotw-series-toc -->

<!--  wotw-repo-link -->
## Code

You can view the code related to this post [under the `post-01-overview` tag](//github.com/wizardsoftheweb/sensible-ssh-with-ansible/tree/post-01-overview).
<!-- /wotw-repo-link -->

## Executive Summary

If you do any sort of remote CLI interaction, you probably use `ssh` already. If you don't remote anywhere, or you don't use `ssh` when you do, you probably don't need to read this (but it can't hurt). Like most best practices, maintaining proper `ssh` can become a chore as your world expands across personal boxes, work machines, online VCS, freelance gigs, and so on. Easy solutions, like using the same key everywhere for years at a time, are nice both as a consumer and as an attacker because they've been so widely documented for years. Better solutions require time and effort to update configuration everywhere, retire old keys, and maintain provenance on new keys. The best solutions automate the entire process and notify you afterward. Using Ansible, my goal is to create such a solution that can be run indefinitely from a trusted control machine. Along the way, I also plan to include and test stronger configurations, randomized options, centralized validation, and probably a good selection of rabbit holes as I figure out how to code everything.

I'm going to assume some familiarity with working in and with `bash`, but I also try to provide a good introduction to each component that plays an important role (Ansible pun intended). If something seems hand-wavy, there's a really good chance I'll explain it either further down the post or in a follow-up (if not, let me know). You'll need a control host capable of running `bash` and nodes capable of handling `ssh` connections. A healthy disdain for Windows isn't necessary, but it makes trying to get any of this to work in Windows a bit more palatable. I've built an example in Vagrant, but you don't need it to use any of the code presented in the series.

## Note

I included all of the code (as opposed to lazy loading) for the AMP CDN, which means [the remote](//github.com/wizardsoftheweb/sensible-ssh-with-ansible/tree/post-01-overview) might be ahead a bit. I'm still figuring out the balance between code blocks that are enjoyable to read and code blocks that don't look terrible. If something is completely unbearable via AMP, sorry I missed it, shoot me an email and I'll find a fix.

For the most part, you should assume a shell environment is a `bash` environment. I actually use `zsh`, so there might be some `zsh`isms mixed in. I've tried to make this run from start to finish via `/bin/bash`, so let me know if I missed something. The assumed-to-be-`bash` shell will look like this:

<!-- wotw-build-bash
['bash', '--version']
-->
```
$ bash --version
GNU bash, version 4.3.46(1)-release (x86_64-pc-linux-gnu)
Copyright (C) 2013 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>

This is free software; you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
```

There's at least one PowerShell snippet. I tried to differentiate the two shells, so PowerShell looks like this:

```powershell
PS$ $PSVersionTable.PSVersion

Major  Minor  Build  Revision
-----  -----  -----  --------
5      1      16299  19
```
You'll most likely need to run PowerShell as an administrator; I can't easily break out elevated commands because, unsurprisingly, Microsoft wanted to do things their own way.

## Software

### Main

* [Vagrant](https://www.vagrantup.com/) for the demo, but not necessary in the final setup
* [OpenSSH](https://www.openssh.com/) (which is probably already on your system)
* [Ansible](https://www.ansible.com/) for easy everything

    Ansible depends on:
    * [Python 2](https://www.python.org/downloads/) (`2.6` or `2.7`)
    * [`pip` (via curl)](https://github.com/pypa/get-pip)

### Windows

Unsurprisingly, trying to do normal things on Windows requires way more work.

* [Windows Containers](https://docs.microsoft.com/en-us/virtualization/windowscontainers/about/) will require some setup.

    **WARNING**: Microsoft wrote their own containerization API (it relies on a different kernel, after all). Unsurprisingly, most of the things you think should work don't. Chances are you'll have to use defaults everywhere, which is so ridiculously insecure that you probably shouldn't use Windows Containers.
* Hyper-V ([10](https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/quick-start/enable-hyper-v) | [Server](https://docs.microsoft.com/en-us/windows-server/virtualization/hyper-v/get-started/install-the-hyper-v-role-on-windows-server)) might be necessary as a provider for Vagrant. It's not pleasant, but you should probably also consider [setting up boot configs](http://www.hanselman.com/blog/SwitchEasilyBetweenVirtualBoxAndHyperVWithABCDEditBootEntryInWindows81.aspx) (unsurprisingly [still relevant](https://marcofranssen.nl/switch-between-hyper-v-and-virtualbox-on-windows/) for newer Windows).
* [Ansible](http://docs.ansible.com/ansible/latest/intro_windows.html) flat out doesn't support Windows. You can use [Ansible through WSL](https://www.jeffgeerling.com/blog/2017/using-ansible-through-windows-10s-subsystem-linux), [Ansible with babun](https://github.com/tiangolo/ansible-babun-bootstrap), or anything else that can run `python` within a `bash` environment on Windows. Unsurprisingly, local support (i.e. true [control](http://docs.ansible.com/ansible/latest/intro_installation.html#control-machine-requirements)) is sketchy at best. Then again, the generally accepted method for managing `ssh` keys on Windows is PuTTy, which is so far from automatable it's not even funny.

    **WARNING:** If you're trying to manage Windows from WSL or vice versa, [you're gonna have a bad time](https://stackoverflow.com/a/41526143). If you do use Ansible to configure WSL, do not expect things to work as intended outside of WSL (e.g. in PowerShell). Unsurprisingly, they will probably work until you least expect it and then you'll spend a day on StackOverflow discovering WSL makes no sense.

### My Environment

I'm running Window's 10 1709, ~~build 16299.19~~ build 17025.1000 (I'll try to keep this updated as I get new builds). Because of the [Windows limitations](#windows), I'll only be using the created virtual environments. That means Ansible is probably [the latest version](https://www.vagrantup.com/docs/provisioning/ansible_local.html#install) (`2.4.1` as of initial writing) and OpenSSH is tied to the VM's repositories ([pertinent packages](https://rpms.remirepo.net/rpmphp/zoom.php?rpm=openssh) are under "EL-7"). That means the my only real versions come from PowerShell:
```powershell
# I'm too lazy to add the *-WindowsFeature cmdlets
PS$ dism.exe /online /Get-Features | Select-String -Pattern " Containers" -Context 0,1

> Feature Name : Containers
  State : Enabled

PS$ dism.exe /online /Get-Features | Select-String "hyper-v" -Context 0,1

> Feature Name : Microsoft-Hyper-V-All
  State : Enabled
> Feature Name : Microsoft-Hyper-V
  State : Enabled
> Feature Name : Microsoft-Hyper-V-Tools-All
  State : Enabled
> Feature Name : Microsoft-Hyper-V-Management-PowerShell
  State : Enabled
> Feature Name : Microsoft-Hyper-V-Management-Clients
  State : Enabled
> Feature Name : Microsoft-Hyper-V-Hypervisor
  State : Enabled
> Feature Name : Microsoft-Hyper-V-Services
  State : Enabled

PS$ (Get-Module hyper-v).Version

Major  Minor  Build  Revision
-----  -----  -----  --------
2      0      0      0

PS$ vagrant -v
Vagrant 2.0.0
```
## Tool Overview

If you're comfortable with the tools listed below, you can skip their respective sections. A quick skim wouldn't hurt, though; I might accidentally use stuff from them later.

### `ssh`

`ssh` is [a protocol](https://www.ssh.com/ssh/protocol/) for creating authentic connections between two parties. A simple breakdown is as follows (although [a verbose breakdown](https://www.mnin.org/write/2006_sshcrypto.html) is pretty neat):

1. A client sends a auth request to a server.
2. The server responds with its public key, giving the client a chance to validate the server.
3. If the transaction moves forward, the server and client negotiate authentication using a variety of methods, some more secure than others.
4. The client, now authenticated, gains access to the server's operating system.

`ssh` assuages a few concerns central to exposed authentication.

* Client and server both validate, so there's a good chance the intended parties (or someone with their keys) are actually communicating.
* Communication happens in [an encrypted tunnel](https://en.wikipedia.org/wiki/Tunneling_protocol#Secure_Shell_tunneling), similar to [SSL/TLS](https://en.wikipedia.org/wiki/Transport_Layer_Security).
* Authentication can be done via [public key cryptography](https://en.wikipedia.org/wiki/Public-key_cryptography) so as to never expose full credentials from either party
* It uses [a well-defined standard](https://www.ssh.com/ssh/protocol/#sec-The-core-protocol) that can be extended as necessary, i.e. it's not chained to bad crypto.

[OpenSSH](https://www.openssh.com/), the FOSS implementation common to most Linux distros, is usually split into two packages: a client package, containing the tools necessary to connect to a remote and manage keys (e.g. `ssh` and `ssh-add`, respectively), and a server package, containing the tools necessary to run an `ssh` host (e.g. `sshd`). It might seem like an annoyance initially, but it's actually a solid security feature by itself. Machines that do not need to host external `ssh` connections don't need the extra app, and, more importantly, they shouldn't have to secure the server defaults. Boxes that host an `ssh` server usually have both, but they're also tailored to secure the configuration (or at least should be).

The client package, usually a variant of `openssh-client*`, contains a few important commands. `ssh-keygen` creates new keys (it can do [so much more](https://linux.die.net/man/1/ssh-keygen)).
```bash
$ ssh-keygen
Generating public/private rsa key pair.
Enter file in which to save the key (/home/user/.ssh/id_rsa):
Created directory '/home/user/.ssh'.
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /home/user/.ssh/id_rsa.
Your public key has been saved in /home/user/.ssh/id_rsa.pub.
The key fingerprint is:
SHA256:kmhSVNUETQDuZ+jD63WsOv3ArvyftaSMby1mAlBl6go user@host
The key's randomart image is:
+---[RSA 2048]----+
|    ..o+*Bo      |
|   . ..o  o      |
|    ..o          |
|   ..+ o         |
|  E o.* S        |
|   + +.= .       |
|    . +o+ o.o    |
|     ..=o*==..   |
|     .*==OB..    |
+----[SHA256]-----+
```
`ssh-copy-id` takes local public keys and adds them to the `authorized_keys` file on the remote. After generating a key, you should send it where you want it.
```bash
$ ssh-copy-id remoteuser@remote
```
However, `ssh-copy-id` relies on potentially insecure handshakes to verify access, so if you've got access to both machines, this accomplishes the same thing:
```bash
# local
$ cat ~/.ssh/id_rsa.pub > ~/remoteuser_authorized_keys
# move the file from local to remote
# remote
$ mkdir -p ~/.ssh
$ chmod u=rwx,go= ~/.ssh
$ mv ~/remoteuser_authorized_keys ~/.ssh/authorized_keys
$ chown remoteuser:remoteuser ~/.ssh/authorized_keys
$ chmod u=rw,go=r ~/.ssh/authorized_keys
```
The extra permissions (`chmod`) setup is managed automatically by `ssh-keygen`, so you typically don't have to worry about it unless you're moving files around and don't respect permissions (e.g. Windows touched the file at some point). If you get it wrong, there are good error messages, or just use [this StackExchange answer](https://superuser.com/a/215506).

Once keys are in place, `ssh` establishes the connection. By default, it assumes the server is listening on port `22` and the `id_rsa` identity should be used for everything ([the man page for `ssh`](https://linux.die.net/man/1/ssh) explains how to not use defaults):
```bash
$ ssh user@host '/bin/true' || echo 'whoops'
Enter passphrase for key '/home/user/.ssh/id_rsa':
# shouldn't see whoops
```

Once multiple identities get involved (e.g. `user1@hosta` and `user2@hostb`), things get messy. Luckily OpenSSH includes tools to handle that. `ssh-agent` ([man here](https://linux.die.net/man/1/ssh-agent)) can hold identities and send them automatically to `ssh`.
```bash
# Ensure it's running
$ pgrep -f ssh-agent -u $(whoami) || ssh-agent $SHELL
# Add key
$ ssh-add
Enter passphrase for key '/home/user/.ssh/id_rsa':
# Check identities
$ ssh-add -l
2048 SHA256:kmhSVNUETQDuZ+jD63WsOv3ArvyftaSMby1mAlBl6go /home/user/.ssh/id_rsa (RSA)
```
The agent attempts to find a match by brute force, which, as you might guess, can lead to issues. A solid unwritten rule is to keep [a max of five identities](https://serverfault.com/a/580860) loaded at any time. This corresponds to [a default `MaxAuthTries` of `6`](https://www.freebsd.org/cgi/man.cgi?sshd_config).

### Ansible

[Ansible](https://www.ansible.com/) scripts your world. As a coder, that's a very powerful statement. [There are other tools](https://www.google.com/search?q=chef+vs+puppet+vs+ansible+vs+salt), but I prefer Ansible. Its syntax is simple, its scope is massive, and it runs just about anywhere (that you'd want to develop, so not Windows).

Ansible is capable of running a plethora of ad-hoc commands [via `ansible`](https://linux.die.net/man/1/ansible), but its power comes from its ability to stitch those together in easily readable YML files. A selling feature of Ansible is that its modules are [idempotent](https://en.wikipedia.org/wiki/Idempotence#Computer_science_meaning) (probably the first time this year I was able to put my math degree to good use, i.e. "I accrued so much debt just to identify obscure jargon"). In theory, a good collection of commands, [called a `playbook`](http://docs.ansible.com/ansible/latest/playbooks_intro.html), should be idempotent as well. In practice, this takes some careful polishing to achieve.

Ansible runs `playbook`s against an [`inventory` of hosts](http://docs.ansible.com/ansible/latest/intro_inventory.html). Each playbook is composed of a list whose items include host selection, variable declaration, and `tasks`. Each `task` is compromised of, essentially, a single command ([`block` support](http://docs.ansible.com/ansible/latest/playbooks_blocks.html) exists with a few caveats). To encourage DRY code, Ansible allows [grouping tasks in `roles`](https://docs.ansible.com/ansible/2.4/playbooks_reuse_roles.html). If that sounds like a lot of directories, it is. Ansible handles that for you with [its configuration file, `ansible.cfg`](http://docs.ansible.com/ansible/latest/intro_configuration.html) (among other things like default arguments).

I'm still new enough to Ansible that I've been afraid to visit [Ansible Galaxy](https://galaxy.ansible.com/), which introduces itself as

> your hub for finding, reusing and sharing the best Ansible content

i.e. it's an Ansible package manager which is awesome because someone smarter probably thought of my idea first. I will eventually update with Galaxy roles; for now this is all local because I need to grok the whole process.

Ansible publishes [best practices](http://docs.ansible.com/ansible/latest/playbooks_best_practices.html), which I've tried to follow throughout. Again, I'm new to Ansible, so I'm still working out how those best practices work in practice.

I'm going to touch on Ansible components as I bring them in, so I'll leave finding and running a basic intro playbook and inventory up to you.

### Optional: Vagrant

If the idea of scripting your environment applies to you, you'll love [Vagrant](https://www.vagrantup.com/). It is a `ruby`-based VM manager with access to all the major hosts. It prides itself on [being easy to use](https://www.vagrantup.com/intro/getting-started/index.html); after installation, you can run
```bash
$ vagrant init hashicorp/precise64
$ vagrant up
$ vagrant ssh
```
and you're inside a virtual Ubuntu box.

Because Vagrant is scriptable and can emulate anything with an image (basically anything you can find an `iso` of), it's a cheap and easy way to test host configurations. [Unlike Docker](https://docs.docker.com/engine/admin/volumes/), its default storage is persistent, as it creates full VMs for each box. As a primary goal of a containerized app is to be as slim and isolated as possible, installing the tooling for Ansible inside a container doesn't make much sense. I feel like Vagrant lends itself more to that role (Ansible pun intended) here, but if you really wanted to you could duplicate this via `Dockerfile`s. If your world is Docker containers inside Docker containers, you might want to do that.

To run the provided `Vagrantfile`, clone the repo and run `vagrant` inside the directory.

```bash
$ git clone https://github.com/wizardsoftheweb/sensible-ssh-with-ansible.git
$ cd sensible-ssh-with-ansible
$ git checkout post-01-overview
$ vagrant up
```

**WARNING:** If you're on Windows running vanilla Containers and Hyper-V, you'll probably need to add `--provider=hyperv` to all `up` commands. If you're not running vanilla, you're probably already aware that trying to run another provider while Hyper-V is running (which is always unless you changed the boot config) won't be pretty. I crashed my system three times one weekend, initially trying to figure out what was wrong and later because I forgot to force Hyper-V.
