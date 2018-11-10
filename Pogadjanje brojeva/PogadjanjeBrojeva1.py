#!/usr/bin/env python
# -*- coding: utf-8 -*-

import spade
import sys
from time import sleep
from random import randint
from random import randrange


class Igrac(spade.Agent.Agent):

    class BColors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'


    #slijede tri ponasanja koja su stanja automata
    #prvo stanje
    class ZamisljanjeBroja(spade.Behaviour.OneShotBehaviour):
        def _process(self):
            sleep(randint(1,5)/10.0)
            if(self.myAgent.verbose):
                self.myAgent.Ispis("%s: ulazi u stanje zamisljanja."%self.myAgent.ime,True,True)
            if self.myAgent.naRedu == False:
                self._exitcode = self.myAgent.NIJE_NA_REDU
                return 
            self.myAgent.zamisljeniBroj = randint(1,10)
            self.myAgent.Ispis("%s: Zamislio sam broj." %self.myAgent.ime)
            self.myAgent.Ispis("(%s je zamislio broj %d.)"%(self.myAgent.ime,self.myAgent.zamisljeniBroj),True,True)
            
            self._exitcode=self.myAgent.BROJ_ZAMISLJEN
            
    #drugo stanje
    class Pogadjanje(spade.Behaviour.OneShotBehaviour):
        def _process(self):
            sleep(randint(1,5)/10.0)
            if(self.myAgent.verbose):
                self.myAgent.Ispis("%s: ulazi u stanje pogadjanja."%self.myAgent.ime,True,True)
            self.myAgent.SlanjePoruke("Prisutan",self.myAgent.suprotni,"Ovdje sam!")
            while True:
                self.msg = self.myAgent.SkidanjePoruke()
                if self.msg.getOntology()!="Prisutan":
                    sleep(1)
                else:
                    break
            while True:
                self.msg = self.myAgent.SkidanjePoruke()
                if self.msg.getOntology()!="Pogodi":
                    sleep(1)
                else:
                    break;
            broj = randint(1,10)
            self.myAgent.Ispis("%s: Pokušavam sa brojem %d" %(self.myAgent.ime,broj))
            self.myAgent.SlanjePoruke("Pogadjanje",self.myAgent.suprotni,str(broj))
            #primanje odgovora
            while True:
                self.msg = self.myAgent.SkidanjePoruke()
                if self.msg.getOntology()!="Ispravno" and self.msg.getOntology()!="Neispravno":
                    sleep(1)
                else:
                    break

            if self.msg.getOntology()=="Ispravno":
                self.myAgent.naRedu = True
                self._exitcode = self.myAgent.POGODIO_SAM
            else:
                self._exitcode = self.myAgent.NISAM_POGODIO

    #trece stanje
    class ProvjeraPogadjanja(spade.Behaviour.OneShotBehaviour):
        def _process(self):
            sleep(randint(1,5)/10.0)
            if(self.myAgent.verbose):
                self.myAgent.Ispis("%s: ulazi u stanje provjere pogadjanja."%self.myAgent.ime,True,True)
            self.msg = None
            while True:
                self.msg = self.myAgent.SkidanjePoruke()
                if self.msg.getOntology()!="Prisutan":
                    sleep(1)
                else:
                    break
            self.myAgent.SlanjePoruke("Prisutan",self.myAgent.suprotni,"Ovdje sam!")
            self.myAgent.SlanjePoruke("Pogodi",self.myAgent.suprotni,"Zamislio sam broj.")
            
            while True:
                self.msg = self.myAgent.SkidanjePoruke()
                if(self.msg.getOntology()!="Pogadjanje"):
                    sleep(1)
                else:
                    break

            if(int(self.msg.getContent())==self.myAgent.zamisljeniBroj):
                rezultat = ">>> Pogodio si! <<<"
                self.myAgent.Ispis("%s: %s"%(self.myAgent.ime,rezultat))
                self.myAgent.naRedu = False
                self.myAgent.Ispis("%s: Mijenjamo se."%(self.myAgent.ime))
                self.myAgent.SlanjePoruke("Ispravno",self.myAgent.suprotni,rezultat)
                self._exitcode = self.myAgent.POGODIO_JE
            else:
                rezultat = "Nisi pogodio!"
                self.myAgent.SlanjePoruke("Neispravno",self.myAgent.suprotni,rezultat)
                self.myAgent.Ispis("%s: %s"%(self.myAgent.ime,rezultat))
                self._exitcode = self.myAgent.NIJE_POGODIO
            

    #ovo ponasanje ide paralelno sa automatom i nije stanje
    class CitanjePoruka(spade.Behaviour.Behaviour):
        def _process(self):
            self.msg=None
            self.msg=self._receive(True,5) #svakih 2 sekundi oslobadja zablokiranu dretvu koja ceka poruku
            if self.msg:
                if self.msg.getOntology() != "Presence": #Presence koje salje sustav ignoriramo
                    self.myAgent.redPoruka.append(self.msg) 
                    if(self.myAgent.verbose):
                        self.myAgent.Ispis("%s: procitana je poruka \"%s\" ontologije \"%s\"" %(self.myAgent.ime,self.msg.getContent(),
                        self.msg.getOntology()),True)
                        self.myAgent.Ispis("%s: Velicina reda poruka: %d"%(self.myAgent.ime,len(self.myAgent.redPoruka)),True)
                elif self.msg.getOntology() == "Zavrsi":
                    self.myAgent._kill()

    def SkidanjePoruke(self):
        while(len(self.redPoruka)==0):
            sleep(0.3)
        self.msg = self.redPoruka.pop(0)
        if(self.verbose):
            self.Ispis("%s: skinuta je poruka ontologije \"%s\" i sadržaja \"%s\""%(self.ime,self.msg.getOntology(),self.msg.getContent()),True)
        return self.msg

    def SlanjePoruke(self, ontologija, primatelj, sadrzaj):
        self.receiver = spade.AID.aid( name="%s@127.0.0.1"%primatelj, addresses=[ "xmpp://%s@127.0.0.1"%primatelj ] )

        self.msg = spade.ACLMessage.ACLMessage()
        self.msg.setPerformative( "inform" )
        self.msg.setOntology( ontologija )
        self.msg.addReceiver( self.receiver ) 
        self.msg.setContent( sadrzaj )
        self.send( self.msg )

    def Ispis(self,sadrzaj,verbose=False,specijal=False):
        if specijal==True:
            print self.bcolors.HEADER+sadrzaj+self.bcolors.ENDC
        elif verbose==True:
            print self.bcolors.FAIL+sadrzaj+self.bcolors.ENDC
        else:
            if(self.naRedu):
                print self.bcolors.WARNING+sadrzaj+self.bcolors.ENDC
            else:
                print self.bcolors.OKGREEN+sadrzaj+self.bcolors.ENDC

    def _setup(self):
        self.bcolors = self.BColors()
        self.redPoruka = []
        self.upravljacPoruka = self.CitanjePoruka()
        self.setDefaultBehaviour(self.upravljacPoruka)

        #STANJA
        self.ZAMISLJANJE = 1
        self.PROVJERA = 2
        self.POGADJANJE = 3

        #PRIJELAZI
        self.NIJE_NA_REDU = 10
        self.BROJ_ZAMISLJEN = 21
        self.NISAM_POGODIO = 22
        self.POGODIO_SAM = 23
        self.NIJE_POGODIO = 24
        self.POGODIO_JE = 25



        stanja = spade.Behaviour.FSMBehaviour()
        stanja.registerFirstState(self.ZamisljanjeBroja(), self.ZAMISLJANJE);
        stanja.registerState(self.ProvjeraPogadjanja(), self.PROVJERA);
        stanja.registerState(self.Pogadjanje(), self.POGADJANJE);
        stanja.registerTransition(self.ZAMISLJANJE, self.POGADJANJE, self.NIJE_NA_REDU)
        stanja.registerTransition(self.ZAMISLJANJE, self.PROVJERA, self.BROJ_ZAMISLJEN)
        stanja.registerTransition(self.POGADJANJE,self.POGADJANJE,self.NISAM_POGODIO)
        stanja.registerTransition(self.POGADJANJE,self.ZAMISLJANJE,self.POGODIO_SAM)
        stanja.registerTransition(self.PROVJERA,self.PROVJERA,self.NIJE_POGODIO)
        stanja.registerTransition(self.PROVJERA,self.POGADJANJE,self.POGODIO_JE)
        
        self.addBehaviour(stanja,None)

        print "Pokrenut je igrač %s." % self.ime




if __name__=="__main__":
    igrac1 = Igrac( "igrac_1@127.0.0.1", "tajna" )
    igrac2 = Igrac( "igrac_2@127.0.0.1", "tajna" )

    igrac1.ime="igrac_1"
    igrac1.suprotni = "igrac_2"
    igrac1.naRedu = True
    
    igrac2.ime="igrac_2"
    igrac2.suprotni = "igrac_1"
    igrac2.naRedu = False

    igrac1.verbose=False
    igrac2.verbose=False
    if len(sys.argv)>1:
        if sys.argv[1]=="-verbose":
            igrac1.verbose=True
            igrac2.verbose=True


    igrac1.start()
    igrac2.start()