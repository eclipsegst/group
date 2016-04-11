from tornado_mysql import pools

pools.DEBUG = True

POOL = pools.Pool(
    dict(host="127.0.0.1", port=3306, user='root', passwd='secret', db='group'),
    max_idle_connections=1,
    max_recycle_sec=3
)