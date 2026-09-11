
ovocie = ["jablko", "banan", "hruska", "marhula", "slivka"]
zelenina = ["mrkva", "petrzlen", "celer", "zemiak"]
sladkosti = ["cokolada", "cukor"]
nastroj= ["lopata", "ryl", "kosa"]

nakupny_kosik = ["mrkva", "mlieko", "celer", "cokolada", "jogurt", "chlieb", "jablko", "zemiak", "cukor", "banan",]


while True:
    print("co chcete pridat do kosika?")
    vstup = input()
    if vstup.lower() == "uz nic" or vstup == "koniec":
        break
    else:
        nakupny_kosik.append(vstup)

print("----------------------")


for polozka in nakupny_kosik:
    if polozka in ovocie:
        print(f"{polozka} je ovocie")
    elif polozka in zelenina:
        print(f"{polozka} je zelenina")
    elif polozka in sladkosti:
        print(f"{polozka} je sladkost")
    elif polozka in nastroj:
        print(f"{polozka} je nastroj")
    else:
        print(f"{polozka} je nieco ine")
