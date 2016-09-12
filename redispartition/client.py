from __future__ import print_function
from redispartition.decorators import pipeiflist
import crc16
import uuid


class RedisCluster(object):

    def __init__(self, connections):
        # list of redis connections
        self.connections = connections
        self.num_conns = len(self.connections)

    @pipeiflist
    def set(self, k, _bytes, conn=None):
        return conn.set(k, _bytes)

    @pipeiflist
    def setbit(self, k, i, bit, conn=None):
        return conn.setbit(k, i, bit)

    @pipeiflist
    def get(self, k, conn=None):
        return conn.get(k)

    @pipeiflist
    def getbit(self, k, i, conn=None):
        return conn.getbit(k, i)

    @pipeiflist
    def rpush(self, k, i, conn=None):
        return conn.rpush(k, i)

    @pipeiflist
    def lrange(self, name, start, end, conn=None):
        return conn.lrange(name, start, end)

    @pipeiflist
    def llen(self, k, conn=None):
        return conn.llen(k)

    @pipeiflist
    def incr(self, *args, conn=None, **kwargs):
        return conn.incr(*args, **kwargs)

    @pipeiflist
    def sadd(self, k, v, conn=None):
        return conn.sadd(k, v)

    @pipeiflist
    def srem(self, k, v, conn=None):
        return conn.srem(k, v)

    @pipeiflist
    def sismember(self, k, v, conn=None):
        return conn.sismember(k, v)

    @pipeiflist
    def delete(self, k, conn=None):
        return conn.delete(k)

    @pipeiflist
    def bitcount(self, k, conn=None):
        return conn.bitcount(k)

    @pipeiflist
    def bitpos(self, k, v, conn=None):
        return conn.bitpos(k, v)

    @pipeiflist
    def scard(self, k, conn=None):
        return conn.scard(k)

    def scan_iter(self, pattern="*"):
        for conn in self.connections:
            for k in conn.scan_iter(pattern):
                yield k

    def _bitop(self, operation, dest, *keys, conn=None):
        return conn.bitop(operation, dest, *keys)

    def bitop(self, operation, dest, *keys):
        bit_op_lists = self._create_bitop_lists(keys)
        temporary_bitarrays = []
        for i, keys in enumerate(bit_op_lists):
            if keys:
                self._bitop(
                    operation, dest, *keys, conn=self.connections[i])
                res = self.connections[i].get(dest)
                temporary_bitarrays.append(res)
        [c.delete(dest) for c in self.connections]
        result = self.logical_reduce(operation, temporary_bitarrays)
        self.set(dest, result)
        return result

    def logical_reduce(self, op, bitarrays):
        c = self.connections[0]
        hashes = [str(uuid.uuid4()) for i in bitarrays]
        for k, v in zip(hashes, bitarrays):
            c.set(k, v)
        c.bitop(op, '%s%s' % (op, hashes[0]), *hashes)
        result = c.get('%s%s' % (op, hashes[0]))
        [c.delete(h) for h in hashes + ['%s%s' % (op, hashes[0])]]
        return result

    def _create_bitop_lists(self, keys):
        bit_op_lists = [[] for _ in range(self.num_conns)]
        for k in keys:
            i = self.get_connection_index(k)
            bit_op_lists[i].append(k)
        return bit_op_lists

    def calculate_memory(self):
        return sum(r.info().get('used_memory') for r in self.connections)

    def flushall(self):
        [r.flushall() for r in self.connections]

    def shutdown(self):
        [r.shutdown() for r in self.connections]

    def dbsize(self):
        return sum([r.dbsize() for r in self.connections])

    def get_connection(self, k):
        if isinstance(k, str):
            k = str.encode(k)
        elif isinstance(k, int):
            k = str.encode(str(k))
        return self._get_connection_from_crc16(crc16.crc16xmodem(k))

    def get_connection_index(self, k):
        if isinstance(k, str):
            k = str.encode(k)
        elif isinstance(k, int):
            k = str.encode(str(k))
        return self._get_connection_index_from_crc16(crc16.crc16xmodem(k))

    def _get_connection_index_from_crc16(self, crc16):
        return crc16 % self.num_conns

    def _get_connection_from_crc16(self, crc16):
        index = self._get_connection_index_from_crc16(crc16)
        return self.connections[index]

    def _create_pipelines(self):
        return [c.pipeline() for c in self.connections]
