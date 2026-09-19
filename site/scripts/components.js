async function loadNavbar() {
    const navbar = document.getElementById("navbar");

    if (!navbar) {
        return;
    }

    try {
        const response = await fetch("/components/navbar.html");

        if (!response.ok) {
            throw new Error("Failed to load navbar.");
        }

        navbar.innerHTML = await response.text();

        const path = window.location.pathname;

        let activePage = "home";

        if (path.includes("/about.html")) {
            activePage = "about";
        } else if (path.includes("/projects/")) {
            activePage = "projects";
        } else if (path.includes("/contact.html")) {
            activePage = "contact";
        }

        const activeLink = navbar.querySelector(
            `[data-nav="${activePage}"]`
        );

        if (activeLink) {
            activeLink.classList.add("active");
        }

    } catch (error) {
        console.error("Navbar error:", error);
    }
}


async function loadFooter() {
    const footer = document.getElementById("footer");

    if (!footer) {
        return;
    }

    try {
        const response = await fetch("/components/footer.html");

        if (!response.ok) {
            throw new Error("Failed to load footer.");
        }

        footer.innerHTML = await response.text();

    } catch (error) {
        console.error("Footer error:", error);
    }
}


loadNavbar();
loadFooter();