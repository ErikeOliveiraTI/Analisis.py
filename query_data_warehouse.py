import sqlite3
import os
from pathlib import Path

# Use environment variables to avoid hard-coded sensitive paths.
# Configure this in a local .env file or via your shell environment.
db_path = os.getenv('DATAWAREHOUSE_DB_PATH') or os.getenv('DATAWAREHOUSE_DB')
if not db_path:
    db_path = r'C:\z\git\rotina\data_warehouse.db'

db_path = Path(db_path).expanduser().resolve()
if not db_path.exists():
    raise FileNotFoundError(f'Database file not found: {db_path}')

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY name")
objs = cur.fetchall()
print('SCHEMA')
for name, typ in objs:
    print(f'{typ}:{name}')
print('---')
for name, typ in objs:
    if typ == 'table':
        cur.execute(f'SELECT COUNT(*) FROM "{name}"')
        print(f'TABLE {name} rows={cur.fetchone()[0]}')
print('---')
for name, typ in objs:
    if typ == 'table':
        cur.execute(f'SELECT * FROM "{name}" LIMIT 10')
        rows = cur.fetchall()
        desc = [d[0] for d in cur.description]
        print(f'ROWS FROM {name}:')
        print('|'.join(desc))
        for row in rows:
            print(row)
        print('---')
conn.close()
