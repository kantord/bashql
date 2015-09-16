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


class SimpleSelectDistinct(SimpleSelect):
    def compile_to_bash(self):
        return super(
            SimpleSelectDistinct, self).compile_to_bash() + " | sort | uniq"


class Query(BaseParseAction):
    def compile_to_bash(self):
        return self._tokens[0].compile_to_bash()
