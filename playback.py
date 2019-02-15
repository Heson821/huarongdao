# Playback a solution in a GUI

from board import Board
import numpy as np
import cv2
import sys
import random
import math
import Tkinter as tk
from PIL import Image, ImageTk


def rgb_to_hex(rgb):
    r,g,b = rgb
    return '#%02x%02x%02x' % (int(r), int(g), int(b))

def hex_to_rgb(hx):
    """hx is a string, begins with #. ASSUME len(hx)=7."""
    if len(hx) != 7:
        raise ValueError("Hex must be #------")
    hx = hx[1:]  # omit the '#'
    r = int('0x'+hx[:2], 16)
    g = int('0x'+hx[2:4], 16)
    b = int('0x'+hx[4:6], 16)
    return (r,g,b)

def inverse_color_rgb(rgb):
    r,g,b = rgb
    return (255-r, 255-g, 255-b)

def inverse_color_hex(hx):
    """hx is a string, begins with #. ASSUME len(hx)=7."""
    return inverse_color_rgb(hex_to_rgb(hx))

def random_unique_color(colors, ctype=1):
    """
    ctype=1: completely random
    ctype=2: red random
    ctype=3: blue random
    ctype=4: green random
    ctype=5: yellow random
    """
    if ctype == 1:
        color = "#%06x" % random.randint(0x444444, 0x999999)
        while color in colors:
            color = "#%06x" % random.randint(0x444444, 0x999999)
    elif ctype == 2:
        color = "#%02x0000" % random.randint(0xAA, 0xFF)
        while color in colors:
            color = "#%02x0000" % random.randint(0xAA, 0xFF)
    elif ctype == 4:  # green
        color = "#00%02x00" % random.randint(0xAA, 0xFF)
        while color in colors:
            color = "#00%02x00" % random.randint(0xAA, 0xFF)
    elif ctype == 3:  # blue
        color = "#0000%02x" % random.randint(0xAA, 0xFF)
        while color in colors:
            color = "#0000%02x" % random.randint(0xAA, 0xFF)
    elif ctype == 5:  # yellow
        h = random.randint(0xAA, 0xFF)
        color = "#%02x%02x00" % (h, h)
        while color in colors:
            h = random.randint(0xAA, 0xFF)
            color = "#%02x%02x00" % (h, h)
    else:
        raise ValueError("Unrecognized color type %s" % (str(ctype)))
    return color


class TkGui(object):

    def __init__(self):
        self._root = None
        self._canvas = None
        self._images = {}  # maps name to [np.array, int]
        self._last_10_keys = []
        self._shapes = {}
        self._key_cb = {}
    
    def init(self):
        self._root = tk.Tk()
        self._width = 0
        self._height = 0
        self._canvas = tk.Canvas(self._root, width=self._width,
                                 height=self._height)
        self._canvas.config(bg='black')
        # pack the canvas into a frame/form
        self._canvas.pack(fill=tk.BOTH)
        self._root.bind("<Key>", self._key_pressed)

    @property
    def root(self):
        return root
    
    def show_image(self, name, img, loc=(0,0), anchor='nw',
                   scale=1, background=False, interpolation=cv2.INTER_LINEAR):
        """
        Given an image `img` as np.array (RGB), display the image on Tk window.
        If name already exists, will override the old one. Returns the size of
        the drawn image.
        """
        if name in self._images:
            self._canvas.delete(self._images[name][0])
        self._images[name] = [img, None, -1]  # image (original size), img_tk (shown), item_id
        img = cv2.resize(img, (int(round(img.shape[1]*scale)),
                               int(round(img.shape[0]*scale))), interpolation=interpolation)
        self._images[name][1] = ImageTk.PhotoImage(image=Image.fromarray(img))
        self._images[name][2] = self._canvas.create_image(loc[0], loc[1],
                                                          anchor=anchor, image=self._images[name][1])
        if background:
            self._width = img.shape[1]
            self._height = img.shape[0]
            self._canvas.config(width=self._width,
                                height=self._height)
        return self._images[name][1].width(), self._images[name][1].height()

    def remove_image(self, name):
        if name not in self._images:
            raise ValueError("Image named %s does not exist!" % name)
        self._canvas.delete(self._images[name][2])
        del self._images[name]

    def spin(self):
        try:
            if self._root:
                self._root.mainloop()
            else:
                raise ValueError("tk root does not exist. Did you init GUI?")
        except KeyboardInterrupt as ex:
            print("Terminating tk...")
            raise ex

    def last_n_keys(self, n=1):
        """Return a list of n keys that were most recently pressed. Most-recent first."""
        if n <= 0 or n > len(self._last_10_keys):
            print("Do not know key! (got: %d; max_length: %d)"
                  % (n, len(self._last_10_keys)))
            return None
        last_n = list(reversed(self._last_10_keys[-n:]))
        if n == 1:
            return last_n[0]
        else:
            return last_n
    
    def _key_pressed(self, event):
        if len(self._last_10_keys) == 10:
            self._last_10_keys.pop(0)
        print("Pressed %s" % repr(event.char))
        self._last_10_keys.append(event.char)
        print(str(self._last_10_keys))

    def register_key_press_event(self, event_name, key, callback):
        """Generic function to register callback when pressed key"""
        if key in self._key_cb:
            raise ValueError("Key %s is already bound to another event." % key)
        self._key_cb[key] = event_name
        self._root.bind("<%s>" % key, callback)
#--- End TkGui ---#


class HrdPlaybackGui(TkGui):
    """Gui to playback Huarongdao solution"""

    def __init__(self, solution_path, height=500):
        """
        Reads solution file from path and enable arrow key control to step through steps.
        """
        
        super(HrdPlaybackGui, self).__init__()
        self._height = height
        self._trace = self._read_file(solution_path)
        # Generate a sequence of images, each for one step in the trace.
        self._step_images = self._generate_images(self._trace)
        self._showing_index = 0

    def _read_file(self, solution_path):
        """
        The file is formatted as:

        ========== Solution ===========
        -------
        Step k
        -------
        xxxxxxx
        xboardx
        xxxxxxx
        [xyz-A]
        """
        trace = []
        k = 0  # step count
        reading_board = False
        current_board = []
        with open(solution_path) as f:
            lines = f.readlines()
            for i in range(len(lines)):
                line = lines[i].rstrip()
                if line.startswith("===="):
                    continue                
                if not reading_board:
                    if not (line.startswith("Step") and line.endswith(str(k))):
                        continue
                    else:
                        reading_board = True
                else:
                    if line.startswith("---"):
                        continue
                    # line is a row of an array or an action.
                    if line.startswith("[") or len(line) is 0:
                        reading_board = False
                        trace.append(np.array(current_board))
                        current_board = []
                        k += 1
                        continue # We don't care about actions for now.
                    else:
                        symmap = {str(Board.symbols[i]):i for i in range(len(Board.symbols))}
                        vals = []
                        for v in line:
                            vals.append(symmap[v])
                        current_board.append(vals)
                    
        return trace


    def _generate_images(self, trace):
        """An image is a numpy array (RGB). Each board in the trace is a numpy array
        of integers. Each integer should map to a color. There should be grid lines
        for easier visualization"""
        images = []
        colors = []
        colors_by_shape = {}
        for board in trace:
            width = int(round((float(board.shape[1]) / board.shape[0]) * self._height))
            cellsize = width / board.shape[1]  # cell size
            img = np.zeros((self._height, width, 3), dtype=np.uint8)

            tiles = {}  # map from integer rep. of the tile to a shape
            for y in range(board.shape[0]):
                for x in range(board.shape[1]):
                    cell = board[y,x]
                    if cell not in tiles:
                        tiles[cell] = (x, y, 1, 1)  # x, y, w, h
                    else:
                        cur_x, cur_y, cur_w, cur_h = tiles[cell]
                        if x >= cur_x + cur_w:
                            cur_w = (x-cur_x) + 1
                        if y >= cur_y + cur_h:
                            cur_h = (y-cur_y) + 1
                        tiles[cell] = (cur_x, cur_y, cur_w, cur_h)

            # Colors
            if len(colors_by_shape) == 0:
                for tid in tiles:
                    shape = (tiles[tid][2], tiles[tid][3])
                    if shape not in colors_by_shape:
                        colors_by_shape[shape] = hex_to_rgb(random_unique_color(colors))
                        colors.append(colors_by_shape[shape])

            for tid in tiles:
                x, y, w, h = tiles[tid]
                shape = (w,h)
                empty = board[y,x] == 0
                x, y, w, h = x*cellsize, y*cellsize, w*cellsize, h*cellsize
                # Draw a filled rectangle without color
                if not empty:
                    cv2.rectangle(img, (x, y), (x+w, y+h), colors_by_shape[shape],-1)
                else:
                    cv2.rectangle(img, (x, y), (x+w, y+h), [0,0,0], -1) #, 8)-
                # Draw a boundary
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 0), 2, 8)
                
            images.append(img)
        return images

    def _display_image(self):
        self.show_image("board", self._step_images[self._showing_index], background=True)

    def _next_step(self, event):
        if self._showing_index < len(self._step_images) - 1:
            self._showing_index += 1
        else:
            self._showing_index = 0
        self._display_image()

            
    def _prev_step(self, event):
        if self._showing_index > 0:
            self._showing_index -= 1
        else:
            self._showing_index = len(self._step_images) - 1
        self._display_image()
        

    def init(self):
        super(HrdPlaybackGui, self).init()
        self._display_image()
        self.register_key_press_event("next_step", "Right",
                                      self._next_step)

        self.register_key_press_event("prev_step", "Left",
                                      self._prev_step)


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Usage: playback.py <Path to solution file>")
        sys.exit(1)
    solution_path = sys.argv[1]
    gui = HrdPlaybackGui(solution_path)
    gui.init()
    gui.spin()
            
