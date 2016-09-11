from __future__ import print_function
from redispartition.decorators import pipeiflist
import crc16
import uuid


def logical_AND_reduce(list_of_bools):
    a = list_of_bools[0]
    for b in list_of_bools[1:]:
        a = bytes([a[0] & b[0]])
    return a


def logical_OR_reduce(list_of_bools):
    return [any(l) for l in zip(*list_of_bools)]


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
        [c.delete(h) for h in hashes]
        return c.get('%s%s' % (op, hashes[0]))

    def _create_bitop_lists(self, keys):
        bit_op_lists = [[] for _ in range(self.num_conns)]
        for k in keys:
            i = self.get_connection_index(k)
            bit_op_lists[i].append(k)
        return bit_op_lists

    def calculate_memory(self):
        return sum(r.info().get('used_memory') for r in self.connections)

    def delete(self):
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
