#!/bin/bash

installflag=0
removeflag=0
searchflag=0
upgradeflag=0

coprflag=0



#########
# FLAGS #
#########
if [ -z "$2" ] || [ -z "$1" ]; then
  echo "missing argument(s)"
  return
fi

for (( i=0; i<${#1}; i++ )); do
  char="${1:i:1}"
  if [ $char = "i" ]; then
    installflag=1
  elif [ $char = "r" ]; then
    removeflag=1
  elif [ $char = "u" ]; then
    upgradeflag=1
  elif [ $char = "q" ]; then
    searchflag=1
  elif [ $char = "c" ]; then
    coprflag=1
  else
    echo "invalid argument(s)"
    return
  fi
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
  echo "https://copr.fedorainfracloud.org/coprs/fulltext/?fulltext=$coprsearchstring"

  echo "dnf search: "
  dnf search "$searchstring"
fi

################
# COPR INSTALL #
# I hate copr. #
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
    if [ $i -ne 1 ]; then
      #echo "package: $input"

      grepout=$(dnf -q search $input | grep -i $input)

      if [ -z "$grepout" ]; then
        echo "Can't find package: $input"
        return
      fi
      
      grepoutlines=$(dnf -q search $input | grep -c -i $input)
      #echo $grepoutlines
      
      option=0
      validinput=0

      if [ $grepoutlines -gt 1 ]; then
        while [ $validinput -ne 1 ]; do
          echo "select an option:"
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

    fi
    i+=1
  done
  
  installstring=${installstring% }

  echo "|$installstring|"

  sudo dnf install $installstring
  
fi
##########
# REMOVE #
##########
if [ $removeflag -eq 1 ]; then
  #dnf list --installed | grep -i $2

  removestring=""
  
  echo "searching for package(s)"

  i=1
  for input in "$@"; do
    if [ $i -ne 1 ]; then
      #echo "package: $input"

      grepout=$(dnf -q list --installed "*$input*" | grep -i $input)

      if [ -z "$grepout" ]; then
        echo "Can't find package: $input"
        return
      fi
      
      grepoutlines=$(dnf -q list --installed "*$input*" | grep -c -i $input)
      #echo $grepoutlines

      option=0
      validinput=0

      if [ $grepoutlines -gt 1 ]; then
        while [ $validinput -ne 1 ]; do
          echo "select an option:"
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

    fi
    i+=1
  done
  
  removestring=${removestring% }

  echo "|$removestring|"

  sudo dnf remove $removestring
fi
