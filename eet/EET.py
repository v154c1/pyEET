'''
Created on 10. 10. 2016

@author: neneko
'''

from Trzba import *
from lxml import etree
from signing import Signing
import wsse
import requests
from eet_ns import NS_EET_URL
import utils
import eet_exceptions

class EET:

    def __init__(self, cert_file, password, provozovna=1, pokladna='lidicka', testing=True, eet_url='https://pg.eet.cz:443/eet/services/EETServiceSOAP/v3'):
        self._cert_file = cert_file
        self._testing = testing
        self._pokladna = pokladna
        self._provozovna = provozovna
        self._eet_url = eet_url
        self._signing = Signing(cert_file, password)

        components = self._signing.get_cert_subject().get_components()
        cn = [x for x in components if x[0] == 'CN']
        assert(len(cn) == 1)
        self._dic = cn[0][1]
        print('DIC: %s' % self._dic)

    def create_payment(self, poradi, amount, first=True, test=True):
        header = TrzbaHeader(first, test)
        return Trzba(header, poradi, self._dic, self._provozovna, self._pokladna, amount)

    def send_payment(self, payment):
        trzba_xml = payment.xml(self._signing)

        soap_xml = wsse.soap_wsse(trzba_xml, self._signing)

        soap_string = etree.tostring(soap_xml)
        open('/tmp/y.xml', 'wb').write(soap_string)

        resp = requests.post(self._eet_url, soap_string)
        resp.raise_for_status()
        try:
            reply = etree.XML(resp.content)
 #           print(etree.tostring(reply, pretty_print=4))
            header = utils.find_node(reply, 'Hlavicka', NS_EET_URL)
        except etree.XMLSyntaxError as e:
            raise eet_exceptions.BadResponse('Failed to parse response from server (%s)'%(str(e)))
        except eet_exceptions.NodeNotFound:
            raise eet_exceptions.BadResponse('Failed to process response - missing node Hlavicka')
        
        try:
            confirmation = utils.find_node(reply, 'Potvrzeni', NS_EET_URL)
            orig_bkp = utils.find_node(trzba_xml, 'bkp')
            bkp = header.get('bkp')
#            print('received bkp: %s, original: %s' % (bkp, orig_bkp.text))
            if bkp != orig_bkp.text:
                raise eet_exceptions.BadResponse('Wrong BKP in response!')
            
            response = {
                'date_received': header.get('dat_prij'),
                'uuid_reply': header.get('uuid_zpravy'),
                'bkp': bkp,
                'fik': confirmation.get('fik'), 
                'test': confirmation.get('test')}
        except eet_exceptions.NodeNotFound:
            try: 
                error = utils.find_node(reply, 'Chyba', NS_EET_URL)
                response = {
                    'date_rejected': header.get('dat_odmit'),
                    'fik': None, 
                    'test': error.get('test'), 
                    'kod':error.get('kod'), 
                    'message': error.text}
            except eet_exceptions.NodeNotFound:
                raise eet_exceptions.BadResponse('Failed to get data from server response')
        return response 
