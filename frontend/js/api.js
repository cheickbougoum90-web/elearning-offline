// ============================================================
// CONFIG — URL du backend
// En local : http://localhost:8000
// Sur AWS  : changer par l'IP EC2
// ============================================================
const API_URL = "";

// ============================================================
// UTILITAIRES
// ============================================================

// Récupérer le token stocké après login
function getToken() {
    return localStorage.getItem("token");
}

// Construire les headers avec le token JWT
function authHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + getToken()
    };
}

// Vérifier si connecté, sinon rediriger vers login
function requireAuth() {
    if (!getToken()) {
        window.location.href = "index.html";
    }
}

// Déconnexion
function logout() {
    localStorage.clear();
    window.location.href = "index.html";
}

// ============================================================
// AUTH
// ============================================================

async function apiLogin(email, password) {
    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    const res = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        body: formData
    });

    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Identifiants incorrects");
    }

    const data = await res.json();
    // Stocker token + infos utilisateur
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("user_id", data.user_id);
    localStorage.setItem("role", data.role);
    localStorage.setItem("nom", data.nom);
    return data;
}

// ============================================================
// COURS
// ============================================================

async function getCours() {
    const res = await fetch(`${API_URL}/api/cours/`, {
        headers: authHeaders()
    });
    if (res.status === 401) { logout(); return; }
    return await res.json();
}

async function createCours(titre, description) {
    const res = await fetch(`${API_URL}/api/cours/`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ titre, description })
    });
    if (!res.ok) throw new Error("Erreur création cours");
    return await res.json();
}

async function deleteCours(id) {
    const res = await fetch(`${API_URL}/api/cours/${id}`, {
        method: "DELETE",
        headers: authHeaders()
    });
    if (!res.ok) throw new Error("Erreur suppression");
    return await res.json();
}

// ============================================================
// LEÇONS
// ============================================================

async function getLecons(coursId) {
    const res = await fetch(`${API_URL}/api/lecons/cours/${coursId}`, {
        headers: authHeaders()
    });
    if (res.status === 401) { logout(); return; }
    return await res.json();
}

async function getLecon(leconId) {
    const res = await fetch(`${API_URL}/api/lecons/${leconId}`, {
        headers: authHeaders()
    });
    return await res.json();
}

// ============================================================
// QUIZ
// ============================================================

async function getQuiz(leconId) {
    const res = await fetch(`${API_URL}/api/quiz/lecon/${leconId}`, {
        headers: authHeaders()
    });
    return await res.json();
}

async function soumettreReponse(quizId, reponseId) {
    const res = await fetch(`${API_URL}/api/quiz/${quizId}/soumettre`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ reponse_id: reponseId })
    });
    return await res.json();
}

// ============================================================
// PROGRESSION
// ============================================================

async function saveProgression(leconId, statut, score) {
    const res = await fetch(`${API_URL}/api/progression/`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ lecon_id: leconId, statut, score })
    });
    return await res.json();
}

// ============================================================
// AVIS
// ============================================================

async function postAvis(coursId, note, commentaire) {
    const res = await fetch(`${API_URL}/api/avis/`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ cours_id: coursId, note, commentaire })
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail);
    }
    return await res.json();
}

async function getClassement() {
    const res = await fetch(`${API_URL}/api/avis/classement/profs`, {
        headers: authHeaders()
    });
    return await res.json();
}

// ============================================================
// USERS (admin)
// ============================================================

async function getUsers() {
    const res = await fetch(`${API_URL}/api/users/`, {
        headers: authHeaders()
    });
    return await res.json();
}

async function createUser(nom, email, mot_de_passe, role) {
    const res = await fetch(`${API_URL}/api/users/`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ nom, email, mot_de_passe, role })
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail);
    }
    return await res.json();
}

async function deleteUser(id) {
    const res = await fetch(`${API_URL}/api/users/${id}`, {
        method: "DELETE",
        headers: authHeaders()
    });
    return await res.json();
}

// ============================================================
// SYNC (admin)
// ============================================================

async function syncData() {
    const res = await fetch(`${API_URL}/api/sync/`, {
        method: "POST",
        headers: authHeaders()
    });
    return await res.json();
}

async function getSyncStatus() {
    const res = await fetch(`${API_URL}/api/sync/status`, {
        headers: authHeaders()
    });
    return await res.json();
}

// ============================================================
// STATS (ajout — manquait dans api.js)
// ============================================================
async function getStats(userId, coursId) {
    const res = await fetch(
        `${API_URL}/api/progression/${userId}/stats?cours_id=${coursId}`,
        { headers: authHeaders() }
    );
    return handleResponse(res);
}

// ======================
// ERREUR CENTRALISÉE (réajoutée — avait été supprimée par erreur)
// ======================
async function handleResponse(res) {
    if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.detail || "Erreur serveur");
    }
    return res.json();
}
