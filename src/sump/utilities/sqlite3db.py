#! /usr/bin/python3

from pathlib import Path
from sump.utilities.files import get_project_root

import sqlite3

class SQLite3DB:
    def __init__(self, db_path : str = f"{get_project_root(Path(__file__))}/data/PompPut.db3", commit_every_stmt : bool = False) -> None:
        self.isConnected = False
        self._connect(db_path)
        self.cursor = None
        self._commit_every_stmt = commit_every_stmt
    
    #def __del__(self):
    def close(self):
        self._commit_and_close_cursor()
        self.connection.close()
        self.isConnected = False
    
    def _connect(self, db_path):
        if self.isConnected == False:
            self.connection = sqlite3.connect(db_path)
            self.isConnected = True
    
    def _commit_and_close_cursor(self):
        self.connection.commit()
        if self.cursor is not None:
            self.cursor.close()
    
    def _init_cursor(self):
        if self.cursor is None:
            self.cursor = self.connection.cursor()
        elif self._commit_every_stmt:
            self._commit_and_close_cursor()
            self.cursor = self.connection.cursor()
    
    def execute(self, sql : str, parameters = (), /):
        self._init_cursor()
        self.cursor.execute(sql, parameters)
        
        return self.cursor.lastrowid
    
    def executescript(self, sql_script : str):
        self.connection.executescript(sql_script)