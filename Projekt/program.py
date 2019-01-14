#!/usr/bin/env python
# -*- coding: utf-8 -*-


from podaci import PodaciDatoteka
from agent import Agent

if __name__=="__main__":
    print "Pokrenut je program"
    podaciDatoteka = PodaciDatoteka("podaci.csv")
    podaciDatoteka.procitaj()
    podaciDatoteka.test()
    listaAgenata = list()
    if len(podaciDatoteka.matrica_susjednosti)>0 and len(podaciDatoteka.matrica_susjednosti)<100:
        for i in range(1,len(podaciDatoteka.matrica_susjednosti)+1):
            agent = Agent( "agent_{0:d}@127.0.0.1".format(i), "tajna" )
            agent.naziv = "Agent {0:d}".format(i)
            agent.brojAgenta = i
            agent.podaciDatoteka = podaciDatoteka
            listaAgenata.append(agent)
        podaciDatoteka.ispis("Pokretanje agenata:")
        for agent in listaAgenata:
            agent.start()
    print "OK"