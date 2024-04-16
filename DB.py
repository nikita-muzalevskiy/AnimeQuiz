import sqlite3

def getCharacterList(animeName):
    connection = sqlite3.connect('AnimeTests.db')
    cursor = connection.cursor()
    cursor.execute(f'select character from {animeName}')
    l = cursor.fetchall()
    connection.close()
    return l

def getAnimeList():
    connection = sqlite3.connect('AnimeTests.db')
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    l = cursor.fetchall()
    l.remove(('sqlite_sequence',))
    connection.close()
    return l

def changeStatistics(user_info):
    connection = sqlite3.connect('AnimeTests.db')
    cursor = connection.cursor()
    for c in user_info["characters"]:
        cursor.execute(f'UPDATE "{user_info["anime"]}" SET win_battle = win_battle + {user_info["characters"][c][0]}, battle = battle + {user_info["characters"][c][1]}, test = test + 1 WHERE character = "{c}"')
    cursor.execute(f'UPDATE {user_info["anime"]} SET win_test = win_test + 1 WHERE character = "{user_info["winners"][0]}"')
    connection.commit()
    connection.close()

def getStatistics(animeName):
    connection = sqlite3.connect('AnimeTests.db')
    cursor = connection.cursor()
    cursor.execute(f"select character, round((1.0 * win_battle / battle), 2)*100 as procentik from {animeName} order by procentik desc")
    res = cursor.fetchall()
    connection.commit()
    connection.close()
    return res