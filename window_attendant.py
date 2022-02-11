import json
from datetime import datetime, timedelta
import random


def get_window_attendant_message(date: datetime = None, config_path: str = None):
    now = date if date is not None else datetime.now()
    path = config_path if config_path is not None else '/home/juhaodong/larkbot/window_attendant.json'
    with open(path, encoding='utf-8') as f:
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


def main():
    msg = get_window_attendant_message(
        date=datetime.now() + timedelta(days=5),
        config_path='window_attendant.json'
    )
    print(msg)


if __name__ == '__main__':
    main()
