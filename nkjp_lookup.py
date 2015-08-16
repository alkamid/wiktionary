# coding=utf-8

import urllib.request, urllib.parse, urllib.error
import random

def nkjp_lookup(ngram):

        servlet="http://nkjp.uni.lodz.pl/NKJPSpanSearchXML"

        #Aby pobrać wyniki w formacie Microsoft Excel XML wywołujemy serwlet:
        #servlet="http://nkjp.uni.lodz.pl/NKJPSpanSearchExcelXML"


        #Zapytanie w składni PELCRA NKJP
        #ngrams=["to bardzo ciekawe","dobra wola","dobra rada","ciekawa sprawa", "pleść** bzdura**"]

        #Klucz dostępu (prosimy o kontakt w celu jego uzyskania)
        api_key="f6a11530-2382-11e4-8c21-0800200c9a66"

        #Maks. odstęp między słowami
        span=0
        #Zachowujemy szyk? true|false
        preserve_order="true"
        #Od którego wyniku zaczynamy?
        offset=0
        #Po czym sortujemy? srodek|lewa|prawa|title_mono|pubDate|channel title_mono to  tytuł publikacji/książki/gazety
        sort="srodek"
        #od 1 do 5000 na raz. Wartości > 5000 są przycinane.
        limit=3
        #Po czym grupujemy? (--- to brak grupowania)  title_mono|pubDate|channel|---|text_id
        #groupBy="title_mono"
        groupBy="---"
        #Limit grupowania (Przy ustawieniu --- ta zmienna jest pomijana)
        groupByLimit=3
        #Teksty nie wcześniejsze niż
        m_date_from=1989
        #Teksty nie późniejsze niż
        m_date_to=2010
        #Styl z taksonomii NKJP. Można podać > 1, rozdzielając przecinkami
        #http://nkjp.uni.lodz.pl/help.jsp#analiza_rejestru
        m_styles="---"
        #Kanał z taksonomii NKJP. Można podać > 1, rozdzielając przecinkami
        m_channels="---"
        #Tytuł książki, gazety, forum internetowego, itp.
        m_title_mono=""
        #Ale z wyłączeniem:
        m_title_mono_NOT=""
        #Tytuł tekstu, wątku, itp.
        m_text_title=""
        #Słowa kluczowe w pasującym akapicie
        m_paragraphKWs_MUST=""
        m_paragraphKWs_MUST_NOT=""
        m_nkjpSubcorpus="all"


        #A to musi już tak na razie być...
        dummystring="ąĄćĆęĘłŁńŃóÓśŚźŹżŻ"
        sid=random.random()

        params = urllib.parse.urlencode({'query': ngram, 'api_key':api_key,'offset': offset, 'span': span,'sort': sort, 'second_sort':'srodek', 'limit': limit,'groupBy':groupBy,'groupByLimit':groupByLimit,'preserve_order':preserve_order,'dummystring':dummystring,'sid':sid,'m_date_from':m_date_from,'m_date_to':m_date_to,'m_styles':m_styles,'m_channels':m_channels,'m_title_mono':m_title_mono,'m_title_mono_NOT':m_title_mono_NOT,'m_paragraphKWs_MUST':m_paragraphKWs_MUST,'m_paragraphKWs_MUST_NOT':m_paragraphKWs_MUST_NOT,"m_nkjpSubcorpus":m_nkjpSubcorpus}) 
        f = urllib.request.urlopen(servlet, params)
        return f.read()




