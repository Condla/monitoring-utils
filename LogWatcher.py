#! /usr/bin/env python
'''
This is a daemon, which attaches itself to configured logfiles
and performs custom actions depending on the configuration.
'''
from threading import Thread
import json, time
from processors import LoglineEventProcessor, LoglineAlerter, Preprocessor

EVENT_PROCESSORS = 'event_processors'
LOGFILES = 'logfiles'
NAME = 'name'
TYPE = 'type'
FILTER = 'filter'

class LogFileWatcher(Thread):
    '''
    Runs in the background and watches logs for certain patterns
    and behaviours
    '''
    def __init__(self, logfilename, event_processors):
        '''
        Initializing the LogFileWatcher 
        '''
        Thread.__init__(self)
        self.logfilename = logfilename
        self.event_processors = event_processors

    def run(self):
        '''
        Main loop of LogWatcher
        '''
        with open(self.logfilename) as logfile:
            while True:
                loglines = logfile.read()
                if loglines:
                    for logline in loglines.split('\n'):
                        self._execute_event_processor_pipeline(logline)
                time.sleep(5)

    def _execute_event_processor_pipeline(self, logline):
        for event_processor, input_argument in self.event_processors:
            ep = event_processor(logline, input_argument)
            ep.process()
            logline = ep.get()
        


class LogFileWatcherController(object):
    '''
    Creates a LogWatcher and spawns it with supervisord
    '''

    def __init__(self, config_filename):
        '''
         
        '''
        self.config_filename = config_filename
        self._extract_properties_from_config_file()
      

    def _extract_properties_from_config_file(self):
        '''
        Internal method to extract config file properties
        '''
        with open(self.config_filename) as config_file:
            config = json.load(config_file)
            self.logfiles = config[LOGFILES]

    def start(self):
        for logfile in self.logfiles:
            event_processors = [
                    (Preprocessor,
                        logfile[TYPE]),
                    (LoglineAlerter,
                        logfile[FILTER])
                    ]
            LogFileWatcher(logfile[NAME], event_processors).start()
        


if __name__ == "__main__":
    CONFIG_JSON = 'config.json'
    lfwc = LogFileWatcherController(CONFIG_JSON)
    lfwc.start()
