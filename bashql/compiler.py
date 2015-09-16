import subprocess
import grammar


def compile(code):
    if code == "":
        raise SyntaxError("Expected a query. Got empty string.")
    else:
        filename = grammar.query.parseString(code)[-1]
        return "cat " + filename


def run(code):
    try:
        result = subprocess.check_output(
            compile(code), shell=True, stderr=subprocess.STDOUT).split("\n")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.output)
    if result == [""]:
        return []
    else:
        return result
