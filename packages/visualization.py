"""Summary
"""
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

    """Plot Class to build a static plot
    
    Attributes:
        ax (plt.Axes): Subplot
        ax_im (plt.axesImage): Image plot in "ax"
        date (str): Date
        fig (plt.figure): Figure of plots
        slider (ipywidget.Slider): Slider widget
        tileCol (int): Column of tile
        tileMatrix (int): Zoom in level
        tileRow (int): Row of tile
    """
    
    def __init__(
            self,
            tileMatrix=5,
            tileCol=6,
            tileRow=5,
            date="2017-10-31"):
        """Implementing information of tiles
        
        Args:
            tileMatrix (int, optional): Zoom in level
            tileCol (int, optional): Column
            tileRow (int, optional): Row
            date (str, optional): Date
        """
        self.fig = None
        self.ax = None
        self.ax_im = None

        self.tileMatrix = tileMatrix
        self.tileCol = tileCol
        self.tileRow =  tileRow
        self.date = date

        self.slider = None

    def subplot(self):
        """Integrating functions and plotting.
        """
        self.fig, self.ax = plt.subplots()
        self.create_imshow()
        self.create_buttons()
        self.create_slider()
        self.render()

    def create_imshow(self):
        """Create image plot and set extent
        """
        extent = (
            self.top_left[1],
            self.bot_right[1],
            self.top_left[0],
            self.bot_right[0]
        )

        self.ax_im = self.ax.imshow(np.zeros((512, 512)), extent=extent)

    def create_buttons(self):
        """Create buttons and set functions
        """
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
        """Create slider and set function
        """
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
        """Rendering(Changing) image on the plot
        """
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
        """Coordinates of top left
        
        Returns:
            latitude: latitude of top left corner
            longitude: longitude of top left corner
        """
        return conversion.get_coordinates(
            tileMatrix = self.tileMatrix,
            tileCol = self.tileCol,
            tileRow = self.tileRow
        )

    @property
    def bot_right(self):
        """Coordinates of bottom right
        
        Returns:
            latitude: latitude of bottom right corner
            longitude: longitude of bottom right corner
        """
        return conversion.get_coordinates(
            tileMatrix = self.tileMatrix,
            tileCol = self.tileCol + 1,
            tileRow = self.tileRow + 1
        )

    def update_ticks(self):
        """Update coordinates corresponds to the tile
        """
        yticks = np.linspace(self.top_left[0], self.bot_right[0], 10)
        xticks = np.arange(self.top_left[1], self.bot_right[1],
            (self.bot_right[1] - self.top_left[1]) / 4.5)

        self.ax.set_yticklabels(yticks)
        self.ax.set_xticklabels(xticks)

    def left_cb(self, event=None):
        """Function for left button widget
        
        Args:
            event (Event, optional): Button click
        """
        self.tileCol -= 1
        self.render()

    def right_cb(self, event=None):
        """Function for right button widget
        
        Args:
            event (None, optional): Button click
        """
        self.tileCol += 1
        self.render()

    def up_cb(self, event=None):
        """Function for up button widget
        
        Args:
            event (None, optional): Button click
        """
        self.tileRow -= 1
        self.render()

    def down_cb(self, event=None):
        """Function for down button widget
        
        Args:
            event (None, optional): Button click
        """
        self.tileRow += 1
        self.render()

    def slider_cb(self, event):
        """Function for slider widget
        
        Args:
            event (TYPE): changed slider point
        """
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

    """Plot Class to build animation
    
    Attributes:
        ax (plt.Axes): Subplot
        ax_im (plt.axesImage): Image plot in "self.ax"
        dates (list): list of dates in str format
        end_date (str): End date of Animation
        fig (plt.figure): Figure of plots
        img (list): List of Images from start date to end date
        start_date (str): Start date of Animation
        tileCol (int): Column
        tileMatrix (int): Zoom in level
        tileRow (int): Row
    """
    
    def __init__(
            self,
            tileMatrix=4,
            tileCol=3,
            tileRow=2,
            start_date = '2017-10-01', 
            end_date = '2017-10-10'):
        """Initialize the starting tile
        
        Args:
            tileMatrix (int, optional): Zoom in level
            tileCol (int, optional): Column
            tileRow (int, optional): Row
            start_date (str, optional): Start date of Animation
            end_date (str, optional): End date of Animation
        """
        self.start_date = start_date
        self.end_date = end_date
        self.dates = []

        self.fig = None
        self.ax = None
        self.ax_im = None
        self.img = None

        self.tileMatrix = tileMatrix
        self.tileCol = tileCol
        self.tileRow =  tileRow

    def subplot(self):
        """Integrate and starting the animation
        
        Returns:
            plt.Animation: Function that has Animation
        """
        self.fig, self.ax = plt.subplots()
        self.load_image()
        self.get_dates()
        self.create_imshow()
        return self.create_animate()

    def load_image(self):
        """Make all images to a list
        """
        #Downloading Images
        img_array = getimage.get_image_date_range(
            tileMatrix = self.tileMatrix,
            tileCol = self.tileCol,
            tileRow = self.tileRow,
            start_date = self.start_date,
            end_date = self.end_date
        )
        #Make an array of image
        self.img = [Image.fromarray(i) for i in img_array]

    def create_imshow(self):
        """Create subplot
        """
        extent = (
            self.top_left[1],
            self.bot_right[1],
            self.top_left[0],
            self.bot_right[0]
        )
        #Put initialized Image data in self.ax_im
        self.ax_im = plt.imshow(np.zeros((512, 512)), extent=extent)

    def get_dates(self):
        """Get a list of date string, Implement in self.dates
        """
        start_date = datetime.datetime.strptime(self.start_date,'%Y-%m-%d')
        end_date = datetime.datetime.strptime(self.end_date,'%Y-%m-%d')
        step = datetime.timedelta(days=1)
        while start_date<=end_date:
            self.dates.append(str(start_date.date()))
            start_date += step

    @property
    def bot_right(self):
        """Coordinates of bottom right
        
        Returns:
            latitude: latitude of bottom right corner
            longitude: longitude of bottom right corner
        """
        return conversion.get_coordinates(
            tileMatrix = self.tileMatrix,
            tileCol = self.tileCol + 1,
            tileRow = self.tileRow + 1
        )

    @property
    def top_left(self):
        """Coordinates of top left
        
        Returns:
            latitude: latitude of top left corner
            longitude: longitude of top left corner
        """
        return conversion.get_coordinates(
            tileMatrix = self.tileMatrix,
            tileCol = self.tileCol,
            tileRow = self.tileRow
        )

    def create_animate(self):
        """Create animation

        Returns:
            plt.Animation: Function that has animation

        """
        # create animate function
        def update_fig(frame):
            """Function to change the image on the plot
            
            Args:
                frame (int): initial number of image
            
            Returns:
                axes.Image: Plot of changed Image
            """
            #updating images on every frame
            self.ax_im.set_data(self.img[frame])
            self.ax.set_title(self.dates[frame])
            return [self.ax_im]

        return animation.FuncAnimation(
            self.fig, 
            update_fig, 
            frames = range(len(self.img)), 
            interval = 600)
