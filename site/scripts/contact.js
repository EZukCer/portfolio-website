const form = document.getElementById("contact-form");
const success = document.getElementById("contact-success");
const errorBox = document.getElementById("contact-error");
const errorMessage = document.getElementById("contact-error-message");

const API_URL =
    "https://ly3sv1pzs0.execute-api.eu-west-2.amazonaws.com/enquiry";


if (form) {

    form.addEventListener("submit", async function (event) {

        event.preventDefault();

        errorBox.hidden = true;

        const formData = new FormData(form);

        const data = {
            firstName: formData.get("firstName"),
            lastName: formData.get("lastName"),
            email: formData.get("email"),
            reason: formData.get("reason"),
            message: formData.get("message"),
            website: formData.get("website")
        };

        const submitButton =
            form.querySelector('button[type="submit"]');

        submitButton.disabled = true;
        submitButton.textContent = "Sending...";


        try {

            const response = await fetch(API_URL, {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(data)
            });


            let result = {};

            try {
                result = await response.json();
            } catch {
                result = {};
            }


            if (!response.ok) {

                if (response.status === 400) {
                    throw new Error(
                        result.message ||
                        "Please check your details and try again."
                    );
                }


                if (response.status === 429) {
                    throw new Error(
                        "You're sending messages too quickly. Please wait a moment before trying again."
                    );
                }


                throw new Error(
                    "Something went wrong while sending your message."
                );
            }


            form.hidden = true;
            success.hidden = false;


        } catch (caughtError) {

            console.error(
                "Contact form error:",
                caughtError
            );


            if (caughtError instanceof TypeError) {

                errorMessage.textContent =
                    "We couldn't reach the contact service. Please check your internet connection and try again.";

            } else {

                errorMessage.textContent =
                    `${caughtError.message} If the problem continues, please try again later or contact me through GitHub.`;
            }


            form.hidden = true;
            errorBox.hidden = false;
        }
    });
}