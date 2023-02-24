try:
    import unittest2 as unittest
except ImportError:
    import unittest
import pytest

try:
    from gmpy2 import mpz

    GMPY = True
except ImportError:
    try:
        from gmpy import mpz

        GMPY = True
    except ImportError:
        GMPY = False

from ._sha3 import shake_256
from ._compat import bytes_to_int, int_to_bytes

B2I_VECTORS = [
    (b"\x00\x01", "big", 1),
    (b"\x00\x01", "little", 0x0100),
    (b"", "big", 0),
    (b"\x00", "little", 0),
]


@pytest.mark.parametrize("bytes_in,endian,int_out", B2I_VECTORS)
def test_bytes_to_int(bytes_in, endian, int_out):
    out = bytes_to_int(bytes_in, endian)
    assert out == int_out


class TestBytesToInt(unittest.TestCase):
    def test_bytes_to_int_wrong_endian(self):
        with self.assertRaises(ValueError):
            bytes_to_int(b"\x00", "middle")

    def test_int_to_bytes_wrong_endian(self):
        with self.assertRaises(ValueError):
            int_to_bytes(0, byteorder="middle")


@pytest.mark.skipif(GMPY == False, reason="requites gmpy or gmpy2")
def test_int_to_bytes_with_gmpy():
    assert int_to_bytes(mpz(1)) == b"\x01"


I2B_VECTORS = [
    (0, None, "big", b""),
    (0, 1, "big", b"\x00"),
    (1, None, "big", b"\x01"),
    (0x0100, None, "little", b"\x00\x01"),
    (0x0100, 4, "little", b"\x00\x01\x00\x00"),
    (1, 4, "big", b"\x00\x00\x00\x01"),
]


@pytest.mark.parametrize("int_in,length,endian,bytes_out", I2B_VECTORS)
def test_int_to_bytes(int_in, length, endian, bytes_out):
    out = int_to_bytes(int_in, length, endian)
    assert out == bytes_out


SHAKE_256_VECTORS = [
    (
        b"Message.",
        32,
        b"\x78\xa1\x37\xbb\x33\xae\xe2\x72\xb1\x02\x4f\x39\x43\xe5\xcf\x0c"
        b"\x4e\x9c\x72\x76\x2e\x34\x4c\xf8\xf9\xc3\x25\x9d\x4f\x91\x2c\x3a",
    ),
    (
        b"",
        32,
        b"\x46\xb9\xdd\x2b\x0b\xa8\x8d\x13\x23\x3b\x3f\xeb\x74\x3e\xeb\x24"
        b"\x3f\xcd\x52\xea\x62\xb8\x1b\x82\xb5\x0c\x27\x64\x6e\xd5\x76\x2f",
    ),
    (
        b"message",
        32,
        b"\x86\x16\xe1\xe4\xcf\xd8\xb5\xf7\xd9\x2d\x43\xd8\x6e\x1b\x14\x51"
        b"\xa2\xa6\x5a\xf8\x64\xfc\xb1\x26\xc2\x66\x0a\xb3\x46\x51\xb1\x75",
    ),
    (
        b"message",
        16,
        b"\x86\x16\xe1\xe4\xcf\xd8\xb5\xf7\xd9\x2d\x43\xd8\x6e\x1b\x14\x51",
    ),
    (
        b"message",
        64,
        b"\x86\x16\xe1\xe4\xcf\xd8\xb5\xf7\xd9\x2d\x43\xd8\x6e\x1b\x14\x51"
        b"\xa2\xa6\x5a\xf8\x64\xfc\xb1\x26\xc2\x66\x0a\xb3\x46\x51\xb1\x75"
        b"\x30\xd6\xba\x2a\x46\x65\xf1\x9d\xf0\x62\x25\xb1\x26\xd1\x3e\xed"
        b"\x91\xd5\x0d\xe7\xb9\xcb\x65\xf3\x3a\x46\xae\xd3\x6c\x7d\xc5\xe8",
    ),
    (
        b"A" * 1024,
        32,
        b"\xa5\xef\x7e\x30\x8b\xe8\x33\x64\xe5\x9c\xf3\xb5\xf3\xba\x20\xa3"
        b"\x5a\xe7\x30\xfd\xbc\x33\x11\xbf\x83\x89\x50\x82\xb4\x41\xe9\xb3",
    ),
]


@pytest.mark.parametrize("msg,olen,ohash", SHAKE_256_VECTORS)
def test_shake_256(msg, olen, ohash):
    out = shake_256(msg, olen)
    assert out == bytearray(ohash)
