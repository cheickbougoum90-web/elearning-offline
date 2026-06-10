let role = "eleve";

function setRole(selectedRole) {
    role = selectedRole;

    const btnEleve = document.getElementById("btnEleve");
    const btnProf = document.getElementById("btnProf");
    const roleText = document.getElementById("roleText");

    if (!btnEleve || !btnProf || !roleText) {
        console.log("❌ éléments HTML introuvables");
        return;
    }

    if (role === "eleve") {

        btnEleve.className =
            "flex-1 py-2 rounded-full text-sm font-medium bg-white shadow text-blue-600";

        btnProf.className =
            "flex-1 py-2 rounded-full text-sm font-medium text-gray-600";

        roleText.innerText = "Rôle sélectionné : Étudiant";

    } else {

        btnProf.className =
            "flex-1 py-2 rounded-full text-sm font-medium bg-white shadow text-green-600";

        btnEleve.className =
            "flex-1 py-2 rounded-full text-sm font-medium text-gray-600";

        roleText.innerText = "Rôle sélectionné : Professeur";
    }

    console.log("ROLE =", role);
}

function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const error = document.getElementById("error");

    error.classList.add("hidden");

    if (!email || !password) {
        error.innerText = "Remplis tous les champs";
        error.classList.remove("hidden");
        return;
    }

    if (!email.includes("@")) {
        error.innerText = "Email invalide";
        error.classList.remove("hidden");
        return;
    }

    // REDIRECTION
    if (role === "eleve") {
        window.location.href = "eleve.html";
    } else {
        window.location.href = "prof.html";
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