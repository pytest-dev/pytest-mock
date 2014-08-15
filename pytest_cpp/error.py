import string

import os
from py._code.code import ReprFileLocation


class CppFailure(Exception):
    """
    Should be raised by test Facades when a test fails. Each framework
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
        raise NotImplementedError

    def get_file_reference(self):
        """
        Return tuple of filename, linenum of the failure.
        """
        raise NotImplementedError


class CppFailureRepr(object):
    """
    "repr" object for pytest that knows how to print a CppFailure instance
    into both terminal and files.
    """
    def __init__(self, failure):
        self.lines = failure.get_lines()
        self.filename, self.linenum = failure.get_file_reference()
        self.repr_location = ReprFileLocation(self.filename, self.linenum,
                                              'C++ failure')

    def __str__(self):
        pure_lines = [x[0] for x in self.lines]
        return "%s\n%s" % ("\n".join(pure_lines),
                           self.repr_location)

    def toterminal(self, tw):
        code_lines = self._get_code_lines(self.filename, self.linenum)
        for line in code_lines:
            tw.line(line, white=True, bold=True)

        if code_lines:
            # get indent used by the code that triggered the error
            indent = self._get_left_whitespace(code_lines[-1])
        else:
            indent = ''

        for line, markup in self.lines:
            markup_params = {m: True for m in markup}
            tw.line(indent + line, **markup_params)

        location = ReprFileLocation(self.filename, self.linenum, 'C++ failure')
        location.toterminal(tw)

    def _get_code_lines(self, filename, linenum):
        """
        return code context lines, with the last line being the line at
        linenum.
        """
        if os.path.isfile(filename):
            index = linenum - 1
            with open(filename) as f:
                return [x.rstrip() for x in f.readlines()[index - 2:index + 1]]
        return []

    def _get_left_whitespace(self, line):
        result = ''
        for c in line:
            if c in string.whitespace:
                result += c
            else:
                break
        return result



