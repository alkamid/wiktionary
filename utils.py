# -*- coding: utf-8 -*-

import requests

def get_nonmain_namespaces(site='pl.wiktionary'):
    url = 'https://{0}.org/w/api.php?action=query&meta=siteinfo&siprop=namespaces|namespacealiases&format=json'.format(site)
    non_main_namespaces = []
    try:
        result = requests.get(url).json()
        for alias in result['query']['namespacealiases']:
            if alias['id'] != 0:
                non_main_namespaces.append(alias['*'])
        for ns in result['query']['namespaces']:
            if ns != 0:
                non_main_namespaces.append(result['query']['namespaces'][ns]['*'])
    except:
        return []

    non_main_namespaces = non_main_namespaces + [a.replace(' ', '_') for a in non_main_namespaces if ' ' in a]
    return non_main_namespaces
