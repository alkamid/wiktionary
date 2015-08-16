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
import aTergo
import resource
from statystyka import *
from klasa import readRCLimit, checkForNewDumps

def main():

	lastDump = readRCLimit('statystyka')
	newDump = checkForNewDumps(lastDump)
	#aTergo.aTergo(lastDump)

	if newDump == 1:
		return 0 # new dump not found, do nothing

	else:
		print('Found new dump (%s), processing... (old dump was %s)' % (newDump, lastDump))
		brakCzesciMowy.brakCzesciMowy(newDump)
		rzeczownik_rodzaj.rzeczownikRodzaj(newDump)
		rzeczownik_rodzaj_niepotrzebny.rzeczownikRodzajNiepotrzebny(newDump)
		fraz.fraz(newDump)
		czescimowy.czescimowy(newDump)
		czescimowyReplace.czescimowyReplace()
		frequencyList.frequencyList(newDump)
		missingLangs.missingLangs(newDump)
		statystyka(lastDump, newDump)
		
	
if __name__ == '__main__':
	main()


