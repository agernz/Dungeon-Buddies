from django.db import connection
from django.conf import settings
import datetime


def getUserInfo(userID, uname):
    c = connection.cursor()
    userInfo = {
        "username": uname,
        "charName": "",
        "exp": "",
        "gold": "",
        "health": "",
        "attack": "",
        "defense": "",
        "speed": ""
    }
    try:
        c.execute("SELECT characterName, experience, gold \
                    health, attack, defense, speed \
                    FROM Account WHERE userID=%s;", [userID])
        uInfo = c.fetchone()
        userInfo["charName"] = uInfo[0]
        userInfo["exp"] = uInfo[1]
        userInfo["gold"] = uInfo[2]
        userInfo["health"] = uInfo[3]
        userInfo["attack"] = uInfo[4]
        userInfo["defense"] = uInfo[5]
        userInfo["speed"] = uInfo[6]
    except Exception as e:
        if settings.DEBUG:
            print(e)
    finally:
        c.close()
    return userInfo


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
            print(e)
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
                print(e)
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
            print(e)
    finally:
        c.close()
    return guild


def getTop100():
    c = connection.cursor()
    accounts = []
    accountInfo = {
        "username": "",
        "charName": "",
        "exp": "",
        "gold": ""
    }
    try:
        c.execute(" SELECT username, characterName, experience, gold \
                    FROM Account \
                    ORDER BY gold desc limit 100;")
        accountInfo = c.fetchall()
        for account in accountInfo:
            accounts.append({"username": account[0], "charName": account[1],
                             "exp": account[2], "gold": account[3]})
    except Exception as e:
        if settings.DEBUG:
            print(e)
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
            print(e)
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
        c.execute("SELECT userID, username, characterName, experience \
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
                            "exp": member[3]})
    except Exception as e:
        if settings.DEBUG:
            print(e)
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
            print(e)
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
            print(e)
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
            print(e)
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
            print(e)
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
            print(e)
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
            print(e)
    finally:
        c.close()


def getRaidInvites(userID):
    responseData = {"invites": []}
    timeToResponse = 45  # seconds
    c = connection.cursor()
    try:
        c.execute(" SELECT username, time \
                    FROM Account \
                    INNER JOIN \
                        (SELECT senderID, time FROM Invite \
                        WHERE recieveID=%s AND time >= %s) AS senders \
                        ON Account.userID = senders.senderID;",
                  [userID, datetime.datetime.utcnow()
                   - datetime.timedelta(seconds=timeToResponse)])
        # responseData = fetchone()
        for tup in c.fetchall():
            timeLeft = datetime.timedelta(seconds=timeToResponse)
            - (datetime.datetime.utcnow() - tup[1])
            timeLeft = int(timeLeft.total_seconds())
            responseData["invites"].append({
                "senderUsername": tup[0],
                "timeLeft": timeLeft
                })
    except Exception as e:
        if settings.DEBUG:
            print(e)
    finally:
        c.close()
    return responseData
