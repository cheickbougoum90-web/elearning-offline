let role = "eleve";

function setRole(selectedRole) {
    role = selectedRole;
    const btnEleve = document.getElementById("btnEleve");
    const btnProf  = document.getElementById("btnProf");
    const roleText = document.getElementById("roleText");

    if (role === "eleve") {
        btnEleve.className = "flex-1 py-2 rounded-full text-sm font-medium bg-white shadow text-blue-600";
        btnProf.className  = "flex-1 py-2 rounded-full text-sm font-medium text-gray-600";
        roleText.innerText = "Rôle sélectionné : Étudiant";
    } else {
        btnProf.className  = "flex-1 py-2 rounded-full text-sm font-medium bg-white shadow text-green-600";
        btnEleve.className = "flex-1 py-2 rounded-full text-sm font-medium text-gray-600";
        roleText.innerText = "Rôle sélectionné : Professeur";
    }
}

async function login() {
    const email    = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const error    = document.getElementById("error");
    const btn      = document.querySelector("button[onclick='login()']");

    error.classList.add("hidden");

    if (!email || !password) {
        error.innerText = "Remplis tous les champs";
        error.classList.remove("hidden");
        return;
    }

    btn.innerText = "Connexion...";
    btn.disabled  = true;

    try {
        const data = await apiLogin(email, password);

        // Vérifier que le rôle correspond au bouton sélectionné
        // (admin peut accéder partout)
        if (data.role === "eleve") {
            window.location.href = "eleve.html";
        } else if (data.role === "professeur") {
            window.location.href = "prof.html";
        } else if (data.role === "admin") {
            window.location.href = "admin.html";
        }

    } catch (err) {
        error.innerText = err.message;
        error.classList.remove("hidden");
        btn.innerText = "Se connecter";
        btn.disabled  = false;
    }
}
async function loginUser(email, password) {

    try {
        const data = await apiLogin(email, password);

        const role = data.role || localStorage.getItem("role");

        if (role === "etudiant") {
            window.location.href = "eleve.html";
        }

        else if (role === "professeur") {
            window.location.href = "prof.html";
        }

        else if (role === "admin") {
            window.location.href = "admin.html";
        }

        else {
            alert("Rôle inconnu");
        }

    } catch (error) {
        alert("Erreur login: " + error.message);
    }
}
