import urllib.request, urllib.parse, urllib.error
import ssl
import json
import config

def nkjp_lookup_new(input_query, max_results=10):

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = 'https://mantel.pelcra.pl/solr/nkjp'
    usr = config.nkjp['new_uname']
    passw = config.nkjp['new_pwd']

    handler = '/spans'
    q = '*:*'
    annot = 'true'
    postSort = 'right'
    spanField = 'utt_tagged'
    fl = 'authors,genre,id,medium_id,text_id,title_a_s,title_j_s,title_m_s,seq,pub_date,medium'
    start = 0
    rows = max_results

    query = 'q=' + q + '&spanq=' + urllib.parse.quote(input_query) + '&annot=' + annot + '&postSort='\
            + postSort + '&spanField' + spanField + '&fl=' + fl + '&start='\
            + str(start) + '&rows=' + str(rows)

    params = urllib.parse.urlencode({'u': usr, 'p':passw,'h': handler, 'q': query})
    req = urllib.request.urlopen(url + '?' + params, context=ctx)

    result = req.read().decode('utf-8')

    return json.loads(result)

def nkjp_find_context(seq, text_id):

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = 'https://mantel.pelcra.pl/solr/nkjp'
    usr = config.nkjp['new_uname']
    passw = config.nkjp['new_pwd']

    handler = '/select'
    q = 'seq:' + str(seq) + ' AND text_id:' + text_id
    annot = 'true'
    postSort = 'right'
    spanField = 'utt_tagged'
    fl = 'authors,genre,id,medium_id,text_id,title_a_s,title_j_s,title_m_s,utt'
    fl = 'utt_tagged,utt'

    rows = 10

    query = 'q=' + q + '&rows=' + str(rows) + '&fl=' + fl

    params = urllib.parse.urlencode({'u': usr, 'p':passw,'h': handler, 'q': query})
    req = urllib.request.urlopen(url + '?' + params, context=ctx)

    result = req.read().decode('utf-8')

    return json.loads(result)['response']['docs']

#usage:
#res = nkjp_lookup_new('(<lemma=położyć> się <lemma=spać>)')
#res = nkjp_find_context(seq=3643, text_id='T9RX')
