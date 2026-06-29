// ============================================================
// DÉTECTION RÉSEAU + SYNCHRONISATION AUTOMATIQUE
// ============================================================

let syncEnCours = false;

async function updateNetworkStatus() {
    const status = document.getElementById("network-status");
    if (!status) return;
    if (!navigator.onLine) {
        status.innerText = "🔴 Hors ligne";
        status.className = "text-red-600 font-semibold";
        return;
    }
    // Tester l'accès réel au cloud via le backend local
    try {
        const res = await fetch("/api/sync/status", {
            headers: { "Authorization": "Bearer " + (localStorage.getItem("token") || "") },
            signal: AbortSignal.timeout(5000)
        });
        const data = await res.json();
        if (data.cloud_accessible) {
            status.innerText = "🟢 En ligne — Cloud accessible";
            status.className = "text-green-600 font-semibold";
        } else {
            status.innerText = "🟡 Réseau local — Cloud inaccessible";
            status.className = "text-yellow-600 font-semibold";
        }
    } catch(e) {
        status.innerText = "🟡 Réseau local — Cloud inaccessible";
        status.className = "text-yellow-600 font-semibold";
    }
}

async function syncAutomatique() {
    if (syncEnCours) return;
    if (!navigator.onLine) return;

    const token = getToken ? getToken() : localStorage.getItem("token");
    if (!token) return;

    const role = localStorage.getItem("role");
    if (role !== "admin") return;

    syncEnCours = true;
    console.log("🔄 Synchronisation automatique déclenchée...");

    const msgEl = document.getElementById("syncMsg");
    if (msgEl) {
        msgEl.innerText = "🔄 Synchronisation automatique en cours...";
        msgEl.className = "mt-3 text-sm text-blue-500";
    }

    try {
        const res = await fetch("/api/sync/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            }
        });

        const data = await res.json();

        if (data.success) {
            console.log("✅ Sync auto réussie :", data.details);
            if (msgEl) {
                msgEl.innerText = `✅ Sync automatique : ${data.details.push_progressions} progression(s) envoyée(s)`;
                msgEl.className = "mt-3 text-sm text-green-600";
            }
            // Recharger le dashboard si on est sur admin.html
            if (typeof loadDashboard === "function") loadDashboard();
        } else {
            console.warn("⚠️ Sync auto partielle :", data.details.errors);
            if (msgEl) {
                msgEl.innerText = "⚠️ Synchronisation partielle";
                msgEl.className = "mt-3 text-sm text-orange-500";
            }
        }
    } catch(e) {
        console.error("❌ Erreur sync auto :", e.message);
    } finally {
        syncEnCours = false;
    }
}

// Déclencher la sync automatiquement au retour d'internet
window.addEventListener("online", () => {
    updateNetworkStatus();
    // Attendre 2 secondes que la connexion soit stable
    setTimeout(syncAutomatique, 2000);
});

window.addEventListener("offline", updateNetworkStatus);
window.addEventListener("load", updateNetworkStatus);
