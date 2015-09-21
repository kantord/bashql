import csv


def passthrough(a, b, tokens):
    assert len(tokens) == 1
    return tokens[0]


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
        return "cat " + " ".join(
            filenames) + self._get_projection().compile_to_bash()

    def _get_projection(self):
        return self._tokens[1]

    def run_py(self):
        for filename in self._tokens[-1].get_files():
            with open(filename) as input_file:
                reader = csv.reader(input_file)
                for row in reader:
                    yield self._get_projection().project(tuple(row))


class SimpleSelectDistinct(SimpleSelect):
    def compile_to_bash(self):
        return super(
            SimpleSelectDistinct, self).compile_to_bash() + " | sort | uniq"

    def _get_projection(self):
        return self._tokens[2]

    def run_py(self):
        return set(super(SimpleSelectDistinct, self).run_py())


class Query(BaseParseAction):
    def compile_to_bash(self):
        return self._tokens[0].compile_to_bash()

    def run_py(self):
        return self._tokens[0].run_py()


class ProjectionStar(BaseParseAction):
    def compile_to_bash(self):
        return ""

    def project(self, row):
        return row


class ProjectionColumns(BaseParseAction):
    def _has_duplicates(self):
        return len(set(self.get_columns())) != len(list(self.get_columns()))

    def compile_to_bash(self):
        if (
            list(self.get_columns()) == list(sorted(self.get_columns())) and
            not self._has_duplicates()
        ):
            column_ids = ",".join(map(str, self.get_columns()))
            return " | cut -d ',' -f " + column_ids
        else:
            args = '","'.join(map(lambda i: "$%d" % i, self.get_columns()))
            return " | awk -F, '{ print %s }'" % args

    def project(self, row):
        return tuple(row[i - 1] for i in self.get_columns())

    def get_columns(self):
        return tuple(
            int(col[1:]) for i, col in enumerate(self._tokens) if i % 2 == 0
        )


class OrderedQuery(BaseParseAction):
    def __init__(self, a, b, tokens):
        self._tokens = tokens

    def get_column(self):
        return int(self._tokens[-1][1:])

    def compile_to_bash(self):
        return self._tokens[0].compile_to_bash() + " | sort -t, -k %d" % (
            self.get_column())

    def run_py(self):
        return sorted(
            self._tokens[0].run_py(), key=lambda r: r[self.get_column() - 1])
