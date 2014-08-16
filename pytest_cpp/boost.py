import os
import subprocess
from xml.etree import ElementTree
from pytest_cpp.error import CppTestFailure


class BoostTestFacade(object):
    """
    Facade for GoogleTests.
    """

    @classmethod
    def is_test_suite(cls, executable):
        try:
            output = subprocess.check_output([executable, '--help'],
                                             universal_newlines=True)
        except (subprocess.CalledProcessError, OSError):
            return False
        else:
            return '--output_format' in output and 'log_format' in output

    def list_tests(self, executable):
        # unfortunately boost doesn't provide us with a way to list the tests
        # inside the executable, so the test_id is a dummy placeholder :(
        return [os.path.basename(os.path.splitext(executable)[0])]

    def run_test(self, executable, test_id):
        args = [
            executable,
            '--output_format=xml',
            '--log_sink=stdout',
            '--report_sink=stderr',
        ]
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if p.returncode not in (0, 201):
            msg = ('Internal Error: calling {executable} '
                   'for test {test_id} failed (returncode={returncode}):\n'
                   'stdout:{stdout}\n'
                   'stderr:{stderr}')
            failure = BoostTestFailure(
                executable,
                linenum=0,
                contents=msg.format(executable=executable,
                                    test_id=test_id,
                                    stdout=stdout,
                                    stderr=stderr,
                                    returncode=p.returncode))
            return [failure]

        results = self._parse_xml(log=stdout, report=stderr)
        if results:
            return results

    def _parse_xml(self, log, report):
        root = ElementTree.fromstring(log)
        result = []
        for elem in root.findall('Exception') + root.findall('Error'):
            filename = elem.attrib['file']
            linenum = int(elem.attrib['line'])
            result.append(BoostTestFailure(filename, linenum, elem.text))
        return result


class BoostTestFailure(CppTestFailure):
    def __init__(self, filename, linenum, contents):
        self.filename = filename
        self.linenum = linenum
        self.lines = contents.splitlines()

    def get_lines(self):
        m = ('red', 'bold')
        return [(x, m) for x in self.lines]

    def get_file_reference(self):
        return self.filename, self.linenum