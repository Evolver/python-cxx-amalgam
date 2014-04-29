
# Copyright (C) 2014 Dmitry Stepanov <dmitry@stepanov.lv>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA

import sys, re, os

class IncludePath:

    def __init__( self, regex, search ):
        self.regex = regex
        self.search = search

# Expands #includes in C/C++ source files.
class Amalgamator:

    include_regex = re.compile( r"""^\s*#\s*include\s+(?P<path>(?:<[^>]*>)|(?:"[^"]*")).*$""" )
    pragma_once_regex = re.compile( r"""^\s*#\s*pragma\s+once.*$"""  )

    def __init__( self, output ):
        self.is_main_file = True
        self.include_paths = []
        self.already_included = []
        self.already_included_sys = []
        self.output = output

    def add_include( self, include_path ):
        self.include_paths.append( include_path )

    def parse( self, path ):
        path_dir = os.path.dirname( path )
        if path_dir == "":
            path_dir = "."
        f = open( path, "rt" )
        try:
            while True:
                line = f.readline()
                if line == "":
                    break
                line_stripped = line.strip()

                # Do not suppress pragma once in main file (if startpoint is header)
                if not self.is_main_file and re.match( self.pragma_once_regex, line_stripped ) != None:
                    continue

                # We're not interested in anything but #includes
                include_macro = re.match( self.include_regex, line_stripped )
                if include_macro == None:
                    self.output.write( line )
                    continue

                self.handle_include( line, path_dir, include_macro.group( 'path' ) )

        finally:
            f.close()

    def handle_include( self, line, path_dir, included_pathspec ):
        if included_pathspec[ 0 ] == '"':
            is_relative = True
        else:
            is_relative = False
        included_path = included_pathspec[ 1 : -1 ]

        try_paths = []

        if is_relative:
            try_paths.append( os.path.abspath( path_dir + "/" + included_path ) )
        else:
            # A system include directive that we already saw earlier
            if included_path in self.already_included_sys:
                return
            self.already_included_sys.append( included_path )

        for system_path in self.include_paths:
            if re.match( system_path.regex, included_path ):
                try_paths.append( os.path.abspath( system_path.search + included_path ) )

        # An include directive we're not interested in.
        if len( try_paths ) == 0:
            self.output.write( line )
            return

        included = False
        for target_path in try_paths:
            if os.path.exists( target_path ):
                self.parse_include( target_path )
                included = True
                break

        if not included:
            raise Exception( "Could not resolve " + line.strip() )

    def parse_include( self, abs_path ):
        if abs_path in self.already_included:
            return

        self.already_included.append( abs_path )
        was_main_file = self.is_main_file
        self.is_main_file = False
        self.parse( abs_path )
        self.is_main_file = was_main_file

