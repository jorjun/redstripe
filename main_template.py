# main template
"""
Building a new logging case

o Create a new case folder, and copy this template to 'main.py'
  o Add `logs` folder for apache logs
  o Add `reports` folder for analysis reports
  
o Configure your log requirements at both the base level 
    and for each individual log required.
o run: python yourcase/main.py
"""

import os
from datetime import datetime

from redstripe.helper import Log, ReportmanagerBase, Robots


class LogBase(Log):
    """ Base settings for all logs
    """
    CASE = 'yourcase'                   # base path to case
    FOLDER = os.path.join(CASE, 'logs') # sub path to apache access log
    exclude_domains = [
        '',
    ]

class YourSite_log(LogBase):
    PATH = 'yoursite-access_log' # apache access log name
    URL = 'dev.yoursite.com'     # URL to test

    
class AnotherSite_log(LogBase):
    PATH = 'anothersite-access_log'
    URL = 'dev.anothersite.co.uk'

    
class Reportmanager(ReportmanagerBase):
    DATE_FMT    = "rs_%y%m%d%H%M%S.txt" # report name format
    REPORT = os.path.join(LogBase.CASE, 'reports', 
            datetime.today().strftime(DATE_FMT)) # Report path
    
    LOGS = [                # List of logs (above) to process
        YourSite_log(), 
        AnotherSite_log(),
    ]
    MAX_TASKS = 10      # Number of concurrent processes
    NEW_TASK_DELAY = 10 # Delay before starting next process
    MAX_TASK_GETS = 100 # Maximum number of gets / process


if __name__ == '__main__':
    Robots.run(ReportManager)
