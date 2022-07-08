from typing import Final


class FetchRepository:
    escape_string: Final = ["--", ";--", ";", "/*", "*/", "@@", "@", "char", "nchar", "varchar", "nvarchar", "alter",
                            "begin", "cast", "create", "cursor", "declare", "delete", "drop", "end", "exec", "execute",
                            "fetch", "insert", "kill", "select", "sys", "sysobjects", "syscolumns", "table", "update"]
    operation: Final = {1: "=", 2: "in", 3: "not in",4:"like"}

    def __init__(self, cur):
        self.cur = cur
        self.__query = ""

    def join_Query(self):
        self


    def select_Query(self,select_param="*"):
        self.__query = 'Select ('+select_param+') from '
        return self
    def select_count(self,select_param="*"):
        self.__query = 'Select count(' + select_param + ') from '
        return self

    def add_table_name(self, table_name):
        self.__query = self.__query + ' ' + table_name + ' '
        return self

    def where_clause(self, column, value, operation):
        if self.queryCheck(column) and self.queryCheck(value):
            self.__query = self.__query + ' where ' + column + ' ' + self.operation[operation] + ' :' + column
        return self

    def and_clause(self, column, value, operation):
        if self.queryCheck(column) and self.queryCheck(value):
            self.__query = self.__query + ' and ' + column + ' ' + self.operation[operation] + ' :' + column
        return self

    def or_clause(self, column, value, operation):
        if self.queryCheck(column) and self.queryCheck(value):
            self.__query = self.__query + ' or ' + column + ' ' + self.operation[operation] + ' :' + column
        return self

    def execute_query_single_result(self, queryParam):
        return self.cur.execute(self.__query, queryParam).fetchone()

    def execute_query_multiple_result(self, queryParam):
        return self.cur.execute(self.__query, queryParam).fetchall()

    def execute_query_update(self, queryParam):
        return self.cur.execute(self.__query, queryParam)

    def insert_query_data(self, queryParam: dict):
        keys = ','.join(queryParam.keys())
        placeHolder = ', :'.join(queryParam.keys())
        self.__query = self.__query + ' (' + keys + ') VALUES ( :' + placeHolder + ')'
        return self
    def save_private_sc_state(self, table_name: str, queryParam: dict):
        keys = ','.join(queryParam.keys())
        question_marks = ','.join(list('?' * len(queryParam)))
        for x in queryParam:
            if (not self.queryCheck(x)):
                return False
            if (not self.queryCheck(queryParam[x])):
                return False
        values = tuple(queryParam.values())
        return self.cur.execute('INSERT INTO ' + table_name + ' (' + keys + ') VALUES (' + question_marks + ')', values)

    def update_private_sc_state(self, table_name: str, queryParam: dict, whereAndParam: dict, whereOrQueryParam: dict):
        keys = ','.join(queryParam.keys())
        question_marks = ','.join(list('?' * len(queryParam)))
        for x in queryParam:
            if (not self.queryCheck(x)):
                return False
            if (not self.queryCheck(queryParam[x])):
                return False
        values = tuple(queryParam.values())
        return self.cur.execute('UPDATE INTO ' + table_name + ' (' + keys + ') VALUES (' + question_marks + ')', values)

    def queryCheck(self, query: str):
        if query in self.escape_string:
            return False
        return True
