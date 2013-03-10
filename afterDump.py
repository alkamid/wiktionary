#!/usr/bin/python
# -*- coding: utf-8 -*-

import brakCzesciMowy
import rzeczownik_rodzaj
import rzeczownik_rodzaj_niepotrzebny
import missingLangs
import fraz
import czescimowy
import czescimowyReplace
import frequencyList
	
def main():
	data = u'20130228'
	brakCzesciMowy.brakCzesciMowy(data)
	rzeczownik_rodzaj.rzeczownikRodzaj(data)
	rzeczownik_rodzaj_niepotrzebny.rzeczownikRodzajNiepotrzebny(data)
	fraz.fraz(data)
	czescimowy.czescimowy(data)
	czescimowyReplace.czescimowyReplace()
	frequencyList.frequencyList(data)
	missingLangs.missingLangs(data)
	
if __name__ == '__main__':
	main()


