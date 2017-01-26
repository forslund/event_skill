import sys
from os.path import dirname, abspath, basename

from mycroft.skills.media import MediaSkill
from mycroft.skills.scheduled_skills import ScheduledSkill, Timer
from adapt.intent import IntentBuilder
from mycroft.messagebus.message import Message


import time
from time import mktime

from os.path import dirname
from mycroft.util.log import getLogger

sys.path.append(abspath(dirname(__file__)))

logger = getLogger(abspath(__file__).split('/')[-2])
__author__ = 'forslund'


class EventSkill(ScheduledSkill):
    def __init__(self):
        super(EventSkill, self).__init__('EventSkill')
        self.waiting = True

    def initialize(self):
        print 'INITIALIZE ', self.name
        self.times = []
        self.events = self.config

        for e in self.events:
            self.register_vocabulary(e, 'EventKeyword')
            print e
            if 'time' in self.events[e]:
                self.add_event(e)

        intent = IntentBuilder('EventIntent')\
                 .require('EventKeyword')\
                 .build()
        self.register_intent(intent, self.handle_run_event)

        self.register_vocabulary('cancel events', 'CancelEventsKeyword')
        intent = IntentBuilder('CancelEventsIntent')\
                 .require('CancelEventsKeyword')\
                 .build()
        self.register_intent(intent, self.handle_cancel_events)


        self.emitter.on('recognizer_loop:audio_output_end',
                        self.ready_to_continue)
        print self.times 
        self.schedule()
    
    def add_event(self, event):
        now = self.get_utc_time()
        time = self.get_utc_time(self.events[event]['time'])
        if time <= now:
            time += self.SECONDS_PER_DAY
        self.times.append((time, event))
        self.times = sorted(self.times)
        self.times.reverse()

    def ready_to_continue(self, message):
        print "!!!!!!!!!!!!!!speech is done"
        self.waiting = False

    def repeat(self, event):
        self.add_event(event)

    def execute_event(self, event):
        for a in self.events[event]['actions']:
            self.waiting = True
            print a
            for key in a:
                self.emitter.emit(Message(key, a[key]))
            timeout = 0
            while self.waiting and timeout < 10:
                time.sleep(1)

    def notify(self, timestamp, event):

        print event, self.config[event]
        self.execute_event(event)
        self.repeat(event)
        self.schedule()

    def get_times(self):
        if len(self.times) > 0:
            return [self.times.pop()]
        else:
            print 'No further events'
            return []

    def schedule(self):
        times = sorted(self.get_times())

        if len(times) > 0:
            self.cancel()
            t, event = times[0]
            now = self.get_utc_time()
            delay = max(float(t) - now, 1)
            print 'starting event in ' + str(delay)
            self.timer = Timer(delay, self.notify, [t, event])
            self.start()

    def handle_run_event(self, message):
        e = message.data.get('EventKeyword')
        self.execute_event(e)

    def handle_cancel_events(self, message):
        self.cancel()
        self.speak('Cancelling all events')


def create_skill():
    return EventSkill()
