produkty = {
    "cukor": (1.5, "sladkost"), "banan": (0.5, "ovocie"), "jablko": (0.7, "ovocie"),
      "chlieb": (1.2, "ine"), "cokolada": (2.0, "sladkost"), "mlieko": (1.0, "ine")
}




nakupny_kosik = ["cukor", "banan", "jablko", "chlieb", "cokolada", "mlieko"]

pocet = int(input("kolko veci chcete pridat do kosika?\n"))
while pocet:
    print("co chcete pridat?")
    nazov = input().strip().lower()

    if nazov in produkty:
        nakupny_kosik.append(nazov)
        pocet -=1
    else:
        print("takato polozka nie je v zozname.")

for polozka in nakupny_kosik:
    cena, kategoria = produkty[polozka]
    print(f"{polozka} - {cena} EUR, - {kategoria}")

