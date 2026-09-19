const projectContainer = document.getElementById("project");

/**
 * Load project data
 */
async function loadProject() {
    try {
        const params = new URLSearchParams(window.location.search);
        const projectId = params.get("id");

        if (!projectId) {
            throw new Error("No project was specified.");
        }

        const response = await fetch("projects.json");

        if (!response.ok) {
            throw new Error("Failed to load project data.");
        }

        const data = await response.json();

        const project = data.projects.find(
            item => item.id === projectId
        );

        if (!project) {
            throw new Error("Project not found.");
        }

        renderProject(project);

    } catch (error) {
        console.error("Project error:", error);

        projectContainer.innerHTML = `
            <p class="eyebrow">Project</p>
            <h1>Project not found.</h1>
            <p>
                The project you're looking for could not
                be loaded.
            </p>
            <div class="links">
                <a href="index.html">
                    ← Back to Projects
                </a>
            </div>
        `;
    }
}


/**
 * Create project body content
 */
function createBodyContent(body) {
    const content = document.createElement("div");
    content.className = "project-content";

    if (!Array.isArray(body)) {
        return content;
    }

    body.forEach(block => {
        if (block.title) {
            const section = document.createElement("section");
            section.className = "project-section";

            const heading = document.createElement("h2");
            heading.textContent = block.title;

            section.appendChild(heading);

            if (Array.isArray(block.paragraphs)) {
                block.paragraphs.forEach(paragraphText => {
                    const paragraph = document.createElement("p");
                    paragraph.textContent = paragraphText;
                    section.appendChild(paragraph);
                });
            }

            if (block.image) {
                const image = createBodyImage(block.image);
                section.appendChild(image);
            }

            content.appendChild(section);
            return;
        }

        if (Array.isArray(block.paragraphs)) {
            block.paragraphs.forEach(paragraphText => {
                const paragraph = document.createElement("p");
                paragraph.textContent = paragraphText;
                content.appendChild(paragraph);
            });
        }

        if (block.image) {
            const image = createBodyImage(block.image);
            content.appendChild(image);
        }
    });

    return content;
}


/**
 * Create a project body image
 */
function createBodyImage(imageData) {
    const figure = document.createElement("figure");
    figure.className = "project-figure";

    const image = document.createElement("img");
    image.className = "project-body-image";

    // Support image paths and image objects
    const imagePath =
        typeof imageData === "string"
            ? imageData
            : imageData.image;

    image.src = imagePath;

    if (
        typeof imageData === "object" &&
        imageData.alt
    ) {
        image.alt = imageData.alt;
    } else {
        const filename = imagePath
            .split("/")
            .pop()
            .replace(/\.[^/.]+$/, "")
            .replace(/[-_]/g, " ");

        image.alt = filename.replace(
            /\b\w/g,
            character => character.toUpperCase()
        );
    }

    image.loading = "lazy";
    image.decoding = "async";

    image.addEventListener("error", () => {
        console.error(
            `Failed to load project image: ${imagePath}`
        );
        figure.remove();
    });

    figure.appendChild(image);

    if (typeof imageData === "object") {
        if (imageData.title) {
            const title = document.createElement("div");
            title.className = "project-image-title";
            title.textContent = imageData.title;
            figure.appendChild(title);
        }

        if (imageData.caption) {
            const caption = document.createElement("figcaption");
            caption.className = "project-image-caption";
            caption.textContent = imageData.caption;
            figure.appendChild(caption);
        }
    }

    return figure;
}


/**
 * Create project images
 */
function createProjectImages(images) {
    if (!Array.isArray(images) || images.length === 0) {
        return null;
    }

    const container = document.createElement("div");
    container.className = "project-images";

    images.forEach(imageData => {
        if (!imageData) {
            return;
        }

        const figure = document.createElement("figure");
        figure.className = "project-figure";

        const image = document.createElement("img");
        image.className = "project-image";

        const imagePath =
            typeof imageData === "string"
                ? imageData
                : imageData.image;

        image.src = imagePath;

        if (
            typeof imageData === "object" &&
            imageData.alt
        ) {
            image.alt = imageData.alt;
        } else {
            const filename = imagePath
                .split("/")
                .pop()
                .replace(/\.[^/.]+$/, "")
                .replace(/[-_]/g, " ");

            image.alt = filename.replace(
                /\b\w/g,
                character => character.toUpperCase()
            );
        }

        image.loading = "lazy";
        image.decoding = "async";

        image.addEventListener("error", () => {
            console.error(
                `Failed to load project image: ${imagePath}`
            );
            figure.remove();
        });

        figure.appendChild(image);

        if (
            typeof imageData === "object" &&
            imageData.title
        ) {
            const title = document.createElement("div");
            title.className = "project-image-title";
            title.textContent = imageData.title;
            figure.appendChild(title);
        }

        if (
            typeof imageData === "object" &&
            imageData.caption
        ) {
            const caption = document.createElement("figcaption");
            caption.className = "project-image-caption";
            caption.textContent = imageData.caption;
            figure.appendChild(caption);
        }

        container.appendChild(figure);
    });

    if (container.children.length === 0) {
        return null;
    }

    return container;
}


/**
 * Create technology list
 */
function createTechnologies(technologiesList) {
    const technologies = document.createElement("div");
    technologies.className = "project-technologies";

    const technologiesLabel = document.createElement("p");
    technologiesLabel.className = "project-section-label";
    technologiesLabel.textContent = "Technologies";

    const list = document.createElement("div");
    list.className = "project-technology-list";

    if (Array.isArray(technologiesList)) {
        technologiesList.forEach(technology => {
            const element = document.createElement("span");
            element.className = "technology";
            element.textContent = technology;
            list.appendChild(element);
        });
    }

    technologies.appendChild(technologiesLabel);
    technologies.appendChild(list);

    return technologies;
}


/**
 * Render project
 */
function renderProject(project) {
    document.title = `${project.title}`;

    const header = document.createElement("header");
    header.className = "project-header";

    const eyebrow = document.createElement("p");
    eyebrow.className = "eyebrow";
    eyebrow.textContent = `${project.type} · ${project.year}`;

    const title = document.createElement("h1");
    title.textContent = project.title;

    const description = document.createElement("p");
    description.className = "project-description";
    description.textContent = project.description;

    header.appendChild(eyebrow);
    header.appendChild(title);
    header.appendChild(description);

    let mainImage = null;

    if (project.image) {
        mainImage = document.createElement("img");
        mainImage.className = "project-image";
        mainImage.src = project.image;
        mainImage.alt = `${project.title} Project Image`;
        mainImage.loading = "eager";
        mainImage.decoding = "async";

        mainImage.addEventListener("error", () => {
            console.error(
                `Failed to load project image: ${project.image}`
            );
            mainImage.remove();
        });
    }

    const technologies = createTechnologies(
        project.technologies
    );

    const projectImages = createProjectImages(
        project.images
    );

    const content = createBodyContent(
        project.body
    );

    const navigation = document.createElement("div");
    navigation.className = "project-navigation";

    const backLink = document.createElement("a");
    backLink.href = "index.html";
    backLink.textContent = "← Back to Projects";

    navigation.appendChild(backLink);

    projectContainer.innerHTML = "";
    projectContainer.appendChild(header);

    if (mainImage) {
        projectContainer.appendChild(mainImage);
    }

    projectContainer.appendChild(technologies);

    if (projectImages) {
        projectContainer.appendChild(projectImages);
    }

    projectContainer.appendChild(content);
    projectContainer.appendChild(navigation);
}


/**
 * Start application
 */
loadProject();