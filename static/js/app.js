const input = document.getElementById("city-input");
const list = document.getElementById("suggestions");

let timer = null;

input.addEventListener("input", () => {
  clearTimeout(timer);

  const q = input.value.trim();
  if (q.length < 2) {
    list.innerHTML = "";
    return;
  }

  timer = setTimeout(() => {
    fetch(`/search?q=${encodeURIComponent(q)}`)
      .then(res => res.json())
      .then(data => {
        list.innerHTML = "";
        data.forEach(city => {
          const li = document.createElement("li");
          li.textContent = `${city.name}, ${city.iso}`;
          li.onclick = () => {
            window.location.href =
              `/data/${city.name}?lat=${city.lat}&lon=${city.lon}`;
          };
          list.appendChild(li);
        });
      });
  }, 300); // debounce
});
