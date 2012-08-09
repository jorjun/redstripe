# Main
"""
Unit tests
"""
import os
from datetime import datetime

from redstripe.helper import Log, ReportManagerBase, Robots
import unittest


class LogBase(Log):
    """ Base settings for all logs
    """
    CASE = '.' # if running from outside containing folder, put relative path here
    FOLDER = os.path.join(CASE)
    EXCLUDE_EXTENSIONS = [
        '.pdf',
        '.jpg',
        '.gif',
        '.png',
        '.js',
        '.css',
        '.swf',
        '.ico',
        '.pdf',
        '.flv',
        '.cgi',
        '.pl',
    ]
    INCLUDE_PATTERNS = []

    
class Test_log(LogBase):
    PATH = 'test-access_log'
    URL = 'dev.aviva.co.uk'
    INCLUDE_PATTERNS = {
        r'^/distinct/(professional-advice\.htm|admin|calculators)': '/content/sites/oneaviva/distinct/django.wsgi', 
        r'/^risksolutions' : '/content/sites/oneaviva/risksolutions/django.wsgi',
        r'^/healthcarezone/individual_products/underwriting\.htm$': '/content/sites/oneaviva/healthcarezone/django.wsgi',
        r'^(/yourbusiness/?|/yourbusiness/.*\.(htm|html))$' : '/content/sites/oneaviva/yourbusiness/django.wsgi',
        r'^/adviser/faa/restricted/(|.*/|.*\.(htm|html))$' : '/content/sites/adviser_faa/django.wsgi',
        r'^/(?!(error-documents|submissions|cgi-bin|cpcalc|absencesolutions|adviser|backup|commercialfinance|corporatehealthzone|distinct|employersolutions|equityrelease|erfunding|fleetwisecare|floodresilienthome|grouphealthzone|happysback|healthcarezone|healthofthenation|landlord|legalprotection|lion|medical-journalism-awards|pahealthzone|RiskManager|riskservices|roadsense|tescohealthzone|wellnesssolutions|yourbusiness|yourwebteam|namechange))' : '/content/sites/aviva_uk/django.wsgi',
    }


class TestReportManager(ReportManagerBase):
    DATE_FMT    = "rs_test.txt"
    
    LOGS = [
        Test_log(), 
    ]
    REPORT = os.path.join(LogBase.CASE, datetime.today().strftime(DATE_FMT))
    MAX_TASKS = 1
    MAX_TASK_GETS = 10
    

class TestBasic(unittest.TestCase):
    def test_startup(self):
        #print('Current path:%s' % os.path.abspath(os.path.curdir))
        asimo = Robots.get_one(TestReportManager)
        log = asimo.log
        
        assert(
            log.get_filter_result('/adwiser/index.html') == '/content/sites/aviva_uk/django.wsgi'
        )
        assert(
            log.get_filter_result('/submissions') == None
        )
        assert(
            log.get_filter_result('/yourbusiness/') == '/content/sites/oneaviva/yourbusiness/django.wsgi'
        )
        assert(
            log.get_filter_result('/distinct/admin') == '/content/sites/oneaviva/distinct/django.wsgi'
        )
        
if __name__ == '__main__':
    unittest.main()