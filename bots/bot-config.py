import sqlite3

with sqlite3.connect('./rsc/wot_furys.sql') as conn:
    cur = conn.cursor()

    cur.execute('SELECT identification FROM clan_members WHERE id=?', (234395307759108106,))
    print(cur.fetchall()[0][0])

    conn.commit()

#
# with sqlite3.connect('./rsc/wot_furys.sql') as conn:
#     cur = conn.cursor()
#
#     for row in sql_data_old:
#         cur.execute('INSERT INTO clan_members (id, name, name_discord, name_displayed, name_wot, identification) VALUES (?, ?, ?, ?, ?, ?)', (row[0], row[1], row[2], row[6], row[3], row[5]))
#         cur.execute('INSERT INTO clan_member_statistics (id) VALUES (?)', (row[0],))
#
#     conn.commit()

# def extract(list):
#     r = []
#     for item in list:
#         r.append(item[0])
#
#     return r
#
# import pandas
# import matplotlib.pyplot as plt
#
# with sqlite3.connect('./rsc/wot_furys.sql') as conn:
#     cur = conn.cursor()
#     cur.execute('SELECT clan_members.name_displayed FROM clan_members, clan_member_statistics WHERE clan_members.id = clan_member_statistics.id and clan_members.name != "~battledroid"')
#     index = cur.fetchall()
#     cur.execute('SELECT clan_member_statistics.active_days FROM clan_members, clan_member_statistics WHERE clan_members.id = clan_member_statistics.id and clan_members.name != "~battledroid"')
#     data = cur.fetchall()
#     conn.commit()
#
# print(extract(data))
# print(extract(index))
#
# plt.bar(extract(index), extract(data))
# plt.xlabel("Discord Nickname")
# plt.show()

import botSupportFuncs as bsf

print(bsf.get_JSON('./rsc/bot.cfg')["D_MESSAGES"]["welcome message"])
