import subprocess
import grammar


def compile(code):
    if code == "":
        raise SyntaxError("Expected a query. Got empty string.")
    else:
        return grammar.query.parseString(code)[0].compile_to_bash()


def run(code):
    try:
        result = subprocess.check_output(
            compile(code), shell=True, stderr=subprocess.STDOUT).split("\n")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.output)
    return result[:-1]
