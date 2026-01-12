
import logging

def job_log_level(status, duration):
    return (logging.ERROR if status != 'done'
        else logging.WARNING if duration > 2
        else logging.INFO if duration > .2
        else logging.DEBUG)
