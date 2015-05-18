# oft_javat.py
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 Kevin Laeufer <kevin.laeufer@rwth-aachen.de>
#
# This file is part of Ostfriesentee.
#
# Ostfriesentee is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ostfriesentee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Ostfriesentee.  If not, see <http://www.gnu.org/licenses/>.

"""
# Ostfriesentee Java Tool

## JavaToJar
This adds a `JavaToJar` builder that overcomes some of the default java
builder's shortcomings.

The problem is, that `scons` needs to know what files will be generated by
a build process before the build tool is run.
Unfortunately, `javac` does not emit one `.class` file for every
`.java` input file. Depending on the source, it might emit several
`.class` files for one input file. To predict these, `scons`
has a built in java parser (see `src/engine/SCons/Tool/JavaCommon.py`).
Unfortunately the parser does not work with some features of the
latest `javac`.
See e.g.
* http://scons.tigris.org/issues/show_bug.cgi?id=1594
* http://scons.tigris.org/issues/show_bug.cgi?id=2547

If `scons` fails to predict `.class` output files, they will be omitted
when creating a `.jar` and thus the result of the `Jar` builder will
be defective.

Since you normally hand all your source files to the `javac` at once
and then hand all the resulting `.class` files to the `jar` tool,
there is not really any need for `scons` to know about the `.class`
files. If one `.java` input changes, the project needs to be rebuilt
(in most cases) anyways.

Thus the `JavaToJar` builder only tells `scons` that it will turn the
`.java` source files into a `.jar`, thus circumventing the problem
of predicting emitted `.class` files.
"""


import SCons
from SCons.Script import Mkdir, Depends
import os

def flag_if_not_empty(env, flag, env_var, default=None):
	if env_var in env and len(env[env_var]) > 0:
		return " {} {}".format(flag, ":".join(env[env_var]))
	elif default and len(default) > 0:
		return " {} {}".format(flag, default)
	else:
		return ""

def java_to_jar_action(target, source, env):
	# derive class dir from jar location
	# TODO: this might not a good idea in all cases
	class_dir = os.path.join(os.path.dirname(str(target[0])), 'class')

	java_src = [str(s) for s in source if os.path.splitext(str(s))[1] == '.java']
	manifest = [str(s) for s in source if os.path.basename(str(s)) == 'MANIFEST.MF']

	# build `javac` command
	javac = "$JAVAC $JAVACFLAGS"
	javac += flag_if_not_empty(env, "-bootclasspath", "JAVABOOTCLASSPATH")
	javac += flag_if_not_empty(env, "-classpath", "JAVACLASSPATH")
	# TODO: add default source path
	javac += flag_if_not_empty(env, "-sourcepath", "JAVASOURCEPATH")
	javac += " -d {}".format(class_dir)
	javac += " {}".format(" ".join(java_src))

	# build `jar` command
	jar = "$JAR cf"
	if len(manifest) > 0:
		jar += "m"
	jar += " {}".format(str(target[0]))
	if len(manifest) > 0:
		jar += " {}".format(str(manifest[0]))
	jar += " -C {} .".format(class_dir)

	env.Execute(Mkdir(class_dir))
	env.Execute(javac)
	env.Execute(jar)
	return 0

def java_to_jar_emitter(target, source, env):
	""" this emitter searches through directories for class files """
	java_src =  env.FindFiles(source, '.java')[0]
	manifest = [str(s) for s in source if os.path.basename(str(s)) == 'MANIFEST.MF']
	return target, java_src + manifest

def java_to_jar_string(target, source, env):
	""" returns an empty string, because the command run by the python action
	    will be displayed
	"""
	return ""

def manifest_action(target, source, env):
	manifest = "Manifest-Version: 1.0\n"
	if 'mainclass' in env:
		manifest += "Main-Class: {}\n".format(env['mainclass'])
	if not 'classpath' in env:
		env['classpath'] = env['JAVACLASSPATH']
	manifest += "Class-Path: {}\n".format(" ".join(env['classpath']))
	open(target[0].abspath, 'w').write(manifest)
	return 0

def manifest_emitter(target, source, env):
	if 'mainclass' in env:
		Depends(target, SCons.Node.Python.Value(env['mainclass']))
	if 'classpath' in env:
		Depends(target, SCons.Node.Python.Value(env['classpath']))
	else:
		Depends(target, SCons.Node.Python.Value(env['JAVACLASSPATH']))
	source = []
	return target, source

def manifest_string(target, source, env):
	return "Manifest"

def run_jar(env, jar, parameters=""):
	""" helper method to run a jar file as pseudo target """
	return env.Command('run_jar_file', jar, 'java -jar {} {}'.format(jar[0].abspath, parameters))

def generate(env):
	# oft java requires the find files tool
	env.Tool('find_files')

	# JavaToJar Builder
	java_to_jar_builder = SCons.Builder.Builder(
		action = env.Action(java_to_jar_action, java_to_jar_string),
		emitter = java_to_jar_emitter,
		target_factory = SCons.Node.FS.File,
		source_factory = SCons.Node.FS.Entry)
	env.Append(BUILDERS = { 'JavaToJar': java_to_jar_builder })

	# Manifest Builder
	manifest_builder = SCons.Builder.Builder(
		action = env.Action(manifest_action, manifest_string),
		emitter = manifest_emitter,
		suffix = '.MF',
		target_factory = SCons.Node.FS.File,
		source_factory = SCons.Node.FS.File)
	env.Append(BUILDERS = { 'Manifest': manifest_builder })

	# helper functions
	env.AddMethod(run_jar, 'RunJar')

	# default Java environment settings
	env.AppendUnique(JAVACFLAGS =
		['-encoding', 'utf8', '-Xlint:deprecation', '-Xlint:unchecked'])

def exists(env):
	return 1