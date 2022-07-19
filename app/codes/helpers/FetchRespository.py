from typing import Final


class FetchRepository:
    __escape_string = ["--", ";--", ";", "/*", "*/", "@@", "@", "char", "nchar", "varchar", "nvarchar", "alter",
                            "begin", "cast", "create", "cursor", "declare", "delete", "drop", "end", "exec", "execute",
                            "fetch", "insert", "kill", "select", "sys", "sysobjects", "syscolumns", "table", "update"]
    __operation = {1: "=", 2: "in", 3: "not in",4:"like"}

    def __init__(self, cur):
        self.__cur = cur
        self.__query = ""

    def join_Query(self):
        self


    def select_Query(self,select_param="*"):
        self.__query = 'Select '+select_param+' from '
        return self
    def select_count(self,select_param="*"):
        self.__query = 'Select count(' + select_param + ') from '
        return self

    def add_table_name(self, table_name):
        self.__query = self.__query + ' ' + table_name + ' '
        return self

    def where_clause(self, column, value, operation):
        if self.queryCheck(column) and self.queryCheck(value):
            self.__query = self.__query + ' where ' + column + ' ' + self.__operation[operation] + ' :' + column
        return self

    def and_clause(self, column, value, operation):
        if self.queryCheck(column) and self.queryCheck(value):
            self.__query = self.__query + ' and ' + column + ' ' + self.__operation[operation] + ' :' + column
        return self

    def or_clause(self, column, value, operation):
        if self.queryCheck(column) and self.queryCheck(value):
            self.__query = self.__query + ' or ' + column + ' ' + self.__operation[operation] + ' :' + column
        return self

    def execute_query_single_result(self, queryParam):
        return self.__cur.execute(self.__query, queryParam).fetchone()

    def execute_query_multiple_result(self, queryParam):
        return self.__cur.execute(self.__query, queryParam).fetchall()

    def execute_query_update(self, queryParam):
        return self.__cur.execute(self.__query, queryParam)

    def queryCheck(self, query: str):
        if query in self.__escape_string:
            return False
        return True
