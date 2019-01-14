#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import spade
from random import randint
from random import randrange
import threading
from time import sleep

from pracenjeAgenta import *

class Agent(spade.Agent.Agent):     
    def _setup(self):
        self.lista_komunikacije = list()
        self.lista_koordinata_susjeda = list()
        self.lista_susjednosti = list()
        self.azuriranje = False
        self.lock = threading.RLock()
        broj_agenata = len(self.podaciDatoteka.matrica_susjednosti)
        self.brojAgenta = self.koordinate.brojAgenta
        for i in range(0,broj_agenata):
            self.lista_susjednosti.append(self.podaciDatoteka.matrica_susjednosti[self.brojAgenta-1][i])
            self.lista_komunikacije.append(0)
            self.lista_koordinata_susjeda.append(None)

        self.sinkronizacijaIspisa = True  
        if 'naziv' in locals():
            self.naziv=self.name
        #inicijalizacija klasa ponasanja
        self.setDefaultBehaviour(PrimanjePoruka())

        #STANJA
        self.ZATRAZI_STANJA = 1
        self.AZURIRAJ = 2
        #PRIJELAZI
        self.ZATRAZENO = 10
        self.AZURIRANO = 20


        stanja = spade.Behaviour.FSMBehaviour()
        stanja.registerFirstState(ZatraziStanja(), self.ZATRAZI_STANJA)
        stanja.registerState(Azuriranje(), self.AZURIRAJ)
        stanja.registerTransition(self.ZATRAZI_STANJA, self.AZURIRAJ, self.ZATRAZENO)
        stanja.registerTransition(self.AZURIRAJ, self.ZATRAZI_STANJA, self.AZURIRANO)
        self.addBehaviour(stanja,None)

