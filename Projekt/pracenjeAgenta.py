#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import spade
from time import sleep

# ponašanje agenta

class PrimanjePoruka(spade.Behaviour.Behaviour):
    def _process(self):
        self.msg=None
        podaci=self.myAgent.podaciDatoteka
        self.msg=self._receive(True,1) #blokirajuća
        if self.msg:
            if self.msg.getOntology() != "Presence": #presence šalje sustav
                if(self.msg.getOntology()=="Uskladjivanje" and self.msg.getPerformative()=="request"):
                    self.posaljiOdgovor(self.msg.sender.getName())
                elif(self.msg.getOntology()=="Uskladjivanje" and self.msg.getPerformative()=="inform"):
                    self.dopuniListuPodataka(self.msg.sender.getName(),self.msg.getContent())
            else: #stigao je presence
                podaci.ispis(self.myAgent.naziv+": Primljena je presence poruka: "+self.msg.getContent())

    def posaljiOdgovor(self,agent):
        podaci = self.myAgent.podaciDatoteka
        posiljatelj = self.myAgent.name
        self.receiver = spade.AID.aid( name=agent, addresses=[ "xmpp://{0:s}".format(agent) ] )
        self.msg = spade.ACLMessage.ACLMessage()
        self.msg.setPerformative( "inform" )
        self.msg.setOntology( "Uskladjivanje" )
        self.msg.addReceiver( self.receiver ) 
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
        podaci.ispis("{0:s} salje odgovor na zahtijev agentu {1:s}".format(posiljatelj,agent))
        self.myAgent.send( self.msg )

    def dopuniListuPodataka(self,agent,content):
        podaci = self.myAgent.podaciDatoteka
        posiljatelj = self.myAgent.name
        agsplt = agent.split("@")[0].split("_")
        broj_agenta = int(agsplt[len(agsplt)-1])
        self.myAgent.lista_komunikacije[broj_agenta-1]=0
        podaci.ispis("{0:s} je dobio odgovor {1:s}".format(self.myAgent.naziv,content))


                

class ZatraziStanja(spade.Behaviour.OneShotBehaviour):
    def _process(self):
        lista_susjednosti = self.myAgent.lista_susjednosti
        for i in range(0,len(lista_susjednosti)):
            if(lista_susjednosti[i]==1):
                self.posaljiZahtijev("agent_{0:d}@127.0.0.1".format(i+1))
                self.myAgent.lista_komunikacije[i]=1
        
        exp_cekanje = 0.001 #ceka da svi agenti odgovore i to cekanje je eksponencijalno
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

    def posaljiZahtijev(self,agent):
        podaci = self.myAgent.podaciDatoteka
        posiljatelj = self.myAgent.name
        self.receiver = spade.AID.aid( name=agent, addresses=[ "xmpp://{0:s}".format(agent) ] )
        podaci.ispis("{0:s} je zatrazio podatke od agenta {1:s}".format(posiljatelj,agent))
        self.msg = spade.ACLMessage.ACLMessage()
        self.msg.setPerformative( "Request" )
        self.msg.setOntology( "Uskladjivanje" )
        self.msg.addReceiver( self.receiver ) 
        self.msg.setContent( "Posalji svoje podatke" )
        self.myAgent.send( self.msg )

class Azuriranje(spade.Behaviour.OneShotBehaviour):
    def _process(self):
        podaci = self.myAgent.podaciDatoteka
        podaci.ispis("Azurirano.")
        self._exitcode=self.myAgent.AZURIRANO