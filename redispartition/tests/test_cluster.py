from redispartition import RedisCluster
import redis
from hypothesis import given
from hypothesis.strategies import text
from hypothesis.strategies import integers
from hypothesis.strategies import binary
import hypothesis.strategies as st
conn1 = redis.StrictRedis(
    host='localhost', port=6379, db=0)
conn2 = redis.StrictRedis(
    host='localhost', port=6379, db=1)
connections = [conn1, conn2]


@given(integers())
def test_choose_connection(i):
    rhd = RedisCluster(connections)
    assert rhd._get_connection_from_crc16(i) in connections


@given(text(min_size=1))
def test_choose_connection_str(i):
    rhd = RedisCluster(connections)
    assert rhd.get_connection(i) in connections


@given(integers())
def test_choose_connection_int(i):
    rhd = RedisCluster(connections)
    assert rhd.get_connection(i) == rhd.get_connection(str(i))


@given(text())
def test_choose_connection_bytes(i):
    rhd = RedisCluster(connections)
    assert rhd.get_connection(i) == rhd.get_connection(str.encode(i))


@given(c=text(min_size=1), _bytes=binary(min_size=1))
def test_set_get_text(c, _bytes):
    rhd = RedisCluster(connections)
    rhd.set(c, _bytes)
    assert rhd.get(c) == _bytes


@given(c=st.lists(text(min_size=1), unique=True, max_size=5, min_size=5), _bytes=st.lists(binary(min_size=1), unique=True, max_size=5, min_size=5))
def test_set_get_pipe(c, _bytes):
    rhd = RedisCluster(connections)
    rhd.set(c, _bytes)
    assert rhd.get(c) == _bytes


@given(c=integers(), _bytes=binary(min_size=1))
def test_set_get_int(c, _bytes):
    rhd = RedisCluster(connections)
    rhd.set(c, _bytes)
    assert rhd.get(c) == _bytes


@given(c=text(min_size=1), i=integers(min_value=0, max_value=100000), bit=integers(min_value=0, max_value=1))
def test_setbit_getbit_int(c, i, bit):
    rhd = RedisCluster(connections)
    rhd.setbit(c, i, bit)
    assert rhd.getbit(c, i) == bit


@given(c=st.lists(text(min_size=1), unique=True, max_size=5, min_size=5), i=st.lists(integers(min_value=0, max_value=100000), max_size=5, min_size=5), bits=st.lists(integers(min_value=0, max_value=1), max_size=5, min_size=5))
def test_setbit_getbit_pipe(c, i, bits):
    rhd = RedisCluster(connections)
    rhd.setbit(c, i, bits)
    assert rhd.getbit(c, i) == bits
