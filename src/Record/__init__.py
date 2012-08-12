##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

_marker = object()


class Record(object):

    __record_schema__ = None
    __slots__ = ('_data', '_schema')

    def __init__(self, data=None):
        cls_schema = type(self).__record_schema__
        if cls_schema is None:
            cls_schema = {}
        self._schema = schema = cls_schema
        len_schema = len(schema)
        if data is not None:
            if isinstance(data, dict):
                self._data = (None, ) * len_schema
                for k, v in data.items():
                    if k in schema:
                        self[k] = v
            elif len(data) == len_schema:
                self._data = tuple(data)
            else:
                self._data = (None, ) * len_schema
                maxlength = min(len(data), len_schema)
                for i in xrange(maxlength):
                    self[i] = data[i]
        else:
            self._data = (None, ) * len(schema)

    def __getstate__(self):
        return self._data

    def __setstate__(self, state):
        self.__init__(state)

    def __getitem__(self, key):
        if isinstance(key, int):
            pos = key
        else:
            try:
                pos = self._schema[key]
            except IndexError:
                raise TypeError('invalid record schema')
        return self._data[pos]

    def __getattr__(self, key, default=_marker):
        if key in self.__slots__:
            return object.__getattribute__(self, key)
        try:
            return self.__getitem__(key)
        except KeyError:
            if default is not _marker:
                return default
            raise AttributeError(key)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            pos = key
        else:
            try:
                pos = self._schema[key]
            except IndexError:
                raise TypeError('invalid record schema')
        old = self._data
        self._data = old[:pos] + (value, ) + old[pos + 1:]

    def __setattr__(self, key, value):
        if key in self.__slots__:
            object.__setattr__(self, key, value)
        else:
            try:
                self.__setitem__(key, value)
            except KeyError:
                raise AttributeError(key)

    def __contains__(self, key):
        return key in self._schema
