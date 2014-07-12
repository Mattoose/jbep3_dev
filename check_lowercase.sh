#/bin/bash

function check_lower_case
{
	for i in `svn list --recursive`
	do
		orig=$i
		new=`echo $i | tr [A-Z] [a-z]`

		if [ "$orig" != "$new" ]
			then
				echo "svn rename $orig $new"
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
cd ../

echo "Check materials folder"
cd materials
check_lower_case
cd ../

echo "Check models folder"
cd models
check_lower_case
cd ../
