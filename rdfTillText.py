################################################################################################
#
#       RDF till text
#       Maria Idebrant (2020-04-08), delar av koden lånade från Mikael Gunnarssons notSoSimpleParser.py
#       
#       Nedanstående skript är skapat som rättningshjälp av rdf-uppgift i 31DBS1 & 31BBS3
#       Syftet med skriptet är att skriva ut URI:er som text istället. URI:er från VIAF hämtas från VIAF, vilket språk som visas slumpas (finns oftast flera föredragna namn)
#
#       För att använda skriptet:
#       1. Lägg det i samma mapp som studentens uppgift
#       2. Öppna det med Python 3 - Idle GUI
#       3. Tryck F5
#       4. Vänta en liten stund. Läs det som står i "Shell" fönstret.
#
#       Lämplig vidareutveckling:
#       - Låta skriptet tugga igenom alla undermappar i en mapp för att leta efter rdf-filer och rätta dem.
#       - Låta skriptet spara outputen i en txt-fil i samma mapp som respektive rdf-fil
#       - Felhantering
#
#       Nedanstående har i stort sett ingen felhantering, vilket gör skriptet olämpligt att bearbera mer än en fil åt gången i nuvarande form.
#
################################################################################################

# load necessary libraries
try:
    from rdflib import Graph, URIRef
except ImportError:
    print("Det verkar som att rdflib inte är installerat. Är du säker på att du startat Python 3?")

try:
    from rdflib.namespace import RDF
except ImportError:
    print("Problem att importera från rdflib.namespace.")

import os


### Funktion: Hämta objekt när subjekt och predikat är känt (den här funktionen borde gå att använda även till att hämta labels från RDARegistry, men får felkod 406 från deras server när jag försöker.

def fetchObject(subjectURI, predicateURI):
    anothergraph = Graph()
    anothergraph.parse(subjectURI)

    subject_ = subjectURI
    predicate_ = predicateURI
    object_ = None

    viafName = anothergraph.value(subject=subject_, predicate=predicate_, object=object_, default=None, any=True)
    return viafName


### Och så själva grundkoden

# RDARegistry verkar inte svara i RDF-format på sina respektive URI:er.
# Går att få hela RDARegistry i RDF-form på http://rdaregistry.info/Elements/w.nt
# men det blir väl mycket för rdflib att läsa in med parse.
# Därför fullösniningen att lägga in de predikat som gavs i uppgiften i en dictionary.

RDARegistryPredicates = {
    "http://rdaregistry.info/Elements/w/P10088": "har titel",
    "http://rdaregistry.info/Elements/w/P10086": "har alternativ titel",
    "http://rdaregistry.info/Elements/w/P10065": "har upphovsperson",
    "http://rdaregistry.info/Elements/w/P10156": "har föregående verk/är en fortsättning på",
    "http://rdaregistry.info/Elements/w/P10020": "har uppföljande verk/fortsätts av",
    "http://rdaregistry.info/Elements/w/P10025": "har filmatiserats i verket",
    "http://rdaregistry.info/Elements/w/P10078": "förverkligas i uttrycket"
    }


# Kolla vad .rdf-filen heter

rdf_files = [f for f in os.listdir('.') if f.endswith('.rdf')]
if len(rdf_files) != 1:
    raise ValueError('Det finns mer än en rdf-fil i mappen. Ta bort överflödiga.')

filename = rdf_files[0]





# Gör en graf och mata den med trippler från studentens inlämnade RDF-fil
g = Graph()
try:
    g.parse(filename, format="turtle")
except IOError:
    print("Filen kan inte hittas. Kontrollera filens namn och var den ligger i filsystemet")
except SyntaxError:
    print("RDF-filen är inte helt korrekt")


# Nedanstående query bit kollar upp vilka subjekt som används i filen.

qres = g.query(
    """SELECT DISTINCT ?subject
       WHERE {
          ?subject ?predicate ?object .
       }""")

if len(qres)>1:
    print("Potentiellt fel i filen. Det finns %s olika subjekt." % len(qres))
    subject = None #rensa värden mellan filer
elif len(qres)<1:
    print("Det finns inga subjekt.")
    subject = None
else:
    for row in qres: #måste finnas ett snyggare sätt att plocka ut ett enskilt värde, men jag orkar inte leta upp det
        print("Subjekt: %s \n\n" % (row))

        #första infångade subjektet lagras som sträng i "subject"
        subject = row[0]
        #subject = str(subjectRaw.toPython())


    #fortsätter med att hämta föredraget namn för subjektet från viaf.org
        title = fetchObject(subject, URIRef("http://schema.org/name"))


    #Hämta in alla trippler med detta subjekt till en lista
    subject_=subject
    predicate_=None
    object_=None

    thisFile = [t for t in g.triples((subject_, predicate_, object_))]
    

    for triple in thisFile:
               
        print("%s (subjekt)" % (title))
        
        print("%s (predikat)" % (RDARegistryPredicates[triple[1].toPython()]))

        objectAsString = triple[2].toPython()
        if objectAsString.startswith( 'http://viaf.org/viaf/'):
            # om objektet börjar med http://viaf.org/viaf/ är det en URI från VIAF.
            name = fetchObject(triple[2], URIRef("http://www.w3.org/2004/02/skos/core#prefLabel"))
            print("%s (objekt sparat som URI)" % (name))

        elif objectAsString.startswith( 'http://'):
            print("%s (objekt sparat som URI, ej från VIAF)" % (triple[2]))
        else:
            print("%s (objekt sparat som textsträng)" % (triple[2]))
        print("\n\n")


    


