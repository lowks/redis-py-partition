# Redis-py-partition

Partition data across multiple redis connections. If you're looking for a client for redis cluster see [redis-py-cluster](https://github.com/Grokzen/redis-py-cluster). 
# Install

	pip install redispartition

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

See [client.py](redispartition/client.py) for supported commands. 

You can also provide commands with a list of arguments and commands will be executed in a pipeline automatically (and across multiple redis instances)

	>>rc.set(['1','2'],['3','4'])
	[True,True]
	>>rc.get(['1','2']) 
	['3','4']

bitoperations AND OR and XOR are supported. RedisCluster uses connection 0 to temporarilty store intermediate results from the other connections. Then, reduces them using redis' native bitop command. 