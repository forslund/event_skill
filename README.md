Event Skill
=====================

A configurable skill that allows the user to configure multiple skills that should be launched at a keyword or at a specific time.

In the mycroft config you define keywords with a list of actions to be taken when the keyword is invoked.

Example Config:

```json
  "EventSkill": {
    "status update": {
        "actions": [{"TimeIntent": {}},
                    {"CurrentWeatherIntent": {}}
        ]
    },
    "wakeup": {
        "actions": [
          {"SpeakIntent": {"Words": "Good morning Sunshine"}},
          {"TimeIntent": {}},
          {"CurrentWeatherIntent": {}},
          {"NextDayWeatherIntent": {}},
          {"NPRNewsIntent": {}}
      ],
      "time": "06:45"
    }
  }
```

In above example when a user says *Hey Mycroft, give me a status update*, the event skill will launch the **status update** event and perform all intents listed under actions. In this case report time and the current weather.

The events are schedulable as well by defining the `time` parameter. The **wakeup** example will be triggered 06:45 each wake the user with a friendly *Good morning Sunshine* Followed by a report of the weather and then the NPR news.
