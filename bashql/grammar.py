from pyparsing import Keyword, Regex, StringEnd


kw_SELECT = Keyword("SELECT")
kw_FROM = Keyword("FROM")
kw_STAR = Keyword("*")
re_filename = Regex("[a-z]+\.csv")
query_select = kw_SELECT + kw_STAR + kw_FROM + re_filename
query = query_select + StringEnd()
