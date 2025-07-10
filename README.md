# day

day is a wrapper for dnf, copr and flatpak

# man page

    NAME
        day - [temp name]
    
    SYNOPSIS
        day ARGS TERMS

        day ARGS TERMS ARGS TERMS
    
    DESCRIPTION
        day is a wrapper for dnf, copr and flatpak

        You can use any number of args and terms

    ARGS
        -h(elp)
            print the help text
        
        -i/I(nstall)
            i:
                Searches for package(s) then installs them
            I:
                Immediately tries to install package(s)
        
        -r(emove)
            Remove package(s)
        
        -c(opr)
            Tells day to use copr instead of dnf
        
        -f(atpak)
            Tells day to use flatpak instead of dnf
        
        -q(uery)
            Search for a package
        
        -u(pgrade)
            Upgrade the whole system
    
    TERMS
        you can think of them as
        dnf install __terms__
    
    EXAMPLES
        Example of installing bspwm, sxhkd and polybar

        day -i