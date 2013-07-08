import sys, os, random

import subprocess

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui
import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure


class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Demo: PyQt with matplotlib')

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.a_box.setText('3000')
	self.b_box.setText('2000')
	self.c_box.setText('1000')
	self.autofit_filename_box.setText('prog_A_GUI_v1.py')
	self.a_set  = '3000'
	self.b_set  = '2000'
	self.c_set  = '1000'      
	self.on_draw()

    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    def on_about(self):
        msg = """ A demo of using PyQt with matplotlib:
        
         * Use the matplotlib navigation bar
         * Add values to the text box and press Enter (or click "Draw")
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        QMessageBox.about(self, "About the demo", msg.strip())
    
    def on_pick(self, event):
        # The event received here is of the type
        # matplotlib.backend_bases.PickEvent
        #
        # It carries lots of information, of which we're using
        # only a small amount here.
        # 
        box_points = event.artist.get_bbox().get_points()
        msg = "You've clicked on a bar with coords:\n %s" % box_points
        
        QMessageBox.information(self, "Click!", msg)
    def A_change(self):
	
	current_value_a = float(self.a_set)
	current_value_b = float(self.b_set)
	current_value_c = float(self.c_set)
	self.on_draw()	
	self.a_box.setText(str(current_value_a+self.slider_a.value()))
	self.b_box.setText(str(current_value_b+self.slider_b.value()))
	self.c_box.setText(str(current_value_c+self.slider_c.value()))
    def replot_button(self):
	self.a_set = unicode(self.a_box.text())
	self.b_set = unicode(self.b_box.text())
	self.c_set = unicode(self.c_box.text())
	self.on_draw()
    def on_draw(self):
        """ Redraws the figure
        """
        #str = unicode(self.a_box.text())
	str = unicode(self.a_box.text())+' '+unicode(self.b_box.text())+' '+unicode(self.c_box.text())      
	
	self.data = str.split()
       	self.data2 = [float(entry) for entry in self.data]
        x = range(len(self.data))

        # clear the axes and redraw the plot anew
        #
        self.axes.clear()        
        self.axes.grid(self.grid_cb.isChecked())
        
        self.axes.scatter(self.data2, [10,20,30])
	self.axes.axis([0, 5000, 0, 100])
        
        self.canvas.draw()
    
    def run_autofit(self):
	filename = unicode(self.autofit_filename_box.text())
	subprocess.Popen("python ./%s"%filename, shell=True)
		



    def create_main_frame(self):
        self.main_frame = QWidget()
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self.axes = self.fig.add_subplot(111)
        
        # Bind the 'pick' event for clicking on one of the bars
        #
        self.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        # Other GUI controls
        # 
        self.a_box = QLineEdit()
	self.b_box = QLineEdit()
	self.c_box = QLineEdit()
        self.DJ_box = QLineEdit()
	self.DJK_box = QLineEdit()
	self.DK_box = QLineEdit()
	self.ua_box = QLineEdit()
	self.ub_box = QLineEdit()
	self.uc_box = QLineEdit()

	self.autofit_filename_box = QLineEdit() 

        self.a_box.setMinimumWidth(100)
	self.b_box.setMinimumWidth(100)
        self.connect(self.a_box, SIGNAL('editingFinished ()'), self.on_draw)
        #self.connect(self.textbox2, SIGNAL('editingFinished ()'), self.on_draw)       
        #self.connect(self.textbox3, SIGNAL('editingFinished ()'), self.on_draw) 
        self.draw_button = QPushButton("&Update Constants")
	self.autofit_button = QPushButton("&Run Autofit")


        self.connect(self.draw_button, SIGNAL('clicked()'), self.replot_button)

        self.connect(self.autofit_button, SIGNAL('clicked()'), self.run_autofit)

        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.on_draw)
        
        slider_label = QLabel('Bar width (%):')
	a_label = QLabel('A')
	b_label = QLabel('B')
	c_label = QLabel('C')
	DJ_label = QLabel('DJ')
	DJK_label = QLabel('DJK')
	DK_label = QLabel('DK')
	ua_label = QLabel('mu a')
	ub_label = QLabel('mu b')
	uc_label = QLabel('mu c')
	autofit_filename_label = QLabel('Autofit Filename') 


        self.slider_a = QSlider(Qt.Horizontal)
        self.slider_a.setRange(-500, 500)
        self.slider_a.setValue(0)
        self.slider_a.setTracking(True)
        self.slider_a.setTickPosition(QSlider.TicksBothSides)
        self.connect(self.slider_a, SIGNAL('valueChanged(int)'), self.A_change)
        
        self.slider_b = QSlider(Qt.Horizontal)
        self.slider_b.setRange(-500, 500)
        self.slider_b.setValue(0)
        self.slider_b.setTracking(True)
        self.slider_b.setTickPosition(QSlider.TicksBothSides)
        self.connect(self.slider_b, SIGNAL('valueChanged(int)'), self.A_change)

        self.slider_c = QSlider(Qt.Horizontal)
        self.slider_c.setRange(-500, 500)
        self.slider_c.setValue(0)
        self.slider_c.setTracking(True)
        self.slider_c.setTickPosition(QSlider.TicksBothSides)
        self.connect(self.slider_c, SIGNAL('valueChanged(int)'), self.A_change)


        #
        # Layout with box sizers
        # 
	"""
	names = ['Cls', 'Bck', '', 'Close', '7', '8', '9', '/',
                '4', '5', '6', '*', '1', '2', '3', '-',
                '0', '.', '=', '+']

        grid = QtGui.QGridLayout()

        j = 0
        pos = [(0, 0), (0, 1), (0, 2), (0, 3),
                (1, 0), (1, 1), (1, 2), (1, 3),
                (2, 0), (2, 1), (2, 2), (2, 3),
                (3, 0), (3, 1), (3, 2), (3, 3 ),
                (4, 0), (4, 1), (4, 2), (4, 3)]

        for i in names:
            button = QtGui.QLabel(i)
            if j == 2:
                grid.addWidget(QtGui.QLabel(''), 0, 2)
            else: grid.addWidget(button, pos[j][0], pos[j][1])
            j = j + 1

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(grid)

        self.main_frame.setLayout(grid)   
        self.setCentralWidget(self.main_frame)
        #self.move(300, 150)
        #self.setWindowTitle('Calculator')    
        #self.show()


	"""
	hbox = QtGui.QGridLayout()
        #hbox = QHBoxLayout()
        #widget_list = [ a_label, self.textbox,b_label,self.textbox2 ,self.draw_button, self.grid_cb,
        #            slider_label, self.slider]
        #for w in range(len(widget_list)):
        #    hbox.addWidget(widget_list[w])
        #    hbox.setAlignment(w, Qt.AlignVCenter)
        hbox.addWidget(a_label,0,1)
        hbox.addWidget(b_label,1,1)
	hbox.addWidget(c_label,2,1)
	hbox.addWidget(DJ_label,3,1)
	hbox.addWidget(DJK_label,4,1)
	hbox.addWidget(DK_label,5,1)
	hbox.addWidget(ua_label,6,1)
        hbox.addWidget(ub_label,7,1)
        hbox.addWidget(uc_label,8,1)

	
        hbox.addWidget(self.a_box,0,2)
        hbox.addWidget(self.b_box,1,2)
	hbox.addWidget(self.c_box,2,2)
	hbox.addWidget(self.DJ_box,3,2)
	hbox.addWidget(self.DJK_box,4,2)
	hbox.addWidget(self.DK_box,5,2)
	hbox.addWidget(self.ua_box,6,2)
        hbox.addWidget(self.ub_box,7,2)
        hbox.addWidget(self.uc_box,8,2)
	
	hbox.addWidget(self.draw_button,0,4)
	hbox.addWidget(self.grid_cb,1,4)
	#hbox.addWidget(slider_label,2,3)
	hbox.addWidget(self.slider_a,0,3)
	hbox.addWidget(self.slider_b,1,3)
	hbox.addWidget(self.slider_c,2,3)
	hbox.addWidget(self.autofit_button,4,4)

	hbox.addWidget(autofit_filename_label,3,3)
	hbox.addWidget(self.autofit_filename_box,3,4)
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
    	
    def create_status_bar(self):
        self.status_text = QLabel("This is a demo")
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        load_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (load_file_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the demo')
        
        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None, 
                        icon=None, tip=None, checkable=False, 
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action


def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
