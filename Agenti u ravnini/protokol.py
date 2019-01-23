#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
from math import sin,cos,sqrt,pi,atan2

#ima ulogu strukture podataka
class StanjeAgenta:
    def __init__(self):
        self.polozaj = list()
        self.brzina = list()
        self.vrijeme = 0.0
        self.norma_brzine = 0.0
        for i in range(0,3):
            self.polozaj.append(0.0)
            self.brzina.append(0.0)
        self.radijus  = 1.0
        self.kut = 0.0
        self.brojAgenta = 0

#protokol komunikacije agenata
class Protokol:
    def __init__(self):
        self.u1x = 0.0
        self.u1y = 0.0
        self.u2x = 0.0
        self.u2y = 0.0
        self.u = list()
        self.u.append(0.0)
        self.u.append(0.0) 
        self.vrijeme = 0.0

        self.u2 = list()
        self.u2.append(0.0)
        self.u2.append(0.0)

    def DajTakt(self):
        self.vrijeme+=0.08

    #jedna vrsta konsenzusa

    def izracunaj_unutarnja(self, koordinate):
        #unutarnja komponenta
        self.u[0] = -koordinate.brzina[1]
        self.u[1] =  koordinate.brzina[0] 
        

    def izracunaj(self, koordinate, koordinateSusjeda):
        koordinateSusjeda2 = list()
        for l in koordinateSusjeda:
            if l != None:
                koordinateSusjeda2.append(l)

        #vanjska komponenta
        u2 = list()

        S1=list()
        S2=list()
        razlika_polozaj = list()
        razlika_brzina = list()
        mat_razlika_brz=list()
        mat_razlika_kut=list()
        for k in range(0,2):
            u2.append(0.0) 
            S1.append(0.0)
            S2.append(0.0)
            razlika_polozaj.append(0.0)
            mat_razlika_brz.append(0.0)
            razlika_brzina.append(0.0)
            mat_razlika_kut.append(0.0)

        inv_radijus_kv = 1.0/(koordinate.radijus*koordinate.radijus)
        for i in range(0,len(koordinateSusjeda2)):
            inv_rad_mjesani = 1.0/(koordinate.radijus*koordinateSusjeda2[i].radijus)
            razlika_kut = koordinate.kut-koordinateSusjeda2[i].kut
            cos_razlika_kut=cos(razlika_kut)
            sin_razlika_kut=sin(razlika_kut)
            
            mat_razlika_kut[0]=(cos_razlika_kut*koordinateSusjeda2[i].brzina[0]-sin_razlika_kut*koordinateSusjeda2[i].brzina[1])
            mat_razlika_kut[1]=(sin_razlika_kut*koordinateSusjeda2[i].brzina[0]+cos_razlika_kut*koordinateSusjeda2[i].brzina[1])
            for k in range(0,2):
                S1[k]+=(inv_radijus_kv*koordinate.brzina[k]-inv_rad_mjesani*mat_razlika_kut[k])
        
        for i in range(0,len(koordinateSusjeda2)):
            for k in range(0,2):
                razlika_polozaj[k]=(koordinate.polozaj[k]-koordinateSusjeda2[i].polozaj[k])
                razlika_brzina[k]=(koordinate.brzina[k]-koordinateSusjeda2[i].brzina[k])
            
            mat_razlika_brz[0]=(                    -razlika_brzina[1])
            mat_razlika_brz[1]=( razlika_brzina[0]) 
            for k in range(0,2):
                S2[k]+=(razlika_polozaj[k]+mat_razlika_brz[k])
        for k in range(0,2):
            self.u2[k]=-S1[k]-S2[k] 

        
    

    def integriraj(self,koordinate):
        vrijeme = self.vrijeme
        dt=vrijeme-koordinate.vrijeme
        koordinate.brzina[0]+=self.u[0]*dt
        koordinate.brzina[1]+=self.u[1]*dt
        koordinate.polozaj[0]+=koordinate.brzina[0]*dt
        koordinate.polozaj[1]+=koordinate.brzina[1]*dt
        koordinate.vrijeme=datetime.datetime.now().microsecond
        koordinate.vrijeme = vrijeme

    def normiraj(self,koordinate, gama):
        self.u[0]+=gama*self.u2[0]
        self.u[1]+=gama*self.u2[1]
        norma = sqrt(koordinate.brzina[0]*koordinate.brzina[0]+koordinate.brzina[1]*koordinate.brzina[1])
        omjer = norma/koordinate.norma_brzine
        if(omjer<1.0):
            return
        for k in range(0,2):
            zeljena_brzina = koordinate.brzina[k]/omjer
            razlika = zeljena_brzina-koordinate.brzina[k]
            koordinate.brzina[k]+=razlika*0.1
        

    #druga vrsta konsenzusa - Randezvous
    def izracunaj2(self, koordinate, koordinateSusjeda, dt,gama):
        koordinateSusjeda2 = list()
        for l in koordinateSusjeda:
            if l != None:
                koordinateSusjeda2.append(l)
        u = list()
        u.append(0.0)
        u.append(0.0)

        for i in range(0,len(koordinateSusjeda2)):
            u[0]+=(koordinateSusjeda2[i].polozaj[0]-koordinate.polozaj[0])
            u[1]+=(koordinateSusjeda2[i].polozaj[1]-koordinate.polozaj[1])
            u[0]+=(koordinateSusjeda2[i].brzina[0]-koordinate.brzina[0])
            u[1]+=(koordinateSusjeda2[i].brzina[1]-koordinate.brzina[1])
        
        drx =  koordinate.brzina[0]*dt
        dry =  koordinate.brzina[1]*dt
        dvx = u[0]*dt
        dvy = u[1]*dt
        koordinate.polozaj[0]+=drx
        koordinate.polozaj[1]+=dry
        koordinate.brzina[0]+=dvx
        koordinate.brzina[1]+=dvy

    #treca vrsta konsenzusa - rotacijski Randezvous
    def izracunaj3(self, koordinate, koordinateSusjeda, dt,gama):
        koordinateSusjeda2 = list()
        for l in koordinateSusjeda:
            if l != None:
                koordinateSusjeda2.append(l)
        u = list()
        u.append(0.0)
        u.append(0.0)

        #unutarnja komponenta
        u1 = list()
        u1.append(0.0)
        u1.append(0.0) 
        u1[0]=-koordinate.brzina[1]
        u1[1]= koordinate.brzina[0] 

        for i in range(0,len(koordinateSusjeda2)):
            u[0]+=(koordinateSusjeda2[i].polozaj[0]-koordinate.polozaj[0])
            u[1]+=(koordinateSusjeda2[i].polozaj[1]-koordinate.polozaj[1])
            u[0]+=(koordinateSusjeda2[i].brzina[0]-koordinate.brzina[0])
            u[1]+=(koordinateSusjeda2[i].brzina[1]-koordinate.brzina[1])
        

        u[0]+=u1[0]
        u[1]+=u1[1]


        drx =  koordinate.brzina[0]*dt
        dry =  koordinate.brzina[1]*dt
        dvx = u[0]*dt
        dvy = u[1]*dt
        koordinate.polozaj[0]+=drx
        koordinate.polozaj[1]+=dry
        koordinate.brzina[0]+=dvx
        koordinate.brzina[1]+=dvy



