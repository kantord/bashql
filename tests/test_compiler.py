import os
import random
import unittest
from bashql import compiler


class TestSelect(unittest.TestCase):
    def setUp(self):
        self.test_dirname = "/tmp/test_%d" % random.randrange(1, 10 ** 100)
        self._files = set()
        os.mkdir(self.test_dirname)
        self._original_pwd = os.getcwd()
        os.chdir(self.test_dirname)
        self._backends = ["bash", "python"]

    def tearDown(self):
        for filename in self._files:
            os.remove(filename)
        os.rmdir(self.test_dirname)
        os.chdir(self._original_pwd)

    def _mock_file(self, filename, content):
        with open(filename, "w") as output_file:
            output_file.write(content)
            self._files.add(filename)

    def test_empty_string_is_not_compilable(self):
        with self.assertRaisesRegexp(SyntaxError, r".*empty.*string.*"):
            compiler.compile("")
        with self.assertRaisesRegexp(SyntaxError, r".*empty.*string.*"):
            compiler.run("bash", "")
        with self.assertRaisesRegexp(SyntaxError, r".*empty.*string.*"):
            compiler.run("python", "")

    def test_select_with_a_single_file_name_is_compilable(self):
        compiler.compile("SELECT * FROM foo.csv")
        compiler.compile("SELECT * FROM Foo.csv")
        compiler.compile("SELECT * FROM oF.csv")
        compiler.compile("SELECT * FROM oF.txt")
        compiler.compile("SELECT * FROM oF.tXt")
        compiler.compile("SELECT * FROM without_dot")
        compiler.compile("SELECT * FROM .hidden_file")
        compiler.compile("SELECT * FROM __")
        compiler.compile("SELECT * FROM abc2312.342adf")

    def test_select_with_a_single_file_name_returns_sane_script(self):
        self.assertIn("cat ", compiler.compile("SELECT * FROM foo.csv"))
        self.assertIn("foo.csv", compiler.compile("SELECT * FROM foo.csv"))
        self.assertIn("foo.csv", compiler.compile("SELECT * FROM foo.csv"))
        self.assertNotIn("bar.csv", compiler.compile("SELECT * FROM foo.csv"))
        self.assertIn("bar.csv", compiler.compile("SELECT * FROM bar.csv"))

    def test_run_single_file_empty(self):
        for backend in self._backends:
            self._mock_file("foo.csv", "")
            self._mock_file("bar.csv", "a,b\na,c\nb,d\n")
            self.assertEqual(
                len(list(compiler.run(backend, "SELECT * FROM foo.csv"))), 0)

    def test_run_single_file_non_empty(self):
        for backend in self._backends:
            self._mock_file("foo.csv", "")
            self._mock_file("bar.csv", "a,b\na,c\nb,d\n")
            self.assertEqual(len(list(
                compiler.run(backend, "SELECT * FROM bar.csv"))), 3)
            self.assertIn(("a", "b", ), compiler.run(
                backend, "SELECT * FROM bar.csv"))

    def test_run_single_non_existent_file(self):
        for backend in self._backends:
            self._mock_file("foo.csv", "")
            self._mock_file("bar.csv", "a,b\na,c\nb,d\n")
            with self.assertRaisesRegexp(Exception, r".*No such file.*"):
                list(compiler.run(backend, "SELECT * FROM bullshit.csv"))

    def test_run_multiple_files_one_empty(self):
        for backend in self._backends:
            self._mock_file("foo.csv", "")
            self._mock_file("bar.csv", "a,b\na,c\nb,d\n")
            results = list(compiler.run(
                backend, "SELECT * FROM bar.csv UNION foo.csv"))
            self.assertEqual(len(results), 3)
            self.assertIn(("a", "b", ), results)
            self.assertIn(("b", "d", ), results)

    def test_run_multiple_files(self):
        for backend in self._backends:
            self._mock_file("foo.csv", "1,2\n")
            self._mock_file("bar.csv", "a,b\na,c\nb,d\n")
            results = list(compiler.run(
                backend, "SELECT * FROM bar.csv UNION foo.csv"))
            self.assertEqual(len(results), 4)
            self.assertIn(("1", "2", ), results)
            self.assertIn(("a", "b", ), results)
            self.assertIn(("b", "d", ), results)

    def test_select_distinct_single_file(self):
        for backend in self._backends:
            self._mock_file("bar.csv", "a,b\na,c\nb,d\na,c\n")
            results = list(compiler.run(
                backend, "SELECT DISTINCT * FROM bar.csv"))
            self.assertEqual(len(results), 3)

    def test_select_multiple_files_distinct(self):
        for backend in self._backends:
            self._mock_file("bar.csv", "a,b\na,c\nb,d\na,c\n")
            self._mock_file("baz.csv", "a,b\na,1\nb,d\na,c\n")
            self._mock_file("foo.csv", "a,b\na,c\nb,d\na,c\n")
            results = list(compiler.run(
                backend,
                "SELECT DISTINCT * FROM bar.csv UNION foo.csv UNION baz.csv"))
            self.assertEqual(len(results), 4)

    def test_select_first_column(self):
        for backend in self._backends:
            self._mock_file("bar.csv", "a,b\na,c\nb,d\na,c\n")
            self._mock_file("baz.csv", "a,b\na,1\n1,d\na,c\n")
            self._mock_file("foo.csv", "a,b\na,c\nb,d\na,c\n")
            results = set(compiler.run(
                backend,
                "SELECT DISTINCT #1 FROM bar.csv UNION foo.csv UNION baz.csv"))
            self.assertSetEqual(results, {("a", ), ("b", ), ("1", ), })

            results = list(compiler.run(
                backend, "SELECT #1 FROM bar.csv"))
            self.assertEqual(results, [("a", ), ("a", ), ("b", ), ("a", )])

    def test_select_no_first_column(self):
        for backend in self._backends:
            self._mock_file("bar.csv", "a,b,3\na,c,3\nb,d,3\na,c,3\n")
            self._mock_file("baz.csv", "a,b,3\na,1,3\n1,d,3\na,c,3\n")
            self._mock_file("foo.csv", "a,b,3\na,c,3\nb,d,3\na,c,3\n")
            results = set(compiler.run(
                backend,
                "SELECT DISTINCT #2,#3 FROM bar.csv UNION foo.csv UNION baz.csv"))  # noqa
            self.assertSetEqual(
                results, {
                    ("c", "3", ), ("b", "3", ), ("1", "3", ), ("d", "3",),
                }
            )

            results = list(compiler.run(
                backend, "SELECT #2,#3 FROM bar.csv"))
            self.assertEqual(
                results, [("b", "3"), ("c", "3"), ("d", "3"), ("c", "3")])

    def test_projection_reorder(self):
        for backend in self._backends:
            self._mock_file("bar.csv", "a,b,3\na,c,3\nb,d,3\na,c,3\n")

            results = list(compiler.run(
                backend, "SELECT #3,#2,#1 FROM bar.csv"))

            self.assertEqual(
                results,
                [("3", "b", "a", ), ("3", "c", "a", ), ("3", "d", "b", ), ("3", "c", "a", ), ])  # noqa

    def test_projection_duplicate(self):
        for backend in self._backends:
            self._mock_file("bar.csv", "a,b,3\na,c,3\nb,d,3\na,c,3\n")
            self._mock_file("baz.csv", "a,b\nb,c\n")

            results = list(compiler.run(
                backend, "SELECT #3,#2,#3 FROM bar.csv"))

            self.assertEqual(
                results,
                [("3", "b", "3", ), ("3", "c", "3", ), ("3", "d", "3", ), ("3", "c", "3", ), ])  # noqa

            results = list(compiler.run(
                backend, "SELECT #1,#1 FROM baz.csv"))

            self.assertEqual(results, [("a", "a", ), ("b", "b", )])

    def test_order_by_single_column(self):
        for backend in self._backends:
            print(backend)
            self._mock_file("bar.csv", "a,a\nx,c\nb,b\nc,d\n")

            results = list(compiler.run(
                backend, "SELECT * FROM bar.csv ORDER BY #2"))
            self.assertEquals(results, [
                ("a", "a", ), ("b", "b", ), ("x", "c", ), ("c", "d", ),
            ])

            results = list(compiler.run(
                backend, "SELECT * FROM bar.csv ORDER BY #1"))
            self.assertEquals(results, [
                ("a", "a", ), ("b", "b", ), ("c", "d", ), ("x", "c", ),
            ])

    def test_numerically_order_by_single_column(self):
        for backend in self._backends:
            self._mock_file("num.csv", "21\n11\n1\n2\n")

            results = list(compiler.run(
                backend, "SELECT * FROM num.csv NUMERICALLY ORDER BY #1"))
            self.assertEquals(results, [("1", ), ("2", ), ("11", ), ("21", )])
