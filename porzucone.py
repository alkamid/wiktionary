# -*- coding: utf-8 -*-

# find Polish orphans - pages that are not linked by other pages from
# the main namespace

from pywikibot import Category
import pywikibot
from pywikibot import pagegenerators
import datetime
import config
from shutil import move

def main():

    site = pywikibot.Site()
    
    # fetch Polish pages only
    cat_allpages = Category(site,'Kategoria:polski (indeks)')
    # dialects are excluded, it would be too difficult to link all of them
    cat_dialects = Category(site, 'Kategoria:Polski_(dialekty_i_gwary)')

    list_allpages = pagegenerators.CategorizedPageGenerator(cat_allpages)
    list_dialects = set(pagegenerators.CategorizedPageGenerator(cat_dialects, recurse=True))

    count_all = 0
    
    intro = ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n'
             '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
             '<html xmlns="http://www.w3.org/1999/xhtml\nxml:lang="pl">\n'
             '<head>\n<meta http-equiv="content-type" content="text/html; charset=UTF-8" />\n'
             '</head><body>')
    
    intro += ('Poniżej znajduje się lista polskich haseł, do których '
              'nie linkuje żadne inne hasło z głównej przestrzeni nazw. W związku '
              'z tym trudno trafić do takiego hasła inaczej niż przez bezpośrednie jego '
              'wyszukanie. Jeśli możesz, dodaj w innym haśle odnośnik do porzuconego '
              'słowa, np. w przykładach lub pokrewnych.')
    
 
    with open('{0}public_html/porzucone.html.1'.format(config.path['home']), 'w', encoding='utf-8') as f:
        f.write(intro)
        for page in list_allpages:
            if page not in list_dialects:
                refs = list(page.getReferences(namespaces=0, total=2)) # only look in the main namespace (because virtually all pages are references somewhere, e.g. in missing pronunciation lists)
                try: refs.remove(page) # reference search is limited to 2. Then the page itself is removed (because on pl.wikt we often self-link pages in examples of usage)
                except ValueError:
                    pass
            
            if len(refs) == 0:
                try: f.write('\n<br /><a href="http://pl.wiktionary.org/wiki/{0}">{0}</a>'.format(page.title()))
                except UnicodeEncodeError:
                    print('Unicode Error: ', page.title())
                    pass
                count_all += 1

        date_now = datetime.datetime.now() + datetime.timedelta(hours=2)
        f.write(date_now.strftime("\nOstatnia aktualizacja listy: %Y-%m-%d, %H:%M:%S"))
        f.write('<br />: Licznik porzuconych: {0}'.format(count_all))
        f.write('</body></html')

    move('{0}public_html/porzucone.html.1'.format(config.path['home']), '{0}public_html/porzucone.html'.format(config.path['home']))

if __name__ == '__main__':
    try:
        main()
    finally:
        pywikibot.stopme()
