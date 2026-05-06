(function () {
    const logMessages = [
        "Handshake with detection engine established.",
        "Normalizing stream envelope and extracting signal layers.",
        "Cross-checking artifact signatures against manipulation heuristics.",
        "Running confidence fusion across multimodal evidence.",
        "Compiling plain-language analyst summary.",
    ];

    function resetProgress() {
        document.querySelectorAll(".progress-steps .step").forEach((step, index) => {
            step.classList.toggle("active", index === 0);
            step.classList.remove("complete");
        });
        const bar = document.getElementById("progress-bar");
        if (bar) bar.style.width = "0%";
        const log = document.getElementById("live-log");
        if (log) log.innerHTML = "";
    }

    function appendLog(message) {
        const log = document.getElementById("live-log");
        if (!log) return;
        const entry = document.createElement("div");
        entry.className = "live-feed-entry";
        entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        log.prepend(entry);
    }

    function simulateRealtime() {
        resetProgress();
        let progress = 0;
        let stepIndex = 0;
        const steps = Array.from(document.querySelectorAll(".progress-steps .step"));
        const timer = setInterval(() => {
            progress = Math.min(progress + 16, 96);
            const bar = document.getElementById("progress-bar");
            if (bar) bar.style.width = `${progress}%`;
            appendLog(logMessages[Math.floor(Math.random() * logMessages.length)]);

            if (progress >= (stepIndex + 1) * 24 && steps[stepIndex]) {
                steps[stepIndex].classList.remove("active");
                steps[stepIndex].classList.add("complete");
                stepIndex += 1;
                if (steps[stepIndex]) {
                    steps[stepIndex].classList.add("active");
                }
            }
        }, 650);
        return timer;
    }

    window.TruthLensRealtime = {
        resetProgress,
        appendLog,
        simulateRealtime,
    };
})();
