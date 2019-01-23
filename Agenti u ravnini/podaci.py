#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import threading
from math import sqrt
from time import sleep
from protokol import Protokol,StanjeAgenta

#učitavanje podataka iz datoteke i prilagođavanje podataka internim strukturama programa
class PodaciDatoteka(threading.Thread):
    def __init__(self,datoteka):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.datoteka = datoteka
        self.lista_redaka=list()
        self.zaglavlje=list()
        self.matrica_susjednosti =list()
        self.imena_agenata = list()
        self.koordinate_agenata = list()

    #glavna metoda čitanja
    def procitaj(self):
        f=open(self.datoteka,"r")
        for line in f:
            l = line.strip()
            if len(l) > 0:
                self.lista_redaka.append(l)
        f.close()
        self.procitajZaglavlje()
        self.procitajMatricuSusjednosti()
        self.procitajKoordinate()

    #cita se zaglavlje i iz njega izvlaci broj agenata
    def procitajZaglavlje(self):
        self.zaglavlje = self.lista_redaka[0].split(":")
        self.brojAgenata = int(self.zaglavlje[1])

    #cita se matrica susjedstva
    def procitajMatricuSusjednosti(self):
        granicaRedaka = min(self.brojAgenata+1,len(self.lista_redaka))
        for i in range(1,granicaRedaka):
            redak = self.lista_redaka[i].split(",")
            redak_vrijednosti=list()
            for s in redak:
                redak_vrijednosti.append(int(s))
            self.matrica_susjednosti.append(redak_vrijednosti)

    #citaju se zapisi koordinata pojedinih agenata (polozaj, brzina, radijus i kut)
    def procitajKoordinate(self):
        for ag in range(0,self.brojAgenata):
            granicaRedaka = min(5*(ag+1)+self.brojAgenata+1,len(self.lista_redaka))
            tip = 0
            stanjeAgenta = StanjeAgenta()
            stanjeAgenta.brojAgenta = ag+1
            for i in range(5*ag+self.brojAgenata+1,granicaRedaka):
                redak = self.lista_redaka[i].split(":")
                if len(redak)<2:
                    continue
                koordinate = redak[1].split(",")
                if tip == 0:
                    self.imena_agenata.append(koordinate[0])
                elif tip == 1:
                    stanjeAgenta.radijus=float(koordinate[0])
                elif tip == 2:
                    stanjeAgenta.kut=float(koordinate[0])
                elif tip == 3:
                    for i in range(0,len(koordinate)):
                        stanjeAgenta.polozaj[i]=float(koordinate[i])
                elif tip == 4:
                    for i in range(0,len(koordinate)):
                        stanjeAgenta.brzina[i]=float(koordinate[i])
                        stanjeAgenta.norma_brzine+=(stanjeAgenta.brzina[i]*stanjeAgenta.brzina[i])
                    stanjeAgenta.norma_brzine = stanjeAgenta.radijus/5.0
                tip+=1
            
            self.koordinate_agenata.append(stanjeAgenta)
        granicaRedaka = min(4*self.brojAgenata+self.brojAgenata+1,len(self.lista_redaka))
        
    #ispisivacka metoda koja je sinkronizirana i koju koristi program generalno
    def ispis(self,sadrzaj):
        self.lock.acquire()
        print sadrzaj
        self.lock.release()

    #prikaz procitanih podataka za testiranje
    def test(self):
        print "Datoteka {0:s}".format(self.datoteka)
        print "Matrica susjedstva:"
        for red in self.matrica_susjednosti:
            for v in red:
                print "{0:d}".format(v),
            print " "
        print " "
        print "Agenti:"
        for ag in self.koordinate_agenata:
            print "Polozaj: ",
            print ag.polozaj
            print "Brzina: ",
            print ag.brzina
            print "Radijus: {0:0.4f}".format(ag.radijus)
            print "Kut: {0:0.4f}".format(ag.kut)


print "Ovo nije pocetni dio programa"
print "OK"

