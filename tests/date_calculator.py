"""
Judy can tell you the dates!

You: Judy!
Judy: [high beep]
You: Today!
Judy: [low beep] February 07

You: Judy!
Judy: [high beep]
You: Tomorrow!
Judy: [low beep] February 08

You: Judy!
Judy: [high beep]
You: Next Friday!
Judy: [low beep] February 17
"""

from datetime import datetime, timedelta
import judy

vin = judy.VoiceIn(adcdev='plughw:1,0',
                   lm='/home/pi/judy/resources/lm/0931.lm',
                   dict='/home/pi/judy/resources/lm/0931.dic')

vout = judy.VoiceOut(device='plughw:0,0',
                     resources='/home/pi/judy/resources/audio')

def handle(phrase):
    if phrase == 'TODAY':
        result = datetime.today()
    elif phrase == 'TOMORROW':
        result = datetime.today() + timedelta(days=1)
    else:
        next = 0
        target = None
        weekdays = {'MONDAY':    0,  # Python convention, Monday=0
                    'TUESDAY':   1, 
                    'WEDNESDAY': 2, 
                    'THURSDAY':  3, 
                    'FRIDAY':    4, 
                    'SATURDAY':  5, 
                    'SUNDAY':    6}

        # Pick up 'NEXT' and any weekday
        for word in phrase.split(' '):
            if word == 'NEXT':
                next += 1

            if word in weekdays:
                target = weekdays[word]
                break

        today = datetime.today()

        # How many days to target weekday?
        diff = target - today.weekday()
        if diff <= 0:
            diff += 7

        result = today + timedelta(weeks=next, days=diff)

    answer = result.strftime('%B %d')
    vout.say(answer)


judy.listen(vin, vout, handle)
