#/bin/bash

function check_lower_case
{
	for i in `find [A-Z]*`
	do
		orig=$i
		new=`echo $i | tr [A-Z] [a-z]`

		if [ "$orig" != "$new" ]
			then
				echo "Renaming $orig --> $new"
				svn rename $orig $new
		fi
	done

}

function check_subfolders
{
	for i in `ls -d */ -a`
	do
		cd $i
		check_lower_case
		cd ../
	done
}

echo "Checking content folders"
cd content
check_subfolders
