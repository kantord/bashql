import subprocess


def compile(code):
    if code == "":
        raise SyntaxError("Expected a query. Got empty string.")
    else:
        return "cat " + code.split("* ")[1].split("FROM")[1]


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
