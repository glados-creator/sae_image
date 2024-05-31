import graphics

f = graphics.BMPFile.setdefault()
f.color_format = [(8,2),(8,1),(8,0)]
f.parse()
f.save()
f.parse()

def symetric_w():
    ret = []
    for i in range(len(f.pixels)):
        row = []
        for j in range(len(f.pixels[0])):
            row.append(f.pixels[i][3-j])
        ret.append(row)
    f.pixels = ret
    
def symetric_h():
    ret = []
    for i in range(len(f.pixels)):
        row = []
        for j in range(len(f.pixels[0])):
            row.append(f.pixels[3-i][j])
        ret.append(row)
    f.pixels = ret

# BROKE :(
def trans_gris():
    ret = []
    for i in range(len(f.pixels)):
        row = []
        for j in range(len(f.pixels[0])):
            row.append([int(sum(f.pixels[i][j])/3)])
        ret.append(row)
    f.pixels = ret
    f.color_format = [(24,0)]

def trans_noire():
    ret = []
    for i in range(len(f.pixels)):
        row = []
        for j in range(len(f.pixels[0])):
            # (R*R+V*V+B*B)>255*255*3/2
            R , V, B = f.pixels[i][j]
            row.append([int((R*R+V*V+B*B)>255*255*3/2)])
        ret.append(row)
    f.pixels = ret
    f.color_format = [(24,0)]


# trans_gris()
trans_noire()
f.save()
