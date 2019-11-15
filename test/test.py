import struct

"""
msg_snd_len = 8
msg_id = 3
msg = ""
msg = bytes(msg, 'utf-8')
params = [msg_snd_len, msg_id, msg]
buf = struct.pack("!" + "2i" + str(len(msg)) +  "s", *params)

print(buf)
"""

"""
msg = [1,2,3]
buf = struct.pack("!" +  str(len(msg)) + "f", *msg)

print(buf)
msg_len=len(buf)
print(msg_len)
sformat = "!" + str(int(msg_len/4)) + "f"
print(sformat)
msg_float_tuple = struct.unpack(sformat, buf)

print(msg_float_tuple)
"""

params = [1., 2., 3.]
sformat = "!" + "%ii" % len(params)
buf = struct.pack(sformat, *params)

msg_float_tuple = struct.unpack(sformat, buf)
print(msg_float_tuple)

msg = "Hello"

if msg:
    print("Hi")