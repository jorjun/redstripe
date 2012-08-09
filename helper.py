__author__ = 'jorjun technical services Ltd, 2009<jorjun@gmail.com>'
__all__ = ['Robots', 'ReportManagerBase', 'Log']


import os, sys
import time
from datetime import datetime
from multiprocessing import Process, Queue, JoinableQueue, Value, Lock
from multiprocessing.sharedctypes import ctypes
import re
import urllib2, httplib
import traceback

class Robots(object):
    NUM_USERS = Value(ctypes.c_int, 0)
    QUEUE = Queue()
    TASKS_Q = JoinableQueue()
    LOCK = Lock()
    
    def __init__(self, task_id, Manager):
        self.task_id = task_id
        self.Manager = Manager
        self.log = Manager.get_log(task_id)
        self.num_gets = 0
    
    @staticmethod
    def run(Manager):
        print >>Manager.RESULTS_LOG_FILE, 'task_id, num_users, req_time, latency, url, handler'
        Manager.RESULTS_LOG_FILE.flush()
        bots = [
            Robots(
                task_id=task_id, 
                Manager= Manager
            )
            for task_id in xrange(1, Manager.MAX_TASKS)
        ]
    
        tasks = [Process(target=bot) for bot in bots]
    
        for bot, task in zip(bots, tasks):
            task.start()

        Robots.TASKS_Q.join()
        Manager.RESULTS_LOG_FILE.close()
        
    @classmethod
    def get_one(cls, Manager):
        return Robots(
                task_id=1, 
                Manager=Manager
            )
    
    def __call__(self):
        Robots.NUM_USERS.value += 1
        Robots.TASKS_Q.put('task')
        report_lines = []
        for item in self.parse_log():
            log_url = item[6]
            handler = item[-1]
            url = '%s%s' % (self.log.url_prefix, log_url)
            req_time = self.time_stamp
            before_time = time.time()
            try:
                res = urllib2.urlopen(url, timeout = 15).read()
                time_delta = time.time() - before_time
                log_line =  self.Manager.LOG_FMT % (self.task_id, Robots.NUM_USERS.value, req_time, time_delta, url, handler)
            except IOError, e:
                log_line =  self.Manager.ERR_LOG_FMT % (self.task_id, Robots.NUM_USERS.value, req_time, url, handler)
            except httplib.BadStatusLine, e:
                log_line =  self.Manager.BAD_STAT_LOG_FMT % (self.task_id, Robots.NUM_USERS.value, req_time, url, handler)
                
            print log_line
            report_lines.append(log_line)

        Robots.QUEUE.put(report_lines)
        Robots.LOCK.acquire()
        for line in Robots.QUEUE.get():
            print >>self.Manager.RESULTS_LOG_FILE, line
        self.Manager.RESULTS_LOG_FILE.flush()
        Robots.LOCK.release()
        Robots.TASKS_Q.task_done()

    def parse_log(self):
        for line in self.log.lines:
            if self.num_gets >= self.Manager.MAX_TASK_GETS: break
            fields = line.split()
            log_url = fields[6]
            handler = self.log.get_filter_result(log_url)
            if handler is None: continue
            
            fields.append(handler)
            yield fields 
            self.num_gets += 1

    @property
    def time_stamp(self):
        return datetime.now().strftime(self.Manager.DATE_FMT)

    
class ReportManagerBase(object):
    @classmethod
    def get_log(cls, task_id):
        log_channel = task_id % len(cls.LOGS)
        return cls.LOGS[log_channel]
        
    
class Log(object):
    FOLDER = ''
    PATH = 'NO PATH'
    exclude_domains = [
        '',
    ]
    
    @property
    def path(self): return os.path.join(self.FOLDER, self.PATH)

    @property
    def url_prefix(self):
        url = self.URL
        if not url.startswith('http://'): url = 'http://%s'% url
        return url

    @property
    def lines(self): return open(self.path).readlines()

    def get_filter_result(self, url):
        """ 
        o Any forbidden EXCLUDE extension, and `url` is rejected
        o Any non-matching INCLUDE pattern, and `url` is rejected
        return None if rejected, else return matching url handler
        """
        for exc in self.EXCLUDE_EXTENSIONS:
            if url.endswith(exc): return None
            
        if self.INCLUDE_PATTERNS == {}:  return 'NO INCLUDE PATTERNS'
        for inc in self.INCLUDE_PATTERNS.keys():
            m = re.match(inc, url)
            if m:
                return self.INCLUDE_PATTERNS[inc]
        return None

    @staticmethod
    def re_compile(pattern):  return re.compile(pattern)
    