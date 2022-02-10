import json
from datetime import datetime
import random


def get_window_attendant_message():
    now = datetime.now()
    with open('/home/juhaodong/larkbot/window_attendant.json', encoding='utf-8') as f:
        settings = json.load(f)

        attendants = [a for a in settings['attendants'] if a['disabled'] is None or not eval(a['disabled'], {
            'dayOfWeek': now.isoweekday()
        })]

        if len(attendants) < 1:
            return

        rng = random.Random(int(now.strftime('%Y%m%d')))

        msg = eval(settings['message'], {
            'date': now.strftime(settings['dateFormat']),
            'attendant': rng.choice(attendants),
        })

        return msg
