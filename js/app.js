(() => {
  const translations = window.KUNDLI_TRANSLATIONS;
  const languageSelect = document.getElementById("language");
  let language = "en";
  const signsEnglish = translations.en.signs;
  const signsHindi = translations.hi.signs;
  const samplePlanets = {
    1: ["Ascendant", "Mars"], 2: ["Venus"], 3: ["Moon"], 4: [],
    5: ["Sun"], 6: ["Mercury"], 7: ["Ketu"], 8: ["Saturn"],
    9: ["Jupiter"], 10: [], 11: ["Rahu"], 12: []
  };
  const planetNames = {
    en: {Ascendant:"Ascendant", Mars:"Mars", Venus:"Venus", Moon:"Moon", Sun:"Sun", Mercury:"Mercury", Ketu:"Ketu", Saturn:"Saturn", Jupiter:"Jupiter", Rahu:"Rahu"},
    hi: {Ascendant:"लग्न", Mars:"मंगल", Venus:"शुक्र", Moon:"चन्द्र", Sun:"सूर्य", Mercury:"बुध", Ketu:"केतु", Saturn:"शनि", Jupiter:"गुरु", Rahu:"राहु"}
  };
  const abbreviations = {Ascendant:"Asc", Mars:"Ma", Venus:"Ve", Moon:"Mo", Sun:"Su", Mercury:"Me", Ketu:"Ke", Saturn:"Sa", Jupiter:"Ju", Rahu:"Ra"};
  const signEnglishHindi = ["मेष","वृषभ","मिथुन","कर्क","सिंह","कन्या","तुला","वृश्चिक","धनु","मकर","कुम्भ","मीन"];
  const houseButtons = [...document.querySelectorAll(".house")];

  function t(key) { return translations[language][key] ?? translations.en[key] ?? key; }

  function renderLanguage() {
    document.documentElement.lang = language === "hi" ? "hi" : "en";
    document.querySelectorAll("[data-i18n]").forEach(el => {
      const key = el.dataset.i18n;
      if (translations[language][key]) el.textContent = translations[language][key];
    });
    houseButtons.forEach(button => {
      const n = Number(button.dataset.house);
      button.setAttribute("aria-label", `${t("house")} ${n}`);
      button.querySelector(".house-number").textContent = n;
      button.querySelector(".house-sign").textContent = language === "hi" ? signsHindi[n-1] : signsEnglish[n-1];
      button.querySelector(".planet-list").textContent = samplePlanets[n].map(p => abbreviations[p]).join(" · ") || "—";
    });
    renderSelectedHouse(Number(document.querySelector(".house.selected")?.dataset.house || 1));
  }

  function renderSelectedHouse(n) {
    houseButtons.forEach(b => b.classList.toggle("selected", Number(b.dataset.house) === n));
    const names = language === "hi" ? signsHindi : signsEnglish;
    document.getElementById("detail-title").textContent = `${t("house")} ${n}`;
    document.getElementById("detail-sign").textContent = `${names[n-1]}${language === "hi" ? "" : " · " + signsHindi[n-1]}`;
    document.getElementById("detail-planets").textContent = samplePlanets[n].length
      ? samplePlanets[n].map(p => planetNames[language][p]).join(", ")
      : (language === "hi" ? "कोई उदाहरण ग्रह नहीं" : "No sample planets");
  }

  houseButtons.forEach(button => button.addEventListener("click", () => renderSelectedHouse(Number(button.dataset.house))));
  languageSelect.addEventListener("change", e => { language = e.target.value; renderLanguage(); });

  document.getElementById("birth-form").addEventListener("submit", e => {
    e.preventDefault();
    const date = document.getElementById("birth-date").value;
    const time = document.getElementById("birth-time").value;
    const place = document.getElementById("birth-place").value.trim();
    const status = document.getElementById("form-status");
    if (!date || !time || !place) {
      status.textContent = t("needFields");
      return;
    }
    const name = document.getElementById("person-name").value.trim();
    const caption = document.getElementById("chart-caption");
    caption.textContent = [name, place, date, time].filter(Boolean).join(" · ") + " — " + (language === "hi" ? "केवल प्रारूप" : "preview only");
    status.textContent = t("submitted");
  });

  renderLanguage();
})();