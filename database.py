import sqlite3


def create_connection(db_file):
    """Создает соединение с базой данных SQLite."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn


def create_table(conn):
    """Создает таблицу для хранения рекордов, если она не существует."""
    try:
        sql = '''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            score INTEGER NOT NULL
        );
        '''

        cur = conn.cursor()
        cur.execute(sql)
    except sqlite3.Error as e:
        print(e)


def save_score(conn, player_name, score):
    """Сохраняет результат игры в базу данных."""
    sql = '''
    INSERT INTO scores (player_name, score) VALUES (?, ?)
    '''

    cur = conn.cursor()
    cur.execute(sql, (player_name, score))
    conn.commit()
    return cur.lastrowid


def get_high_scores(conn, limit=5):
    """Получает топ-N лучших результатов."""
    sql = '''
    SELECT player_name, score FROM scores ORDER BY score DESC LIMIT ?
    '''

    cur = conn.cursor()
    cur.execute(sql, (limit,))
    return cur.fetchall()


if __name__ == '__main__':
    database = "scores.db"
    conn = create_connection(database)
    if conn is not None:
        create_table(conn)
        conn.close()
    else:
        print("Ошибка! Невозможно создать соединение с базой данных.")
