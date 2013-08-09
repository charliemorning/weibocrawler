
import MySQLdb
import mongoengine
import pdb
from user import User, Weibo
import datetime

def user_tomysql():

    try:

        conn = MySQLdb.connect(host="localhost",user="root",passwd="root",db="snner_db",port=3306,charset="utf8")

        cur = conn.cursor()

        mongoengine.connect("weibo", host="192.168.0.188")

        allUsers = User.objects.filter()

        # user_values = []

        added_user = []

        for u in allUsers:

            # pdb.set_trace()

            if u.infoFetched and u.uid:
                now = datetime.datetime.now()


                val = (u.uid, u.nickname, u.nickname, u.domain, u.sex, u.area, "city_unknown", "prov_unknown", "lang_unknown", u.desc, u.auth, -1, u.fansCnt, u.followCnt, u.weiboCnt, -1, -1, -1, -1, 0, 0, 0,
                "", "", "", now, now,)

                cur.execute("INSERT INTO network_snuser(idstr,name,screen_name,domain,gender,location,city,province,lang,description,verified,bi_followers_count,followers_count,friends_count,statuses_count,favourites_count,online_status,block_word,star,allow_all_comment,allow_all_act_msg,geo_enabled,profile_url,profile_image_url,avatar_large,insert_at,last_update) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", val)

                added_user.append(u)

        conn.commit()

        ids = [u.id for u in added_user]

        for u in added_user:

            count = cur.execute("SELECT * FROM network_snuser WHERE idstr='" + u.uid + "'")
            if count <= 0:
                print "nouser found"
                continue

            follower = cur.fetchone()



            for fid in u.follows:

                # pdb.set_trace()

                if fid in ids:

                    count = cur.execute("SELECT * FROM network_snuser WHERE domain='" + fid + "'")
                    if count <= 0:
                        print "nouser found"
                        continue

                    followee = cur.fetchone()

                    val = (follower[0], followee[0])

                    cur.execute("INSERT INTO network_snuserrelation(follower_id, followee_id) VALUES(%s,%s)",val)

        conn.commit()

        cur.close()

        conn.close()

    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

def status_tomysql():

    try:

        conn = MySQLdb.connect(host="localhost",user="root",passwd="root",db="snner_db",port=3306,charset="utf8")

        cur = conn.cursor()

        mongoengine.connect("weibo", host="192.168.0.188")

        allWeibos = Weibo.objects.filter()

        i = 0


        for w in allWeibos:
            now = datetime.datetime.now()


            sql = "SELECT id FROM network_snuser WHERE domain='%s'" % w.user.domain



            count = cur.execute(sql)

            if count != 0:
                print i

                # pdb.set_trace()

                user = cur.fetchone()

                user_id = user[0]
                now = datetime.datetime.now()

                val = (w.id, user_id, w.id, w.id, w.text, False, "", 0, 0, 0, "", "", "", 0, 0, w.postTime, now, now)

                cur.execute("INSERT INTO network_status(idstr,user_id,wid,mid,text,truncated,source,comments_count,reposts_count,attitudes_count,bmiddle_pic,original_pic,thumbnail_pic,geox,geoy,created_at,insert_at,last_update) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", val)

                i += 1

                if i % 1000 == 0:
                    conn.commit()


        conn.commit()

        cur.close()

        conn.close()

    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])
user_tomysql()
status_tomysql()