let projects = [];

const projectsList = document.getElementById("projects-list");
const technologyFilters = document.getElementById("technology-filters");
const typeFilters = document.getElementById("type-filters");
const sortSelect = document.getElementById("project-sort");


async function loadProjects() {
    try {
        const response = await fetch("projects.json");

        if (!response.ok) {
            throw new Error("Failed to load projects.");
        }

        const data = await response.json();

        projects = data.projects;

        createTechnologyFilters();
        createTypeFilters();
        renderProjects();

    } catch (error) {
        console.error("Projects error:", error);

        projectsList.innerHTML = `
            <p>
                Projects could not be loaded.
                Please try again later.
            </p>
        `;
    }
}


/*
 * Create technology filters from projects.json
 */

function createTechnologyFilters() {
    const technologies = new Set();

    projects.forEach(project => {
        project.technologies.forEach(technology => {
            technologies.add(technology);
        });
    });

    const sortedTechnologies = [...technologies].sort(
        (a, b) => a.localeCompare(b)
    );

    technologyFilters.innerHTML = "";

    sortedTechnologies.forEach(technology => {
        const label = document.createElement("label");

        const input = document.createElement("input");

        input.type = "checkbox";
        input.value = technology;

        input.addEventListener(
            "change",
            renderProjects
        );

        label.appendChild(input);
        label.append(
            document.createTextNode(` ${technology}`)
        );

        technologyFilters.appendChild(label);
    });
}


/*
 * Create project type filters from projects.json
 */

function createTypeFilters() {
    const types = new Set();

    projects.forEach(project => {
        types.add(project.type);
    });

    const sortedTypes = [...types].sort(
        (a, b) => a.localeCompare(b)
    );

    typeFilters.innerHTML = "";

    sortedTypes.forEach(type => {
        const label = document.createElement("label");

        const input = document.createElement("input");

        input.type = "checkbox";
        input.value = type;

        input.addEventListener(
            "change",
            renderProjects
        );

        label.appendChild(input);
        label.append(
            document.createTextNode(` ${type}`)
        );

        typeFilters.appendChild(label);
    });
}


/*
 * Get selected technology filters
 */

function getSelectedTechnologies() {
    return [...technologyFilters.querySelectorAll(
        'input[type="checkbox"]:checked'
    )].map(input => input.value);
}


/*
 * Get selected type filters
 */

function getSelectedTypes() {
    return [...typeFilters.querySelectorAll(
        'input[type="checkbox"]:checked'
    )].map(input => input.value);
}


/*
 * Filter projects
 */

function filterProjects(projectList) {
    const selectedTechnologies =
        getSelectedTechnologies();

    const selectedTypes =
        getSelectedTypes();

    return projectList.filter(project => {

        const technologyMatch =
            selectedTechnologies.length === 0 ||
            selectedTechnologies.every(technology =>
                project.technologies.includes(technology)
            );

        const typeMatch =
            selectedTypes.length === 0 ||
            selectedTypes.includes(project.type);

        return technologyMatch && typeMatch;
    });
}


/*
 * Sort projects
 */

function sortProjects(projectList) {
    const sortValue = sortSelect.value;

    return [...projectList].sort((a, b) => {

        switch (sortValue) {

            case "newest":
                return b.year - a.year;

            case "oldest":
                return a.year - b.year;

            case "az":
                return a.title.localeCompare(b.title);

            case "za":
                return b.title.localeCompare(a.title);

            default:
                return 0;
        }
    });
}


/*
 * Create a project card
 */

function createProjectCard(project) {

    const card = document.createElement("a");

    card.href = `project.html?id=${encodeURIComponent(
        project.id
    )}`;

    card.className = "project-card";

    const content = document.createElement("div");

    content.className = "project-card-content";


    const header = document.createElement("div");

    header.className = "project-card-header";


    const title = document.createElement("h2");

    title.textContent = project.title;


    const year = document.createElement("span");

    year.textContent = project.year;


    header.appendChild(title);
    header.appendChild(year);


    const description = document.createElement("p");

    description.textContent = project.description;


    content.appendChild(header);
    content.appendChild(description);


    /*
     * Technology footer
     */

    const footer = document.createElement("div");

    footer.className = "project-card-footer";


    project.technologies.forEach(technology => {

        const technologyElement =
            document.createElement("span");

        technologyElement.className =
            "technology";

        technologyElement.textContent =
            technology;

        /*
         * Add a CSS class based on the technology.
         *
         * This lets technologies such as AWS and Python
         * have their own colours without changing the JSON.
         */

        const technologyClass =
            technology
                .toLowerCase()
                .replace(/[^a-z0-9]+/g, "-")
                .replace(/^-|-$/g, "");

        technologyElement.classList.add(
            `technology-${technologyClass}`
        );

        footer.appendChild(
            technologyElement
        );
    });


    card.appendChild(content);
    card.appendChild(footer);


    return card;
}


/*
 * Render filtered and sorted projects
 */

function renderProjects() {

    const filteredProjects =
        filterProjects(projects);

    const sortedProjects =
        sortProjects(filteredProjects);

    projectsList.innerHTML = "";


    if (sortedProjects.length === 0) {

        const emptyMessage =
            document.createElement("p");

        emptyMessage.textContent =
            "No projects match the selected filters.";

        projectsList.appendChild(
            emptyMessage
        );

        return;
    }


    sortedProjects.forEach(project => {

        const card =
            createProjectCard(project);

        projectsList.appendChild(card);
    });
}


/*
 * Sorting
 */

sortSelect.addEventListener(
    "change",
    renderProjects
);


/*
 * Start application
 */

loadProjects();