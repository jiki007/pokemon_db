import sqlite3
import os

DB_PATH = 'db.sqlite3'
OUTPUT  = 'mysql_dump.sql'

TABLES = [
    'cards_cardset',
    'cards_type',
    'cards_card',
    'cards_cardtype',
    'cards_attack',
    'cards_weakness',
    'cards_resistance',
    'cards_price',
]

TYPE_MAP = {
    'INTEGER': 'INT',
    'REAL':    'DOUBLE',
    'TEXT':    'LONGTEXT',
    'BLOB':    'LONGBLOB',
    'NUMERIC': 'DECIMAL(10,2)',
}

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

lines = []
lines.append('-- MySQL dump generated from SQLite')
lines.append('-- Import this into phpMyAdmin/XAMPP')
lines.append('')
lines.append('SET FOREIGN_KEY_CHECKS=0;')
lines.append('SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";')
lines.append('')

for table in TABLES:
    # Get column info
    cursor.execute(f'PRAGMA table_info({table})')
    columns = cursor.fetchall()

    lines.append(f'-- Table: {table}')
    lines.append(f'DROP TABLE IF EXISTS `{table}`;')
    lines.append(f'CREATE TABLE `{table}` (')

    col_defs = []
    for col in columns:
        col_name = col['name']
        col_type = col['type'].upper()

        # Map SQLite types to MySQL
        mysql_type = 'LONGTEXT'
        for sqlite_t, mysql_t in TYPE_MAP.items():
            if sqlite_t in col_type:
                mysql_type = mysql_t
                break

        # Handle special cases
        if 'VARCHAR' in col_type or 'CHAR' in col_type:
            mysql_type = col_type.replace('VARCHAR', 'VARCHAR').replace('CHAR', 'CHAR')
        if 'BOOL' in col_type:
            mysql_type = 'TINYINT(1)'
        if 'DATETIME' in col_type:
            mysql_type = 'DATETIME'
        if 'DATE' in col_type and 'DATETIME' not in col_type:
            mysql_type = 'DATE'
        if 'DECIMAL' in col_type:
            mysql_type = col_type

        not_null = 'NOT NULL' if col['notnull'] else 'DEFAULT NULL'
        if col['pk']:
            col_defs.append(f'  `{col_name}` {mysql_type} NOT NULL AUTO_INCREMENT')
        else:
            default = ''
            if col['dflt_value'] is not None:
                val = col['dflt_value']
                default = f" DEFAULT {val}"
            col_defs.append(f'  `{col_name}` {mysql_type} {not_null}{default}')

    # Add primary key
    pk_cols = [col['name'] for col in columns if col['pk']]
    if pk_cols:
        col_defs.append(f'  PRIMARY KEY (`{"`, `".join(pk_cols)}`)')

    lines.append(',\n'.join(col_defs))
    lines.append(') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;')
    lines.append('')

    # Insert data
    cursor.execute(f'SELECT * FROM {table}')
    rows = cursor.fetchall()

    if rows:
        lines.append(f'INSERT INTO `{table}` VALUES')
        row_strings = []
        for row in rows:
            values = []
            for val in row:
                if val is None:
                    values.append('NULL')
                elif isinstance(val, (int, float)):
                    values.append(str(val))
                else:
                    escaped = str(val).replace('\\', '\\\\').replace("'", "\\'")
                    values.append(f"'{escaped}'")
            row_strings.append(f"({', '.join(values)})")
        lines.append(',\n'.join(row_strings) + ';')
        lines.append('')

lines.append('SET FOREIGN_KEY_CHECKS=1;')

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

conn.close()
print(f'Done! Exported to {OUTPUT}')