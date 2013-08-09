
import exceptions

class WeiboException(exceptions.BaseException):

    MSG = None

    def __init__(self, msg):
        exceptions.BaseException.__init__(self)
        self.MSG = msg

    def __str__(self):
        return self.MSG

    def __unicode__(self):
        return self.MSG

