'''
Created on 15. 10. 2016

@author: neneko
'''

import datetime
import pytz
import eet_exceptions

def format_num(number):
    '''Format a number to an EET compatible format.
    
    Keyword arguments:
    number -- number to format
    '''
    return '%0.2f'%number

def format_time(time):
    '''Format a datetime object to an EET compatible format.
    
    Keyword arguments:
    time -- time to format, including a timezone
    '''
    st = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    return st[:-2]+':'+st[-2:]

def get_current_time(timezone = 'Europe/Prague'):
    '''Returns a formated datetime for EET.
    
    Keyword arguments:
    time -- time to format, including a timezone
    '''
    return format_time(datetime.datetime.now(pytz.timezone(timezone)))
    
def prepare_pkp(dic, provozovna, pokladna, uctenka, datum, trzba):
    '''Prepares PKP for EET message
    
    Keyword arguments:
    dic -- time to format, including a timezone
    provozovna
    pokladna
    uctenka
    datum
    trzba
    '''
    return '%s|%d|%s|%s|%s|%s'%(
        dic,
        provozovna,
        pokladna,
        uctenka,
        datum,
        format_num(trzba))

def find_node(root, tag, ns = None):
    '''Returns first node with specified name and namespace, or throws
    
    Keyword arguments:
    root -- Root of subtree to search (lxml.Element)
    tag -- name of XML tag to find
    ns -- Namespace URL for the tag (optional)
    '''
    if ns:
        node_tag = '{%s}%s' % (ns, tag)
        nodes = [x for x in root.iter() if x.tag == node_tag]
    else:
        nodes = [x for x in root.iter() if x.tag[-len(tag):] == tag]
    if len(nodes) < 1:
        raise eet_exceptions.NodeNotFound('Node %s not found'%tag)
    return nodes[0]
