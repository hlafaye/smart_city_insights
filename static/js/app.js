document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("cityInput");
    const list = document.getElementById("suggestions");
    const latEl = document.getElementById("lat");
    const lonEl = document.getElementById("lon");
    const bboxEl = document.getElementById("bbox");
    const btn = document.getElementById("exploreBtn");
  
    if (!input || !list || !latEl || !lonEl || !btn) return;
  
    let timer = null;
  
    function clearSuggestions() {
      list.innerHTML = "";
      list.classList.remove("open");
    }
  
    function setSelected(city) {
      input.value = `${city.name}, ${city.iso}`;
      latEl.value = city.lat;
      lonEl.value = city.lon;
      bboxEl.value = JSON.stringify(city.bbox);
      btn.disabled = false;
      clearSuggestions();
    }
  
    input.addEventListener("input", () => {
      clearTimeout(timer);
  
      latEl.value = "";
      lonEl.value = "";
      btn.disabled = true;
  
      const q = input.value.trim();
      if (q.length < 2) {
        clearSuggestions();
        return;
      }
  
      timer = setTimeout(async () => {
        try {
          const res = await fetch(`/search?q=${encodeURIComponent(q)}`);
          const data = await res.json();
  
          clearSuggestions();
          if (!Array.isArray(data) || data.length === 0) return;
  
          data.forEach((city) => {
            const li = document.createElement("li");
            li.className = "suggestion-item";
  
            li.innerHTML = `
              <span class="city-name">${city.name}</span>
              <span class="city-iso">${city.iso}</span>
            `;
  
            li.addEventListener("click", () => setSelected(city));
            list.appendChild(li);
          });
  
          list.classList.add("open");
        } catch (e) {
          clearSuggestions();
        }
      }, 250);
    });
  
    // click dehors => ferme
    document.addEventListener("click", (e) => {
      if (!e.target.closest(".autocomplete")) clearSuggestions();
    });
  });
  



//   #overall score

  document.addEventListener("DOMContentLoaded", () => {
    const score = window.__OVERALL_SCORE__ ?? 0;
    const max = 100;
  
    const circle = document.querySelector(".gauge-progress");
    const valueEl = document.getElementById("overallValue");
    const labelEl = document.getElementById("overallLabel");
  
    if (!circle) return;
  
    const radius = 50;
    const circumference = 2 * Math.PI * radius;
  
    circle.style.strokeDasharray = circumference;
  
    const offset = circumference * (1 - score / max);
    requestAnimationFrame(() => {
      circle.style.strokeDashoffset = offset;
    });
  
    // compteur animé
    let current = 0;
    const step = Math.max(1, Math.floor(score / 40));
  
    const interval = setInterval(() => {
      current += step;
      if (current >= score) {
        current = score;
        clearInterval(interval);
      }
      valueEl.textContent = current;
    }, 20);
  
    labelEl.textContent = window.__OVERALL_LABEL__ || "";
  });
  