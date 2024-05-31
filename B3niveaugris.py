from PIL import Image

def convertir_gris():
    image = Image.open("image.bmp")
    image_niveaux_de_gris = image.convert("L")
    image_niveaux_de_gris.save("B3.bmp")

# convertir_gris()

def convertir_noire():
    image = Image.open("image.bmp")
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            r, g, b = image.getpixel((x, y))
            if (r*r+g*g+b*b) > 255*255*3/2:
                image.putpixel((x, y), (255, 255, 255))
            else:
                image.putpixel((x, y), (0, 0, 0))
    image.save("B4.bmp")

# convertir_noire()

def cacher_logo():
    hall = Image.open("B2_original.bmp")
    logo = Image.open("B4.bmp").convert("L")
    logo = logo.resize(hall.size)
    for x in range(hall.width):
        for y in range(hall.height):
            val = hall.getpixel((x, y))[0]
            hall.putpixel((x, y), (val - (val*2), *hall.getpixel((x, y))[1:]))
    hall.save("B5_cacher.bmp")

cacher_logo()
def extraire_logo():
    image_stegano = Image.open("B5_cacher.bmp")
    logo = Image.new("L", image_stegano.size)
    for x in range(image_stegano.width):
        for y in range(image_stegano.height):
            logo.putpixel((x, y), ((image_stegano.getpixel((x, y))[0])% 2) * 255)
    logo.save("B5_clear.bmp")

extraire_logo()