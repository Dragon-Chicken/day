# This is a work in Progress

<div align="center">
  <img src="./.github/logo.png" width="50%">
  <br>
  <b>DAY - Dnf Assisted Yank. A fast multitool wrapper for the DNF package manager</b>
  <br>
  <sub>Welpyes, Dragon.chicken (2025)</sub>
</div>

---

> [!NOTE]
> This Tool will Likely be rewritten
> in Golang or C++ in the future 

## Table Of Contents
- [Features](#Features)
- [Manual](#Manual)
- [Installation](#Installation)

## Features

- Fast Copr search
- Copr integration to `install`
- Quality of life features
   * Aliased Commands 
   * `--force` flag for `remove`/`rm`

## Installation

Clone this repository:
```sh
git clone https://github.com/Dragon-Chicken/day
```
Install the Dependencies
```
python3
python3-requests
python3-beautifulsoup
pythob3-termcolor
dnf5
```
Then run `day.py`
<br>
For installation on `$PATH` you can symlink it to your bin directory
```sh
for local bin directory
ln -s day.py ~/.local/bin/day

for global bin directory
ln -s day.py /bin/day
```


## Manual

<details>
<summary>Man Page Dropdown</summary>
<pre><code>
DAY(1)                            Day Manual                            DAY(1)

NAME
       day - Dnf Assisted Yank, A dnf wrapper with
       quality of life fearures

SYNOPSIS
       day [--help] [--help-dnf] [command] [arguments...]

DESCRIPTION
       Day is a Python-based dnf wrapper for RPM-based Linux Distributions.
       It integrates Copr features namely the Search fucntion to the dnf
       Package Manager and installs copr projects found in
       https://copr.fedorainfracloud.org with ease

OPTIONS
       --help, -h
              Displays the Day specific help page

       --help-dnf
              Displays the Dnf help page

COMMANDS
       search <query>
              Search for packages matching the query in standard repositories. If no
              matches are found, prompts to search COPR repositories.
              Example:
                  day search bottom
                  # If no matches, prompts: "Would you like to search COPR repositories? (Y/n)"

       copr search <query>
              Search COPR repositories for projects matching the query. Displays
              project names, supported architectures, and truncated descriptions.
              Example:
                  day copr search bottom
                  # Output: Project names with highlighted matches, architectures, and descriptions

       install, i, in <package>...
              Install one or more packages. Supports COPR projects by specifying
              <owner/project> (e.g., atim/bottom), which automatically enables the
              COPR repository before installing the package. Uses -y for non-interactive
              installation.
              Example:
                  day install git atim/bottom
                  # Enables atim/bottom COPR repository and installs git and bottom

       remove, rm <package>... [-f|--force]
              Remove one or more installed packages. Checks for DNF database locks
              and requires sudo. The --force (-f) option uses rpm -e --nodeps to bypass
              dependency checks, but verifies package existence first.
              Example:
                  day remove nano
                  # Runs dnf5 remove -y nano
                  day remove nano -f
                  # Runs rpm -e --nodeps nano after verifying nano is installed

       upgrade, ug, upg [<package>...]
              Upgrade specified packages or all packages if none are specified. Passes
              additional arguments to dnf5 upgrade.
              Example:
                  day upgrade
                  # Runs dnf5 upgrade
                  day upg vim
                  # Runs dnf5 upgrade vim

       list, ls [<options>...]
              List packages (e.g., installed, available, extras). Passes additional
              arguments to dnf5 list.
              Example:
                  day list installed
                  # Runs dnf5 list installed

       download, dw <package>... [--srpm] [--debuginfo]
              Download packages to the current or specified directory without installing.
              Supports --srpm for source RPMs and --debuginfo for debuginfo RPMs.
              Example:
                  day download vim --srpm
                  # Runs dnf5 download vim --srpm

       cl
              Clean all cached data, equivalent to dnf5 clean all.
              Example:
                  day cl
                  # Runs dnf5 clean all

       <other dnf5 commands> [<subcommand>] [<arguments>...]
              Any unrecognized command is passed directly to dnf5, supporting all dnf5
              commands and subcommands (e.g., advisory summary, history list, copr add).
              Example:
                  day history list
                  # Runs dnf5 history list
                  day copr add myproject/mypackage
                  # Runs dnf5 copr add myproject/mypackage
                  day advisory summary
                  # Runs dnf5 advisory summary

EXAMPLES
       Search for a package and fall back to COPR:
           day search bottom

       Install a package from a COPR repository:
           day install atim/bottom

       Remove a package forcefully:
           day rm nano -f

       List transaction history:
           day history list

       Add a COPR repository:
           day copr add myproject/mypackage

       Upgrade all packages:
           day upg

SEE ALSO
       dnf5(8), dnf5-plugins(8), dnf.conf(5)

       Online documentation:
           https://dnf5.readthedocs.io
           https://dnf-plugins-core.readthedocs.io
</code></pre>
</details>

---

## Thanks & Inspiration

- [Paru](https://github.com/Morganamilo/paru) – Helper Idea 
- [sowm](https://github.com/dylanaraps/sowm) – Readme Inspiration

--- 
<p align="center">
  <em>Contributions are very much welcome!</em>
</p>

