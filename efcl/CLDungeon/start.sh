#!/bin/bash
#set -x

txt() {
cat <<- EOM
.AM
.TH CLDungeon 6 "August 2021"
.SH NAME
CLDungeon \- discover commands related to file management.
.SH DESCRIPTION
Welcome to this small game/tutorial that will guide you through
the filesystem and some Linux basic commands.
.PP
Your journey starts with the following three commands:
.TP
.B ls
list the content of the current directory.
.TP
.B cat \fIfile
display the content of \fIfile\fP on the terminal.
.TP
.B cd \fIdir
change the current directory to \fIdir\fP.
.PP
Inside each directory you will find one or more files you may
read. Doing so you will learn new commands and could carry on
your journey to the end of this dungeon.
.SH START
Your journey starts by moving to the
.B level_1
directory using the 
.B cd
command.

Before that, you could use the 
.B ls
command to discover what's in this directory.
EOM
}

export PS1="$> "

if [ "$1" == "-p" ];
then
	txt | groff -Tutf8 -man | cat
else
	txt | groff -Tutf8 -man | less -X -E -F -d
fi

exec bash --norc
