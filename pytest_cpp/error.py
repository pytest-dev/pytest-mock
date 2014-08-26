import string

import os
from py._code.code import ReprFileLocation


class CppFailureError(Exception):
    """
    Should be raised by test Facades when a test fails.

    Contains a list of `CppFailure` instances.
    """
    def __init__(self, failures):
        self.failures = failures


class CppTestFailure(object):
    """
    Represents a failure in a C++ test. Each framework
    must implement the abstract functions to build the final exception
    message that will be displayed in the terminal.
    """

    def get_lines(self):
        """
        Returns list of (line, markup) that will be displayed to the user,
        where markup can be a sequence of color codes from

        TerminalWriter._esctable:
            'black', 'red', 'green', 'yellow',
            'blue', 'purple', 'cyan', 'white',
            'bold', 'light', 'blink', 'invert'
        """
        raise NotImplementedError  # pragma: no cover

    def get_file_reference(self):
        """
        Return tuple of filename, linenum of the failure.
        """
        raise NotImplementedError  # pragma: no cover


class CppFailureRepr(object):
    """
    "repr" object for pytest that knows how to print a CppFailure instance
    into both terminal and files.
    """
    failure_sep = '---'

    def __init__(self, failures):
        self.failures = failures

    def __str__(self):
        reprs = []
        for failure in self.failures:
            pure_lines = '\n'.join(x[0] for x in failure.get_lines())
            repr_loc = self._get_repr_file_location(failure)
            reprs.append("%s\n%s" % (pure_lines, repr_loc))
        return self.failure_sep.join(reprs)

    def _get_repr_file_location(self, failure):
        filename, linenum = failure.get_file_reference()
        return ReprFileLocation(filename, linenum, 'C++ failure')

    def toterminal(self, tw):
        for index, failure in enumerate(self.failures):
            filename, linenum = failure.get_file_reference()
            code_lines = get_code_context_around_line(filename, linenum)
            for line in code_lines:
                tw.line(line, white=True, bold=True)  # pragma: no cover

            indent = get_left_whitespace(code_lines[-1]) if code_lines else ''

            for line, markup in failure.get_lines():
                markup_params = {m: True for m in markup}
                tw.line(indent + line, **markup_params)

            location = self._get_repr_file_location(failure)
            location.toterminal(tw)

            if index != len(self.failures) - 1:
                tw.line(self.failure_sep, cyan=True)


def get_code_context_around_line(filename, linenum):
    """
    return code context lines, with the last line being the line at
    linenum.
    """
    if os.path.isfile(filename):
        index = linenum - 1
        with open(filename) as f:
            index_above = index - 2
            index_above = index_above if index_above >= 0 else 0
            return [x.rstrip() for x in f.readlines()[index_above:index + 1]]
    return []


def get_left_whitespace(line):
    result = ''
    for c in line:
        if c in string.whitespace:
            result += c
        else:
            break
    return result



