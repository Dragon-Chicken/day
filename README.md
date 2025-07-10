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
                Tries to install package(s) without searching
        
        -r/R(emove)
            r:
                Searchs for installed package(s) then remove them
            R:
                Tries to remove package(s) without searching
        
        -c(opr)
            Tells day to use copr instead of dnf
        
        -f(atpak)
            Tells day to use flatpak instead of dnf
        
        -q(uery)
            Search for a package
        
        -u(pgrade)
            Upgrade the whole system
    
    TERMS
        You can think of them as:
        dnf install terms
                    ^^^^^
    
    EXAMPLES
        Example of installing bspwm, sxhkd and polybar

        Search for packages then install:
        day -i bspwm sxhkd polybar

        or

        Don't search but still install:
        day -I bspwm sxhkd polybar
