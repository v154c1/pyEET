'''
Created on 12. 10. 2016

@author: neneko
'''
from OpenSSL import crypto


class Signing(object):

    def __init__(self, pkcs, password):
        self._pkcs = crypto.load_pkcs12(open(pkcs).read(), password)
        self._cert = self._pkcs.get_certificate()
        self._key = self._pkcs.get_privatekey()

    def sign_text(self, data, digest='sha256'):
        return crypto.sign(self._key, data, digest)

    def get_cert_subject(self):
        return self._cert.get_subject()

    def get_cert_binary(self):
        return crypto.dump_certificate(crypto.FILETYPE_ASN1, self._cert)
