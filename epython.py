from fastapi import FastAPI, HTTPException
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

@app.post("/api/nakup")
def spracuj_nakup(objednavka: Objednavka):
    celkova_cena = 0.0
    for p in objednavka.polozky:
        nazov = p.nazov.lower()
        if nazov not in sklad:
            raise HTTPException(status_code=400, detail=f"Tovar '{nazov}' nemame v ponuke.")
        
        # Bezpecne vytiahnutie hodnot zo zoznamu
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
            .inputs { margin-top: 15px; }
            .admin-section { display: none; background: #fff3cd; border: 2px solid #ffeeba; }
            .admin-input { width: 60px; padding: 4px; }
        </style>
    </head>
    <body>
        <h1>
            <span>🛒 Tesco Obchod</span>
            <button class="btn-admin" id="auth-btn" onclick="prepniAdminZobrazenie()">🛠️ Aktivovat Admin Mod</button>
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
                            <th>Akcia</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td><strong>Jablko</strong></td><td>0.70 €</td><td>ovocie</td><td><button onclick="pridajDoKosika('jablko')">🛒 Pridat do kosika</button></td></tr>
                        <tr><td><strong>Banan</strong></td><td>0.50 €</td><td>ovocie</td><td><button onclick="pridajDoKosika('banan')">🛒 Pridat do kosika</button></td></tr>
                        <tr><td><strong>Cukor</strong></td><td>1.50 €</td><td>sladkost</td><td><button onclick="pridajDoKosika('cukor')">🛒 Pridat do kosika</button></td></tr>
                        <tr><td><strong>Chlieb</strong></td><td>1.20 €</td><td>ine</td><td><button onclick="pridajDoKosika('chlieb')">🛒 Pridat do kosika</button></td></tr>
                        <tr><td><strong>Cokolada</strong></td><td>2.00 €</td><td>sladkost</td><td><button onclick="pridajDoKosika('cokolada')">🛒 Pridat do kosika</button></td></tr>
                        <tr><td><strong>Mlieko</strong></td><td>1.00 €</td><td>ine</td><td><button onclick="pridajDoKosika('mlieko')">🛒 Pridat do kosika</button></td></tr>
                    </tbody>
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
                <h2>🛠️ Admin Panel (Doplnanie zasob)</h2>
                <table>
                    <thead>
                        <tr><th>Tovar</th><th>Pridat ks</th><th>Akcia</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>Jablko</td><td><input type="number" id="input-jablko" class="admin-input" value="10"></td><td><button class="btn-doplnit" onclick="doplnitTovar('jablko')">📦 Doplnit sklad</button></td></tr>
                        <tr><td>Banan</td><td><input type="number" id="input-banan" class="admin-input" value="10"></td><td><button class="btn-doplnit" onclick="doplnitTovar('banan')">📦 Doplnit sklad</button></td></tr>
                        <tr><td>Cukor</td><td><input type="number" id="input-cukor" class="admin-input" value="10"></td><td><button class="btn-doplnit" onclick="doplnitTovar('cukor')">📦 Doplnit sklad</button></td></tr>
                        <tr><td>Chlieb</td><td><input type="number" id="input-chlieb" class="admin-input" value="10"></td><td><button class="btn-doplnit" onclick="doplnitTovar('chlieb')">📦 Doplnit sklad</button></td></tr>
                        <tr><td>Cokolada</td><td><input type="number" id="input-cokolada" class="admin-input" value="10"></td><td><button class="btn-doplnit" onclick="doplnitTovar('cokolada')">📦 Doplnit sklad</button></td></tr>
                        <tr><td>Mlieko</td><td><input type="number" id="input-mlieko" class="admin-input" value="10"></td><td><button class="btn-doplnit" onclick="doplnitTovar('mlieko')">📦 Doplnit sklad</button></td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            let kosik = {};

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
                        tbody.innerHTML += `<tr><td>${nazov}</td><td>${kosik[nazov]} ks</td></tr>`;
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
                if(res.ok) { kosik = {}; vykresliKosik(); }
            }

            function prepniAdminZobrazenie() {
                const box = document.getElementById('admin-box');
                const btn = document.getElementById('auth-btn');
                if (box.style.display === 'block') {
                    box.style.display = 'none';
btn.innerText = '🛠️ Aktivovat Admin Mod';
} else {
box.style.display = 'block';
btn.innerText = '🔒 Deaktivovat Admin Mod';
}
}
async function doplnitTovar(nazov) {
const ks = parseInt(document.getElementById(input-${nazov}).value);
const res = await fetch('/api/admin/doplnit', {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify({ nazov: nazov, mnozstvo: ks })
});
if(res.ok) alert('Tovar ' + nazov + ' bol uspesne naskladneny!');
}



"""
