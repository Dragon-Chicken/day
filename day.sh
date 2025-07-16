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
fi

if [ -z "$2" ]; then
  daymissing
  return
fi

#########
# FLAGS #
#########
for (( i=0; i<${#1}; i++ )); do
  char="${1:i:1}"
  
  case $char in
    "i" | "I")
      installflag=1

      if [ $char = "I" ]; then
        nosearch=1
      fi
    ;;

    "r")
      removeflag=1
    ;;

    "u")
      upgradeflag=1
    ;;

    "q")
      searchflag=1
    ;;

#    "c")
#      coprflag=1
#    ;;

    *)
      echo "invalid argument(s)"
      return
    ;;
  esac
done

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
        echo "Can't find package: $input"
        return
      fi
      
      grepoutlines=$(dnf -q search $input | grep -c -i $input)
      #echo $grepoutlines # debug
      
      option=0
      validinput=0

      if [ $grepoutlines -gt 1 ]; then
        while [ $validinput -ne 1 ]; do
          echo "Select an option:"
          echo "$grepout"
          read -p "> " option 

          if [ $option -lt 1 ] || [ $option -gt $grepoutlines ]; then
            echo "Please pick a valid number"
          else
            validinput=1
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

##########
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
        echo "Can't find package: $input"
        return
      fi
      
      grepoutlines=$(dnf -q list --installed "*$input*" | grep -c -i "$input")
      #echo $grepoutlines

      option=0
      validinput=0

      if [ $grepoutlines -gt 1 ]; then
        while [ $validinput -ne 1 ]; do
          echo "Select an option:"
          echo "$grepout"
          read -p "> " option 

          if [ $option -lt 1 ] || [ $option -gt $grepoutlines ]; then
            echo "Please pick a valid number"
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
        echo "Package $packagetoremove was installed with copr."
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
