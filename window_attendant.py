import json
import random
from datetime import datetime, timedelta
from typing import Optional


def get_window_attendant_message(date: Optional[datetime] = None, config_path: Optional[str] = None) -> Optional[str]:
    now = date if date is not None else datetime.now()
    path = config_path if config_path is not None else '/home/juhaodong/larkbot/window_attendant.json'
    with open(path, encoding='utf-8') as f:
        settings = json.load(f)

        attendants = [a for a in settings['attendants'] if a['disabled'] is None or not eval(a['disabled'], {
            'dayOfWeek': now.isoweekday()
        })]

        if len(attendants) < 1:
            return None

        rng = random.Random(int(now.strftime('%Y%m%d')))

        msg = str(eval(settings['message'], {
            'date': now.strftime(settings['dateFormat']),
            'attendant': rng.choice(attendants),
        }))

        return msg


def main():
    msg = get_window_attendant_message(
        date=datetime.now() + timedelta(days=5),
        config_path='window_attendant.json'
    )
    print(msg)


if __name__ == '__main__':
    main()
