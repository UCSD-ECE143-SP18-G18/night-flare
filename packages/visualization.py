import numpy as np
import matplotlib as matplot
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
from PIL import Image
from getimage import *
from conversion import *
import matplotlib.animation as animation
import datetime

def cordin(tileMatrix, tileCol, tileRow):
	"""
	Get coordinates to set labels

	Args:
		tileMatrix (int) : Zoom in level
		tileCol (int): Column
		tileRow (int) : Row
	Returns:
		lst (list) : [left_down, left_up, right_down, right_up]
	"""
	left_up = get_coordinates(tileMatrix, tileCol, tileRow)
	left_down = get_coordinates(tileMatrix, tileCol, tileRow + 1)
	right_up = get_coordinates(tileMatrix, tileCol + 1, tileRow)
	right_down = get_coordinates(tileMatrix, tileCol + 1, tileRow + 1)
	lst = [left_down, left_up, right_down, right_up]
	return lst

def center(lst):
	"""
	Get center coordinates of tile

	Args:
		lst (list) : 4 corner coordinates of tile
	Returns:
		(latitude,longitude) : Center coordinates
	"""
    
	latitude = sum([lst[0][0], lst[1][0], lst[2][0], lst[3][0]])/4
	longitude = sum([lst[0][1], lst[1][1], lst[2][1], lst[3][1]])/4
	return (latitude,longitude)

def base(tileMatrix = 5, tileCol = 6, tileRow = 5, date="2017-10-31"):
    """
    Make a base plot

    Args:
        tileMatrix (int, optional) : Zoom in level
        tileCol (int, optional) : Column
        tileRow (int, optional) : Row
        date (str, optional) : date

    Returns:
        fig (matplotlib.figure) : figure
        ax (matplotlib.axes): Subplot
        ax1 (matplotlib.axes) : Space of subplot
    """
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.2)

    img = get_image(tileMatrix = tileMatrix, tileCol = tileCol, tileRow = tileRow, date="2017-10-31")
    coor = cordin(tileMatrix, tileCol, tileRow)
    cen = center(coor)
    img = Image.fromarray(img)
    width, height = img.size
    img = img.convert('RGB')

    plt.title('This place will hold the date')
    plt.xlabel('Range : -180 ~ 180')
    plt.ylabel('Range : -90 ~ 90')
    ax1 = ax.imshow(img,extent = [coor[0][1],coor[2][1],coor[0][0],coor[1][0]])
    ax.set_yticklabels(np.arange(coor[0][0], coor[1][0]+1, (coor[1][0]-coor[0][0])/9))
    ax.set_xticklabels(np.arange(coor[0][1], coor[2][1]+1, (coor[2][1]-coor[0][1])/4.5))
    ax.set_title(date)
    plt.grid()

    return fig, ax, ax1

def button_class(ax, ax1):
    """
    Building a button class for changing tiles
    
    Args:
        ax(matplotlib.axes) : Subplot
        ax1(matplotlib.axes) : Space of subplot
    Returns:
        callback (Index) : Instance of Class Index()
        bright (Button) : right button 
        bnup (Button) : up button
        bleft (Button) : left button
        bdown (Button) : down button
    """
    
    class Index(object):
        tileMatrix = 5
        tileCol = 6
        tileRow =  5
        cen = [34.031598, -118.229542]

        def right(self, event):
        
            self.tileCol = self.tileCol + 1
            img = get_image(tileMatrix = self.tileMatrix, tileCol = self.tileCol, tileRow = self.tileRow)
            coor = cordin(self.tileMatrix, self.tileCol, self.tileRow)
            self.cen = center(coor)
            img = Image.fromarray(img)
            img = img.convert('RGB')
            ax1.set_data(img)

            ax.set_yticklabels(np.arange(coor[0][0], coor[1][0]+1, (coor[1][0]-coor[0][0])/9))
            ax.set_xticklabels(np.arange(coor[0][1], coor[2][1]+1, (coor[2][1]-coor[0][1])/4.5))
            plt.draw()

        def left(self, event):

            self.tileCol = self.tileCol - 1
            img = get_image(tileMatrix = self.tileMatrix, tileCol = self.tileCol, tileRow = self.tileRow)
            coor = cordin(self.tileMatrix, self.tileCol, self.tileRow)
            self.cen = center(coor)
            img = Image.fromarray(img)
            img = img.convert('RGB')
            ax1.set_data(img)

            ax.set_yticklabels(np.arange(coor[0][0], coor[1][0]+1, (coor[1][0]-coor[0][0])/9))
            ax.set_xticklabels(np.arange(coor[0][1], coor[2][1]+1, (coor[2][1]-coor[0][1])/4.5))
            plt.draw()

        def up(self,event):
        
            self.tileRow = self.tileRow -1
            img = get_image(tileMatrix = self.tileMatrix, tileCol = self.tileCol, tileRow = self.tileRow)
            coor = cordin(self.tileMatrix, self.tileCol, self.tileRow)
            self.cen = center(coor)
            img = Image.fromarray(img)
            img = img.convert('RGB')
            ax1.set_data(img)

            ax.set_yticklabels(np.arange(coor[0][0], coor[1][0]+1, (coor[1][0]-coor[0][0])/9))
            ax.set_xticklabels(np.arange(coor[0][1], coor[2][1]+1, (coor[2][1]-coor[0][1])/4.5))
            plt.draw()

        def down(self,event):

            self.tileRow = self.tileRow + 1
            img = get_image(tileMatrix = self.tileMatrix, tileCol = self.tileCol, tileRow = self.tileRow)
            coor = cordin(self.tileMatrix, self.tileCol, self.tileRow)
            self.cen = center(coor)
            img = Image.fromarray(img)
            img = img.convert('RGB')
            ax1.set_data(img)
            ax.set_yticklabels(np.arange(coor[0][0], coor[1][0]+1, (coor[1][0]-coor[0][0])/9))
            ax.set_xticklabels(np.arange(coor[0][1], coor[2][1]+1, (coor[2][1]-coor[0][1])/4.5))
            plt.draw()

    callback = Index()

    axleft = plt.axes([0.80, 0.2, 0.07, 0.0375])
    axright = plt.axes([0.89, 0.2, 0.07, 0.0375])

    axup = plt.axes([0.845, 0.250, 0.07, 0.0375])
    axdown = plt.axes([0.845, 0.150, 0.07, 0.0375])

    bright = Button(axright, 'Right')
    bnup = Button(axup, 'Up')
    bleft = Button(axleft, 'Left')
    bdown = Button(axdown, 'Down')

    return callback, bright, bnup, bleft, bdown

def slider(fig, ax, ax1, callback):
    """
    Make a Slider for changing zoom in level
    Args:
        fig (matplotlib.figure) : figure
        ax (matplotlib.axes) : Subplot
        ax1 (matplotlib.axes) : Space of subplot
        callback (Index) : instance of Class Index()
    Returns:
        sfreq (Slider) : Slider that changes zoom in level
        update (function) : Function call for Slider
    """

    def update(val):
        freq = sfreq.val
        freq = int(freq)
        latitude, longtitude = callback.cen
        tileRow, tileCol = get_tile_info(latitude, longtitude, freq)
        img = get_image(tileMatrix = freq, tileCol = tileCol, tileRow = tileRow)
        coor = cordin(freq, tileCol, tileRow)
        callback.tileCol = tileCol
        callback.tileRow = tileRow
        callback.tileMatrix = freq
    
        cen = center(coor)
        img = Image.fromarray(img)
        img = img.convert('RGB')
        ax1.set_data(img)
        ax.set_yticklabels(np.arange(coor[0][0], coor[1][0]+1, (coor[1][0]-coor[0][0])/9))
        ax.set_xticklabels(np.arange(coor[0][1], coor[2][1]+1, (coor[2][1]-coor[0][1])/4.5))
        plt.draw()
        fig.canvas.draw_idle()

    plt.subplots_adjust(bottom=0.25)
    axcolor = 'lightgoldenrodyellow'
    axfreq = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
    sfreq = Slider(axfreq, 'Zoom in Level', 1, 7, valinit=5, valfmt = "%d")

    return sfreq, update

def plot():
    """
    Combine all steps and make a final plot
    Args:
        None
    Returns:
        None
	"""
    fig, ax, ax1 = base()
    callback, bright, bnup, bleft, bdown = button_class(ax, ax1)

    bright.on_clicked(callback.right)

    bnup.on_clicked(callback.up)

    bleft.on_clicked(callback.left)

    bdown.on_clicked(callback.down)

    sfreq, update = slider(fig,ax,ax1,callback)

    sfreq.on_changed(update)

    plt.show()

def plot_date_range(start_date = '2017-10-01', end_date = '2017-10-10'):
    """
    Plotting by specific date range
    Args:
        start_date (str, optional) : start date of range
        end_date (str, optional) : end date of range
    Returns:
        anim (matplotlib.animation) : animation by dates.
	"""

    tileMatrix = 5
    tileCol = 6
    tileRow = 5

    left_up = get_image_date_range(tileMatrix = tileMatrix, tileCol = tileCol, tileRow = tileRow, 
    	start_date = '2017-10-01', end_date = '2017-10-10')
    left_down = get_image_date_range(tileMatrix = tileMatrix, tileCol = tileCol, tileRow = tileRow+1,
    	start_date = '2017-10-01', end_date = '2017-10-10')
    right_up = get_image_date_range(tileMatrix = tileMatrix, tileCol = tileCol+1, tileRow = tileRow,
    	start_date = '2017-10-01', end_date = '2017-10-10')
    right_down = get_image_date_range(tileMatrix = tileMatrix, tileCol = tileCol+1, tileRow = tileRow+1,
    	start_date = '2017-10-01', end_date = '2017-10-10')

    left_up = [Image.fromarray(i) for i in left_up]
    left_down = [Image.fromarray(i) for i in left_down]
    right_up = [Image.fromarray(i) for i in right_up]
    right_down = [Image.fromarray(i) for i in right_down]

    width, height = left_up[0].size
    left_up = [i.convert('RGB') for i in left_up]
    left_down = [i.convert('RGB') for i in left_down]
    right_up = [i.convert('RGB') for i in right_up]
    right_down = [i.convert('RGB') for i in right_down]

    coor = cordin(tileMatrix, tileCol, tileRow)
    fig, ax = plt.subplots()

    plt.grid()

    img = []

    for i in range(10):
        new_im = Image.new('RGB',(width*2,height))
        new_im2 = Image.new('RGB',(width*2,height))
        new_final = Image.new('RGB',(width*2, height*2))
        x_offset = 0
        new_im.paste(left_up[i],(x_offset,0))
        x_offset += width
        new_im.paste(right_up[i],(x_offset,0))

        x_offset = 0
        new_im2.paste(left_down[i],(x_offset,0))
        x_offset += width
        new_im2.paste(right_down[i],(x_offset,0))

        y_offset = 0
        new_final.paste(new_im,(0,y_offset))
        y_offset += height
        new_final.paste(new_im2,(0,y_offset))
        img.append(new_final)

    dates = []
    start_date = datetime.datetime.strptime(start_date,'%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date,'%Y-%m-%d')
    step = datetime.timedelta(days = 1)
    while start_date<=end_date:
        dates.append(str(start_date.date()))
        start_date += step

    ax1 = ax.imshow(img[0],extent = [coor[0][1],coor[2][1]+(coor[2][1]-coor[0][1]),
    coor[0][0]-(coor[1][0]-coor[0][0]),coor[1][0]])

    plt.xlabel('longitude')
    plt.ylabel('latitude')
    ax.set_xlim([-125,-115])
    ax.set_ylim([32,44])

    def updatefig(j):
        ax1.set_data(img[j])
        ax.set_title(dates[j])
        return [ax1]

    anim = animation.FuncAnimation(fig, updatefig, frames = range(len(img)), interval = 800, blit=True)
    plt.close()
    return anim
