import subprocess
import tempfile
from xml.etree import ElementTree

import pytest
from pytest_cpp.error import CppFailure


class GTestFacade(object):
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
            return '--gtest_list_tests' in output

    def list_tests(self, executable):
        output = subprocess.check_output([executable, '--gtest_list_tests'],
                                         universal_newlines=True)
        test_suite = None
        result = []
        for line in output.splitlines():
            if line.endswith('.'):
                test_suite = line
            elif line.startswith('  '):
                result.append(test_suite + line.strip())
        return result

    def run_test(self, executable, test_id):
        xml_filename = tempfile.mktemp()
        args = [
            executable,
            '--gtest_filter=' + test_id,
            '--gtest_output=xml:%s' % xml_filename,
        ]
        try:
            subprocess.check_output(args, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            if e.returncode != 1:
                msg = ('Internal Error: calling {executable} '
                       'for test {test_id} failed (returncode={returncode}):\n'
                       '{output}')
                raise GTestError(
                    msg.format(executable=executable, test_id=test_id,
                               output=e.output,
                               returncode=e.returncode))

        results = self._parse_xml(xml_filename)
        for (executed_test_id, failure, skipped) in results:
            if executed_test_id == test_id:
                if failure is not None:
                    raise GTestError(failure)
                elif skipped:
                    pytest.skip()
                else:
                    return

        msg = ('Internal Error: could not find test '
               '{test_id} in results:\n{results}')
        results_list = '\n'.join(x for (x, f) in results)
        raise GTestError(msg.format(test_id=test_id, results=results_list))

    def _parse_xml(self, xml_filename):
        root = ElementTree.parse(xml_filename)
        result = []
        for test_suite in root.findall('testsuite'):
            test_suite_name = test_suite.attrib['name']
            for test_case in test_suite.findall('testcase'):
                test_name = test_case.attrib['name']
                failure_elem = test_case.find('failure')
                if failure_elem is not None:
                    failure = failure_elem.text
                else:
                    failure = None
                skipped = test_case.attrib['status'] == 'notrun'
                result.append(
                    (test_suite_name + '.' + test_name, failure, skipped))

        return result


class GTestError(CppFailure):
    def __init__(self, contents):
        Exception.__init__(self, contents)

        self.lines = contents.splitlines()
        self.filename = 'unknown file'
        self.linenum = 0
        if self.lines:
            fields = self.lines[0].rsplit(':', 1)
            if len(fields) == 2:
                self.filename = fields[0]
                self.linenum = int(fields[1])
                self.lines.pop(0)

    def get_lines(self):
        m = ('red', 'bold')
        return [(x, m) for x in self.lines]


    def get_file_reference(self):
        return self.filename, self.linenum