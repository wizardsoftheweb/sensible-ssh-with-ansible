This directory contains the working files for the series of posts as well as my first Python script ever.

## Overview

I was trying to accomplish a few things with [`compile.py`](compile.py):

* learn some Python
* automatically update "The Series so Far"
* automatically build bash output for specific commands

As I was building those features, I added a few other things:

* include local files from the proper revision with a default to whatever currently exists
* include some common post components

I'd like to eventually update the posts themselves on my blog, but I use Ghost and there isn't (currently) a way to programmatically update posts. Selenium is an option but that's way more work that copypasta.

If you have suggestions or improvements, I'd love to hear them. I have no idea what I don't know about Python yet.

## Usage

Honestly, don't. I reinvented the wheel as a learning experience. I will eventually replace this with a properly vetted build system (e.g. [Jinja](http://jinja.pocoo.org/), the template engine used by Ansible [I didn't even think of using Jinja until just now, warning you not to use this; that would have been really simple]).

The script takes a file like this:
```markdown
<!--  wotw-series-toc -->
<!-- /wotw-series-toc -->

<!--  wotw-repo-link -->
<!-- /wotw-repo-link -->

<!-- wotw-include-file filename:provisioning/main.yml -->

<!-- wotw-build-bash
['tree', 'provisioning/inventory', '--dirsfirst']
-->
```
and updates it to look like this:
````markdown
<!--  wotw-series-toc -->
## The Series so Far

1. [Overview](//blog.wizardsoftheweb.pro/sensible-ssh-with-ansible-overview)
2. [Creating the Status Quo](//blog.wizardsoftheweb.pro/sensible-ssh-with-ansible-vagrant-setup)
3. [Populating the Status Quo](//blog.wizardsoftheweb.pro/sensible-ssh-with-ansible-ansible-setup)
<!-- /wotw-series-toc -->

<!--  wotw-repo-link -->
## Code

You can view the code related to this post [under the `sample` tag](//github.com/wizardsoftheweb/sensible-ssh-with-ansible/tree/sample).
<!-- /wotw-repo-link -->

<!-- wotw-include-file filename:provisioning/main.yml -->
[`provisioning/main.yml`](//github.com/wizardsoftheweb/sensible-ssh-with-ansible/tree/sample/provisioning/main.yml):
```yml
---
- hosts: all:!setup

  roles:
    # `ansible_os_family` defined [here](https://github.com/ansible/ansible/blob/devel/lib/ansible/module_utils/facts/system/distribution.py#L406)
    - { role: common_yum, when: ansible_os_family == "RedHat" }
```

<!-- wotw-build-bash
['tree', 'provisioning/inventory', '--dirsfirst']
-->
```
$ tree provisioning/inventory --dirsfirst
provisioning/inventory
├── group_vars
│   ├── all.yml
│   ├── controller.yml
│   └── setup.yml
├── controller.yml
├── foundation.yml
└── setup.yml

1 directory, 6 files
```
````


## TODOs

* DRY regex usage
* Polish file with best practices
* learn best practices
