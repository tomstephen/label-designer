import dearpygui.dearpygui as dpg
import socket
import os
from PIL import Image
import zpl

mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         
host = "10.0.1.3"
port = 9100

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


dpg.create_context()
dpg.create_viewport(title="Tom's Label Designer")
dpg.setup_dearpygui()

with dpg.window(tag="main window"):
    dpg.add_text("Enter your text to print, then press print!")
    dpg.add_input_text(label="Text to print", tag="str_input")
    dpg.add_button(label="Print", callback=print_callback)

dpg.show_viewport()

dpg.set_primary_window("main window", True)

dpg.start_dearpygui()
dpg.destroy_context()
mysocket.close () #closing connection
