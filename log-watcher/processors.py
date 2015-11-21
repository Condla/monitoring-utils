#! /usr/bin/env python
'''
Processors
'''
from time import strptime


class LoglineEventProcessor(object):
    '''
    Interface that provides the methods that a logline should have
    in order to be processed correctly.
    ''' 

    def __init__(self, logline, input_argument=None):
        #print("LoglineEventProcessor: " + self.name)
        self.logline = logline
        self._process_logline()
        self.input_argument = input_argument
        self.condition = self.eval_condition()

    def process(self):
        '''
        This will execute the code subsequentially
        '''
        if self.condition:
            self.do_on_condition_true()
    
        else:
            self.do_on_condition_false()

        self.do_always()


    def get(self):
        try:
            return self.transformed_logline
        except:
            return self.logline

    def eval_condition(self):
        pass

    def do_on_condition_true(self):
        pass

    def do_on_condition_false(self):
        pass

    def do_always(self):
        pass

    def _process_logline(self):
        try:
            (self.timestruct,
                    self.loglevel,
                    self.message) = self.logline
        except:
            pass


class LoglineAlerter(LoglineEventProcessor):
    '''
    Filters Logline according to special criteria
    '''
    name = "LoglineAlerter"
    last_alert = 0

    def eval_condition(self):
        for filterword in self.input_argument:
            if filterword in self.message:
                return True
            try:
                if filterword in self.loglevel:
                    return True
            except:
                pass

    def do_on_condition_true(self):
        print(self.message)


class Preprocessor(LoglineEventProcessor):
    '''
    This preprocessor parses the log lines and splits them into 
    understandable variables.
    '''

    name = "Preprocessor"

    def do_always(self):
        self.transformed_logline = self._parse_entries()

    def _parse_entries(self):
        self.logline = self.logline.replace('\n', '')
        if self.input_argument == 'log4j':
            try:
                return self._parse_log4j_entries()
            except:
                return self._parse_rawline_entries()

    def _parse_log4j_entries(self):
        templine_list = self.logline.split()
        timestruct = strptime(
                templine_list[0] + ' ' + templine_list[1],
                '%y/%m/%d %H:%M:%S')
        loglevel = templine_list[2]
        message = ' '.join(templine_list[3:])
        return timestruct, loglevel, message

    def _parse_rawline_entries(self):
        message = self.logline
        timestruct = None
        loglevel = None
        return timestruct, loglevel, message
