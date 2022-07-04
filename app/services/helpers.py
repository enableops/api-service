from datetime import datetime

current_timestamp = lambda: int(datetime.timestamp(datetime.now()))
