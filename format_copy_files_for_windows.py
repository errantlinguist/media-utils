#!/usr/bin/env python2

# Copyright 2012--2013 Todd Shore
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

'''
A script with copies UNIX-style files to a given destination directory in a Windows-compatible format,
replacing invalid characters with Windows-compatible ones. NOTE: This script is "over-engineered" to show how to use Python's documentation features, interopability with different OSs, etc.

@author: Todd Shore
@version: 2012-09-19
@since: 2012-09-19
@copyright: Copyright 2012 Todd Shore. Licensed for distribution under the Apache License 2.0.

@var BAD_CHAR_REPLACEMENTS: A dictionary of characters to replace as keys mapped to their replacement characters as values.
'''

# Standard imports
import os
import re
import shutil
import sys

# Constants --------------------------------------------------------------------

# A dictionary of characters to replace as keys mapped to their replacement characters as values.
BAD_CHAR_REPLACEMENTS = {'<' : '_', '>' : '_', ':' : '-', '"' : '\'', '\\' : '_', '|' : '_', '?' : '_', '*' : '_'}

# A pattern matching the immediate relative UNIX directories "./" "../" and "/".
__RELATIVE_PATH_PREFIX = re.compile("^\.*" + re.escape(os.sep))

# Free functions ---------------------------------------------------------------

def copy_path(source, dest):
	'''
	Copies a file at a given path at a given destination path, creating any necessary subdirectories.
	@param source: The source path to copy from.
	@type source: str
	@param dest: The destination path to copy to.
	@type dest: str
	'''
	print >> sys.stderr, source, '>',
	dest_directory = os.path.split(dest)[0]
	if not os.path.exists(dest_directory):
		os.makedirs(dest_directory)
	shutil.copy(source, dest)
	print >> sys.stderr, dest

def format_bad_path(path):
	'''
	Formats a UNIX-compatible path into a Windows-compatible one. If the path is already Windows compatible, None is returned.
	@param path: The path to format.
	@type path: str
	@return: A version of the given path with the Windows-illegal characters replaced, or None if no formatting was necessary.
	@rtype: str
	'''
	formatted_path = path
	for bad_char, replacement in BAD_CHAR_REPLACEMENTS.iteritems():
		formatted_path = formatted_path.replace(bad_char, replacement)
	if path != formatted_path:
		result = formatted_path
	else:
		result = None
		
	return result

def format_bad_filenames(path):
	'''
	Recursively walks a given path to find all files with Windows-illegal path names and renames them, for each illegal path yielding a version of the given path with 
	the Windows-illegal characters replaced.
	@param path: The path to convert all illegal subordinate file path names thereof.
	@type path: str
	@return: A converted path name with the Windows-illegal characters replaced.
	@rtype: str
	'''
	for root, _, files in os.walk(path, followLinks=True):
		relative_base = os.path.relpath(root)

		for filename in files:
			formatted_path = format_bad_path(os.path.join(relative_base, filename))
			if formatted_path is not None:
				original_path = os.path.join(relative_base, filename)
				
				yield original_path, formatted_path


# Main procedure ---------------------------------------------------------------

if __name__=="__main__":

	def __get_usage_exit_code():
		'''
		Gets an OS-dependent exit code for invalid command-line usage.
		@return: An OS-dependent exit code for invalid command-line usage.
		@rtype: int
		'''
		if os.name == "posix":
			result = os.EX_USAGE
		elif os.name == "nt":
			try:
				# Try to load winerror module from the 3rd-party pywin32 package <http://sourceforge.net/projects/pywin32/>
				from winerror import ERROR_INVALID_COMMAND_LINE as result
			except ImportError:
				# Set the code manually <http://msdn.microsoft.com/en-us/library/windows/desktop/ms681385.aspx>
				result = 1639
		else:
			# Just set the exit code manually to the one defined in the POSIX sysexits.h
			result = 64
			
		return result

	def __exit_usage():
		'''
		Exits the program and displays usage info.
		'''
		print >> sys.stderr, "Usage: %s %s" %(sys.argv[0], "SOURCE_PATH DEST_PATH")
		exit_code = __get_usage_exit_code()
		sys.exit(exit_code)
		
	# Check number of command-line arguments
	if len(sys.argv) != 3:
		__exit_usage()
	else:
		inpath_dest_paths = format_bad_filenames(sys.argv[1])
		for source, relative_dest_path in inpath_dest_paths:
			stripped_relative_path = __RELATIVE_PATH_PREFIX.sub('', relative_dest_path, 1)
			dest = os.path.join(sys.argv[2], stripped_relative_path)
			copy_path(source, dest)
