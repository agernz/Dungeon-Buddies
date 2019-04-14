from django.db import connection
from django.conf import settings
import random as r
import datetime


def getUserInfo(userID):
    c = connection.cursor()
    userInfo = {}
    try:
        c.execute("SELECT * FROM Account WHERE userID=%s;", [userID])
        uInfo = c.fetchone()
        userInfo["userID"] = uInfo[0]
        userInfo["username"] = uInfo[1]
        userInfo["characterName"] = uInfo[3]
        userInfo["exp"] = uInfo[4]
        userInfo["gold"] = uInfo[5]
        userInfo["guildID"] = uInfo[6]
        userInfo["level"] = uInfo[7]
        userInfo["health"] = uInfo[8]
        userInfo["attack"] = uInfo[9]
        userInfo["defense"] = uInfo[10]
        userInfo["speed"] = uInfo[11]
    except Exception as e:
        if settings.DEBUG:
            print("getUserInfo:", e)
    finally:
        c.close()
    return userInfo


def updateUserInfo(user):
    c = connection.cursor()
    try:
        new_data = list(user.values())[1:]
        new_data.append(user['userID'])
        c.execute("UPDATE Account SET username=%s, characterName=%s, experience=%s, \
                      gold=%s, guildID=%s, level=%s, health=%s, attack=%s, \
                      defense=%s, speed=%s WHERE userID=%s;", new_data)
    except Exception as e:
        if settings.DEBUG:
            print("updateUserInfo:", e)
    finally:
        c.close()


def getUserRank(userID):
    c = connection.cursor()
    rank = None
    try:
        c.execute(" SELECT ranking.gold_rank \
                    FROM (  SELECT A.userID, A.gold, COUNT(B.gold) \
                            as gold_rank \
                            FROM Account A, Account B \
                            WHERE A.gold < B.gold OR (A.gold = B.gold AND \
                            A.userID = B.userID) \
                            GROUP BY A.userID, A.gold \
                            ORDER BY A.gold DESC, A.userID DESC) as ranking \
                    WHERE ranking.userID=%s;", [userID])
        rank = c.fetchone()
    except Exception as e:
        if settings.DEBUG:
            print("getUserRank:", e)
    finally:
        c.close()
    return rank[0]


def getGuildRank(guildID):
    rank = None
    if guildID:
        c = connection.cursor()
        try:
            c.execute(" SELECT ranking.gold_rank \
                        FROM (  SELECT A1.guildID, A1.GOLD, COUNT(B.GOLD) \
                                as gold_rank \
                                FROM (SELECT  G.guildID, COUNT(M.userID) \
                                MEMBERS, SUM(A.gold) GOLD \
                                    FROM Guild G, Member M, Account A \
                                    WHERE G.guildID = M.guildID \
                                    AND M.userID = A.userID \
                                    GROUP BY G.guildID \
                                    ORDER BY GOLD DESC) A1, \
                                    (SELECT G.guildID, COUNT(M.userID) \
                                    MEMBERS, SUM(A.gold) GOLD \
                                    FROM Guild G, Member M, Account A \
                                    WHERE G.guildID = M.guildID AND M.userID \
                                    = A.userID \
                                    GROUP BY G.guildID \
                                    ORDER BY GOLD DESC) B \
                                WHERE   A1.GOLD < B.GOLD OR (A1.GOLD = \
                                B.GOLD AND A1.guildID = B.guildID) \
                                GROUP BY A1.guildID, A1.GOLD \
                                ORDER BY A1.GOLD DESC, A1.guildID DESC) \
                                as ranking \
                            WHERE ranking.guildID=%s;", [guildID[0]])
            rank = c.fetchone()
        except Exception as e:
            if settings.DEBUG:
                print("getGuildRank:", e)
        finally:
            c.close()
    return rank[0]


def getUserGuild(userID):
    c = connection.cursor()
    guild = None
    try:
        c.execute("SELECT Guild.guildID, Guild.name, Member.admin \
                  FROM Account, Guild, Member \
                  WHERE Account.userID=%s AND Member.userID = %s \
                  AND Guild.guildID=Account.guildID;", [userID, userID])
        guild = c.fetchone()
    except Exception as e:
        if settings.DEBUG:
            print("getUserGuild:", e)
    finally:
        c.close()
    return guild


def getTop100():
    c = connection.cursor()
    accounts = []
    accountInfo = {
        "username": "",
        "charName": "",
        "level": "",
        "gold": ""
    }
    try:
        c.execute(" SELECT username, characterName, level, gold \
                    FROM Account \
                    ORDER BY gold desc limit 100;")
        accountInfo = c.fetchall()
        for account in accountInfo:
            accounts.append({"username": account[0], "charName": account[1],
                             "level": account[2], "gold": account[3]})
    except Exception as e:
        if settings.DEBUG:
            print("getTop100:", e)
    finally:
        c.close()
    return accounts


def getTop100Guilds():
    c = connection.cursor()
    guilds = []

    try:
        c.execute(" SELECT  G.name NAME, COUNT(M.userID) MEMBERS, SUM(A.gold) GOLD \
                    FROM    Guild G, Member M, Account A \
                    WHERE   G.guildID = M.guildID AND M.userID = A.userID \
                    GROUP BY G.guildID \
                    ORDER BY GOLD DESC LIMIT 100;")
        guildInfo = c.fetchall()
        for guild in guildInfo:
            guilds.append({"guildName": guild[0],
                           "members": guild[1], "gold": guild[2]})

    except Exception as e:
        if settings.DEBUG:
            print("getTop100Guilds:", e)
    finally:
        c.close()
    return guilds


def getGuildMembers(userID, guildID, includeSelf=True):
    c = connection.cursor()
    members = []
    memberInfo = {
        "name": "",
        "charName": "",
        "exp": ""
    }
    try:
        c.execute("SELECT userID, username, characterName, level \
            FROM Account \
            WHERE Account.userID IN ( \
              SELECT userID \
              FROM Member as m \
              WHERE m.guildID=%s AND m.pending=0) \
            ORDER BY experience;", [guildID])
        memberInfo = c.fetchall()
        for member in memberInfo:
            if not includeSelf and member[0] == userID:
                continue
            members.append({"userID": member[0],
                            "name": member[1], "charName": member[2],
                            "level": member[3]})
    except Exception as e:
        if settings.DEBUG:
            print("getGuildMembers:", e)
    finally:
        c.close()
    return members


def sendGuildInvite(username, guildID):
    c = connection.cursor()
    try:
        c.execute("SELECT userID FROM Account WHERE username=%s;", [username])
        userID = c.fetchone()[0]
        c.execute("INSERT INTO Member(userID, guildID) values(%s, %s);",
                  [userID, guildID])
    except Exception as e:
        if settings.DEBUG:
            print("sendGuildInvite:", e)
    finally:
        c.close()


def deleteInvites(senderID):
    c = connection.cursor()
    try:
        c.execute("DELETE FROM Invite WHERE senderID=%s;", [senderID])
    except Exception as e:
        if settings.DEBUG:
            print("deleteInvites:", e)
    finally:
        c.close()


def getGuildInvites(userID):
    c = connection.cursor()
    guilds = []
    try:
        c.execute("SELECT temp.guildID, temp.name, temp.num_members \
            FROM (SELECT Guild.guildID, Guild.name, \
            COUNT(*) as num_members \
                  FROM Member INNER JOIN Guild ON \
                    Member.guildID=Guild.guildID \
                  WHERE Member.pending=0 \
                  GROUP BY Member.guildID) as temp \
            WHERE temp.guildID IN (SELECT m.guildID \
            FROM Member as m WHERE m.userID=%s AND m.pending=1);", [userID])
        for tup in c.fetchall():
            guilds.append({"gID": tup[0],
                           "name": tup[1], "num_members": tup[2]})
    except Exception as e:
        if settings.DEBUG:
            print("getGuildInvites:", e)
    finally:
        c.close()
    return guilds


def leaveGuild(userID):
    c = connection.cursor()
    try:
        c.execute("UPDATE Account SET guildID=Null WHERE userID=%s;", [userID])
        c.execute("DELETE FROM Member WHERE userID=%s \
                  AND pending=0;", [userID])
        c.execute("DELETE FROM Guild WHERE owner=%s;", [userID])
    except Exception as e:
        if settings.DEBUG:
            print("leaveGuild:", e)
    finally:
        c.close()


def joinGuildMember(userID, guildID):
    c = connection.cursor()
    try:
        c.execute("DELETE FROM Member WHERE userID=%s;", [userID])
        c.execute("INSERT INTO Member(userID, guildID, pending) \
                       VALUES(%s, %s, 0);",
                  [userID, guildID])
        c.execute("UPDATE Account SET guildID=%s WHERE Account.userID=%s;",
                  [guildID, userID])
    except Exception as e:
        if settings.DEBUG:
            print("joinGuildMember:", e)
    finally:
        c.close()


def createNewGuild(userID, guildName):
    c = connection.cursor()
    try:
        c.execute("DELETE FROM Member WHERE userID=%s;", [userID])
        c.execute("INSERT INTO Guild(name, owner) \
                       VALUES(%s, %s);",
                  [guildName, userID])
        c.execute("SELECT guildID FROM Guild WHERE owner=%s;", [userID])
        guildID = c.fetchone()[0]
        c.execute("INSERT INTO Member(userID, guildID, pending, admin) \
                       VALUES(%s, %s, 0, 1);",
                  [userID, guildID])
        c.execute("UPDATE Account SET guildID=%s WHERE Account.userID=%s;",
                  [guildID, userID])
    except Exception as e:
        if settings.DEBUG:
            print("createNewGuild:", e)
    finally:
        c.close()


def sendRaidInvite(senderID, recieveID):
    c = connection.cursor()
    try:
        c.execute("DELETE FROM Invite WHERE senderID=%s \
                  AND recieveID=%s;", [senderID, recieveID])
        c.execute("INSERT INTO Invite(senderID, recieveID, time) \
                       VALUES(%s, %s, %s);",
                  [senderID, recieveID,
                   datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')])
    except Exception as e:
        if settings.DEBUG:
            print("sendRaidInvite:", e)
    finally:
        c.close()


def getRaidInvites(userID):
    responseData = {"invites": []}
    c = connection.cursor()
    try:
        c.execute(" SELECT username \
                    FROM Account \
                    INNER JOIN \
                        (SELECT senderID FROM Invite \
                        WHERE recieveID=%s) AS senders \
                        ON Account.userID = senders.senderID;",
                  [userID])
        # responseData = fetchone()
        for tup in c.fetchall():
            print(tup)
            responseData["invites"].append({
                "senderUsername": tup[0]
                })
    except Exception as e:
        if settings.DEBUG:
            print("getRaidInvites:", e)
    finally:
        c.close()
    return responseData


def noMonsters(userID):
    c = connection.cursor()
    no_monsters = False
    try:
        c.execute("SELECT monsterID FROM Monster \
                  WHERE raidID=%s;", [userID])
        if c.fetchone() is None:
            no_monsters = True
    except Exception as e:
        if settings.DEBUG:
            print("noMonsters:", e)
    finally:
        c.close()
    return no_monsters


def generateMonsters(userID, rl):
    succes = True
    monster_names = ["Slime", "Skeleton", "Zombie", "Dennis", "Wolf", "Dragon", "Samurai", "Ninja", "Wisp", "Bear", "Giant Snake", "Giant Slime"]
    c = connection.cursor()
    try:
        c.execute("SELECT SUM(level) \
                   FROM Account as a, Raid as r \
                   WHERE r.userID1=%s AND (a.userID=r.userID1 \
                   OR a.userID=r.userID2 OR a.userID=r.userID3);", [userID])
        pl = c.fetchone()[0]
        if rl == 1:
            nm = 1
        else:
            nm = r.randint(1, 3)
        for i in range(nm):
            m_name = monster_names[r.randint(0, 3)]
            m_health = max((r.randint(0, pl) + rl) // nm, 1)
            m_attack = max((r.randint(0, pl) + rl) // nm, 1)
            m_defense = max((r.randint(0, pl) + rl) // nm, 1)
            m_speed = max((r.randint(0, pl) + rl) // nm, 1)
            c.execute("INSERT INTO Monster(raidID, name, health, attack, defense, \
                      speed) VALUES(%s, %s, %s, %s, %s, %s);",
                      [userID, m_name, m_health, m_attack, m_defense, m_speed])
    except Exception as e:
        succes = False
        if settings.DEBUG:
            print("generateMonsters:", e)
    finally:
        c.close()
    return succes


def createRaid(userID, level, health):
    c = connection.cursor()
    succes = True
    try:
        c.execute("INSERT INTO Raid(userID1, raidLevel, health1) \
                   VALUES(%s, %s, %s);",
                  [userID, level, health])
    except Exception as e:
        succes = False
        if settings.DEBUG:
            print("createRaid:", e)
    finally:
        c.close()
    return succes


def getRaidStatus(userID):
    c = connection.cursor()
    is_stageing = -1
    try:
        c.execute("SELECT stageing FROM Raid WHERE userID1=%s \
                  OR userID2=%s OR userID3=%s;",
                  [userID, userID, userID])
        res = c.fetchone()
        if res:
            is_stageing = res[0]
    except Exception as e:
        if settings.DEBUG:
            print("getRaidStatus:", e)
    finally:
        c.close()
    return is_stageing


def getRaid(userID):
    c = connection.cursor()
    raid = {}
    try:
        c.execute("SELECT * FROM Raid WHERE userID1=%s \
                  OR userID2=%s OR userID3=%s;",
                  [userID, userID, userID])
        data = c.fetchone()
        raid["user1"] = data[0]
        raid["user2"] = data[1]
        raid["user3"] = data[2]
        raid["health1"] = data[3]
        raid["health2"] = data[4]
        raid["health3"] = data[5]
        raid["move1"] = data[6]
        raid["move2"] = data[7]
        raid["move3"] = data[8]
        raid["raidLevel"] = data[9]
        raid["stageing"] = data[10]
    except Exception as e:
        if settings.DEBUG:
            print("getRaid:", e)
    finally:
        c.close()
    return raid


def getMonsters(userID):
    c = connection.cursor()
    monsters = []
    try:
        c.execute("SELECT * FROM Monster WHERE raidID=%s;", [userID])
        data = c.fetchall()
        for row in data:
            monsters.append({
                "monsterID": row[0],
                "name": row[2],
                "health": row[3],
                "attack": row[4],
                "defense": row[5],
                "speed": row[6],
            })
    except Exception as e:
        if settings.DEBUG:
            print("getMonsters:", e)
    finally:
        c.close()
    return monsters


def updateMonsters(monsters):
    c = connection.cursor()
    try:
        for m in monsters:
            c.execute("UPDATE Monster SET health=%s \
                      WHERE monsterID=%s;",
                      [m['health'], m['monsterID']])
    except Exception as e:
        if settings.DEBUG:
            print("updateMonsters:", e)
    finally:
        c.close()


def getPartyNames(usernames):
    partyNames = []
    c = connection.cursor()
    try:
        c.execute("SELECT characterName FROM Account \
                  WHERE userID=%s OR userID=%s OR userID=%s;", usernames)
        partyNames = [row[0] for row in c.fetchall()]
    except Exception as e:
        if settings.DEBUG:
            print("getPartyNames:", e)
    finally:
        c.close()
    return partyNames


def updateRaid(raid):
    c = connection.cursor()
    try:
        new_data = list(raid.values())[3:]
        new_data.pop(6)
        new_data.append(raid['user1'])
        c.execute("UPDATE Raid SET health1=%s, health2=%s, health3=%s, \
                      move1=%s, move2=%s, move3=%s, stageing=%s\
                   WHERE userID1=%s;", new_data)
    except Exception as e:
        if settings.DEBUG:
            print("updateRaid:", e)
    finally:
        c.close()


def deleteRaid(userID):
    c = connection.cursor()
    try:
        c.execute("DELETE FROM Raid WHERE userID1=%s;", [userID])
    except Exception as e:
        if settings.DEBUG:
            print("deleteRaid:", e)
    finally:
        c.close()
