import subprocess
import grammar


def compile(code):
    if code == "":
        raise SyntaxError("Expected a query. Got empty string.")
    else:
        return grammar.query.parseString(code)[0].compile_to_bash()


def run_bash(code):
    try:
        result = subprocess.check_output(
            compile(code), shell=True, stderr=subprocess.STDOUT).split("\n")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.output)
    return map(lambda r: tuple(r.split(",")), result[:-1])


def run_py(code):
    if code == "":
        raise SyntaxError("Expected a query. Got empty string.")
    else:
        return grammar.query.parseString(code)[0].run_py()


def run(backend, code):
    if backend == "bash":
        return run_bash(code)
    elif backend == "python":
        return run_py(code)
