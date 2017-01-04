import unittest
import klasa as plw
import pywikibot as pwb

class TestFieldExtraction(unittest.TestCase):


    maxDiff = None
    def setUp(self):
        testpage = pwb.Page(pwb.Site('pl', 'wiktionary'), 'robić')
        testpagetext = testpage.getOldVersion(5306968)
        
        self.testHaslo = plw.Haslo('robić')
        self.testHaslo.content = testpagetext
        self.testHaslo.langs()
        self.testHaslo.listLangs[0].pola()

    def test_lang_in_header(self):
        self.assertEqual(self.testHaslo.listLangs[0].lang, 'polski')

    def test_examples(self):
        self.assertEqual(self.testHaslo.listLangs[0].subSections['przykłady'].text, "\n: (1.1) ''[[w|W]] [[ten|tej]] [[fabryka|fabryce]] [[robić|robią]] [[samochód|samochody]].''\n: (1.2) ''[[mój|Moja]] [[siostra]] [[dziś]] [[mieć|ma]] [[studniówka|studniówkę]] [[i]] [[od]] [[rano|rana]] [[robić|robi]] [[makijaż]].''")

if __name__ == '__main__':
    unittest.main()
