from datetime import datetime, timezone
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record.setdefault('timestamp', datetime.now(timezone.utc).isoformat())
        log_record['level'] = log_record.get('level', record.levelname).upper()


formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
