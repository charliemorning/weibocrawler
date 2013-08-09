# -*- coding: UTF-8 -*-


import threading
from log import logger
from user import User

class BaseTask(threading.Thread):

    def __init__(self, u, gsid):
        threading.Thread.__init__(self)
        self.u = u
        self.gsid = gsid

class FollowsTask(BaseTask):

    def __init__(self, u, gsid, **options):

        BaseTask.__init__(self, u, gsid)
        self.r = options["r"] if "r" in options else 1000

    def getFollows(self):

        self.u.lock(FollowsTask.__name__)

        stats = self.u.getUserStats(fresh=True, vt='4', gsid=self.gsid)

        followCnt = float(stats[0])
        fansCnt = float(stats[1])

        ratio = .0

        if int(followCnt) == 0:
            ratio = .0
        else:
            ratio = fansCnt / followCnt

        d = {'object': self.u.domain, 'extra': 'ratio:%f'%ratio};logger.info(u'粉丝%d 关注%d', int(fansCnt), int(followCnt), extra=d)

        if ratio < self.r:

            self.u.normal = True
            self.u.informative = False
            follows = []

        else:
            self.u.normal = False
            self.u.informative = True

            follows = self.u.getFollows(vt='4', gsid=self.gsid)

            followsDomains = [f.domain for f in follows]

            followsDomains += self.u.follows

            self.u.follows = followsDomains

        self.u.save_by_followcrawler()

        self.u.unlock()

        for f in follows:

            f.save()

    def run(self):
        self.getFollows()

class UpdateInfoTask(BaseTask):

    def __init__(self, u, gsid, **options):
        BaseTask.__init__(self, u, gsid)


    def updateInfo(self):
        self.u.lock(UpdateInfoTask.__name__)

        try:

            # to fetch the id of user
            self.u.fetchMyID(vt='4', gsid=self.gsid)

            # 获取用户的基本信息
            self.u.fetchMyInfo(vt='4', gsid=self.gsid)

            self.u.fetchAuthType(vt='4', gsid=self.gsid)
        except:
            print "error to fetch info"
            self.u.unlock()

        self.u.save_by_infocrawler()

        self.u.unlock()

    def run(self):
        self.updateInfo()


class WeiboTask(BaseTask):

    def __init__(self, u, gsid, **options):
        BaseTask.__init__(self, u, gsid)

    def fetchWeibo(self):

        self.u.lock(WeiboTask.__name__)

        weibos = self.u.getWeibos(vt='4', gsid=self.gsid)

        self.u.weibos += [w.wid for w in weibos]

        self.u.save_by_weibocrawler()

        self.u.unlock()

        for w in weibos:
            w.save_by_weibocrawler()

    def run(self):

        self.fetchWeibo()


class BuildNetworkTask(BaseTask):

    def __init__(self, u, gsid, maxDepth=2):

        BaseTask.__init__(self, u, gsid)
        self.maxDepth = maxDepth

    def buildNetwork(self, u, d):

        # pdb.set_trace()

        if d > self.maxDepth:
            return

        task = FollowsTask(u, self.gsid)
        task.start()
        task.join()


        fids = [f for f in u.follows]

        follows = User.objects.filter(uid__in=fids)

        for f in follows:
            self.buildNetwork(f, d+1)

    def run(self):
        self.buildNetwork(self.u, 0)


