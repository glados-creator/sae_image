import base64
data = "TU4EAAAAAAAAKgQAACgAAAAEAAAABAAAAAEACAABAAAAGAAAAAAAAAAAAAAAAAEAAAABAAAAAP8A////AAAAAAAA/wAA/w=="
data2 = "AgEBBAEBAAABAAEDAgAAAAIDAQABAwAAAQEBAAEBAQAAAAAB"

data = base64.b64decode(data)
data2 = base64.b64decode(data2)
data = bytearray(data)
data2 = bytearray(data2)
data[0] = 66
data[1] = 77
data[2] = 109
data[3] = 0
data[9] = 0
data[47] = 0
data[46] = 4
data[51] = 0
data[10] = 74
data[11] = 0
data.insert(11,0)
data.insert(71,0)
data.insert(71,0)
data.insert(71,0)

with open('A10.bmp','wb') as file:
    file.write(data)
    file.write(data2)