#!/bin/sh

# Copyright 2017 Todd Shore

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

# A script for trying to compress an arbitary amount of PDFs using qpdf in-place (i.e. the new, compressed file replacing the old one).
# Author: Todd Shore <errantlinguist+github@gmail.com>
# Since: 2017-07-31
# Website: https://github.com/errantlinguist/media-utils

compress_pdf_inplace()
{
	inpath="$1"
	file_size_func="${2}"
	tmpfile_path=`mktemp -qt "${3}"`
	result=$?
	if [ ${result} -eq 0 ]
	then
		echo "Compressing \"${inpath}\"..."
		qpdf --stream-data=compress "${inpath}" "${tmpfile_path}"
		result=$?
		if [ "${result}" -eq 0 ]
		then
			orig_size=`${file_size_func} "${inpath}"`
			compressed_size=`${file_size_func} "${tmpfile_path}"`
			size_diff=`expr "${orig_size}" - "${compressed_size}"`
			if [ "${size_diff}" -gt 0 ]
			then
				echo "Compressing \"${inpath}\" saved ${size_diff} bytes(s)."
				mv "${tmpfile_path}" "${inpath}"
				result=$?
				if [ ${result} -ne 0 ]
				then
					echo "Could not move \"${tmpfile_path}\" to \"${inpath}\"; Exit code ${result}."
				fi
			else
				echo "\"${inpath}\" is not smaller after compression."
				rm "${tmpfile_path}"
			fi			
		else
			echo "Could not compress \"${inpath}\"; Exit code ${result}."
		fi
	else
		echo "Could not create a temporary file; Exit code ${result}."
	fi
	
	return ${result}
}

# SYNOPSIS
#   fileSize file ...
# DESCRIPTION
#   Returns the size of the specified file(s) in bytes, with each file's 
#   size on a separate output line.
# See: https://stackoverflow.com/a/23332217/1391325
file_size_linux()
{
  stat -c "%s" "$@"
}

# SYNOPSIS
#   fileSize file ...
# DESCRIPTION
#   Returns the size of the specified file(s) in bytes, with each file's 
#   size on a separate output line.
# See: https://stackoverflow.com/a/23332217/1391325
file_size_bsd()
{
  stat -f "%z" "$@"
}

TMPFILE_TEMPLATE="${0##*/}.XXXXXXXXXX"

exit_code=1

if [ $# -lt 1 ]
then
	echo "Usage: $0 INPATHS..."
	exit_code=64
else
	kernel=`uname -s`
	echo "Defining file size comparison function for kernel \"${kernel}\"..."
	# https://stackoverflow.com/a/23472637/1391325
	case "${kernel}" in
		*BSD*) echo "Using BSD-style file size function."; file_size_func="file_size_bsd" ;;
		*Darwin*) echo "Using Darwin-style file size function."; file_size_func="file_size_bsd" ;;
		*) echo "Using Linux-style file size function."; file_size_func="file_size_linux" ;;
	esac

	for inpath in "$@"
	do
		compress_pdf_inplace "${inpath}" "${file_size_func}" "${TMPFILE_TEMPLATE}"
		exit_code=$?
		if [ "${exit_code}" -ne 0 ]
		then
			echo "An error occurred while processing \"${inpath}\"."
			break
		fi
	done
fi

exit ${exit_code}
