'''
Created on 12. 10. 2016

@author: neneko
'''


import hashlib
import base64
from lxml import etree
import uuid
import utils

TAX_NONE=0
TAX_BASIC=1
TAX_REDUCED=2
TAX_REDUCED2=3
TAX_TRAVEL=4
TAX_USED=5
TAX_USED_REDUCED=6
TAX_USED_REDUCED2=7
TAX_AMOUNT_TO_DRAW=8
TAX_AMOUNT_DRAW=9



class TrzbaHeader:

    def __init__(self, first=True, test=True):
        self.uuid = str(uuid.uuid4())
        self.dat_odesl = utils.get_current_time()
        self.prvni_zaslani = first
        self.overeni = test

    def xml(self):
        return etree.Element('Hlavicka',
                             uuid_zpravy=self.uuid,
                             dat_odesl=self.dat_odesl,
                             prvni_zaslani=str(self.prvni_zaslani).lower(),
                             overeni=str(self.overeni).lower())


class Trzba:

    def __init__(self, header, poradi, dic_poplatnika, provozovna, pokladna, amount, dat_trzby=None, dic_poverujiciho=None):
        self.header = header
        self.porad_cis = poradi
        self.dic_popl = dic_poplatnika
        self.dic_poverujici = dic_poverujiciho
        self.id_provoz = provozovna
        self.id_pokl = pokladna
        self.celk_trzba = amount
        self.dat_trzby = dat_trzby if dat_trzby else header.dat_odesl
        self.zakl_nepodl_dph = 0
        self.zakl_dan1 = 0
        self.dan1 = 0
        self.zakl_dan2 = 0
        self.dan2 = 0
        self.zakl_dan3 = 0
        self.dan3 = 0
        self.cest_sluzby = 0
        self.pouzit_zboz1 = 0
        self.pouzit_zboz2 = 0
        self.pouzit_zboz3 = 0
        self.urceno_cerp_zuct = 0
        self.cerp_zuct = 0
        

    def set_amount(self, tax_rate, base_amount, tax_amount):
        '''Sets amounts for different tax rates.
        
        Keyword arguments:
        tax_rate -- Tax rate. Use TAX_* constants
        base_amount -- Basic amount to calculate the tax
        tax_amount - - computed tax value'''
        if tax_rate == TAX_NONE:
            self.zakl_nepodl_dph = base_amount
        elif tax_rate == TAX_BASIC:
            self.zakl_dan1 = base_amount
            self.dan1 = tax_amount
        elif tax_rate == TAX_REDUCED:
            self.zakl_dan2 = base_amount
            self.dan2 = tax_amount
        elif tax_rate == TAX_REDUCED2:
            self.zakl_dan3 = base_amount
            self.dan3 = tax_amount
        elif tax_rate == TAX_TRAVEL:
            self.cest_sluzby = base_amount
        elif tax_rate == TAX_USED:
            self.pouzit_zboz1 = base_amount
        elif tax_rate == TAX_USED_REDUCED:
            self.pouzit_zboz2 = base_amount
        elif tax_rate == TAX_USED_REDUCED2:
            self.pouzit_zboz3 = base_amount
        elif tax_rate == TAX_AMOUNT_TO_DRAW:
            self.urceno_cerp_zuct = base_amount
        elif tax_rate == TAX_AMOUNT_DRAW:
            self.cerp_zuct = base_amount
        else:
            raise ValueError('Wrong value for tax_rate')
        return True
        
    def _get_pkp(self, signing):
        pkp = utils.prepare_pkp(self.dic_popl,
                                self.id_provoz,
                                self.id_pokl,
                                self.porad_cis,
                                self.dat_trzby,
                                self.celk_trzba)

        digest_pkp = signing.sign_text(pkp, 'sha256')
        digest_bkp = hashlib.sha1(digest_pkp).hexdigest()
        final_bkp = '-'.join([digest_bkp[8 * i:8 * i + 8]
                              for i in range(0, 5)])
        codes = etree.Element('KontrolniKody')
        pkp_node = etree.SubElement(codes, 'pkp',
                                    cipher='RSA2048',
                                    encoding='base64',
                                    digest='SHA256')

        pkp_node.text = base64.b64encode(digest_pkp)
        bkp_node = etree.SubElement(codes, 'bkp',
                                    encoding='base16',
                                    digest='SHA1')
        bkp_node.text = final_bkp
        return codes

    def xml(self, pkey):
        trzba = etree.Element(
            'Trzba', nsmap={None: 'http://fs.mfcr.cz/eet/schema/v3'})
        trzba.append(self.header.xml())
        data = etree.Element(
            'Data',
            dic_popl=str(self.dic_popl),
            porad_cis=str(self.porad_cis),
            id_provoz=str(self.id_provoz),
            id_pokl=str(self.id_pokl),
            dat_trzby=str(self.dat_trzby),
            celk_trzba=utils.format_num(self.celk_trzba),
            rezim="0")
        if self.dic_poverujici:
            data.set('dic_poverujiciho', self.dic_poverujici)
        trzba.append(data)
        trzba.append(self._get_pkp(pkey))
        return trzba
