import os
import random
import unittest
import subprocess
from bashql import compiler


class TestSelect(unittest.TestCase):
    def setUp(self):
        self.test_dirname = "/tmp/test_%d" % random.randrange(1, 10 ** 100)
        self._files = set()
        os.mkdir(self.test_dirname)
        os.chdir(self.test_dirname)

    def tearDown(self):
        for filename in self._files:
            os.remove(filename)
        os.rmdir(self.test_dirname)

    def _create_file(self, filename, content):
        with open(filename, "w") as output_file:
            output_file.write(content)
            self._files.add(filename)

    def test_empty_string_is_not_compilable(self):
        with self.assertRaisesRegexp(SyntaxError, r".*empty.*string.*"):
            compiler.compile("")
        with self.assertRaisesRegexp(SyntaxError, r".*empty.*string.*"):
            compiler.run("")

    def test_select_with_a_single_file_name_is_compilable(self):
        compiler.compile("SELECT * FROM foo.csv")

    def test_select_with_a_single_file_name_returns_sane_script(self):
        self.assertIn("cat ", compiler.compile("SELECT * FROM foo.csv"))
        self.assertIn("foo.csv", compiler.compile("SELECT * FROM foo.csv"))
        self.assertIn("foo.csv", compiler.compile("SELECT * FROM foo.csv"))
        self.assertNotIn("bar.csv", compiler.compile("SELECT * FROM foo.csv"))
        self.assertIn("bar.csv", compiler.compile("SELECT * FROM bar.csv"))

    def test_run_single_file_empty(self):
        self._create_file("foo.csv", "")
        self._create_file("bar.csv", "a,b\na,c\nb,d")
        self.assertEqual(len(compiler.run("SELECT * FROM foo.csv")), 0)

    def test_run_single_file_non_empty(self):
        self._create_file("foo.csv", "")
        self._create_file("bar.csv", "a,b\na,c\nb,d")
        self.assertEqual(len(compiler.run("SELECT * FROM bar.csv")), 3)
        self.assertIn("a,c", compiler.run("SELECT * FROM bar.csv"))

    def test_run_single_non_existent_file(self):
        self._create_file("foo.csv", "")
        self._create_file("bar.csv", "a,b\na,c\nb,d")
        with self.assertRaisesRegexp(RuntimeError, r".*No such file.*"):
            compiler.run("SELECT * FROM bullshit.csv")
