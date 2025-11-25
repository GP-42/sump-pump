#! /usr/bin/python3

from contextlib import closing
from pathlib import Path
from sump.utilities.files import get_project_root

import sump.utilities.sqlite3db as db
import traceback

def create_database(db_path: str, sql_script_path: str) -> None:
    if not Path(sql_script_path).is_file():
        raise FileNotFoundError(f"SQL script not found: {sql_script_path}")
    
    with closing(db.SQLite3DB(db_path)) as database:
        with open(sql_script_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
        
        database.executescript(sql_script)
        print(f"Database '{db_path}' created successfully and intialized.")

if __name__ == "__main__":
    try:
        db_file = f"{get_project_root(Path(__file__))}/data/test.db3"
        sql_file = f"{get_project_root(Path(__file__))}/data/CreateDB.sql"

        create_database(db_file, sql_file)
    
    except Exception as e:
        traceback.print_exc()