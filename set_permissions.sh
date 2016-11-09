#!/bin/sh

# Copyright 2016 Todd Shore

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# A script for batch-setting permissions for directories and files, checking each file for a shebang in order to determine if it should have user-set "executable file" permissions applied to it or not.
# Author: Todd Shore <errantlinguist+github@gmail.com>
# Since: 2016-11-05
# Website: https://github.com/errantlinguist/media-utils

is_executable_file()
{
	filepath="$1"
	has_shebang "${filepath}"
	# TODO: Check for binary executables?
	return $?
}

has_shebang()
{
	filepath="$1"
	# Modified from SE answer <http://stackoverflow.com/a/2439587/1391325>
	line=`head -n 1 "${filepath}"`
	# Modified from SE answer <http://stackoverflow.com/a/33013693/1391325>
	echo "${line}" | grep -q '^#!'
	return $?
}

set_default_executable_file_permissions()
{
	exec_file_permissions="$1"
	default_file_permissions="$2"
	if is_executable_file "${f}"
	then
		new_file_permissions="${exec_file_permissions}"
	fi
	chmod "${new_file_permissions}" "${f}"
	#echo "Set permissions for \"${f}\" to ${new_file_permissions}."
}

set_permissions()
{
	root_dir="$1"
	dir_permissions="$2"
	exec_file_permissions="$3"
	default_file_permissions="$4"

	echo "Setting directory permissions for \"${root_dir}\" and its children to ${dir_permissions}."
	chmod "${dir_permissions}" "${root_dir}"
	if [ $? -eq 0 ]
	then
		find "${root_dir}" -type d -exec chmod "${dir_permissions}" {} +
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

USAGE_MSG="Usage: $0 ROOT_DIR DIR_PERMISSIONS EXEC_FILE_PERMISSIONS DEFAULT_FILE_PERMISSIONS"

ROOT_DIR="${1:?"Root directory not set.
${USAGE_MSG}"}"
DIR_PERMISSIONS="${2:?"Directory permissions not set.
${USAGE_MSG}"}" # e.g. 700
EXEC_FILE_PERMISSIONS="${3:?"Executable file permissions not set.
${USAGE_MSG}"}" # e.g. 700 for private files or 755 for semi-private
DEFAULT_FILE_PERMISSIONS="${4:?"Default file permissions not set.
${USAGE_MSG}"}" # e.g. 600 for private files or 644 for semi-private

set_permissions "${ROOT_DIR}" "${DIR_PERMISSIONS}" "${EXEC_FILE_PERMISSIONS}" "${DEFAULT_FILE_PERMISSIONS}"
