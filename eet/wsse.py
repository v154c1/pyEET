'''
Created on 12. 10. 2016

@author: neneko
'''

from lxml import etree
import StringIO
import hashlib
import uuid
from eet_ns import *
from string import Template
import base64
from utils import find_node

envelope_template = Template('''<${soap}:Envelope xmlns:${soap}="${soap_url}">
<${soap_env}:Header xmlns:${soap_env}="${soap_env_url}">
            <${wsse}:Security xmlns:${wsse}="${wsse_url}" xmlns:${wsu}="${wsu_url}" ${soap}:mustUnderstand="1">
               <${wsse}:BinarySecurityToken ${wsu}:Id="${cert_id}" EncodingType="${encoding_base64_url}" ValueType="${value_x509_url}">${sec_token}</${wsse}:BinarySecurityToken>
               <${ds}:Signature xmlns:${ds}="${ds_url}" Id="${sig_id}">
                  <${ds}:SignedInfo xmlns:${ds}="${ds_url}">
                     <${ds}:CanonicalizationMethod Algorithm="${ec_url}">
                        <${ec}:InclusiveNamespaces xmlns:${ec}="${ec_url}" PrefixList="${soap}"/>
                     </${ds}:CanonicalizationMethod>
                     <${ds}:SignatureMethod Algorithm="${algo_sha256}"/>
                     <${ds}:Reference URI="#${body_id}">
                        <${ds}:Transforms>
                           <${ds}:Transform Algorithm="${ec_url}">
                              <${ec}:InclusiveNamespaces xmlns:${ec}="${ec_url}" PrefixList=""/>
                           </${ds}:Transform>
                        </${ds}:Transforms>
                        <${ds}:DigestMethod Algorithm="${algo_digest_sha256}"/>
                        <${ds}:DigestValue></${ds}:DigestValue>
                     </${ds}:Reference>
                  </${ds}:SignedInfo>
                  <${ds}:SignatureValue></${ds}:SignatureValue>
                  <${ds}:KeyInfo Id="${key_id}">
                     <${wsse}:SecurityTokenReference ${wsu}:Id="${sec_token_id}">
                        <${wsse}:Reference URI="#${cert_id}" ValueType="${value_x509_url}"/>
                     </${wsse}:SecurityTokenReference>
                  </${ds}:KeyInfo>
               </${ds}:Signature>
            </${wsse}:Security>
         </${soap_env}:Header>
         <${soap}:Body wsu:Id="${body_id}" xmlns:${wsu}="${wsu_url}" xmlns:${soap}="${soap_url}"></${soap}:Body>
</${soap}:Envelope>''')

namespaces_dict = {
    'soap': NS_SOAP,
    'soap_url': NS_SOAP_URL,
    'soap_env': NS_SOAP_ENV,
    'soap_env_url': NS_SOAP_ENV_URL,
    'wsse': NS_WSSE,
    'wsse_url': NS_WSSE_URL,
    'wsu': NS_WSU,
    'wsu_url': NS_WSU_URL,
    'ds': NS_DS,
    'ds_url': NS_DS_URL,
    'ec': NS_EC,
    'ec_url': NS_EC_URL,
    'eet_url': NS_EET_URL,
    'algo_sha256': ALGORITHM_SHA256,
    'algo_digest_sha256': ALGORITHM_DIGEST_SHA256,
    'value_x509_url': VALUE_X509_URL,
    'encoding_base64_url': ENCODING_BASE64_URL

}


def get_normalized_subtree(node, includive_prefixes=[]):
    tree = etree.ElementTree(node)
    ss = StringIO.StringIO()
    tree.write_c14n(
        ss, exclusive=True, inclusive_ns_prefixes=includive_prefixes)
    return ss.getvalue()


def calculate_node_digest(node):
    data = get_normalized_subtree(node, ['soap'])
    return hashlib.sha256(data).digest()



def soap_wsse(payload_node, signing):
    '''Stores payload_node into a SOPA envelope and calculates the wsse signature
    
    Keyword arguments:
    payload_node - top node for the payload (lxml.Element)
    signing - signing object (eet.Signing)
    '''
    # Prepare parser
    parser = etree.XMLParser(remove_blank_text=True, ns_clean=False)
    # Prepare IDs for header
    body_id = 'id-'+uuid.uuid4().get_hex()
    cert_id = 'X509-'+uuid.uuid4().get_hex()
    sig_id = 'SIG-' + uuid.uuid4().get_hex()
    key_id = 'KI-'+ uuid.uuid4().get_hex()
    sec_token_id='STR-'+ uuid.uuid4().get_hex()

#     body_id = 'id-874636aa99da4d19a3edc6013b81c725'
#     cert_id = 'X509-67a252aca8ae4828aecfb092128277d9'
#     sig_id = 'SIG-fe080e8070694b61ab02fc821222c9f9'
#     key_id = 'KI-95fc8c906a3f4ac1a13145e1b795164c'
#     sec_token_id = 'STR-020d884701ec45d7a619849e112cfbfa'

    values = dict(namespaces_dict)
    values.update({'body_id': body_id, 'cert_id': cert_id, 'sig_id': sig_id, 'key_id':
                   key_id, 'sec_token_id': sec_token_id, 'sec_token': base64.b64encode(signing.get_cert_binary())})

    # Create SOAP envelope
    envelope = etree.XML(envelope_template.substitute(values), parser=parser)

    # Find soap:Body
    body = find_node(envelope, 'Body', NS_SOAP_URL)
    # Fill in Trzby into soap:Body
    body.append(payload_node)
    # Calculate digest of soap:Body
    body_digest = calculate_node_digest(body)

    # Find ds:DigestValue and store the computed digest
    digest_node = find_node(envelope, 'DigestValue', NS_DS_URL)
    digest_node.text = base64.b64encode(body_digest)

    # Find ds:SignedInfo node and get normalized text of it
    signature_node = find_node(envelope, 'SignedInfo', NS_DS_URL)
    normalized_signing = get_normalized_subtree(signature_node, ['soap'])
    
    # FInd ds:SignatureValue and store there signature of ds:SignedInfo
    signature_value_node = find_node(envelope, 'SignatureValue', NS_DS_URL)
    signature_value_node.text = base64.b64encode(
        signing.sign_text(normalized_signing, 'sha256'))

    return envelope
