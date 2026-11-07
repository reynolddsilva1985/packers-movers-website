/* Movers4Less website interactions.
   Before launch, set quoteEmail in this file or connect a dedicated form endpoint.
   Do not publish the quote form as live until this is configured and tested. */
const MOVERS4LESS_CONFIG = {
  quoteEmail: "", // Add the business enquiry email address before launch.
};

document.addEventListener("DOMContentLoaded", () => {
  const year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();

  const menuButton = document.querySelector(".menu-toggle");
  const navigation = document.getElementById("primary-nav");

  if (menuButton && navigation) {
    menuButton.addEventListener("click", () => {
      const expanded = menuButton.getAttribute("aria-expanded") === "true";
      menuButton.setAttribute("aria-expanded", String(!expanded));
      menuButton.setAttribute("aria-label", expanded ? "Open navigation" : "Close navigation");
      navigation.classList.toggle("is-open", !expanded);
    });

    navigation.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        menuButton.setAttribute("aria-expanded", "false");
        menuButton.setAttribute("aria-label", "Open navigation");
        navigation.classList.remove("is-open");
      });
    });
  }

  const dateField = document.getElementById("move-date");
  if (dateField) {
    const today = new Date();
    const localToday = new Date(today.getTime() - today.getTimezoneOffset() * 60000)
      .toISOString()
      .slice(0, 10);
    dateField.min = localToday;
  }

  const form = document.getElementById("quote-form");
  const status = document.getElementById("form-message");

  if (form && status) {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      status.classList.remove("is-visible");
      status.textContent = "";

      const data = new FormData(form);
      if (String(data.get("companyWebsite") || "").trim()) return;

      if (!form.reportValidity()) return;

      const quoteEmail = MOVERS4LESS_CONFIG.quoteEmail.trim();
      if (!quoteEmail) {
        status.textContent = "The quotation form is designed and ready, but it has not yet been connected to the business enquiry inbox. Please do not publish this version until the contact email and form delivery have been configured and tested.";
        status.classList.add("is-visible");
        return;
      }

      const subject = encodeURIComponent("Movers4Less quote request - " + String(data.get("name")).trim());
      const lines = [
        "New Movers4Less quote request",
        "",
        "Name: " + data.get("name"),
        "Email: " + data.get("email"),
        "Phone: " + (data.get("phone") || "Not provided"),
        "Service: " + data.get("moveType"),
        "Preferred date: " + (data.get("moveDate") || "Not specified"),
        "Moving from: " + data.get("fromPostcode"),
        "Moving to: " + data.get("toPostcode"),
        "",
        "Additional details:",
        data.get("details") || "None provided"
      ];
      const body = encodeURIComponent(lines.join("\n"));
      window.location.href = "mailto:" + encodeURIComponent(quoteEmail) + "?subject=" + subject + "&body=" + body;
      status.textContent = "Your email app should open with the quote details ready to send. Please send the email to complete your enquiry.";
      status.classList.add("is-visible");
    });
  }
});