# 2014_02_14
#   Choose multiple spectrum files and open them.
#   These files are examined regularly for changes (based on their timestamp)
#   They are reloaded automatically if they are changed.
#
import os
import sys
import Tkinter

# Sparky packages
import sparky
import sputil
import tkutil

DEBUG = 1

class OpenReloadDialog(tkutil.Dialog):

    def __init__(self, session):
        """ Initialization
        """
        self.session = session
        tkutil.Dialog.__init__(self, session.tk,
                               'Open & Autoreload Multiple Spectra')
        
        proj = session.project
        mfs = tkutil.multiple_file_selection(self.top, proj.sparky_directory)
        mfs.frame.pack(side = 'top', anchor = 'nw', fill = 'both', expand = 1)
        self.files = mfs

        r = Tkinter.Label(self.top, justify = 'left')
        r.pack(side = 'top', anchor = 'nw')

        self.result = r
        br = tkutil.button_row(self.top,
                               ('Open', self.open_cb),
                               ('Reload', self.reload_spectra),
                               ('Cancel', self.close_cb),
                               ('Help',
                                sputil.help_cb(session,
                                               'OpenAutoreloadSpectra')),
                               )
        br.frame.pack(side = 'top', anchor = 'nw')

        self.paths      = None  # list of spectrum files to open
        self.spectra    = []    # spectra already opened

    def open_spectra(self):
        """ Open specified spectrum files 
        """
        bad_paths = []
        for path in self.paths:  # open each

            spectrum = self.session.open_spectrum(path)
            print spectrum.__dict__
            if spectrum is None:
                bad_paths.append(path)
            else:
                self.spectra.append(spectrum)
                
        print 'spectra list:', self.session.project.spectrum_list()
        print 'view list:', self.session.project.view_list()

        if bad_paths:
            message = 'Could not open files:'
            for path in bad_paths:
                message = message + '\n' + path
            else:
                message = 'Opened %d spectra' % len(self.paths)
                self.result['text'] = message
                

    def open_cb(self):
        """ Open button is clicked. Open and reload (multiple) spectrum files
        """
        self.paths = self.files.selected_paths()
        self.open_spectra()


    def reload_spectra(self):
        """ Force the opened files to be reloaded
        """
        if self.paths:
            if self.spectra: # if spectra have been opend
                             # destroy them first
                for v in self.session.project.view_list():
                    if v.spectrum in self.spectra:
                        v.destroy()
                        
            self.open_spectra()
        else:  # click on reload before any spectra are loaded. 
               # Cannot make the button grey because it is a poorly 
               # wrapped class by the tkutil.
            sys.stderr.write('ERROR: No file(s) opened yet!\n')
            

    def close_cb(self):
        """ Cancel button is clicked. 
        """
        tkutil.Dialog.close_cb(self)




# -----------------------------------------------------------------------------
#
def show_file_dialog(session):
    d = sputil.the_dialog(OpenReloadDialog, session)
    d.show_window(1)
