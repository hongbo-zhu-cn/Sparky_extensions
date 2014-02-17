# 2014_02_14
#   Choose multiple spectrum files and open them.
#   These files are examined regularly for changes (based on their timestamp)
#   They are reloaded automatically if they are changed.
#
import os
import sys
import time
import threading
import sched
import Queue

import Tkinter

# Sparky packages
import sparky
import sputil
import tkutil

DEBUG = 1

class OpenAutoreloadDialog(tkutil.Dialog):

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
                               ('Set Timer', self.set_timer),
                               ('Toggle Autoreload', self.toggle_autoreload),
                               ('Cancel', self.close_cb),
                               ('Help',
                                sputil.help_cb(session,
                                               'OpenAutoreloadSpectra')),
                               )
        br.frame.pack(side = 'top', anchor = 'nw')

        self.autoreload = True  # if the spectrum files should be autoreloaded
        self.paths      = None  # list of spectrum files to open
        self.tslist     = None  # list of timestamps for the spectrum files
        self.tth        = None  # threading.Timer instance
        self.q = Queue.Queue(1)
       

    def set_timer(self):
        
        # stop autoreload to avoid conflict
        self.autoreload = False
        sys.stdout.write('INFO: autoreload set to False.\n')
            
        if self.q.empty():  self.q.put(self.session)
        sys.stdout.write('Timer set\n')
        t = threading.Timer(0.1, self.open_spectra, args=[])
        t.start()
        sys.stdout.write('Timer done\n')
        
        
    def toggle_autoreload(self):
        if self.autoreload:  
            self.autoreload = False
            sys.stdout.write('INFO: autoreload set to False.\n')
        else:                
            self.autoreload = True
            sys.stdout.write('INFO: autoreload set to True.\n')
        

    def open_spectra_autoreload(self, interval=2):
        
        self.open_spectra(self.session.open_spectrum)
        self.q = Queue.Queue(len(self.paths))
        if self.autoreload:
            if self.q.empty(): self.q.put(self.session)
            threading.Timer(interval, self.check_spectra_update, []).start()
            self.q.join()
        

    def check_spectra_update(self):
        
        for i in xrange(len(self.paths)):  # open each

            path, ts = self.paths[i], self.tslist[i]
            newts = os.path.getmtime(path)
            if DEBUG:
                print 'old ts =', ts
                print 'new ts =', newts
                
            if ts != newts:  # if forece open or timestamp differs

                self.tslist[i] = newts  # update timestamp
                q.put(path)
                if DEBUG:
                    print 'timestamp differs. we are opening', path

                
    def open_spectra(self, open_spectrum_func):
        """ Open specified spectrum files and autoreload them if they are
            changed (timestamp changed)
        """

        bad_paths = []

        #for i in xrange(len(self.paths)):  # open each
        for path in self.q.get():

            self.opensprlt = open_spectrum_func(path)
                
            if DEBUG:
                print 'opensprlt =', self.opensprlt
            if self.opensprlt == None:
                bad_paths.append(path)

        if bad_paths:
            message = 'Could not open files:'
            for path in bad_paths:
                message = message + '\n' + path
            else:
                message = 'Opened %d spectra' % len(self.paths)
                self.result['text'] = message       

    #def open_spectra(self, open_spectrum_func):
    #    """ Open specified spectrum files and autoreload them if they are
    #        changed (timestamp changed)
    #    """
    #    print 'current thread =', threading.currentThread().getName()
    #    print 'session diffs? ', se, self.session
    #    print 'sparky.session_list', sparky.session_list
    #    bad_paths = []
    #
    #    for i in xrange(len(self.paths)):  # open each
    #
    #        path, ts = self.paths[i], self.tslist[i]
    #        newts = os.path.getmtime(path)
    #        if DEBUG:
    #            print 'old ts =', ts
    #            print 'new ts =', newts
    #            
    #        if ts != newts:  # if forece open or timestamp differs
#
#                self.tslist[i] = newts  # update timestamp
#                if DEBUG:
#                    print 'timestamp differs. we are opening', path
#                    print 'session to be used =', self.session
#                    print self.session.__dict__
#
#                #self.opensprlt = self.session.open_spectrum(path)
#                #self.opensprlt = se.open_spectrum(path)
#                self.opensprlt = open_spectrum_func(path)
#                
#                if DEBUG:
#                    print 'opensprlt =', self.opensprlt
#                if self.opensprlt == None:
#                    bad_paths.append(path)
#            else:
#                if DEBUG: 
#                    print 'timestamp did not change. no action', time.time()
#                    print 'session info:', self.session.__dict__
#
#        if bad_paths:
#            message = 'Could not open files:'
#            for path in bad_paths:
#                message = message + '\n' + path
#            else:
#                message = 'Opened %d spectra' % len(self.paths)
#                self.result['text'] = message
#                
#        # only if the OpenFileDialog is open && session is open && spectra is
#        # open (TODO)
        # TODO: how to stop the loop when view is destroyed?
        # at the moment, the loop can only be stopped by clicking on Cancel
        #if self.autoreload and self.session.tk and \
        #       self.session and self.opensprlt:
        #print 'Now I set timer'
        #if self.autoreload:
        #    self.tth = threading.Timer(2, self.open_sp_autoreload, [se,])
        #    self.tth.start()


    def open_cb(self):
        """ Open button is clicked. Open and reload (multiple) spectrum files
        """
        self.paths = self.files.selected_paths()
        self.tslist = [None] * len(self.paths)
        if DEBUG:
            print 'session before open_sp:', self.session
            print self.session.__dict__
        self.autoreload = True
        self.open_spectra_autoreload()
        print 'I returned.'
           

    def close_cb(self):
        """ Cancel button is clicked. 
        """
        # remove the following two lines if you want to stop spectrum files
        # from being updated
        self.autoreload = False
        if self.tth: self.tth.cancel()  # cancel the current Timer
        # till here

        tkutil.Dialog.close_cb(self)




# -----------------------------------------------------------------------------
#
def show_file_dialog(session):
    d = sputil.the_dialog(OpenAutoreloadDialog, session)
    d.show_window(1)
