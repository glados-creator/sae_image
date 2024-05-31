import os
import random
import json
pixel_size = 20
DEBUG = False
try:
    # python 2.X
    import Tkinter as tk
    import Tkinter.messagebox as tk_messagebox
    import Tkinter.filedialog as tk_filedialog
    import Tkinter.colorchooser as tk_colorchooser
    import Tkinter.dnd as tk_dnd
except Exception:
    try:
        # python 3.X
        import tkinter as tk
        import tkinter.messagebox as tk_messagebox
        import tkinter.filedialog as tk_filedialog
        import tkinter.colorchooser as tk_colorchooser
        import tkinter.dnd as tk_dnd
    except Exception as ec:
        print("[ERROR] : could not resolve tkinter default lib")
        print("'Tkinter' python 2.x")
        print("'tkinter' python 3.x")
        print("please fix at least one of them")
        raise ec


class BMPFile:
    __slots__ = ["FILE_DATA", "HEADER_DATA", "ICC_COLOR_PROFILE",
                 "color_format", "palette", "pixels",]

    FILE_HEADER_FIELDS = [
        ('identifier', 2),  # 'BM' in ASCII
        ('file_size', 4),
        ('reserved1', 2),
        ('reserved2', 2),
        ('pixel_data_offset', 4),
        ('header_size', 4),  # normaly in INFOHEADER BUT COMMON SO HERE
        # DO NOT FORGET TO DO OFFSET
    ]

    BITMAPCOREHEADER_FIELDS = [
        ('width', 2),
        ('height', 2),
        ('color_planes', 2),  # = 1
        ('bits_per_pixel', 2),  # = 8
    ]

    BITMAPINFOHEADER_FIELDS = [
        ('width', 4),
        ('height', 4),
        ('color_planes', 2),
        ('bits_per_pixel', 2),
        ('compression_method', 4),
        ('image_size', 4),
        ('horizontal_resolution', 4),
        ('vertical_resolution', 4),
        ('palette_colors', 4),
        ('important_colors', 4),
    ]

    BITMAPV2INFOHEADER_FIELDS = [
        ('width', 4),
        ('height', 4),
        ('color_planes', 2),
        ('bits_per_pixel', 2),
        ('compression_method', 4),
        ('image_size', 4),
        ('horizontal_resolution', 4),
        ('vertical_resolution', 4),
        ('palette_colors', 4),
        ('important_colors', 4),
        ('red_mask', 4),
        ('green_mask', 4),
        ('blue_mask', 4),
    ]

    BITMAPV3INFOHEADER_FIELDS = [
        ('width', 4),
        ('height', 4),
        ('color_planes', 2),
        ('bits_per_pixel', 2),
        ('compression_method', 4),
        ('image_size', 4),
        ('horizontal_resolution', 4),
        ('vertical_resolution', 4),
        ('palette_colors', 4),
        ('important_colors', 4),
        ('red_mask', 4),
        ('green_mask', 4),
        ('blue_mask', 4),
        ('alpha_mask', 4),
    ]

    BITMAPV4INFOHEADER_FIELDS = [
        ('width', 4),
        ('height', 4),
        ('color_planes', 2),
        ('bits_per_pixel', 2),
        ('compression_method', 4),
        ('image_size', 4),
        ('horizontal_resolution', 4),
        ('vertical_resolution', 4),
        ('palette_colors', 4),
        ('important_colors', 4),
        ('red_mask', 4),
        ('green_mask', 4),
        ('blue_mask', 4),
        ('alpha_mask', 4),
        ('cs_type', 4),
        ('endpoints', 36),
        ('gamma_red', 4),
        ('gamma_green', 4),
        ('gamma_blue', 4),
    ]

    BITMAPV5INFOHEADER_FIELDS = [
        ('width', 4),
        ('height', 4),
        ('color_planes', 2),
        ('bits_per_pixel', 2),
        ('compression_method', 4),
        ('image_size', 4),
        ('horizontal_resolution', 4),
        ('vertical_resolution', 4),
        ('palette_colors', 4),
        ('important_colors', 4),
        ('red_mask', 4),
        ('green_mask', 4),
        ('blue_mask', 4),
        ('alpha_mask', 4),
        ('cs_type', 4),
        ('endpoints', 36),
        ('gamma_red', 4),
        ('gamma_green', 4),
        ('gamma_blue', 4),
        ('intent', 4),
        ('profile_data', 4),
        ('profile_size', 4),
        ('reserved', 4),
    ]

    DIBSLIST = [BITMAPCOREHEADER_FIELDS, BITMAPINFOHEADER_FIELDS, BITMAPV2INFOHEADER_FIELDS,
                BITMAPV3INFOHEADER_FIELDS, BITMAPV4INFOHEADER_FIELDS, BITMAPV5INFOHEADER_FIELDS]

    BITMAPHEADERDICT = {sum([pix for _, pix in x])+4: x for x in DIBSLIST}

    def __init__(self):
        self.FILE_DATA: dict = dict.fromkeys(
            key for key, _ in BMPFile.FILE_HEADER_FIELDS)
        self.HEADER_DATA: dict = dict.fromkeys(
            key for key, _ in BMPFile.DIBSLIST[0])
        self.palette: list = None
        self.pixels: list = []
        self.color_format: list = []  # RGBAX (nb bits , pos)
        self.ICC_COLOR_PROFILE = None

    def get_header_ver(self):
        for header in BMPFile.DIBSLIST:
            if len(header) == len(list(self.HEADER_DATA.keys())):
                return header
        raise ValueError("header not found")
    
    def update(self):
        def check(field,val):
            if field in self.HEADER_DATA:
                if self.HEADER_DATA[field] != val:
                    print(f"WARNING : {field} {self.HEADER_DATA[field]} != {val}")

        check("color_planes",1)
        if self.HEADER_DATA["bits_per_pixel"] not in [1, 4, 8, 16, 24, 32]:
            print(f"WARNING : bits_per_pixel unusual : {self.HEADER_DATA['bits_per_pixel']}")
        check("reserved",0)

        if self.FILE_DATA["identifier"] != 19778:  # 'BM' in ASCII
            print(f"WARNING : identifier != 19778 , {self.FILE_DATA['identifier']}")
        if self.FILE_DATA["reserved1"] != 0:
            print(f"WARNING : reserved1 != 0 , {self.FILE_DATA['reserved1']}")
        if self.FILE_DATA["reserved2"] != 0:
            print(f"WARNING : reserved2 != 0 , {self.FILE_DATA['reserved2']}")
        if self.FILE_DATA["file_size"] != self.calculate_file_size():
            print(f"WARNING : file_size != calculate_file_size() , {self.FILE_DATA['file_size']} , {self.calculate_file_size()}")
        
        if self.palette is not None:
            check("palette_colors",len(bin(len(self.palette)-1))-2)
    
        check("horizontal_resolution", 2835)
        check("vertical_resolution", 2835)
        
        check("important_colors", 0)
        
        check("red_mask", 16711680)
        check("green_mask", 65280)
        check("blue_mask", 255)
        check("alpha_mask", 4278190080)
        
        check("cs_type", 544106839)
        check("endpoints", 0)
        
        check("gamma_red", 1)
        check("gamma_green", 1)
        check("gamma_blue", 1)
        
        check("intent", 0)
        check("profile_data", 0)
        check("profile_size", 0)
        check("reserved", 0)
        
    def change_header(self,form):
        print("changed header",sum([pix for _, pix in form])+4)
        print(form)
        HEADER_DATA = dict.fromkeys(key for key, _ in form)
        for key in HEADER_DATA.keys():
            if key in self.HEADER_DATA:
                HEADER_DATA[key] = self.HEADER_DATA[key]
            else:
                HEADER_DATA[key] = 0
        
        if "color_planes" in HEADER_DATA:
            HEADER_DATA["color_planes"] = 1
        if "horizontal_resolution" in HEADER_DATA:
            HEADER_DATA["horizontal_resolution"] = 2835
        if "vertical_resolution" in HEADER_DATA:
            HEADER_DATA["vertical_resolution"] = 2835
        if "palette_colors" in HEADER_DATA:
            if self.palette is not None:
                HEADER_DATA["palette_colors"] = len(bin(len(self.palette)-1))-2
        if "important_colors" in HEADER_DATA:
            HEADER_DATA["important_colors"] = 0

        # for nb_bit, off in self.color_format:
        #     value = 0
        #     for j in range(nb_bit):
        #         value |= ((pixel_data[off + j // 8] >> (j % 8)) & 1) << j
        if "red_mask" in HEADER_DATA:
            HEADER_DATA["red_mask"] = 16711680
            HEADER_DATA["green_mask"] = 65280
            HEADER_DATA["blue_mask"] = 255
            if len(self.color_format) == 4:
                HEADER_DATA["alpha_mask"] = 4278190080
        
        if "cs_type" in HEADER_DATA:
            HEADER_DATA["cs_type"] = 544106839
        if "endpoints" in HEADER_DATA:
            HEADER_DATA["endpoints"] = 0
        
        if "gamma_red" in HEADER_DATA:
            HEADER_DATA["gamma_red"] = 1
            HEADER_DATA["gamma_green"] = 1
            HEADER_DATA["gamma_blue"] = 1
        
        if "intent" in HEADER_DATA:
            HEADER_DATA["intent"] = 0
        if "profile_data" in HEADER_DATA:
            HEADER_DATA["profile_data"] = 0
            HEADER_DATA["profile_size"] = 0
        if "reserved" in HEADER_DATA:
            HEADER_DATA["reserved"] = 0
        
        self.HEADER_DATA = HEADER_DATA
        self.FILE_DATA["file_size"] = self.calculate_file_size()
        self.FILE_DATA["header_size"] = sum([pix for _, pix in form])+4

        self.update()
    
    @classmethod
    def setdefault(cls, width=4, height=None):
        self = cls()
        self.HEADER_DATA["width"] = width
        self.HEADER_DATA["height"] = width if height is None else height
        self.HEADER_DATA["color_planes"] = 1
        self.HEADER_DATA["bits_per_pixel"] = 32
        self.color_format = [(8,2),(8,1),(8,0),(8,3)] # RGBAX
        self.pixels = [
            [[random.randint(0, 255),0,0,0] for _ in range(width)] for _ in range(width if height is None else height)]
        self.FILE_DATA["identifier"] = 19778  # 'BM' in ASCII
        self.FILE_DATA["reserved1"] = 0
        self.FILE_DATA["reserved2"] = 0
        self.FILE_DATA['pixel_data_offset'] = 26
        self.FILE_DATA['header_size'] = sum(
            [pix for _, pix in BMPFile.BITMAPCOREHEADER_FIELDS]) + 4
        assert self.FILE_DATA['header_size'] == 12
        self.FILE_DATA["file_size"] = self.calculate_file_size()
        self.update()
        return self

    def calculate_file_size(self):
        bytes_per_pixel = self.HEADER_DATA["bits_per_pixel"] // 8
        # Calculate padding
        padding = ((self.HEADER_DATA["width"] * bytes_per_pixel) % 4) % 4
        if self.palette is None:
            palette_size = 0
            data_size = (self.HEADER_DATA["width"] * bytes_per_pixel + padding) * self.HEADER_DATA["height"]
        else:
            palette_size = self.HEADER_DATA["bits_per_pixel"] * self.HEADER_DATA["palette_colors"]
            padding = ((self.HEADER_DATA["width"] * self.HEADER_DATA["bits_per_pixel"]) % 4) % 4
            data_size = (self.HEADER_DATA["width"] * self.HEADER_DATA["bits_per_pixel"] + padding) * self.HEADER_DATA["height"]
        # BMP header size 14 - OFFSET common HEADER size
        file_header = sum([pix for _, pix in BMPFile.FILE_HEADER_FIELDS])-4
        header_size = sum([pix for _, pix in self.get_header_ver()])+4
        file_size = file_header + header_size + palette_size + data_size
        print(f"calculated file size {file_size} , file header {file_header} , header {header_size} , palette {palette_size} ,pixels {data_size}")
        return file_size

    def set_pixel(self, x, y, color):
        if 0 <= x < self.HEADER_DATA["width"] and 0 <= y < self.HEADER_DATA["height"]:
            self.pixels[y][x] = color
            return
        raise ValueError("Pixel coordinates out of bounds",x,y)

    def get_pixel(self, x, y):
        if 0 <= x < self.HEADER_DATA["width"] and 0 <= y < self.HEADER_DATA["height"]:
            return self.pixels[y][x]
        raise ValueError("Pixel coordinates out of bounds",x,y)
    
    def set_pal(self, x ,color):
        if self.palette is not None and 0 <= x < len(self.palette):
            self.palette[x] = color
            return
        raise ValueError("pal coordinates out of bounds / none",self.palette,x)

    def get_pal(self, x):
        if self.palette is not None and 0 <= x < len(self.palette):
            return self.palette[x]
        raise ValueError("pal coordinates out of bounds / none" , self.palette,x)
    
    def trans_palette(self):
        print("trans_palette")
        if self.palette is None:
            self.palette = []
            for i in range(len(self.pixels)):
                for j in range(len(self.pixels[0])):
                    color = self.get_pixel(i,j)
                    if color not in self.palette:
                        self.palette.append(color)
                    self.set_pixel(i,j,[self.palette.index(color)])
            self.HEADER_DATA["palette_colors"] = len(bin(len(self.palette)-1))-2
            self.HEADER_DATA["bits_per_pixel"] = len(bin(len(self.palette)-1))-2
        else:
            for i in range(len(self.pixels)):
                for j in range(len(self.pixels[0])):
                    color = self.get_pixel(i,j)
                    self.set_pixel(i,j,self.palette[color[0]])
            self.palette = None
    
    def change_alpha(self,enable : bool = False):
        if enable:
            # diable
            self.HEADER_DATA["bits_per_pixel"] = 24
            self.color_format = [(8,2),(8,1),(8,0)] # RGBAX
            # if self.palette is None:
            #     raise
            # else:
            #     pass
        else:
            self.HEADER_DATA["bits_per_pixel"] = 32
            self.color_format = [(8,2),(8,1),(8,0),(8,3)] # RGBAX
    
    def parse(self,filename="./image.bmp"):
        print()
        HEADER_DATA = {}
        FILE_DATA = {}
        pixels = []
        neg_col = False
        neg_row = False
        with open(filename, 'rb') as file:
            # File header
            for field, size in BMPFile.FILE_HEADER_FIELDS:
                print("reading FILE DATA",field,"size",size,"bytes")
                bit = file.read(size)
                FILE_DATA[field] = int.from_bytes(bit, byteorder='little')
                print(bit.hex(),FILE_DATA[field])
            
            if FILE_DATA["file_size"] != os.path.getsize(filename):
                print(f"WARNING : os file size is not header file size {FILE_DATA['file_size']} != {os.path.getsize(filename)} (os)")
            
            for field, size in BMPFile.BITMAPHEADERDICT[FILE_DATA["header_size"]]:
                print("reading HEADER DATA",field,"size",size,"bytes")
                bit = file.read(size)
                HEADER_DATA[field] = int.from_bytes(bit, byteorder='little')
                print(bit.hex(),HEADER_DATA[field])

            if HEADER_DATA["width"] > (2**16)-1:
                neg_col = True
                print("neg width",HEADER_DATA["width"])
                HEADER_DATA["width"] = -1*(HEADER_DATA["width"]-2**32)
                print("neg width",HEADER_DATA["width"])
            if HEADER_DATA["height"] > (2**16)-1:
                neg_row = True
                print("neg height",HEADER_DATA["height"])
                HEADER_DATA["height"] = -1*(HEADER_DATA["height"]-2**32)
                print("neg height",HEADER_DATA["height"])

            # parse color mask
            # NO
            # parse palette
            if HEADER_DATA["palette_colors"] != 0:
                self.palette = []
                for i in range(HEADER_DATA["palette_colors"]):
                    color = []
                    pixel_data = file.read(self.HEADER_DATA["bits_per_pixel"]//8)
                    # print(pixel_data)
                    for nb_bit, off in sorted(self.color_format,key=lambda x:x[1]):
                        value = 0
                        if off < self.HEADER_DATA["bits_per_pixel"]//8:
                            for j in range(nb_bit):
                                value |= ((pixel_data[off + j // 8] >> (j % 8)) & 1) << j
                        color.append(value)
                    self.palette.append(color)
                print("palette")
                print(self.palette)
            else:
                self.palette = None
            
            # parse pixels
            file.seek(FILE_DATA["pixel_data_offset"])
            if self.palette is not None:
                palette_size = HEADER_DATA["bits_per_pixel"] * HEADER_DATA["palette_colors"]
                self.HEADER_DATA = HEADER_DATA
                pixel_glob = file.read(FILE_DATA["file_size"]-(14+sum([pix for _, pix in self.get_header_ver()])+4+palette_size))
            for i in range(HEADER_DATA["height"]):
                row = []
                for j in range(HEADER_DATA["width"]):
                    # Read pixel data based on bit depth
                    color = []
                    if self.palette is None:
                        pixel_data = file.read(HEADER_DATA["bits_per_pixel"] // 8)
                        assert HEADER_DATA["bits_per_pixel"] == sum(nb_bit for nb_bit, _ in self.color_format), "{} != {}".format(HEADER_DATA["bits_per_pixel"], sum(nb_bit for nb_bit, _ in self.color_format))
                        for nb_bit, off in self.color_format:
                            value = 0
                            if off < HEADER_DATA["bits_per_pixel"]//8:
                                for j in range(nb_bit):
                                    value |= ((pixel_data[off + j // 8] >> (j % 8)) & 1) << j

                            color.append(value)
                    else:
                        byte_position = (i * HEADER_DATA["width"] + j) * HEADER_DATA["bits_per_pixel"] // 8
                        bit_position = (i * HEADER_DATA["width"] + j) * HEADER_DATA["bits_per_pixel"] % 8

                        value = (pixel_glob[byte_position] >> bit_position) & ((1 << HEADER_DATA["bits_per_pixel"]) - 1)
                        color.append(value)
                    row.append(color)
                    if neg_col:
                        row = row[::-1]
                pixels.append(row)
            if neg_row:
                pixels = pixels[::-1]
            print("color",color)
            # parse ICC data

        self.HEADER_DATA = HEADER_DATA
        self.FILE_DATA = FILE_DATA
        self.pixels = pixels
        self.update()
    
    def save(self, output_filename="./image.bmp"):
        def get_byte_size(struct,name):
            return next(size for field, size in struct if field == name)
        
        print()
        self.update()
        bits = bytearray()
        header_ver = self.get_header_ver()
        print("header selected",header_ver)
        self.FILE_DATA["header_size"] = sum(by for _,by in header_ver)+4
        print("header size",self.FILE_DATA["header_size"])
        self.FILE_DATA["file_size"] = self.calculate_file_size()
        if self.palette is not None:
            print("palette_colors",len(self.palette),len(bin(len(self.palette)-1))-2)
            self.HEADER_DATA["bits_per_pixel"] = len(bin(len(self.palette)-1))-2
            self.HEADER_DATA["palette_colors"] = len(bin(len(self.palette)-1))-2
        
        # Write BMP file header
        for field, size in self.FILE_HEADER_FIELDS:
            print("writing FILE DATA",field,"size",size,"bytes ; val :",self.FILE_DATA[field],self.FILE_DATA[field].to_bytes(size, byteorder='little').hex())
            bits.extend(self.FILE_DATA[field].to_bytes(size, byteorder='little'))
            # print("size",len(bits))
            
        for field, size in BMPFile.BITMAPHEADERDICT[self.FILE_DATA["header_size"]]:
            print("writing HEADER DATA",field,"size",size,"bytes ; val :",self.HEADER_DATA[field],self.HEADER_DATA[field].to_bytes(size, byteorder='little').hex())
            bits.extend(self.HEADER_DATA[field].to_bytes(size, byteorder='little'))
            # print("size",len(bits))
            
        print("write header size",len(bits),"done")
        # write palette
        if self.palette is not None:
            # x = sum(map(lambda x:x[0],BMPFile.color_format))
            if "red_mask" in self.HEADER_DATA:
                raise
            size = int(self.HEADER_DATA["bits_per_pixel"] / 3)
            print("pixel array chanel size",size,"total",self.HEADER_DATA["bits_per_pixel"])
            for color in self.palette:
                pix = bytearray(size)
                # assert size*8 == sum(nb_bit for nb_bit,_ in self.color_format) , "{} != {}".format(size*8,sum(nb_bit for nb_bit,_ in self.color_format))
                for i,(nb_bit, off) in enumerate(self.color_format):
                    bin_rep = bin(color[i])[2:].zfill(nb_bit)
                    for j in range(nb_bit):
                        # Set the corresponding bit in pix
                        if bin_rep[j] == '1':
                            pix[off+j // 8] |= (1 << (j % 8))
                        else:
                            pix[off+j // 8] &= ~(1 << (j % 8))
                bits.extend(pix)
                # do it properly Samir.... You re breaking the car
        # write pixels
        # pixel offset
        bits[10:14] = len(bits).to_bytes(get_byte_size(BMPFile.FILE_HEADER_FIELDS,"pixel_data_offset"), byteorder='little')
        print("pixel offset",get_byte_size(BMPFile.FILE_HEADER_FIELDS,"pixel_data_offset"),len(bits),len(bits).to_bytes(get_byte_size(BMPFile.FILE_HEADER_FIELDS,"pixel_data_offset"), byteorder='little').hex())

        size = int(self.HEADER_DATA["bits_per_pixel"]//8)
        print("bits per pixel ,",self.HEADER_DATA["bits_per_pixel"],", bytes",self.HEADER_DATA["bits_per_pixel"]/8,size,", per channel",size/3)
        for row in self.pixels:
            start = len(bits)
            for color in row:
                if self.palette is None:
                    pix = bytearray(size)
                    assert size*8 == sum(nb_bit for nb_bit,_ in self.color_format) , "{} != {}".format(size*8,sum(nb_bit for nb_bit,_ in self.color_format))
                    for i,(nb_bit, off) in enumerate(self.color_format):
                        bin_rep = bin(color[i])[2:].zfill(nb_bit)
                        for j in range(nb_bit):
                            # Set the corresponding bit in pix
                            if bin_rep[j] == '1':
                                pix[off+j // 8] |= (1 << (j % 8))
                            else:
                                pix[off+j // 8] &= ~(1 << (j % 8))
                    bits.extend(pix)
                    # RAISE do it properly Samir.... You re breaking the car
                    # bits.extend(color[0].to_bytes(size, byteorder='little'))
                    # bits.extend(color[1].to_bytes(size, byteorder='little'))
                    # bits.extend(color[2].to_bytes(size, byteorder='little'))
                    print(start,color,pix.hex())
                else:
                    bits.extend(color.to_bytes(self.HEADER_DATA["bits_per_pixel"],byteorder='little'))
            remainder = (len(bits) - start) % 4
            print("remainder",remainder)
            if remainder != 0:
                bits.extend(bytes(remainder))
        # write ICC data
        self.ICC_COLOR_PROFILE = None
        # NOPE

        # do not forget to have corret file  size
        # bits[2:6] = len(bits).to_bytes(get_byte_size(BMPFile.FILE_HEADER_FIELDS,"file_size"), byteorder='little')
        print("file size",len(bits),len(bits).to_bytes(get_byte_size(BMPFile.FILE_HEADER_FIELDS,"file_size"), byteorder='little').hex())
        print(bits[2:6].hex())

        with open(output_filename, 'wb') as file:
            file.write(bits)
        # print(bits.hex())


class gstate(object):
    l_widget = ("Button", "Checkbutton", "Entry", "Frame", "Label", "LabelFrame", "Listbox", "Menu", "Canvas",
                "Menubutton", "Message", "PanedWindow", "Radiobutton", "Scale", "Scrollbar", "Spinbox", "Text")

    def __init__(self, root, menu_main):
        """
        Replace default tk widget, basically tkinter.
        Button, Checkbutton, Entry, Frame, Label, LabelFrame, Menubutton, PanedWindow, Radiobutton, Scale, and Scrollbar.
        """

        self.root: any = root  # : tkinter.Tk()
        self.stack: list = [menu_main]
        self.colortheme = {
            'borderwidth': 2,                  # Border width
            'background': 'gray',              # Background color
            'foreground': 'black',             # Foreground color
            'highlightbackground': 'grey',     # Highlight background color
            'highlightcolor': '#FFD700',       # Golden highlight color
            'activebackground': 'gray',        # Active background color
            'activeforeground': 'black',       # Active foreground color
            'disabledbackground': 'gray',      # Disabled background color
            'disabledforeground': 'gray50',    # Disabled foreground color
            'selectcolor': '#FFD700',           # Selection color
            'selectbackground': 'gray',        # Selection background color
            'selectforeground': 'black'        # Selection foreground color
        }

        def _reset_stack():
            self.stack = [menu_main]
            self.dispatch()

        self.root.bind("<Escape>", lambda e: exit(0))
        self.root.bind("<n>", lambda e: _reset_stack())

        def _valide(widget):
            valide_kwarg = widget(self.root).keys()

            def _inner(*args, **kwargs):
                ret = {}
                if not args:
                    ret["master"] = self.root
                for k in valide_kwarg:
                    if k in kwargs:
                        ret[k] = kwargs[k]
                    elif k in self.colortheme:
                        ret[k] = self.colortheme[k]
                return widget(*args, **ret)
            return lambda *args, **kwargs: _inner(*args, **kwargs)

        for widget in gstate.l_widget:
            setattr(self, widget,  _valide(getattr(tk, widget)))

    def dispatch(self):
        self.stack[-1](self)


###########################################################################

def handy_clear(widget: tk.Widget):
    for x in list(widget.children):
        widget.children[x].destroy()


def handy_backbtn(state, frame):
    def _com(state):
        state.stack.pop()
        state.dispatch()
    return state.Button(frame, text="précédent", command=lambda *args: _com(state))


def handy_config(frame, row: int, column = None):
    if not isinstance(row, int):
        raise ValueError("not correct type")
    if column is None:
        column = row
    if not isinstance(column, int):
        raise ValueError("not correct type")
    for i in range(column):
        frame.columnconfigure(i, weight=row-1)
    for i in range(row):
        frame.rowconfigure(i, weight=column-1)


def handy_show_grid(master):
    if not DEBUG:
        return
    if not isinstance(master, tk.Widget):
        raise ValueError("not correct type")
    rows = master.grid_size()[1]
    cols = master.grid_size()[0]
    print("[INFO] : grid size", rows, cols)
    for i in range(rows):
        for j in range(cols):
            frame = tk.Frame(master, bd=10, relief=tk.SOLID)
            frame.grid(row=i, column=j)
            tk.Label(frame, text="Row {}, Col {}".format(i, j)).pack()


def handy_grid(master=None, repeatewidget_func = None, rows: int = 3, cols = None, *args, **kwargs):
    if repeatewidget_func is None:
        raise ValueError(
            "repeatewidget_func must be provided.")

    if cols is None:
        cols = rows

    grid = []
    for i in range(rows):
        grid.append([])
        for j in range(cols):
            # Create a new widget using the repeatewidget function and the given arguments
            widget = repeatewidget_func(master, i, j, * args, **kwargs)
            widget.grid(row=i, column=j)
            grid[-1].append(widget)
    handy_show_grid(master)
    return grid

###########################################################################


def menu_demo(state):
    """
    une simple démo pour démontrer l'apparence et les différente capabilité
    """
    handy_clear(state.root)
    gride = state.Frame(state.root)
    gride.pack()
    # custome backbutton

    def _com(state):
        state.stack.pop()
        state.root.config(menu="")
        state.dispatch()
    state.Button(gride, text="return",
                 command=lambda *args: _com(state)).grid(row=0, column=0)

    f = state.Frame(gride)
    state.Button(f, text="Button").pack()
    state.Checkbutton(f, text="Checkbutton").pack()

    tmpframe = state.Frame(f, relief=tk.RIDGE)
    state.Label(tmpframe, text="Entry RIDGE", relief=tk.RIDGE).pack()
    state.Entry(tmpframe, relief=tk.RIDGE).pack()
    tmpframe.pack()

    x = state.LabelFrame(f, text="LabelFrame GROOVE", relief=tk.GROOVE)
    x.pack()
    state.Label(x, text="Label").pack()

    menubar = state.Menu(f)
    menu = state.Menu(menubar)
    menu.add_command(label="test")
    menu.add_command(label="exemple")
    menu.add_separator()
    menu.add_command(label="idk")
    menubar.add_cascade(label="Menu click me", menu=menu)
    # menu.add_command(label = "Menubutton")
    state.root.config(menu=menubar)

    x = state.PanedWindow(f, relief=tk.SUNKEN)
    x.pack()
    l = state.Label(x, text="PanedWindow 1 ->")
    x.add(l)
    l = state.Label(x, text="<- PanedWindow 2 SUNKEN")
    x.add(l)

    tmp = state.Frame(f, relief=tk.RAISED)
    var = tk.IntVar(gride, value=0)
    state.Radiobutton(tmp, text="Radiobutton1", variable=var,
                      value=0, relief=tk.RAISED).pack()
    state.Radiobutton(tmp, text="Radiobutton2 RAISED",
                      variable=var, value=1, relief=tk.RAISED).pack()
    tmp.pack()

    state.Scale(f, label="Scale").pack(side="left")

    tk.Canvas(f, bg="red", height=100).pack()

    scroll = state.Scrollbar(f)
    scroll.pack(side="right", fill="y")
    x = state.Listbox(f, yscrollcommand=scroll.set)
    for i in range(50):
        x.insert(1, "Listbox {}".format(i))
    x.pack(side="bottom")
    scroll.configure(command=x.yview)

    state.Message(f, text="Message1\nMessage2\nMessage3").pack(side="bottom")
    # state.PanedWindow(f).pack()
    state.Spinbox(f, from_=0, to=10).pack()

    f.grid(column=1, row=0, rowspan=3, columnspan=1)


def menu_option(state):
    """
    le menu de base pour les option renvoie a API.option
    """
    handy_clear(state.root)
    gride = state.Frame(state.root)
    gride.pack(fill=tk.BOTH, expand=True)
    handy_config(gride, 4, 4)
    handy_backbtn(state, gride).grid(row=0, column=0)

    def _com_load(state, strvar):
        state.colortheme = json.load(open(strvar.get(), "r"))
        state.dispatch()

    def _com_pick_load(strvar):
        strvar.set(tk_filedialog.askopenfilename(filetypes=(
            ("Json File", "*.json"), ("All Files", "*.*")), title="Choose a file."))
        state.dispatch()

    # path Entry pick load

    f = state.Frame(gride)
    state.Label(f, text="chemin charger").pack(side="left")
    load_var = tk.StringVar()
    load_var.set("default.json")
    state.Entry(f, textvariable=load_var).pack()
    state.Button(f, text="choisir un fichier",
                 command=lambda *args: _com_pick_load(load_var)).pack()
    state.Button(f, text="charger", command=lambda *args: _com_load(state,
                 load_var)).pack(side="right")
    f.grid(row=0, column=1)

    def _com_save(state, strvar):
        json.dump(state.colortheme, open(strvar.get(), "w"))

    def _com_pick_save(strvar):
        strvar.set(tk_filedialog.asksaveasfilename(
            confirmoverwrite=True, defaultextension=".json"))

    # save path Entry pick save

    f = state.Frame(gride)
    state.Label(f, text="chemin sauvegarder").pack(side="left")
    save_var = tk.StringVar()
    save_var.set("default.json")
    state.Entry(f, textvariable=save_var).pack()
    state.Button(f, text="choisir un fichier",
                 command=lambda *args: _com_pick_save(save_var)).pack()
    state.Button(f, text="sauvegarder", command=lambda *args: _com_save(state,
                 save_var)).pack(side="right")
    f.grid(row=1, column=1)

    def _com_add_dispatch(state):
        state.stack.append(menu_demo)
        state.dispatch()

    state.Button(gride, text="demo",
                 command=lambda *args: _com_add_dispatch(state)).grid(row=2, column=1)

    def selector(state, master, name):
        def _update_color(value, name):
            state.colortheme[name] = value
            state.dispatch()

        f0 = state.Frame(master)
        state.Label(f0, text=name).pack(side="left")
        scale_var = tk.IntVar()
        scale_var.set(state.colortheme[name])
        scale = state.Scale(f0, from_=0, to=5,
                            variable=scale_var, orient="horizontal")
        scale.pack(side="left")
        scale.bind("<ButtonRelease>", lambda event: _update_color(
            scale_var.get(), name))
        f0.pack()

    def colorchooser(state, master, name):
        def _inner(state, name):
            chooser = tk_colorchooser.Chooser()
            x = chooser.show()
            if x is None:
                return

            state.colortheme[name] = x[1]
            state.dispatch()

        f0 = state.Frame(master)
        state.Label(f0, text=name).pack(side="left")
        state.Button(f0, text="choisir",
                     command=lambda *args: _inner(state, name)).pack()
        state.Canvas(f0, width=20, height=20,
                     bg=state.colortheme[name]).pack(side="right")
        f0.pack()

    f = state.Frame(gride)
    f1 = state.Frame(f)
    selector(state, f1, "borderwidth")
    colorchooser(state, f1, "background")
    colorchooser(state, f1, "foreground")
    colorchooser(state, f1, "highlightbackground")
    colorchooser(state, f1, "highlightcolor")
    colorchooser(state, f1, "activebackground")
    f2 = state.Frame(f)
    colorchooser(state, f2, "activeforeground")
    colorchooser(state, f2, "disabledbackground")
    colorchooser(state, f2, "disabledforeground")
    colorchooser(state, f2, "selectcolor")
    colorchooser(state, f2, "selectbackground")
    colorchooser(state, f2, "selectforeground")

    f1.pack(side="left")
    f2.pack(side="right")
    f.grid(row=1, column=0)


def menu_edit(state):
    handy_clear(state.root)
    gride = state.Frame(state.root)
    gride.pack(fill=tk.BOTH, expand=True)
    handy_config(gride, 2)
    handy_backbtn(state, gride).grid(row=0, column=0)

    # default bmp default is 4*4
    image = BMPFile.setdefault()

    options = state.Frame(gride)
    options.grid(row=1, column=1)

    def update_color():
        print("color mode changed")
        _com_draw()
        raise

    def update_alpha():
        print("alpha changed")
        image.change_alpha(not alpha_var.get())
        print(image.color_format)
    
    def _com_charger():
        image.parse()
        _com_draw()
    
    def _com_trans_palette():
        image.trans_palette()
        _com_draw()
    
    def rotate():
        image.pixels = [list(row[::-1]) for row in zip(*image.pixels)]
        _com_draw()
    
    def symetric_w():
        ret = []
        for i in range(len(image.pixels)):
            row = []
            for j in range(len(image.pixels[0])):
                row.append(image.pixels[i][3-j])
            ret.append(row)
        image.pixels = ret
        _com_draw()
    
    def symetric_h():
        ret = []
        for i in range(len(image.pixels)):
            row = []
            for j in range(len(image.pixels[0])):
                row.append(image.pixels[3-i][j])
            ret.append(row)
        image.pixels = ret
        _com_draw()

    bool_var = tk.BooleanVar(state.root, value=False)
    alpha_var = tk.BooleanVar(state.root, value=False)
    header_ver_var = tk.IntVar(state.root,value=12)
    state.Checkbutton(options, text="palette mode",
                      variable=bool_var, command=update_color).pack()
    state.Checkbutton(options, text="alpha chanel",
                      variable=alpha_var, command=update_alpha).pack()
    state.Button(options,text="sauvegarder",command=lambda *e:image.save()).pack()
    state.Button(options,text="charger",command=lambda *e:_com_charger()).pack()
    state.Button(options,text="trans palette",command=lambda *e:_com_trans_palette()).pack()
    state.Button(options,text="rotate",command=lambda *e:rotate()).pack()
    state.Button(options,text="symetric_w",command=lambda *e:symetric_w()).pack()
    state.Button(options,text="symetric_h",command=lambda *e:symetric_h()).pack()
    state.Label(options,text="header size").pack()
    header_master = state.Frame(options)
    header_master.pack()
    for x in BMPFile.DIBSLIST:
        val = sum([pix for _, pix in x])+4
        def make_lam(form):
            def _inner(*e):
                print(form)
                image.change_header(form)
                _com_draw()
            return _inner
        state.Radiobutton(header_master,text=str(val),value=val,variable=header_ver_var,command=make_lam(x)).pack()


    pixarry = state.Frame(gride)
    pixarry.grid(row=1, column=0)

    pallette = state.Frame(gride)
    pallette.grid(row=0, column=1)

    def create_pixarry(row, col):
        def _com_click(widget, i, j):
            def _inner():
                print("pix", i, j, "clicked",bool_var.get())
                if not bool_var.get():
                    p = image.get_pixel(i, j)
                    print("origin",p)
                    chooser = tk_colorchooser.Chooser(initialcolor="#{:02x}{:02x}{:02x}".format(*p))
                    color = chooser.show()
                    color = list(color[0])
                    print("now",color)
                    if color is not None:
                        image.set_pixel(i, j,color)
                _com_draw()
            widget.bind("<Button-1>", lambda *e:_inner())
            
        def _com_create_pix(master, i, j, * args, **kwargs):
            i, j = j, col-i-1
            c = state.Canvas(master, width=pixel_size, height=pixel_size)
            c.bind("<ButtonPress>", lambda *e: _com_click(c, i, j))
            c.configure(scrollregion=(0, 0, pixel_size, pixel_size))
            w = pixel_size
            h = pixel_size
            p = image.get_pixel(i, j)
            if image.palette is not None:
                # print("p",p)
                # print(image.pixels)
                p = image.palette[p[0]]
            c.create_rectangle(0, 0, w, h, fill="#{:02x}{:02x}{:02x}".format(*p))
            return c

        handy_grid(pixarry, _com_create_pix, rows=row, cols=col)

    def create_pallete(nb):
        squarre = len(bin(len(image.palette))[2:])
        print("squarre",squarre,len(image.palette))
        # state.Spinbox() # set new nb of pallete

        def _com_click(widget, i, j):
            def _inner():
                print("pix", i, j, "clicked")
                _com_draw()
            widget.bind("<Button-1>", lambda *e:_inner())

        def _com_create_pix(master, i, j, * args, **kwargs):
            i , j = j ,i
            f = state.Frame(master,width=pixel_size*2, height=pixel_size*2)
            c = state.Canvas(f, width=pixel_size, height=pixel_size)
            c.configure(scrollregion=(0, 0, pixel_size, pixel_size))
            c.bind("<ButtonPress>", lambda *e: _com_click(c, i, j))
            c.pack()
            w = pixel_size
            h = pixel_size
            r = 0
            g = 0
            b = 0
            if squarre*j+i < len(image.palette):
                p = image.get_pal(squarre*j+i)
                r = p[image.color_format[0][1]]
                g = p[image.color_format[1][1]]
                b = p[image.color_format[2][1]]
            print(int((r*8) / image.color_format[0][0]),
                  int((g*8) / image.color_format[1][0]),
                  int((b*8) / image.color_format[2][0]), "#{:02x}{:02x}{:02x}".format(int((r*8) / image.color_format[0][0]),
                                                                                      int((
                                                                                          g*8) / image.color_format[1][0]),
                                                                                      int((b*8) / image.color_format[2][0])))
            c.create_rectangle(0, 0, w, h, fill="#{:02x}{:02x}{:02x}".format(int((r*8) / image.color_format[0][0]),
                                                                             int((
                                                                                 g*8) / image.color_format[1][0]),
                                                                             int((b*8) / image.color_format[2][0])))
            return f
        
        handy_grid(pallette, _com_create_pix, rows=squarre)
    
    def _com_draw():
        handy_clear(pallette)
        handy_clear(pixarry)
        if image.palette is not None:
            create_pallete(len(image.palette))
        create_pixarry(image.HEADER_DATA["width"], image.HEADER_DATA["height"])
    
    _com_draw()


def menu_main(state):
    handy_clear(state.root)

    def _cm_menu_option():
        state.stack.append(menu_option)
        state.dispatch()

    def _cm_menu_demo():
        state.stack.append(menu_demo)
        state.dispatch()

    def _cm_menu_edit():
        state.stack.append(menu_edit)
        state.dispatch()

    top = state.Frame(state.root)
    state.Button(top, command=_cm_menu_option, text="options").pack()
    state.Button(top, command=_cm_menu_demo, text="demo").pack()
    state.Button(top, command=_cm_menu_edit, text="edit").pack()

    top.pack(fill=tk.BOTH, expand=True)


def main():
    root = gstate(tk.Tk(), menu_main)
    root.root.update()
    menu_main(root)
    root.root.mainloop()


if __name__ == "__main__":
    main()
else:
    print("WARNING : sae image graphic.py is imported")
