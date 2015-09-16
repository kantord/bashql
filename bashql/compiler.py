import subprocess
import grammar


def compile(code):
    if code == "":
        raise SyntaxError("Expected a query. Got empty string.")
    else:
        filenames = grammar.query.parseString(code)[-1]
        command = "cat " + " ".join(filenames)
        if "DISTINCT" == grammar.query.parseString(code)[1]:
            command += " | sort | uniq"
        return command


def run(code):
    try:
        result = subprocess.check_output(
            compile(code), shell=True, stderr=subprocess.STDOUT).split("\n")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e.output)
    return result[:-1]
