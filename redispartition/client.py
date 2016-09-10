from __future__ import print_function
from redispartition.decorators import pipeiflist
import crc16


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
