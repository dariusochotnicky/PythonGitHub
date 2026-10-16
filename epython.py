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
