import os
import string
import subprocess
import tempfile
from xml.etree import ElementTree


class GTestError(Exception):

    def __init__(self, failure):
        import colorama
        lines = failure.splitlines()
        if lines:
            filename, linenum = self._extract_file_reference(lines)
            code = self._get_code(filename, linenum)
            error_color = colorama.Fore.RED + colorama.Style.BRIGHT
            reset = colorama.Style.RESET_ALL
            if code:
                code_indent = self._get_line_indent(code[-1])
                code_color = colorama.Fore.WHITE + colorama.Style.BRIGHT
                code = [code_color + x.rstrip() + reset for x in code]
                lines = [code_indent + error_color + x + reset for x in lines]
                failure = '\n'.join(code + lines)
                failure += '\n\n{0}:{1}'.format(filename, linenum)
            else:
                failure = error_color + ''.join(lines) + reset

        Exception.__init__(self, failure)


    def _extract_file_reference(self, lines):
        first_line = lines.pop(0)
        fields = first_line.rsplit(':', 1)
        if len(fields) == 2:
            filename, linenum = fields
        else:
            filename = fields[0]
            linenum = '-1'
        return filename, int(linenum)


    def _get_code(self, filename, linenum):
        index = linenum - 1
        if os.path.isfile(filename):
            with open(filename) as f:
                return f.readlines()[index-2:index+1]


    def _get_line_indent(self, line):
        result = ''
        for c in line:
            if c not in string.whitespace:
                break
            else:
                result += c
        return result


class GTestFacade(object):

    @classmethod
    def is_test_suite(cls, executable):
        try:
            output = subprocess.check_output([executable, '--help'], universal_newlines=True)
        except (subprocess.CalledProcessError, OSError):
            return False
        else:
            return '--gtest_list_tests' in output


    def list_tests(self, executable):
        output = subprocess.check_output([executable, '--gtest_list_tests'], universal_newlines=True)
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

        results = self.parse_xml(xml_filename)
        for (executed_test_id, failure) in results:
            if executed_test_id == test_id:
                if failure is not None:
                    raise GTestError(failure)
                else:
                    return

        msg = ('Internal Error: could not find test '
               '{test_id} in results:\n{results}')
        results_list = '\n'.join(x for (x, f) in results)
        raise GTestError(msg.format(test_id=test_id, results=results_list))



    def parse_xml(self, xml_filename):
        root = ElementTree.parse(xml_filename)
        result = []
        for test_suite in root.findall('testsuite'):
            test_suite_name = test_suite.attrib['name']
            for test_case in test_suite.findall('testcase'):
                test_name = test_case.attrib['name']
                failure_elem = test_case.find('failure')
                if failure_elem is not None:
                    failure = failure_elem.attrib['message']
                else:
                    failure = None
                result.append((test_suite_name + '.' + test_name, failure))

        return result