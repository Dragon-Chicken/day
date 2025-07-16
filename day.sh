#!/bin/bash

installflag=0
removeflag=0
searchflag=0
upgradeflag=0

coprflag=0

nosearch=0

#############
# HELP TEXT #
######################
# TO DO:             #
# sync the python    #
# and bash project's #
# help text and      #
# other things       #
######################
dayhelp() {
  echo \
"usage: day [options] [command] [arguments...]

Day - Dnf Assisted Yank, a dnf wrapper with quality of life features

positional arguments:
  command     Command to execute
  args        Additional arguments

options:
  -h, --help  Show this help message
  --help-dnf  Show DNF5 help

Commands:
search, copr search, install (i, in), remove (rm, -f/--force), upgrade (ug, upg), list (ls), download (dw), cl, advisory <subcommand>, copr <subcommand>, history <subcommand>, or any dnf5 command.
Use 'day --help-dnf' for DNF5 help."
  return
}

daymissing() {
  echo "missing argument(s)"
  echo "use 'day --help' for more info"
  return
}

##########
# CHECKS #
##########
if [ -z "$1" ]; then
  daymissing
  return
fi

if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
  dayhelp
  return
elif [ "$1" = "--help-dnf" ]; then
  dnf --help
  return
fi

if [ -z "$2" ]; then
  daymissing
  return
fi

############
# COMMANDS #
############

case $1 in
  "install" | "Install" | "i" | "I" | "in" | "In")
    installflag=1

    if [ ${1:0:1} = "I" ]; then
      nosearch=1
    fi
  ;;

  "remove" | "rm")
    removeflag=1
  ;;

  "search")
    searchflag=1
  ;;
  
  "upgrade" | "ug" | "upg")
    upgradeflag=1
  ;;

  # list ls

  # download, dw

  # cl

  *)
    echo "passing through dnf"
    return
esac


# need to combine shit into one string first
# rather than doing it in each if


##########
# SEARCH #
##########
if [ $searchflag -eq 1 ]; then
  searchstring=""

  i=1
  for input in "$@"; do
    if [ $i -ne 1 ]; then
      searchstring+="$input "
    fi
    i+=1
  done
  
  searchstring=${searchstring% }
  coprsearchstring=$(echo "$searchstring" | sed "s/\//%2F/g" | sed "s/\ /+/g")

  echo "copr search: "
  echo "https://copr.fedorainfracloud.org/coprs/fulltext/?projectname=$coprsearchstring"

  echo "dnf search: "
  dnf search "$searchstring"
fi

################
# COPR INSTALL #
################
coprinstall() {
  sudo dnf copr enable $1
  sudo dnf install ${1#*/}
}

###########
# INSTALL #
###########
if [ $installflag -eq 1 ]; then

  if [ $coprflag -eq 1 ]; then
    coprinstall $2
  fi

  installstring=""
  
  echo "searching for package(s)"

  i=1
  for input in "$@"; do
    if [ $i -ne 1 ] && [ $nosearch -eq 0 ]; then

      grepout=$(dnf -q search $input | grep -i $input)

      if [ -z "$grepout" ]; then
        echo "can't find package: $input"
        return
      fi
      
      grepoutlines=$(dnf -q search $input | grep -c -i $input)
      #echo $grepoutlines # debug
      
      option=0
      validinput=0

      if [ $grepoutlines -gt 1 ]; then
        while [ $validinput -ne 1 ]; do
          echo "select an option:"
          echo "$grepout" | cat -n
          read -p "> " option

          if ! [[ $option =~ "^[0-9]+$" ]]; then
            if [[ $option -lt 1 ]] || [[ $option -gt $grepoutlines ]]; then
              echo "please pick a valid number"
              echo "|$option| |$option -lt 1| |$option -gt $grepoutlines|"
            else
              validinput=1
            fi
          fi
        done
      fi

      readarray -t splitarray <<<"$grepout"

      packagetoinstall=${splitarray[$option -1]%%.*}
      packagetoinstall=${packagetoinstall:1}

      installstring+="$packagetoinstall "

    elif [ $i -ne 1 ]; then
      installstring+="$input "
    fi

    i+=1
  done
  
  installstring=${installstring% }

  #echo "|$installstring|" #debug

  sudo dnf install $installstring

  return
fi

########## !! TO ADD -F AND --FORCE SUPPORT !!
# REMOVE #
##########
if [ $removeflag -eq 1 ]; then

  removestring=""

  echo "searching for package(s)"

  i=1
  for input in "$@"; do
    if [ $i -ne 1 ]; then

      grepout=$(dnf -q list --installed "*$input*" | grep -i "$input")

      if [ -z "$grepout" ]; then
        echo "can't find package: $input"
        return
      fi
      
      grepoutlines=$(dnf -q list --installed "*$input*" | grep -c -i "$input")
      #echo $grepoutlines

      option=0
      validinput=0

      if [ $grepoutlines -gt 1 ]; then
        while [ $validinput -ne 1 ]; do
          echo "select an option:"
          echo "$grepout" | cat -n
          read -p "> " option

          if ! [[ $option =~ "^[0-9]+$" ]] || [ $option -lt 1 ] || [ $option -gt $grepoutlines ]; then
            echo "please pick a valid number"
          else
            validinput=1
          fi
        done
      fi

      readarray -t splitarray <<<"$grepout"

      packagetoremove=${splitarray[$option -1]%%.*}
      #packagetoremove=${packagetoremove:1}

      removestring+="$packagetoremove "

      # copr stuff...
      # testing...
      if ! [ -z "$(dnf copr list | grep "$packagetoremove")" ]; then
        echo "package $packagetoremove was installed with copr."
        read -p "Remove the copr repo? [Y/n]: " option

        coprrepotoremove=$(dnf copr list | grep "$packagetoremove")
        #echo "${coprrepotoremove#*/}"
        #sudo dnf copr remove "${coprrepotoremove#*/}"

      fi

    fi
    i+=1
  done
  
  removestring=${removestring% }

  #echo "|$removestring|" # debug

  sudo dnf remove $removestring

  return
fi
