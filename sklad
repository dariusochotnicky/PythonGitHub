sklad = {
    "cukor": (1.5, "sladkost", 5),
    "banan": (0.5, "ovocie", 20),
    "jablko": (0.7, "ovocie", 40),
    "chlieb": (1.2, "ine", 2),
    "cokolada": (2.0, "sladkost", 10),
    "mlieko": (1.0, "ine", 3)
}


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
         

print(celkova_cena)




zaokruhli_celkova_cena = round(celkova_cena, 2)
print(zaokruhli_celkova_cena)
