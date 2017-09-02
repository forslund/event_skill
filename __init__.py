import sys
from os.path import abspath
from mycroft.skills.scheduled_skills import ScheduledSkill, Timer
from adapt.intent import IntentBuilder
from mycroft.messagebus.message import Message
from mycroft.skills.intent_service import IntentParser
import time

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
        self.times = []
        self.skill_events = self.config
        self.intent_parser = IntentParser(self.emitter)
        for e in self.skill_events:
            self.register_vocabulary(e, 'EventKeyword')
            logger.debug(e)
            if 'time' in self.skill_events[e]:
                self.add_skill_event(e)

        intent = IntentBuilder('EventIntent') \
            .require('EventKeyword') \
            .build()
        self.register_intent(intent, self.handle_run_event)

        self.register_vocabulary('cancel events', 'CancelEventsKeyword')
        intent = IntentBuilder('CancelEventsIntent') \
            .require('CancelEventsKeyword') \
            .build()
        self.register_intent(intent, self.handle_cancel_events)

        self.emitter.on('recognizer_loop:audio_output_end',
                        self.ready_to_continue)
        self.schedule()

    def add_skill_event(self, event):
        now = self.get_utc_time()
        conf_times = self.skill_events[event]['time']
        if not isinstance(conf_times, list):
            conf_times = [conf_times]
        for t in conf_times:
            time = self.get_utc_time(t)
            if time <= now:
                time += self.SECONDS_PER_DAY
            self.times.append((time, event))
            self.times = sorted(self.times)
            self.times.reverse()

    def ready_to_continue(self, message):
        self.waiting = False

    def repeat(self, event):
        self.add_skill_event(event)

    def execute_event(self, event):
        for a in self.skill_events[event]['actions']:
            self.waiting = True
            for key in a:
                skill_id = self.intent_parser.get_skill_id(key)
                if int(skill_id) == 0:
                    continue
                key = str(skill_id) + ":" + key
                self.emitter.emit(Message(key, a[key], self.message_context))
            timeout = 0
            while self.waiting and timeout < 10:
                time.sleep(1)

    def notify(self, timestamp, event):

        self.execute_event(event)
        self.repeat(event)
        self.schedule()

    def get_times(self):
        if len(self.times) > 0:
            return [self.times.pop()]
        else:
            logger.debug('No further events')
            return []

    def schedule(self):
        times = sorted(self.get_times())

        if len(times) > 0:
            self.cancel()
            t, event = times[0]
            now = self.get_utc_time()
            delay = max(float(t) - now, 1)
            logger.debug('starting event in ' + str(delay))
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
