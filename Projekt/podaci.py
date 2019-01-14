#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import threading
from time import sleep

class StanjeAgenta:
    def __init__(self):
        self.polozaj = list()
        self.brzina = list()
        for i in range(0,3):
            self.polozaj.append(0.0)
            self.brzina.append(0.0)
        self.radijus  = 1.0
        self.kut = 0.0
        self.brojAgenta = 0

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

    def procitaj(self):
        f=open(self.datoteka,"r")
        for line in f:
            line=line.replace("\n","")
            if len(line)>0:
                self.lista_redaka.append(line)
        f.close()
        self.procitajZaglavlje()
        self.procitajMatricuSusjednosti()
        self.procitajKoordinate()

    def procitajZaglavlje(self):
        self.zaglavlje = self.lista_redaka[0].split(":")
        self.brojAgenata = int(self.zaglavlje[1])

    def procitajMatricuSusjednosti(self):
        granicaRedaka = min(self.brojAgenata+1,len(self.lista_redaka))
        for i in range(1,granicaRedaka):
            redak = self.lista_redaka[i].split(",")
            redak_vrijednosti=list()
            for s in redak:
                redak_vrijednosti.append(int(s))
            self.matrica_susjednosti.append(redak_vrijednosti)

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
                tip+=1
            self.koordinate_agenata.append(stanjeAgenta)
        granicaRedaka = min(4*self.brojAgenata+self.brojAgenata+1,len(self.lista_redaka))
        
            


    def ispis(self,sadrzaj):
        self.lock.acquire()
        print sadrzaj
        self.lock.release()

        
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

