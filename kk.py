import datetime
from datetime import date
now = datetime.datetime.now()
today = date.today()
if (now.day == 23 and now.hour==17 and now.minute==37):
  print("今天13.30开会", today)

