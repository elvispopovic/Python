#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import spade

from time import sleep
from podaci import *

# ponašanje agenta
class PrimanjePoruka(spade.Behaviour.Behaviour):
     #proces koji prima poruke
    def _process(self):
        self.msg=None
        podaci=self.myAgent.podaciDatoteka
        ime_agenta = self.myAgent.getName().split("@")[0]
        self.msg=self._receive(True,1) #blokirajuća
        if self.msg:
            if self.msg.getOntology() != "Presence": #presence šalje sustav
                if(self.msg.getOntology()=="Uskladjivanje" and self.msg.getPerformative()=="request"):
                    self.posaljiOdgovor(self.msg.sender.getName())
                elif(self.msg.getOntology()=="Uskladjivanje" and self.msg.getPerformative()=="inform"):
                    self.dopuniListuPodataka(self.msg.getContent())
            else: #stigao je presence
                podaci.ispis("Agent {0:s}: primljena je presence poruka: {1:s}.".format(ime_agenta,self.msg.getContent()))

    #metoda koja automatski šalje odgovor na upit o koordinatama, ima mutex sa ažuriranjem
    #kodira vlastite koordinate u poruku i šalje susjedima koji su zatražili te koordinate
    def posaljiOdgovor(self,agent):
        podaci = self.myAgent.podaciDatoteka
        posiljatelj = self.myAgent.getName().split("@")[0]
        primatelj = agent.split("@")[0]
        self.receiver = spade.AID.aid( name=agent, addresses=[ "xmpp://{0:s}".format(agent) ] )
        self.msg = spade.ACLMessage.ACLMessage()
        self.msg.setPerformative( "inform" )
        self.msg.setOntology( "Uskladjivanje" )
        self.msg.addReceiver( self.receiver ) 

        self.myAgent.lock.acquire()
        self.sadrzaj = "agent:{0:d};".format(self.myAgent.brojAgenta)
        self.sadrzaj += "radijus:{0:f};".format(self.myAgent.koordinate.radijus)
        self.sadrzaj += "kut:{0:f};".format(self.myAgent.koordinate.kut)
        self.sadrzaj += "polozaj:"
        polozaj = self.myAgent.koordinate.polozaj
        for i in range(0, len(polozaj)-1):
            self.sadrzaj += "{0:f},".format(polozaj[i])
        self.sadrzaj += "{0:f};".format(polozaj[len(polozaj)-1])
        self.sadrzaj += "brzina:"
        brzina = self.myAgent.koordinate.brzina
        for i in range(0, len(brzina)-1):
            self.sadrzaj += "{0:f},".format(brzina[i])
        self.sadrzaj += "{0:f};".format(brzina[len(brzina)-1])
        self.msg.setContent( self.sadrzaj )
        self.myAgent.lock.release()
        podaci.ispis("Agent {0:s} salje odgovor na zahtijev agentu {1:s}.".format(posiljatelj,primatelj))
        self.myAgent.send( self.msg )

    #ova metoda dekodira primljenu poruku od susjeda i upisuje sadržaj u listu koordinata susjeda
    def dopuniListuPodataka(self,content):
        ime_agenta = self.myAgent.getName().split("@")[0]
        podaci = self.myAgent.podaciDatoteka
        contsplt = content.split(";")
        broj_agenta = int(contsplt[0].split(":")[1])
        stanjeAgenta = StanjeAgenta()
        stanjeAgenta.brojAgenta = broj_agenta
        rowsplt = contsplt[1].split(":")
        if rowsplt[0]=="radijus":
            stanjeAgenta.radijus = float(rowsplt[1])
        else:
            stanjeAgenta.radijus = 0.0
        rowsplt = contsplt[2].split(":")
        if rowsplt[0]=="kut":
            stanjeAgenta.kut = float(rowsplt[1])
        else:
            stanjeAgenta.kut = 0.0
        rowsplt = contsplt[3].split(":")
        if rowsplt[0]=="polozaj":
            coordsplit = rowsplt[1].split(",")
            for i in range(0,len(coordsplit)):
                stanjeAgenta.polozaj[i]=float(coordsplit[i])
        else:
            for i in range(0,3):
                stanjeAgenta.polozaj[i]=0.0
        rowsplt = contsplt[4].split(":")
        if rowsplt[0]=="brzina":
            coordsplit = rowsplt[1].split(",")
            for i in range(0,len(coordsplit)):
                stanjeAgenta.brzina[i]=float(coordsplit[i])
        else:
            for i in range(0,3):
                stanjeAgenta.polozaj[i]=0.0
        self.myAgent.lista_komunikacije[broj_agenta-1]=0
        self.myAgent.lista_koordinata_susjeda[broj_agenta-1] = stanjeAgenta

                

class ZatraziStanja(spade.Behaviour.OneShotBehaviour):
    #proces koji šalje upit susjedima i čeka da odgovore - eksponencijalno čekanje
    def _process(self):
        lista_susjednosti = self.myAgent.lista_susjednosti
        imena_agenata = self.myAgent.podaciDatoteka.imena_agenata
        for i in range(0,len(lista_susjednosti)):
            if(lista_susjednosti[i]==1):
                self.posaljiZahtijev("{0:s}@127.0.0.1".format(imena_agenata[i]))
                self.myAgent.lista_komunikacije[i]=1
        
        exp_cekanje = 0.001 
        primljeno = False
        while primljeno == False:
            primljeno = True
            sleep(exp_cekanje)
            for v in self.myAgent.lista_komunikacije:
                if v == 1:
                    primljeno = False
            if(exp_cekanje<10.0):
                exp_cekanje*=10
        self._exitcode=self.myAgent.ZATRAZENO

    #ova metoda šalje zahtijev susjedima za koordinatama
    def posaljiZahtijev(self,agent):
        posiljatelj = self.myAgent.getName().split("@")[0]
        primatelj = agent.split("@")[0]
        podaci = self.myAgent.podaciDatoteka
        self.receiver = spade.AID.aid( name=agent, addresses=[ "xmpp://{0:s}".format(agent) ] )
        podaci.ispis("Agent {0:s} je zatrazio podatke od agenta {1:s}.".format(posiljatelj,primatelj))
        self.msg = spade.ACLMessage.ACLMessage()
        self.msg.setPerformative( "Request" )
        self.msg.setOntology( "Uskladjivanje" )
        self.msg.addReceiver( self.receiver ) 
        self.msg.setContent( "Posalji svoje podatke" )
        self.myAgent.send( self.msg )

class Azuriranje(spade.Behaviour.OneShotBehaviour):
    #metoda protokola: ovdje se ažuriraju vlastite koordinate na osnovu pristiglih koordinata susjeda.
    #metoda je sinkronizirana mutexom da se ne bi istovremeno moglo i ažurirati i slati vlastite koordinate
    def _process(self):
        podaci = self.myAgent.podaciDatoteka
        ime_agenta = self.myAgent.getName().split("@")[0]
        lista_susjeda = self.myAgent.lista_koordinata_susjeda
        self.myAgent.lock.acquire()
        sadrzajIspisa = ""
        #for a in self.myAgent.lista_koordinata_susjeda:
        for i in range(0,len(lista_susjeda)):
            a = lista_susjeda[i]
            if a != None:
                sadrzajIspisa += "{0:s}: Stanje susjednog agenta {1:d}: radijus: {2:.2f}, kut: {3:f}, polozaj x: {4:f}, y: {5:f},\
brzina x: {6:f}, y: {7:f}\n".format(ime_agenta,a.brojAgenta,a.radijus,a.kut,a.polozaj[0],a.polozaj[1],a.brzina[0],a.brzina[1])
            else:
                sadrzajIspisa += "{0:s}: Nema povezanosti sa agentom {1:d}.\n".format(ime_agenta,i+1)    
        podaci.ispis(sadrzajIspisa)
        self.myAgent.lock.release()
        podaci.ispis("Azurirano.")
        self._exitcode=self.myAgent.AZURIRANO