from typing import List, Union, Any


# allowed libraries: math, typing, types


def encode_BOOLEAN(data: bool) -> bytes:
    bit_data: str = format(1, "08b")*2

    if data:
        return int(bit_data + "1"*8, 2).to_bytes(3, "big")

    return int(bit_data + "0"*8, 2).to_bytes(3, "big")


def encode_INTEGER(data: int) -> bytes:
    bit_data: str = format(2, "08b")

    bin_num: str = format(abs(data), "b")

    if data < 0:
        if (len(bin_num) % 8 == 0) and (bin_num[0] == 0):
            bin_num = "1" + bin_num[1:]

        elif (len(bin_num) % 8 == 0) and (bin_num[0] == 1):
            bin_num = "10000000" + bin_num

        else:
            bin_num = "0"*(8 - len(bin_num) % 8)+bin_num
            bin_num = "1" + bin_num[1:]

        bin_num = ''.join('1' if x == '0' else '0' for x in bin_num[1:])
        bin_num = "1" + bin_num

        bin_num = bin(int(bin_num, 2) + int("00000001", 2))[2:]

    if (len(bin_num) % 8) != 0:
        bin_num = "0"*(8 - len(bin_num) % 8) + bin_num

    bit_num_len: str = format(int(len(bin_num)/8), "08b")
    if (len(bit_num_len) % 8) != 0:
        bit_num_len = "0"*(8 - len(bit_num_len) % 8) + bit_num_len

    bit_data += bit_num_len
    bit_data += bin_num

    return int(bit_data, 2).to_bytes(int(len(bit_data)/8), "big")


def encode_NULL(data: None) -> bytes:
    bit_data: str = format(5, "08b")
    bit_data += format(0, "08b")

    return int(bit_data, 2).to_bytes(2, "big")


def encode_IA5String(data: str) -> bytes:
    bit_data: str = format(22, "08b")
    bit_data += format(len(data), "08b")
    for character in data:
        bit_data += format(ord(character), "08b")

    return int(bit_data, 2).to_bytes(int(len(bit_data)/8), "big")


AnyDERType = Union[int, str, None, List[Any]]


def encode_SEQUENCE(data: List[AnyDERType]) -> bytes:
    bit_data: str = format(48, "08b")
    byte_data: bytes = bytes()
    for value in data:
        byte_data += encode_any(value)

    bit_data += format(int(len(byte_data)), "08b")

    return int(bit_data, 2).to_bytes(2, "big") + byte_data


def encode_any(data: AnyDERType) -> bytes:
    type_match: dict = {
        str: encode_IA5String,
        int: encode_INTEGER,
        type(None): encode_NULL,
        list: encode_SEQUENCE,
        bool: encode_BOOLEAN,
        }

    return type_match[type(data)](data)


def encode(data: List[AnyDERType]) -> bytes:
    byte_data: bytes = bytes()
    for value in data:
        byte_data += encode_any(value)

    return byte_data


# Tests
# We still highly encourage writing your own tests,
# but with these tests you can verify the basic
# functionalities of the program.
def main() -> None:
    print(encode_any(1))  # b'\x02\x01\x01'
    print(encode_any(-1))  # b'\x02\x01\xff'
    print(encode_any(0))  # b'\x02\x01\x00'
    print(encode_any(256))  # b'\x02\x02\x01\x00'
    print(encode_any(-255))  # b'\x02\x02\xff\x01'

    # Python always tries to map byte values
    # to their ASCII value representations,
    # that is why:
    # print(b'\x68') -> b'h'
    print(encode_any("A"))  # b'\x16\x01A'
    print(encode_any("Hello World!"))  # b'\x16\x0cHello World!'
    print(encode_any("Karlik <3"))  # b'\x16\tKarlik <3'

    print(encode_any([]))  # b'0\x00'
    print(encode_any([1]))  # b'0\x03\x02\x01\x01'
    print(encode_any([0, 1, 2]))  # b'0\t\x02\x01\x00\x02\x01\x01\x02\x01\x02'

    print(encode_any([True, None, "Hi", None, 1]))
    # b'0\x0e\x01\x01\xff\x05\x00\x16\x02Hi\x05\x00\x02\x01\x01'

    print(encode([None, 1, [[]], "YO"]))
    # b'\x05\x00\x02\x01\x010\x020\x00\x16\x02YO'


if __name__ == '__main__':
    main()
