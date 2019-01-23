#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Tkinter import *
from podaci import PodaciDatoteka
from agent import Agent


class GUI(Frame):
    
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.root = master
        self.canvas = Canvas(self.root, width=800, height = 800)
        self.canvas.pack()

    def obrisi(self):
        self.canvas.delete(ALL)

    def nacrtajTekst(self,x,y,skala,tekst,boja):
        cx = self.canvas.winfo_width()/2.0
        cy = self.canvas.winfo_height()/2.0
        posx = cx+skala*x
        posy = cy+skala*y
        self.canvas.create_text(posx,posy+14,fill=boja,font="Times 12 italic bold",text=tekst)


    def nacrtaj(self,x,y,skala,boja):
        cx = self.canvas.winfo_width()/2.0
        cy = self.canvas.winfo_height()/2.0
        posx = cx+skala*x
        posy = cy+skala*y
        self.canvas.create_oval(posx-5.0,posy-5.0,posx+5.0,posy+5.0, fill=boja)
        

    def animiraj(self,agenti):
        self.obrisi()
        for i in range(0,len(agenti)):
            agent = agenti[i]
            agent.lock.acquire()
            agent.protokol.DajTakt()
            agent.protokol.izracunaj_unutarnja(agent.koordinate)
            agent.protokol.izracunaj(agent.koordinate,agent.lista_koordinata_susjeda)
            
            agent.lock.release()
            polozaj = agent.koordinate.polozaj
            self.nacrtaj(polozaj[0],polozaj[1],20.0,"red")
        for i in range(0,len(agenti)):
            agent = agenti[i]
            polozaj = agent.koordinate.polozaj
            agent.lock.acquire()
            agent.protokol.normiraj(agent.koordinate,0.8)
            agent.protokol.integriraj(agent.koordinate)
            agent.lock.release()
            self.nacrtajTekst(polozaj[0], polozaj[1], 20.0, agent.naziv,"red")
        self.root.update()
        self.canvas.after(50, self.animiraj,agenti)

if __name__=="__main__":
    print "Pokrenut je program"
    podaciDatoteka = PodaciDatoteka("podaci.csv")
    podaciDatoteka.procitaj()
    podaciDatoteka.test()
    listaAgenata = list()
    if len(podaciDatoteka.matrica_susjednosti)>0 and len(podaciDatoteka.matrica_susjednosti)<100:
        root = Tk()
        root.title("Kretanje agenata")
        gui = GUI(root)
        for i in range(1,len(podaciDatoteka.matrica_susjednosti)+1):
            ime_agenta = podaciDatoteka.imena_agenata[i-1]
            agent = Agent( "{0:s}@127.0.0.1".format(ime_agenta), "tajna" )
            agent.podaciDatoteka = podaciDatoteka
            agent.koordinate = agent.podaciDatoteka.koordinate_agenata[i-1]
            agent.gui = gui
            agent.naziv = ime_agenta
            listaAgenata.append(agent)
        podaciDatoteka.ispis("Pokretanje agenata:")
        for agent in listaAgenata:
            agent.start()
        print "OK"

        gui.animiraj(listaAgenata)
        root.mainloop()

        for agent in listaAgenata:
            agent.zavrsi()
            podaciDatoteka.ispis("Agent {0:s} zavrsava.".format(agent.getName()))
    print "Svi agenti su zavrsili."