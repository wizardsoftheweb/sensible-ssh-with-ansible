This directory contains the working files for the series of posts as well as my second Python script ever. It replaced [my first Python script ever](/wizardsoftheweb/sensible-ssh-with-ansible/tree/v0.6.0/post/compile.py) after I realized I should just be building these via [Jinja](http://jinja.pocoo.org/).

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

[`compile.py`](compile.py) does several things when run:

1. `rm -rf ./build`
2. `mkdir ./build`
3. For each `post-*.j2` in `./templates`:
    1. render the template to `./build/post-*.md`
    2. insert TOC via [`markdown_toclify`](https://github.com/rasbt/markdown-toclify)
    3. ~~strip dashes from `markdown_toclify` slugs~~
    3. parse basic `markdown_toclify` and insert links

I've [submitted a PR](https://github.com/rasbt/markdown-toclify/pull/14) to include the final action in `markdown_toclify`, but it might not get approved.

However, `markdown_toclify` parses all lines. In doing so, it strips left whitespace, which completely breaks codeblocks. The `nolink` option prevents `markdown_toclify` from doing so, but also requires additional work to build links.

## TODOs

* DRY regex usage
* Polish file with best practices
* learn best practices
