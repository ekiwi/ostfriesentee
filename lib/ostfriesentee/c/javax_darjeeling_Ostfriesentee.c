/*
 * javax_darjeeling_Darjeeling.c
 * 
 * Copyright (c) 2008-2010 CSIRO, Delft University of Technology.
 * 
 * This file is part of Darjeeling.
 * 
 * Darjeeling is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * Darjeeling is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public License
 * along with Darjeeling.  If not, see <http://www.gnu.org/licenses/>.
 */

// generated at infusion time
#include <jlib_base.h>

#include <execution.h>
#include <array.h>

#include <unistd.h>

// standard posix write, only needs to accept fildes=1 for stdout
ssize_t write(int fildes, const void *buf, size_t nbyte);

void javax_ostfriesentee_Ostfriesentee_void__print_java_lang_String()
{
	// Pop string object from the stack.
	BASE_STRUCT_java_lang_String * stringObject = (BASE_STRUCT_java_lang_String*)REF_TO_VOIDP(dj_exec_stackPopRef());

	if (stringObject == NULL)
	{
		dj_exec_createAndThrow(BASE_CDEF_java_lang_NullPointerException);
		return;
	}

	// Get byte array
	dj_int_array * byteArray = (dj_int_array*)REF_TO_VOIDP(stringObject->value);

	if (byteArray == NULL)
	{
		dj_exec_createAndThrow(BASE_CDEF_java_lang_NullPointerException);
		return;
	}

	write(1, byteArray->data.bytes, stringObject->count);
}

//int javax.darjeeling.Darjeeling.getMemFree()
void javax_ostfriesentee_Ostfriesentee_int_getMemFree()
{
	dj_exec_stackPushInt(dj_mem_getFree());
}
