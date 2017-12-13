#!/usr/bin/python
# -*- coding: utf-8 -*-
#


DOCUMENTATION = '''
---

'''

EXAMPLES = '''


'''

import socket


try:
    import json
    import requests
except ImportError:
    requests_found = False
else:
    requests_found = True


class BigIpCommon(object):
    def __init__(self, module):
        self._username = module.params.get('user')
        self._password = module.params.get('password')
        self._hostname = module.params.get('server')
        self._transactionId = module.params.get('transactionId')
        self._partition = module.params.get('partition')
        self._name = module.params.get('name')
        self._description = module.params.get('description')
        self._hasParent = module.params.get('hasParent')
        self._virtual = module.params.get('virtual')
        self._manualVirtualServers = []	#module.params.get('manualVirtualServers')
        self._parentPolicyName = module.params.get('parentPolicyName')
        self._appLang = module.params.get('lang')
        self._enforceMode = module.params.get('enforcementMode')
        self._validate_certs = module.params.get('validate_certs')
	self._virtualServers = ["/" + self._partition + "/" + self._virtual]

class BigIpRest(BigIpCommon):
    def __init__(self, module):
        super(BigIpRest, self).__init__(module)

        self._uri = 'https://%s/mgmt/tm/asm/policies' % (self._hostname)

        self._headers = {'Content-Type': 'application/json', 'X-F5-REST-Coordination-Id': self._transactionId}
        
	self._payload = {
            "name": self._name, 
            "description": self._description,
            "partition": self._partition,
            "hasParent": self._hasParent,
	    "parentPolicyName": self._parentPolicyName,
	    "virtualServers": self._virtualServers,
	    "manualVirtualServers": self._manualVirtualServers, 
            "applicationLanguage": self._appLang,
            "enforcementMode": self._enforceMode
        }

    def read(self):
        resp = requests.get(self._uri,
                            auth=(self._username, self._password),
                            verify=self._validate_certs)

        if resp.status_code != 200:
            return {}
        else:
            return resp.json() #['name']

    def run(self):
        changed = False
        current = self.read()

        if current == self._name:
            return False

        resp = requests.post(self._uri,
                            headers=self._headers,
                            auth=(self._username, self._password),
                            data=json.dumps(self._payload),
                            verify=self._validate_certs)


        if resp.status_code == 200:
	    changed = True
        else:
	    res = resp.json()
	    #raise Exception(res['message'])
	    changed = False
        return changed



def main():
    changed = False

    module = AnsibleModule(
       argument_spec=dict(
            server=dict(required=True),
            transactionId=dict(default=''),
            partition=dict(default='Common'),     
            name=dict(required=True),
            description=dict(default=''),
	    virtual=dict(required=True),
	    hasParent=dict(default='true'),
#	    manualVirtualServers=dict(default=[]),
	    parentPolicyName=dict(default='/Common/myParentPolicy'),
	    caseInsensitive=dict(default='false', type='bool'),
            lang=dict(default='utf-8', choices=['utf-8', 'western']),
            enforcementMode=dict(default='blocking', choices=['blocking', 'transparent']),
            user=dict(required=True, aliases=['username']),
            password=dict(required=True),
            validate_certs=dict(default='no', type='bool')
        )

    )


    obj = BigIpRest(module)


    asmpolicy = obj.run()
    if asmpolicy:
        changed = True
 
    module.exit_json(changed=changed, policy=asmpolicy)



from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()

