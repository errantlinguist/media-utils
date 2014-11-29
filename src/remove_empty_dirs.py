#!/usr/bin/env python

# Copyright 2014 Todd Shore

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

'''
A script for cleaning up (sub)directories in a directory tree which do not contain files matching a given content type pattern, e.g. media files such as "*.mp3" or "*.mpg" by default.

@author: Todd Shore
@copyright: 2014 Todd Shore. Licensed for distribution under the Apache License 2.0: See the files "NOTICE" and "LICENSE".
@see: <a href="https://github.com/errantlinguist/media-utils">The project GitHub site</a>
@version: 2014-11-29
@since: 2014-09-25
@todo: Test on Windows systems
'''

import os
import re

'''
The regular expression constant for matching positive user input.
'''
YES_PATTERN = re.compile("y(?:es)?", re.IGNORECASE)
'''
The regular expression constant for matching negative user input.
'''
NO_PATTERN = re.compile("no?", re.IGNORECASE)

def find_empty_dirs(rootdir, content_file_pattern, subdir_exclusion_pattern=None):
	'''
	Walks a given root directory and finds subdirectories which do not contain any files matching a given filename pattern or subdirectories matching a given name exclusion pattern.
	@param rootdir: The directory to search.
	@param content_file_pattern: A regular expression pattern matching valid content files.
	@param subdir_exclusion_pattern: A regular expression pattern matching subdirectory names to exclude from potential deletion.
	@return: The set of sub-directory trees for which there were no sub-directories underneath which contain files matching the given pattern or subdirectories matching the given exclusion pattern. 
	'''
	result = set()

	walk_generator = os.walk(rootdir, topdown=False, followlinks=True)
	if subdir_exclusion_pattern:
		for dirpath, subdirnames, filenames in walk_generator:
			if not subdir_exclusion_pattern.match(dirpath):
				__add_empty_dirs(dirpath, subdirnames, filenames, content_file_pattern, result)
	else:
		# subdir_exclusion_pattern is None; Don't do an exclusion check
		for dirpath, subdirnames, filenames in walk_generator:
			__add_empty_dirs(dirpath, subdirnames, filenames, content_file_pattern, result)		
	
	return result

def parse_confirmation(user_input):
	'''
	Parses a given string as positive or negative user confirmation ("Y"/"N").
	@param user_input: The input to parse.
	@return: True for positive confirmation ("Y"), False for negative confirmation ("N") or None for any input not recognized as the former two.
	'''
	result = None

	is_positive = YES_PATTERN.match(user_input)
	if is_positive:
		result = True
	else:
		is_negative = NO_PATTERN.match(user_input)
		if is_negative:
			result = False

	return result

def prompt_confirmation_input(prompt):
	'''
	Prompts the user to provide confirmation ("Y"/"N").
	@param prompt: The string prompt to display to the user.
	@return: True for positive confirmation ("Y") or False for negative confirmation ("N").
	'''
	result = parse_confirmation(raw_input(prompt))
	while result is None:
		result = parse_confirmation(raw_input(prompt))
	return result

def __add_empty_dirs(dirpath, subdirnames, filenames, content_file_pattern, empty_dirs):
	# Look for content files in the immediate directory
	has_content_files = any((content_file_pattern.match(filename) for filename in filenames))
	if not has_content_files:	
		if subdirnames:
			subdirpaths = frozenset((os.path.join(dirpath, subdirname) for subdirname in subdirnames))
			has_only_empty_subdirs = subdirpaths.issubset(empty_dirs)
			if has_only_empty_subdirs:
				empty_dirs -= subdirpaths	# Remove the subdirectories and replace them with this one (their parent)
				empty_dirs.add(dirpath)
		else:
			# The directory is a terminal node in the tree; If there are no content files in it, add it to the set of empty directories
			if not has_content_files:
				empty_dirs.add(dirpath)		


if __name__ == "__main__":
	import argparse
	import shutil
	import sys

	# Classes used only when running file as a script ----------------------
	class PatternAction(argparse.Action):
		'''
		An Action which compiles a regular expression from the given argument string.		
		'''
		def __init__(self, option_strings, dest, nargs=None, **kwargs):
			if nargs is not None:
				raise ValueError("nargs not allowed")
			super(PatternAction, self).__init__(option_strings, dest, **kwargs)

		def __call__(self, parser, namespace, values, option_string=None):
			value_pattern = re.compile(values)
			setattr(namespace, self.dest, value_pattern)


	# Functions used only when running file as a script --------------------
	def __create_default_content_file_pattern():
		'''
		A convenience function for creating the pattern constant for recognizing various media file types. 
		@return: The default media file name pattern.
		'''
		return re.compile(__create_default_content_file_pattern_str(), re.IGNORECASE)

	def __create_default_content_file_pattern_str():
		'''
		A convenience function for creating the pattern constant for recognizing various media file types. 
		@return: The default media file name pattern string.
		'''
		content_file_extension_patterns = ("aif[cf]?", "wav", "flac", "m4[ap]", "ape", "wm[av]", "mp[234]", "aac", "midi?", "ogg", "avi", "flv", "m[1234]v", "mov", "mp(?:e?g)|e")
		content_file_patterns = ("^.*\." + content_file_extension_pattern + "$" for content_file_extension_pattern in content_file_extension_patterns)
		return __create_disjoint_pattern(content_file_patterns)

	def __create_default_subdir_exclusion_pattern():
		'''
		A convenience function for creating the pattern constant for recognizing various names for subdirectories which should not be deleted even if they are found to be empty of recognized content file types.
		@return: The default subdir name exclusion pattern.
		'''
		return re.compile(__create_default_subdir_exclusion_pattern_str(), re.IGNORECASE)

	def __create_default_subdir_exclusion_pattern_str():
		'''
		A convenience function for creating the pattern constant for recognizing various names for subdirectories which should not be deleted even if they are found to be empty of recognized content file types.
		@return: The default subdir name exclusion pattern string.
		'''
		subdir_exclusion_patterns = (".*/artwork",)
		return __create_disjoint_pattern(subdir_exclusion_patterns)

	def __create_disjoint_pattern(patterns):
		disjunction_start = "(?:"
		disjunction_end = ")"
		joiner = disjunction_end + "|" + disjunction_start
		return disjunction_start + joiner.join(patterns) + disjunction_end

	def __delete_interactively(paths):
		'''
		Prompts the user to confirm the deletion of each path in a set and then deletes the path on confirmation.
		@param paths: An iterable object containing the paths to confirm deletion for.
		@return: The total number of paths out of the set which were (explicitly) deleted.
		'''
		result = 0

		for path in paths:
			deletion_prompt = "Delete path \"%s\"? [Y/N]: " % path
			confirmation = prompt_confirmation_input(deletion_prompt)
			if confirmation is True:
				shutil.rmtree(path)		
				result += 1

		return result
	# ----------------------------------------------------------------------

	exitcode = 1

	argparser = argparse.ArgumentParser(description="A script for cleaning up (sub-)directories in a directory tree which do not contain files matching a given content type pattern, e.g. media files such as \"*.mp3\" or \"*.mpg\" by default.")
	indir_arg = "indir"
	argparser.add_argument(indir_arg, help="the root directory to search for subdirectories not containing valid content files")
	content_file_pattern_arg = "content_file_pattern"
	argparser.add_argument("-f --content_file_pattern", action=PatternAction, dest=content_file_pattern_arg, default=__create_default_content_file_pattern(), help="the root directory to search for subdirectories not containing valid content files")
	subdir_exclusion_pattern_arg = "subdir_exclusion_pattern"
	argparser.add_argument("-e --subdir_exclusion_pattern", action=PatternAction, dest=subdir_exclusion_pattern_arg, default=__create_default_subdir_exclusion_pattern(), help="a pattern matching subdirectories to be excluded from search and possible deletion")
	args = argparser.parse_args()

	empty_dirs = find_empty_dirs(getattr(args, indir_arg), getattr(args, content_file_pattern_arg), getattr(args, subdir_exclusion_pattern_arg))
	deleted_dir_count = __delete_interactively(sorted(empty_dirs))
	print >> sys.stderr, "Deleted %d director(y|ies)." % deleted_dir_count
	exitcode = 0

	sys.exit(exitcode)

