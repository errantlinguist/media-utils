#!/bin/sh

# A script for batch-setting permissions for directories and files, checking each file for a shebang in order to determine if it should have user-set "executable file" permissions applied to it or not.
# Author: Todd Shore <errantlinguist@gmail.com>
# Since: 2016-11-05

check_shebang()
{
	filepath="$1"
	# <http://stackoverflow.com/a/2439587/1391325>
	line=`head -n 1 "${filepath}"`
	# Modified from SE answer <http://stackoverflow.com/a/33013693/1391325>
	echo "${line}" | grep -q '^#!'
	return $?
}

is_executable_file()
{
	filepath="$1"
	check_shebang "${filepath}"
	# TODO: Check for binary executables?
	return $?
}

set_permissions()
{
	root_dir="$1"
	dir_permissions="$2"
	default_file_permissions="$3"
	exec_file_permissions="$4"

	echo "Setting directory permissions for \"${root_dir}\" and its children to ${dir_permissions}."
	chmod "${dir_permissions}" "${root_dir}"
	if [ $? -eq 0 ]
	then
		find "${root_dir}" -type d -print0 | xargs -0 chmod "${dir_permissions}"
		if [ $? -eq 0 ]
		then
			echo "Setting file permissions underneath \"${root_dir}\" to ${exec_file_permissions} for executable types and ${default_file_permissions} for non-executables."
			find "${root_dir}" -type f | while read f
			do
				new_file_permissions="${default_file_permissions}"
				if is_executable_file "${f}"
				then
					new_file_permissions="${exec_file_permissions}"
				fi
				chmod "${new_file_permissions}" "${f}"
				#echo "Set permissions for \"${f}\" to ${new_file_permissions}."
			done
		else
			return $?
		fi
	else
    	return $?
	fi	
}


ROOT_DIR="${1:?"Root directory not set."}"
DIR_PERMISSIONS="${2:?"Directory permissions not set."}" # e.g. 700
DEFAULT_FILE_PERMISSIONS="${3:?"Default file permissions not set."}" # e.g. 600 for private files or 644 for semi-private
EXEC_FILE_PERMISSIONS="${4:?"Executable file permissions not set."}" # e.g. 700 for private files or 755 for semi-private

set_permissions "${ROOT_DIR}" "${DIR_PERMISSIONS}" "${DEFAULT_FILE_PERMISSIONS}" "${EXEC_FILE_PERMISSIONS}"
