/* Movers4Less site interactions. No analytics, advertising scripts or cookies are installed by this site code. */
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
    const localToday = new Date(today.getTime() - today.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
    dateField.min = localToday;
  }
});
