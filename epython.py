from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Tesco Nakupny System")

# Sklad na backende: [cena, kategoria, mnozstvo]
sklad = {
    "cukor": [1.5, "sladkost", 5],
    "banan": [0.5, "ovocie", 20],
    "jablko": [0.7, "ovocie", 40],
    "chlieb": [1.2, "ine", 2],
    "cokolada": [2.0, "sladkost", 10],
    "mlieko": [1.0, "ine", 3]
}

zlavove_kody = {
    "samko": 0.2,
    "beli": 0.4,
    "marek": 0.3
}

# Heslo pre admina
ADMIN_HESLO = "patrikjuraj"

class PolozkaKosika(BaseModel):
    nazov: str
    mnozstvo: int

class Objednavka(BaseModel):
    polozky: List[PolozkaKosika]
    ma_klubovu_kartu: bool = False
    zlavovy_kod: Optional[str] = None

class DoplnenieZasob(BaseModel):
    nazov: str
    mnozstvo: int

class NovyTovar(BaseModel):
    nazov: str
    cena: float
    kategoria: str
    mnozstvo: int

class AdminLogin(BaseModel):
    heslo: str

@app.post("/api/admin/login")
def admin_login(data: AdminLogin):
    if data.heslo == ADMIN_HESLO:
        return {"sprava": "Prihlásenie úspešné"}
    raise HTTPException(status_code=401, detail="Nesprávne heslo!")

@app.post("/api/nakup")
def spracuj_nakup(objednavka: Objednavka):
    celkova_cena = 0.0
    for p in objednavka.polozky:
        nazov = p.nazov.lower()
        if nazov not in sklad:
            raise HTTPException(status_code=400, detail=f"Tovar '{nazov}' nemame v ponuke.")
        
        polozka_skladu = sklad.get(nazov)
        cena = float(polozka_skladu[0])
        dostupne = int(polozka_skladu[2])
        
        if dostupne <= 0:
            raise HTTPException(status_code=400, detail=f"Tovar '{nazov}' je vypredany!")
        if p.mnozstvo > dostupne:
            raise HTTPException(status_code=400, detail=f"Na sklade mame len {dostupne} ks.")
        celkova_cena += cena * p.mnozstvo
    
    if objednavka.ma_klubovu_kartu:
        celkova_cena *= 0.9
    
    kod = (objednavka.zlavovy_kod or "").strip().lower()
    if kod in zlavove_kody:
        celkova_cena *= (1 - zlavove_kody[kod])

    for p in objednavka.polozky:
        tovar = p.nazov.lower()
        sklad[tovar][2] = sklad[tovar][2] - p.mnozstvo
        
    return {"sprava": "Nakup uspesny! 🎉", "zaokruhli_celkova_cena": round(celkova_cena, 2)}

@app.post("/api/admin/doplnit")
def doplnit_zasoby(data: DoplnenieZasob):
    nazov = data.nazov.lower()
    if nazov in sklad:
        sklad[nazov][2] = sklad[nazov][2] + data.mnozstvo
        return {"sprava": "Doplnene", "novy_stav": sklad[nazov][2]}
    raise HTTPException(status_code=404, detail="Tovar nenajdeny")

@app.post("/api/admin/pridat")
def pridat_novy_tovar(data: NovyTovar):
    nazov = data.nazov.lower()
    sklad[nazov] = [data.cena, data.kategoria, data.mnozstvo]
    return {"sprava": "Tovar pridaný"}

@app.delete("/api/admin/odstranit/{nazov}")
def odstranit_tovar(nazov: str):
    nazov = nazov.lower()
    if nazov in sklad:
        del sklad[nazov]
        return {"sprava": "Tovar odstránený"}
    raise HTTPException(status_code=404, detail="Tovar nenájdený")

@app.get("/api/sklad")
def daj_sklad():
    return sklad

@app.get("/", response_class=HTMLResponse)
def get_ui():
    return """
    <!DOCTYPE html>
    <html lang="sk">
    <head>
        <meta charset="UTF-8">
        <title>Vitajte v Tescu</title>
        <style>
            body { font-family: sans-serif; margin: 30px; background: #eef2f5; }
            h1 { color: #00539C; display: flex; justify-content: space-between; align-items: center; }
            .flex { display: flex; gap: 20px; flex-wrap: wrap; }
            .box { background: white; padding: 20px; border-radius: 8px; flex: 1; min-width: 300px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background: #00539C; color: white; }
            button { background: #28a745; color: white; border: none; padding: 6px 12px; cursor: pointer; border-radius: 4px; }
            button:hover { background: #218838; }
            .btn-admin { background: #6c757d; font-size: 14px; }
            .btn-admin:hover { background: #5a6268; }
            .btn-doplnit { background: #007bff; }
            .btn-doplnit:hover { background: #0069d9; }
            .btn-zmazat { background: #dc3545; }
            .btn-zmazat:hover { background: #c82333; }
            .inputs { margin-top: 15px; }
            .admin-section { display: none; background: #fff3cd; border: 2px solid #ffeeba; }
            .admin-input { width: 60px; padding: 4px; }
            .form-group { margin-bottom: 10px; }
            .form-group input { padding: 5px; width: 100%; box-sizing: border-box; }
        </style>
    </head>
    <body onload="nacitajStranku()">
        <h1>
            <span>🛒 Tesco Obchod</span>
            <button class="btn-admin" id="auth-btn" onclick="prepniAdminZobrazenie()">🛠️ Prihlásiť sa ako Admin</button>
        </h1>
        
        <div class="flex">
            <div class="box">
                <h2>Ponuka skladu (Zakaznik)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Nazov</th>
                            <th>Cena</th>
                            <th>Kategoria</th>
                            <th>Sklad</th>
                            <th>Akcia</th>
                        </tr>
                    </thead>
                    <tbody id="ponuka-table"></tbody>
                </table>
            </div>

            <div class="box">
                <h2>Vas nakupny kosik</h2>
                <table>
                    <thead>
                        <tr><th>Polozka</th><th>Mnozstvo</th></tr>
                    </thead>
                    <tbody id="kosik-table"></tbody>
                </table>
                <div class="inputs">
                    <label><input type="checkbox" id="klubova-karta"> Clubova karta (10% zlava)</label><br><br>
                    <input type="text" id="zlavovy-kod" placeholder="Zlavovy kod"><br><br>
                    <button onclick="odoslatNakup()">Zaplatit nakup</button>
                </div>
                <div id="vysledok" style="margin-top:15px; font-weight:bold;"></div>
            </div>

            <div class="box admin-section" id="admin-box">
                <h2>🛠️ Admin Panel</h2>
                <h3>Existujúce produkty</h3>
                <table>
                    <thead>
                        <tr><th>Tovar</th><th>Pridat ks</th><th>Akcie</th></tr>
                    </thead>
                    <tbody id="admin-table"></tbody>
                </table>

                <h3 style="margin-top: 20px;">Pridať nový produkt</h3>
                <div class="form-group"><input type="text" id="novy-nazov" placeholder="Názov tovaru"></div>
                <div class="form-group"><input type="number" step="0.01" id="novy-cena" placeholder="Cena (€)"></div>
                <div class="form-group"><input type="text" id="novy-kategoria" placeholder="Kategória"></div>
                <div class="form-group"><input type="number" id="novy-mnozstvo" placeholder="Množstvo na sklade"></div>
                <button class="btn-doplnit" onclick="pridajNovyTovar()">Pridať produkt do ponuky</button>
            </div>
        </div>

        <script>
            let kosik = {};
            let isAdmin = false;

            async function nacitajStranku() {
                const res = await fetch('/api/sklad');
                const sklad = await res.json();
                
                const ponukaTbody = document.getElementById('ponuka-table');
                const adminTbody = document.getElementById('admin-table');
                
                ponukaTbody.innerHTML = '';
                adminTbody.innerHTML = '';

                Object.keys(sklad).forEach(nazov => {
                    const [cena, kategoria, mnozstvo] = sklad[nazov];
                    const capitalized = nazov.charAt(0).toUpperCase() + nazov.slice(1);
                    
                    // Zakaznicka tabulka
                    ponukaTbody.innerHTML += `
                        <tr>
                            <td><strong>${capitalized}</strong></td>
                            <td>${cena.toFixed(2)} €</td>
                            <td>${kategoria}</td>
                            <td>${mnozstvo} ks</td>
                            <td><button onclick="pridajDoKosika('${nazov}')">🛒 Pridat</button></td>
                        </tr>
                    `;

                    // Admin tabulka
                    adminTbody.innerHTML += `
                        <tr>
                            <td>${capitalized}</td>
                            <td><input type="number" id="input-${nazov}" class="admin-input" value="10"></td>
                            <td>
                                <button class="btn-doplnit" onclick="doplnitTovar('${nazov}')">📦 Doplniť</button>
                                <button class="btn-zmazat" onclick="odstranitTovar('${nazov}')">🗑️ Zmazať</button>
                            </td>
                        </tr>
                    `;
                });
            }

            function pridajDoKosika(nazov) {
                if (!kosik[nazov]) kosik[nazov] = 0;
                kosik[nazov]++;
                vykresliKosik();
            }

            function vykresliKosik() {
                const tbody = document.getElementById('kosik-table');
                tbody.innerHTML = '';
                Object.keys(kosik).forEach(nazov => {
                    if (kosik[nazov] > 0) {
                        const capitalized = nazov.charAt(0).toUpperCase() + nazov.slice(1);
                        tbody.innerHTML += `<tr><td>${capitalized}</td><td>${kosik[nazov]} ks</td></tr>`;
                    }
                });
            }

            async function odoslatNakup() {
                const polozky = Object.keys(kosik).filter(n => kosik[n] > 0).map(nazov => ({ nazov: nazov, mnozstvo: kosik[nazov] }));
                if(polozky.length === 0) { alert('Kosik je prazdny!'); return; }
                
                const res = await fetch('/api/nakup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        polozky: polozky,
                        ma_klubovu_kartu: document.getElementById('klubova-karta').checked,
                        zlavovy_kod: document.getElementById('zlavovy-kod').value || null
                    })
                });
                const data = await res.json();
                document.getElementById('vysledok').innerText = res.ok ? `${data.sprava} Cena: ${data.zaokruhli_celkova_cena} €` : `Chyba: ${data.detail}`;
                if(res.ok) { 
                    kosik = {}; 
                    vykresliKosik(); 
                    nacitajStranku();
                }
            }

            async function prepniAdminZobrazenie() {
                const box = document.getElementById('admin-box');
                const btn = document.getElementById('auth-btn');

                if (!isAdmin) {
                    const heslo = prompt("Zadajte admin heslo:");
                    if (!heslo) return;

                    const res = await fetch('/api/admin/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ heslo: heslo })
                    });

                    if (!res.ok) {
                        alert("Nesprávne heslo!");
                        return;
                    }
                    isAdmin = true;
                }

                if (box.style.display === 'block') {
                    box.style.display = 'none';
                    btn.innerText = '🛠️ Prihlásiť sa ako Admin';
                    isAdmin = false;
                } else {
                    box.style.display = 'block';
                    btn.innerText = '🔒 Odhlásiť sa z Admin módu';
                }
            }

            async function doplnitTovar(nazov) {
                const ksInput = document.getElementById(`input-${nazov}`);
                const ks = parseInt(ksInput.value);
                const res = await fetch('/api/admin/doplnit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nazov: nazov, mnozstvo: ks })
                });
                if(res.ok) {
                    alert('Tovar ' + nazov + ' bol úspešne naskladnený!');
                    nacitajStranku();
                }
            }

            async function odstranitTovar(nazov) {
                if(!confirm(`Naozaj chcete vymazať tovar ${nazov} zo skladu?`)) return;
                const res = await fetch(`/api/admin/odstranit/${nazov}`, { method: 'DELETE' });
                if(res.ok) {
                    alert('Tovar bol odstránený.');
                    nacitajStranku();
                }
            }

            async function pridajNovyTovar() {
                const nazov = document.getElementById('novy-nazov').value;
                const cena = parseFloat(document.getElementById('novy-cena').value);
                const kategoria = document.getElementById('novy-kategoria').value;
                const mnozstvo = parseInt(document.getElementById('novy-mnozstvo').value);

                if(!nazov || isNaN(cena) || !kategoria || isNaN(mnozstvo)) {
                    alert('Vyplňte všetky polia pre nový produkt správne!');
                    return;
                }

                const res = await fetch('/api/admin/pridat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nazov, cena, kategoria, mnozstvo })
                });

                if(res.ok) {
                    alert('Nový produkt bol pridaný do ponuky!');
                    document.getElementById('novy-nazov').value = '';
                    document.getElementById('novy-cena').value = '';
                    document.getElementById('novy-kategoria').value = '';
                    document.getElementById('novy-mnozstvo').value = '';
                    nacitajStranku();
                }
            }
        </script>
    </body>
    </html>
    """
