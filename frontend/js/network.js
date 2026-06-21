function updateNetworkStatus() {
    const status = document.getElementById("network-status");

    if (!status) return;

    if (navigator.onLine) {
        status.innerText = "🟢 En ligne";
        status.className = "text-green-600 font-semibold";
    } else {
        status.innerText = "🔴 Hors ligne";
        status.className = "text-red-600 font-semibold";
    }
}

// Détection connexion
window.addEventListener("online", updateNetworkStatus);
window.addEventListener("offline", updateNetworkStatus);

// Initialisation
window.addEventListener("load", updateNetworkStatus);