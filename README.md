# Redis-py-partition

Partition data across multiple redis connections. If you're looking  a client for redis cluster see [redis-py-cluster](https://github.com/Grokzen/redis-py-cluster). 

# Usage

	>>from redispartition import RedisCluster
	>>import redis
	>>conn1 = redis.StrictRedis(
	    host='localhost', port=6379, db=0)
	>>conn2 = redis.StrictRedis(
	    host='localhost', port=6379, db=1)
	>>connections = [conn1, conn2]	
	>>rc=RedisCluster(connections)
	>>rc.set('1','2')
	True
	>>rc.get('1') 
	'2'

You can also provide certain commands with a list of arguments and commands will be executed in a pipeline

	>>rc.set(['1','2'],['3','4'])
	[True,True]
	>>rc.get(['1','2']) 
	['3','4']

