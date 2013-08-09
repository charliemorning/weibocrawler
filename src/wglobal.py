# -*- coding: UTF-8 -*-

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

Usages = enum('FetchFollows', 'FetchFans', 'UpdateInfo', 'FetchWeibo', 'FetchComment', 'Center', 'Network')

