import dearpygui.dearpygui as dpg
import socket
import os
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import zpl
import numpy as np
import datetime

mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         
host = "10.0.1.3"
port = 9100

myPrinter = zpl.TCPPrinter(host)
print(myPrinter.get_dpi())

def str_to_bytes(inp):
    return bytes(inp, 'utf-8')

def zpl_cmd(label):
    return str_to_bytes(label.dumpZPL())

def str_dpmm(num, label):
    return str(num * label.dpmm)

def add_box(label, x, y, width, height, thickness):
    label.code += "^FO " + str_dpmm(x, label) + ", " + str_dpmm(y, label) +" ^GB " + str_dpmm(width, label) + ", " + str_dpmm(height, label) + ", " + str_dpmm(thickness, label) + " ^FS"

print("connecting...")
mysocket.connect((host, port)) # connecting to host

def print_callback():
    print("printing the string " + dpg.get_value("str_input"))
    l = zpl.Label(30, 60)

    l.origin(l.width / 2, l.height / 2)
    l.write_text(dpg.get_value("str_input"), font = "B", char_height=5, char_width=2, orientation="N", justification = "L")
    l.endorigin()

    try:
        print("sending...")
        mysocket.send(bytes(l.dumpZPL(), 'utf-8'))    #using bytes
        print("closing...")
        print("Label Sent")
    except:
        print("Error with the connection")

def create_label_image(text, textsize):
    label = Image.new('RGBA', (240, 120), (255,255,255,255))
    draw = ImageDraw.Draw(label)
    font = ImageFont.truetype("fonts/Roboto.ttf", size = textsize)
    size_width, size_height = draw.textsize(text, font)
    draw.text(((240 - size_width) / 2, (120 - size_height) / 2), text, (0, 0, 0, 255), font=font)
    return label

class App:
    def __init__(self):
        self.num_labels = 0
    
    def new_label_row(self):
        self.num_labels += 1
        with dpg.table_row(parent = "table"):
            texture_tag = "texture_tag" + str(self.num_labels)

            blank_image = create_label_image("todo", 24)
            dpg_image = np.frombuffer(blank_image.tobytes(), dtype=np.uint8) / 255.0
            with dpg.texture_registry(show=False):
                dpg.add_dynamic_texture(width=240, height=120, default_value=dpg_image, tag=texture_tag)

            dpg.add_input_text(tag = "label_text" + str(self.num_labels))
            dpg.add_slider_int(tag = "text_size" + str(self.num_labels))
            dpg.add_image(texture_tag, tag="preview_image"+str(self.num_labels))

    def update_previews(self):
        for i in range(1, self.num_labels + 1):
            text = dpg.get_value("label_text" + str(i))
            text_size = dpg.get_value("text_size" + str(i))

            texture_tag = "texture_tag" + str(i)
            new_image = create_label_image(text, text_size)
            dpg_image = np.frombuffer(new_image.tobytes(), dtype=np.uint8) / 255.0
            dpg.set_value(texture_tag, dpg_image)
    
    def print_labels(self):
        for i in range(1, self.num_labels + 1):
            text = dpg.get_value("label_text" + str(i))
            text_size = dpg.get_value("text_size" + str(i))
            label_image = create_label_image(text, text_size)
            # label_image = label_image.resize((60, 30))

            l = zpl.Label(30, 60, dpmm=7)
            l.origin(0, 0)
            l.write_graphic(label_image, 100)
            l.endorigin()

            # print(l.dumpZPL())

            # l.preview()
            try:
                print("sending...")
                mysocket.send(bytes(l.dumpZPL(), 'utf-8'))    #using bytes
                print("closing...")
                print("Label Sent")
            except:
                print("Error with the connection")



dpg.create_context()
dpg.create_viewport(title="Tom's Label Designer")
dpg.setup_dearpygui()

with dpg.window(tag="main window"):
    dpg.add_text("Enter your text to print, then press print!")
    dpg.add_input_text(label="Text to print", tag="str_input")
    dpg.add_button(label="Print", callback=print_callback)

    with dpg.table(tag = "table", header_row=True, borders_outerH=True, borders_innerV=True):
        dpg.add_table_column(label="Text")
        dpg.add_table_column(label="Text Size")
        dpg.add_table_column(label="Preview")

        data = App()
        data.new_label_row()

    dpg.add_button(label="+ label", callback=data.new_label_row)
    dpg.add_button(label="Preview All", callback=data.update_previews)
    dpg.add_button(label="Print All", callback=data.print_labels)

dpg.show_viewport()

dpg.set_primary_window("main window", True)

dpg.start_dearpygui()
dpg.destroy_context()
mysocket.close () #closing connection
