import csv


class BaseParseAction(object):
    def __init__(self, a, b, tokens):
        self._tokens = tokens


class FileList(BaseParseAction):
    def get_files(self):
        return tuple(
            file_name for i, file_name in enumerate(self._tokens) if i % 2 == 0
        )


class SimpleSelect(BaseParseAction):
    def compile_to_bash(self):
        filenames = self._tokens[-1].get_files()
        return "cat " + " ".join(filenames)

    def run_py(self):
        for filename in self._tokens[-1].get_files():
            with open(filename) as input_file:
                reader = csv.reader(input_file)
                for row in reader:
                    yield tuple(row)


class SimpleSelectDistinct(SimpleSelect):
    def compile_to_bash(self):
        return super(
            SimpleSelectDistinct, self).compile_to_bash() + " | sort | uniq"

    def run_py(self):
        return set(super(SimpleSelectDistinct, self).run_py())


class Query(BaseParseAction):
    def compile_to_bash(self):
        return self._tokens[0].compile_to_bash()

    def run_py(self):
        return self._tokens[0].run_py()
