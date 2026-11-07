/* Movers4Less concept site interactions. No analytics, tracking or form submission. */
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

  // This calculator uses only anonymous selections in the current browser session.
  const estimator = document.getElementById("estimate-form");
  const result = document.getElementById("estimate-result");
  if (estimator && result) {
    const money = (value) => new Intl.NumberFormat("en-GB", {
      style: "currency", currency: "GBP", maximumFractionDigits: 0
    }).format(value);

    estimator.addEventListener("submit", (event) => {
      event.preventDefault();
      const data = new FormData(estimator);
      const size = String(data.get("size") || "one");
      const distance = String(data.get("distance") || "local");
      const access = String(data.get("access") || "easy");
      const packing = String(data.get("packing") || "self");
      const extra = String(data.get("extra") || "none");

      if (size === "large" || distance === "long" || access === "complex" || extra === "special") {
        result.innerHTML = '<span class="estimate-result__label">A personal assessment would be needed</span><p>This combination is too complex for a simple guide estimate. A future service would need an inventory, access review and specialist assessment before pricing.</p>';
        return;
      }

      const base = {
        part: [245, 375], studio: [350, 475], one: [495, 625],
        two: [695, 895], three: [895, 1175], four: [1250, 1650]
      };
      const distanceAdd = {
        local: [0, 0], near: [45, 65], mid: [100, 145], far: [210, 290]
      };
      const packAdd = {
        part: { kit:[15,25], fragile:[70,110], full:[120,180] },
        studio: { kit:[35,50], fragile:[95,145], full:[160,230] },
        one: { kit:[35,50], fragile:[95,155], full:[180,260] },
        two: { kit:[55,75], fragile:[125,190], full:[280,380] },
        three: { kit:[75,105], fragile:[155,230], full:[390,540] },
        four: { kit:[110,150], fragile:[190,280], full:[550,750] }
      };
      let low = base[size][0], high = base[size][1];
      low += distanceAdd[distance][0]; high += distanceAdd[distance][1];
      if (access === "one") { low *= 1.05; high *= 1.08; }
      if (access === "both") { low *= 1.10; high *= 1.15; }
      if (packing !== "self") {
        const addition = packAdd[size][packing];
        low += addition[0]; high += addition[1];
      }
      if (extra === "bulky") { low += 50; high += 120; }

      const assumptions = [];
      assumptions.push(distance === "local" ? "journey up to 15 miles" : "distance allowance included");
      assumptions.push(access === "easy" ? "straightforward access" : "additional access allowance included");
      assumptions.push(packing === "self" ? "self-packing" : "packing allowance included");
      if (extra === "bulky") assumptions.push("bulky-item allowance included");
      result.innerHTML = '<span class="estimate-result__label">Illustrative planning range</span><strong>' + money(low) + ' – ' + money(high) + '</strong><p>Based on ' + assumptions.join(", ") + '. This is not a quotation, booking, price guarantee or availability check. VAT treatment and the actual inventory would need to be confirmed before any future service launch.</p>';
    });
  }
});
