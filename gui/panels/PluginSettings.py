"""
The Plugin Settings panel
"""
from PyQt4 import Qt, QtCore, QtGui, QtOpenGL
from PyQt4.QtCore import *
from OpenGL import GL

from settings import Settings
#from plugins.ScopePlugin import ScopePlugin
#import PluginPanel
import random

# -------------------------------------------------------------------------------
#                              PLUGIN SETTINGS
# -------------------------------------------------------------------------------

class GLPreviewWidget(QtOpenGL.QGLWidget):

    def __init__(self,  illuminationWidget, parent=None):
        # Set up to sync with double-buffer, vertical refresh.  Add
        # Alpha and Depth buffers.  This should prevent frame tearing.
        fmt = QtOpenGL.QGLFormat()
        fmt.setSwapInterval(1)
        fmt.setDoubleBuffer(True)
        fmt.setAlpha(True)
        fmt.setDepth(True)
        QtOpenGL.QGLWidget.__init__(self, fmt, parent, illuminationWidget)
        self.illuminationWidget = illuminationWidget

        # Render 30 frames per second
        self.timerId = self.startTimer(1000./30.0)

        # Default values
        self.width = 512
        self.height = 512

    def timerEvent(self, event):
        '''
        Call the OpenGL update function if necessary
        '''
        if self.isVisible():
            self.updateGL()

    # --------------------- EVENT HANDLING CODE ------------------

    def mouseDoubleClickEvent(self, event):
        if self.illuminationWidget.isVisible():
            self.illuminationWidget.setVisible(False)
        else:
            self.illuminationWidget.setVisible(True)

    def resizeGL(self, width, height):
        self.width = width
        self.height = height

    def paintGL(self):
        GL.glViewport(0,0,self.width,self.height);
        GL.glMatrixMode(GL.GL_PROJECTION);
        GL.glLoadIdentity();
        localAspect = float(self.width) / self.height
        GL.glOrtho(-1.0, 1.0, -1.0, 1.0, -1.0, 1.0);
        GL.glMatrixMode(GL.GL_MODELVIEW);
        GL.glLoadIdentity();
        GL.glClearColor(0.4,0.4,0.4,1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glColor((0.0,0.0,0.0,1.0))

        aspect = 1
        if (self.illuminationWidget.framebufferTexture):
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.illuminationWidget.framebufferTexture)
            aspect = float(self.illuminationWidget.width)/self.illuminationWidget.height
            GL.glEnable(GL.GL_TEXTURE_2D)
            GL.glColor((1.0,1.0,1.0,1.0))

        if (aspect/localAspect > 1.0):
            GL.glBegin(GL.GL_QUADS);
            GL.glTexCoord2f(  0.0,  0.0 );  GL.glVertex2d( -1.0, -1.0/aspect*localAspect);
            GL.glTexCoord2f(  1.0,  0.0 );  GL.glVertex2d(  1.0, -1.0/aspect*localAspect);
            GL.glTexCoord2f(  1.0,  1.0 );  GL.glVertex2d(  1.0,  1.0/aspect*localAspect);
            GL.glTexCoord2f(  0.0,  1.0 );  GL.glVertex2d( -1.0,  1.0/aspect*localAspect);
            GL.glEnd();
        else:
            GL.glBegin(GL.GL_QUADS);
            GL.glTexCoord2f(  0.0,  0.0 );  GL.glVertex2d( -aspect/localAspect, -1.0)
            GL.glTexCoord2f(  1.0,  0.0 );  GL.glVertex2d(  aspect/localAspect, -1.0)
            GL.glTexCoord2f(  1.0,  1.0 );  GL.glVertex2d(  aspect/localAspect,  1.0)
            GL.glTexCoord2f(  0.0,  1.0 );  GL.glVertex2d( -aspect/localAspect,  1.0)
            GL.glEnd();

        GL.glDisable(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
    

# -------------------------------------------------------------------------------
#                              PLUGIN SETTINGS
# -------------------------------------------------------------------------------

# class PluginSettings(QtGui.QWidget, PluginPanel.Ui_pluginPanel):
#     """
#     A window that has the various display-specific settings
#     """

#     def __init__(self, pluginManager, illuminationWidget, parent = None):
#         QtGui.QWidget.__init__(self, parent)
#         self.setupUi(self)
        
#         self.settings = Settings()
#         self.pluginManager = pluginManager
#         self.illuminationWidget = illuminationWidget
#         (plugin_keys, plugin_names, plugin_descriptions) = self.pluginManager.list_plugins()

#         # Create the GL Preview Window
#         self.glPreviewWidget = GLPreviewWidget(illuminationWidget, parent = self)
#         self.previewBox.layout().addWidget(self.glPreviewWidget)

#         # Populate the pull-down menu and select the previous plugin
#         # we were using, if it is available.
#         prev_plugin = None
#         if self.settings['plugins'].contains('current_plugin'):
#             prev_plugin = self.settings['plugins'].current_plugin

#         self.current_plugin_idx = -1
#         for name in plugin_names:
#             self.manualSelectionBox.addItem(name)
            
#         idx = self.manualSelectionBox.findText(prev_plugin)
#         if idx != -1:
#             self.manualSelectionBox.setCurrentIndex(idx)

#         self.update()

#         self.ttlCheckBox.setChecked(self.settings['illumination'].refreshWithDefault('draw_on_ttl', False))
#         self.ttlBlankCheckBox.setChecked(self.settings['illumination'].refreshWithDefault('blank_after_ttl_frame', True))

#         validator = QtGui.QIntValidator(self.randomSeedInput)
#         validator.setBottom(0)
#         self.randomSeedInput.setValidator(validator)

#         self.connect(self.randomSeedButton,
#                      QtCore.SIGNAL('clicked(bool)'),
#                      self.setRandomSeed)

#     # Set the random seed to user input value
#     def setRandomSeed(self):
#         seed = int(str(self.randomSeedInput.text()).strip())
#         random.seed(seed)

    # --------------------------------------------------------------------
    #                               ACTIONS 
    # --------------------------------------------------------------------

    def on_manualSelectionBox_currentIndexChanged(self, index):
        # Ignore signals with string arguments
        if (type(index) is not int):
            return

        # Ignore if this is just the same argument
        if (index == self.current_plugin_idx):
            return

        (plugin_keys, plugin_names, plugin_descriptions) = self.pluginManager.list_plugins()
        self.pluginManager.select_plugin(plugin_keys[index])
        self.descriptionLabel.setText(plugin_descriptions[index])
        self.settings['plugins'].current_plugin = plugin_names[index]

    def on_ttlCheckBox_toggled(self, state):
        self.settings['illumination'].draw_on_ttl = state

    def on_ttlBlankCheckBox_toggled(self, state):
        self.settings['illumination'].blank_after_ttl_frame = state
