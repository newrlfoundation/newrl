from typing import Final


class CentralRepository:
    escape_string: Final = ["--", ";--", ";", "/*", "*/", "@@", "@", "char", "nchar", "varchar", "nvarchar", "alter",
                            "begin", "cast", "create", "cursor", "declare", "delete", "drop", "end", "exec", "execute",
                            "fetch", "insert", "kill", "select", "sys", "sysobjects", "syscolumns", "table", "update"]
    operation: Final = {1: "=", 2: "in", 3: "not in"}

    def __init__(self, cur, read_cur):
        self.cur = cur
        self.read_cur = read_cur
        self.query = ""

    def join_Query(self):
        pass

    def insert_Query(self):
        self.query = 'INSERT INTO '
        return self

    def select_Query(self):
        self.query = 'Select * from '
        return self

    def add_table_name(self, table_name):
        self.query = self.query + ' ' + table_name + ' '
        return self

    def where_clause(self, column, value, operation):
        if self.queryCheck(column) and self.queryCheck(value):
            self.query = self.query + ' where ' + column + ' ' + self.operation[operation] + ' :' + column
        return self

    def and_clause(self, column, value, operation):
        if self.queryCheck(column) and self.queryCheck(value):
            self.query = self.query + ' and ' + column + ' ' + self.operation[operation] + ' :' + column
        return self

    def or_clause(self, column, value, operation):
        if self.queryCheck(column) and self.queryCheck(value):
            self.query = self.query + ' or ' + column + ' ' + self.operation[operation] + ' :' + column
        return self

    def execute_query_single_result(self, queryParam):
        return self.cur.execute(self.query, queryParam).fetchone()

    def execute_query_multiple_result(self, queryParam):
        return self.cur.execute(self.query, queryParam).fetchall()

    def execute_query_update(self, queryParam):
        return self.cur.execute(self.query, queryParam)

    def insert_query_data(self, queryParam: dict):
        keys = ','.join(queryParam.keys())
        placeHolder = ', :'.join(queryParam.keys())
        self.query = self.query + ' (' + keys + ') VALUES ( :' + placeHolder + ')'
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

    def update_private_sc_state(self, table_name: str, queryParam: dict, unique_column: str, unique_value: str,
                                contract_address: str):
        keys = ','.join(queryParam.keys())
        question_marks = ','.join(list('?' * len(queryParam)))
        for x in queryParam:
            if not self.queryCheck(x):
                return False
            if not self.queryCheck(queryParam[x]):
                return False
        if not self.queryCheck(unique_column):
            return False
        if not self.queryCheck(unique_value):
            return False
        if not self.queryCheck(contract_address):
            return False
        values = tuple(queryParam.values())
        values.append(unique_value, contract_address)
        return self.cur.execute(
            'UPDATE INTO ' + table_name + ' (' + keys + ') VALUES (' + question_marks + ') WHERE ' + unique_column + '=? AND contract_address=?',
            values)
    def delete_private_sc_state(self, table_name: str,  unique_column: str, unique_value: str,
                                contract_address: str):

        if not self.queryCheck(unique_column):
            return False
        if not self.queryCheck(unique_value):
            return False
        if not self.queryCheck(contract_address):
            return False
        values=[unique_value, contract_address]
        return self.cur.execute(
            'DELETE FROM ' + table_name +  ' WHERE ' + unique_column + '=? AND contract_address=?',
            values)
    def queryCheck(self, query: str):
        if query in self.escape_string:
            return False
        return True
