from pyparsing import Keyword, Regex, StringEnd, ZeroOrMore
import tree


kw_SELECT = Keyword("SELECT")
kw_DISTINCT = Keyword("DISTINCT")
kw_FROM = Keyword("FROM")
kw_STAR = Keyword("*")
kw_UNION = Keyword("UNION")
re_filename = Regex("[A-z\.0-9]+")
file_list = ZeroOrMore(re_filename + kw_UNION) + re_filename
query_select = kw_SELECT + kw_STAR + kw_FROM + file_list
query_select_distinct = kw_SELECT + kw_DISTINCT + kw_STAR + kw_FROM + file_list
query = (query_select + StringEnd()) | (query_select_distinct + StringEnd())


file_list.setParseAction(tree.FileList)
query_select.setParseAction(tree.SimpleSelect)
query_select_distinct.setParseAction(tree.SimpleSelectDistinct)
query.setParseAction(tree.Query)
