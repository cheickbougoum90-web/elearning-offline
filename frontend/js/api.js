// ============================================================
// CONFIG — URL du backend
// En local : http://localhost:8000
// Sur AWS  : changer par l'IP EC2
// ============================================================
const API_URL = "http://localhost:8000";

// ======================
// TOKEN
// ======================
function getToken() {
    return localStorage.getItem("token");
}

function authHeaders() {
    const token = getToken();

    return {
        "Content-Type": "application/json",
        ...(token && { "Authorization": "Bearer " + token })
    };
}

// ======================
// ERREUR CENTRALISÉE
// ======================
async function handleResponse(res) {
    if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        throw new Error(error.detail || "Erreur serveur");
    }
    return res.json();
}

// ======================
// AUTH CHECK
// ======================
function requireAuth() {
    if (!getToken()) {
        window.location.href = "index.html";
    }
}

function logout() {
    localStorage.clear();
    window.location.href = "index.html";
}
async function apiLogin(email, password) {

    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    const res = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        body: formData
    });

    const data = await handleResponse(res);

    localStorage.setItem("token", data.access_token);
    localStorage.setItem("user_id", data.user_id);
    localStorage.setItem("role", data.role);
    localStorage.setItem("nom", data.nom);

    return data;
}
async function getCours() {
    const res = await fetch(`${API_URL}/api/cours/`, {
        headers: authHeaders()
    });
    return handleResponse(res);
}

async function createCours(titre, description) {
    const res = await fetch(`${API_URL}/api/cours/`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ titre, description })
    });

    return handleResponse(res);
}

async function deleteCours(id) {
    const res = await fetch(`${API_URL}/api/cours/${id}`, {
        method: "DELETE",
        headers: authHeaders()
    });

    return handleResponse(res);
}
async function getLecons(coursId) {
    const res = await fetch(`${API_URL}/api/lecons/cours/${coursId}`, {
        headers: authHeaders()
    });
    return handleResponse(res);
}

async function getLecon(leconId) {
    const res = await fetch(`${API_URL}/api/lecons/${leconId}`, {
        headers: authHeaders()
    });
    return handleResponse(res);
}

async function getQuiz(leconId) {
    const res = await fetch(`${API_URL}/api/quiz/lecon/${leconId}`, {
        headers: authHeaders()
    });
    return handleResponse(res);
}

async function soumettreReponse(quizId, reponseId) {
    const res = await fetch(`${API_URL}/api/quiz/${quizId}/soumettre`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ reponse_id: reponseId })
    });

    return handleResponse(res);
}
async function saveProgression(leconId, statut, score) {
    const res = await fetch(`${API_URL}/api/progression/`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ lecon_id: leconId, statut, score })
    });

    return handleResponse(res);
}

async function postAvis(coursId, note, commentaire) {
    const res = await fetch(`${API_URL}/api/avis/`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ cours_id: coursId, note, commentaire })
    });

    return handleResponse(res);
}

async function getClassement() {
    const res = await fetch(`${API_URL}/api/avis/classement/profs`, {
        headers: authHeaders()
    });

    return handleResponse(res);
}

async function getUsers() {
    const res = await fetch(`${API_URL}/api/users/`, {
        headers: authHeaders()
    });

    return handleResponse(res);
}

async function createUser(nom, email, mot_de_passe, role) {
    const res = await fetch(`${API_URL}/api/users/`, {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ nom, email, mot_de_passe, role })
    });

    return handleResponse(res);
}

async function deleteUser(id) {
    const res = await fetch(`${API_URL}/api/users/${id}`, {
        method: "DELETE",
        headers: authHeaders()
    });

    return handleResponse(res);
}
async function syncData() {
    const res = await fetch(`${API_URL}/api/sync/`, {
        method: "POST",
        headers: authHeaders()
    });

    return handleResponse(res);
}

async function getSyncStatus() {
    const res = await fetch(`${API_URL}/api/sync/status`, {
        headers: authHeaders()
    });

    return handleResponse(res);
}
