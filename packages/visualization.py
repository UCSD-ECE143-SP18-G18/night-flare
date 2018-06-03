import numpy as np
import matplotlib as matplot
import matplotlib.pyplot as plt
from ipywidgets import Button, VBox, HBox, IntSlider
from IPython.display import display
from PIL import Image
import getimage
import conversion
import matplotlib.animation as animation
import datetime

class StaticPlot:
    def __init__(
            self,
            tileMatrix=5,
            tileCol=6,
            tileRow=5,
            date="2017-10-31"):
        self.fig = None
        self.ax = None
        self.ax_im = None

        self.tileMatrix = tileMatrix
        self.tileCol = tileCol
        self.tileRow =  tileRow
        self.date = date

        self.slider = None

    def subplot(self):
        self.fig, self.ax = plt.subplots()
        self.create_imshow()
        self.create_buttons()
        self.create_slider()
        self.render()

    def create_imshow(self):
        extent = (
            self.top_left[1],
            self.bot_right[1],
            self.top_left[0],
            self.bot_right[0]
        )

        self.ax_im = self.ax.imshow(np.zeros((512, 512)), extent=extent)

    def create_buttons(self):
        # Create buttons
        button_left  = Button(description='Left')
        button_right = Button(description='Right')
        button_up    = Button(description='Up')
        button_down  = Button(description='Down')

        # Register callbacks
        button_left .on_click(self.left_cb)
        button_right.on_click(self.right_cb)
        button_up   .on_click(self.up_cb)
        button_down .on_click(self.down_cb)

        # Layout buttons
        left_right = HBox([button_left, button_right])
        up_down = VBox([button_up, button_down])
        all_buttons = VBox([left_right, up_down])
        display(all_buttons)

    def create_slider(self):
        # Create a slider
        self.slider = IntSlider(
            value=5,
            min=1,
            max=7,
            step=1,
            description='Zoom in',
            readout=True,
            readout_format='d'
        )

        # Register callback
        self.slider.observe(self.slider_cb, names="value")

        # Show the slider
        display(self.slider)

    def render(self):
        img_array = getimage.get_image(
            tileMatrix = self.tileMatrix,
            tileCol = self.tileCol,
            tileRow = self.tileRow,
            date = self.date
        )

        img = Image.fromarray(img_array)
        self.ax_im.set_data(img)

        self.update_ticks()
        plt.draw()

    @property
    def top_left(self):
        return conversion.get_coordinates(
            tileMatrix = self.tileMatrix,
            tileCol = self.tileCol,
            tileRow = self.tileRow
        )

    @property
    def bot_right(self):
        return conversion.get_coordinates(
            tileMatrix = self.tileMatrix,
            tileCol = self.tileCol + 1,
            tileRow = self.tileRow + 1
        )

    def update_ticks(self):
        yticks = np.linspace(self.top_left[0], self.bot_right[0], 10)
        xticks = np.arange(self.top_left[1], self.bot_right[1],
            (self.bot_right[1] - self.top_left[1]) / 4.5)

        self.ax.set_yticklabels(yticks)
        self.ax.set_xticklabels(xticks)

    def left_cb(self, event=None):
        self.tileCol -= 1
        self.render()

    def right_cb(self, event=None):
        self.tileCol += 1
        self.render()

    def up_cb(self, event=None):
        self.tileRow -= 1
        self.render()

    def down_cb(self, event=None):
        self.tileRow += 1
        self.render()

    def slider_cb(self, event):
        center_latitude = (self.top_left[0] + self.bot_right[0]) / 2.0
        center_longitude = (self.top_left[1] + self.bot_right[1]) / 2.0

        self.tileMatrix = event["new"]
        self.tileRow, self.tileCol = conversion.get_tile_info(
            center_latitude,
            center_longitude,
            self.tileMatrix
        )

        self.render()

class AnimatedPlot:
    pass
