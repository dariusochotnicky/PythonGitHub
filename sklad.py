sklad = {
    "cukor": (1.5, "sladkost", 5),
    "banan": (0.5, "ovocie", 20),
    "jablko": (0.7, "ovocie", 40),
    "chlieb": (1.2, "ine", 2),
    "cokolada": (2.0, "sladkost", 10),
    "mlieko": (1.0, "ine", 3)
}

print("mate nasu klubovu kartu?")
klubova_karta = input()
if klubova_karta == "ano":
        print("mate 10% zlavu")
        for polozka in sklad.keys():
            cena, kategoria, mnozstvo = sklad[polozka]
            nova_cena = cena * 0.9
            sklad[polozka] = (nova_cena, kategoria, mnozstvo)
else:
    print("nemate zlavu")

zlavovy_kod = {
    "samko": 0.2,
    "beli": 0.4,
    "marek": 0.3
}                                   

print("mate nejaky zlavovy kod?")
zlavovy_kod = input()

kosik = []

celkova_cena = 0
while True:
    print("vloz polozku do kosika")
    polozka = input()
    if polozka == "koniec":
        break
    if polozka in sklad.keys():
        kosik.append(polozka) 
        celkova_cena = celkova_cena + sklad[polozka][0]
        cena, kategoria, mnozstvo = sklad[polozka]

        sklad[polozka] = (cena, kategoria, mnozstvo - 1)
    else:
        print("nemame")
    if polozka not in sklad.keys():
        print("nemame")

    if mnozstvo == 0:
        print("vypredane")
        celkova_cena = celkova_cena - sklad[polozka][0]

if zlavovy_kod == "beli":
    celkova_cena = celkova_cena * 0.6
elif zlavovy_kod == "samko":
    celkova_cena = celkova_cena * 0.8
elif zlavovy_kod == "marek":
    celkova_cena = celkova_cena * 0.7
zaokruhli_celkova_cena = round(celkova_cena, 2)
print("celkova_cena : ", zaokruhli_celkova_cena, "€")
