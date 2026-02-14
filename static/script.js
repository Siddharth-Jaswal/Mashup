const form = document.getElementById("mashupForm");
const loading = document.getElementById("loading");
const result = document.getElementById("result");
const downloadLink = document.getElementById("downloadLink");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const singer = document.getElementById("singer").value.trim();
    const videos = parseInt(document.getElementById("videos").value);
    const duration = parseInt(document.getElementById("duration").value);

    // 🔥 Frontend Validation
    if (!singer) {
        alert("Singer name cannot be empty.");
        return;
    }

    if (isNaN(videos) || videos <= 10) {
        alert("Number of videos must be greater than 10.");
        return;
    }

    if (isNaN(duration) || duration <= 20) {
        alert("Duration must be greater than 20 seconds.");
        return;
    }

    loading.classList.remove("hidden");
    result.classList.add("hidden");

    const response = await fetch("/create-mashup", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            singer: singer,
            number_of_videos: videos,
            duration: duration,
            output_file: "web_mashup.mp3"
        })
    });

    const data = await response.json();
    loading.classList.add("hidden");

    if (!response.ok) {
        alert("Error: " + data.error);
        return;
    }

    downloadLink.href = `/download/web_mashup.mp3`;
    result.classList.remove("hidden");

    // 🔥 60-second countdown
    let seconds = 60;
    downloadLink.textContent = `Download (Available for ${seconds}s)`;
    downloadLink.classList.remove("disabled");

    const countdown = setInterval(() => {
        seconds--;
        downloadLink.textContent = `Download (Available for ${seconds}s)`;

        if (seconds <= 0) {
            clearInterval(countdown);
            downloadLink.textContent = "File expired";
            downloadLink.style.pointerEvents = "none";
            downloadLink.style.background = "gray";
        }
    }, 1000);

    // 🔒 Disable after first click
    downloadLink.onclick = () => {
        downloadLink.style.pointerEvents = "none";
        downloadLink.textContent = "Downloading...";
    };
});
