from settings import *

INSTALLED_APPS += (
    'devserver',
)

DEVSERVER_MODULES = (
    # 'devserver.modules.sql.SQLRealTimeModule',
    'devserver.modules.sql.SQLSummaryModule',
    # 'devserver.modules.profile.ProfileSummaryModule',
    # 'devserver.modules.ajax.AjaxDumpModule',
    # 'devserver.modules.profile.MemoryUseModule',
    #'devserver.modules.cache.CacheRealTimeModule',
    'devserver.modules.cache.CacheSummaryModule',
    # 'devserver.modules.profile.LineProfilerModule',
)

REST_THUMBNAILS_USE_SECRET_PARAM = False
