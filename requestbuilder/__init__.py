# Copyright (c) 2012, Eucalyptus Systems, Inc.
#
# Permission to use, copy, modify, and/or distribute this software for
# any purpose with or without fee is hereby granted, provided that the
# above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import argparse

__version__ = '0.0'

class Arg(object):
    """
    A command line argument.  Positional and keyword arguments to __init__
    are the same as those to argparse.ArgumentParser.add_argument.

    The value specified by the 'dest' argument (or the one inferred if
    none is specified) is used as the name of the parameter to server
    queries unless send=False is also supplied.
    """

    def __init__(self, *pargs, **kwargs):
        self.route  = kwargs.pop('route_to', PARAMS)
        self.pargs  = pargs
        self.kwargs = kwargs

    def __eq__(self, other):
        if isinstance(other, Arg):
            return sorted(self.pargs) == sorted(other.pargs)
        return False


class MutuallyExclusiveArgList(list):
    """
    Pass Args as positional arguments to __init__ to create a set of
    command line arguments that are mutually exclusive.  If the first
    argument passed to __init__ is True then the user must specify
    exactly one of them.

    Example:  MutuallyExclusiveArgList(Arg('--one'), Arg('--two'))
    """

    def __init__(self, *args):
        if len(args) > 0 and isinstance(args[0], bool):
            self.required = args[0]
            list.__init__(self, args[1:])
        else:
            self.required = False
            list.__init__(self, args)


class Filter(object):
    """
    An AWS API filter.  For APIs that support filtering by key/value
    pairs, adding a Filter to a request's list of filters will allow a
    user to send an output filter to the server with '--filter key=value'
    at the command line.

    The value specified by the 'dest' argument (or the 'name' argument,
    if none is given) is used as the name of a filter in queries.
    """
    def __init__(self, name, dest=None, type=str, choices=None, help=None):
        self.name    = name         # the name as shown on the command line
        self.dest    = dest or name # the name as sent to the server
        self.type    = type
        self.choices = choices
        self.help    = help

    def convert(self, str_value):
        """
        Convert a value to the data type expected by this filter by calling
        self.type on the value.  If this doesn't work then an ArgumentTypeError
        will result.  If the conversion succeeds but does not appear in
        self.choices when it exists, an ArgumentTypeError will result as well.
        """
        try:
            value = self.type(str_value)
        except ValueError:
            raise argparse.ArgumentTypeError('%s does not have type %s' %
                                             (str_value, self.type.__name__))
        if self.choices and value not in self.choices:
            msg = 'filter value %s does not match any of %s' % (value,
                    ', '.join([str(choice) for choice in self.choices]))
            raise argparse.ArgumentTypeError(msg)
        return value


# Constants (enums?) used for arg routing
CONNECTION = '==CONNECTION=='
PARAMS     = '==PARAMS=='


STD_AUTH_ARGS = [
        Arg('-I', '--access-key-id', dest='aws_access_key_id',
            metavar='KEY_ID', route_to=CONNECTION),
        Arg('-S', '--secret-key', dest='aws_secret_access_key', metavar='KEY',
            route_to=CONNECTION)]