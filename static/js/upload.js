(function () {
    function setVerdictBadge(element, verdict) {
        element.className = `verdict-badge ${verdict}`;
        if (verdict === "fake") {
            element.textContent = "✗ DEEPFAKE DETECTED";
        } else if (verdict === "real") {
            element.textContent = "✔ AUTHENTIC";
        } else {
            element.textContent = "◌ UNCERTAIN";
        }
    }

    function updateRing(score) {
        const circle = document.getElementById("confidence-circle");
        const value = document.getElementById("confidence-value");
        if (!circle || !value) return;
        const circumference = 301.59;
        const offset = circumference - (Math.max(0, Math.min(100, score)) / 100) * circumference;
        circle.style.strokeDashoffset = offset;
        value.textContent = `${Math.round(score)}%`;
        circle.style.stroke = score >= 60 ? "var(--danger)" : "var(--mint)";
    }

    function updateMetric(id, score) {
        const element = document.getElementById(id);
        if (element) {
            element.style.width = `${score || 0}%`;
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        if (document.body.dataset.page !== "dashboard") return;

        const zone = document.getElementById("upload-zone");
        const input = document.getElementById("file-input");
        const browse = document.getElementById("browse-button");
        const selectedFile = document.getElementById("selected-file");
        const startButton = document.getElementById("start-analysis");
        const abortButton = document.getElementById("abort-analysis");
        const resultCard = document.getElementById("result-card");
        const badge = document.getElementById("verdict-badge");
        const explanation = document.getElementById("explanation-text");
        const tabs = Array.from(document.querySelectorAll(".tab-button"));
        const resetButton = document.getElementById("analyze-another");
        const reportLink = document.getElementById("download-report");
        let selectedType = "video";
        let currentFile = null;
        let activeController = null;
        let realtimeTimer = null;

        function syncSelectedFile(file) {
            currentFile = file || null;
            selectedFile.textContent = file ? file.name : "No file selected";
        }

        function resetDashboard() {
            resultCard.classList.add("hidden");
            input.value = "";
            syncSelectedFile(null);
            window.TruthLensRealtime.resetProgress();
        }

        tabs.forEach((tab) => {
            tab.addEventListener("click", function () {
                tabs.forEach((item) => item.classList.remove("active"));
                tab.classList.add("active");
                selectedType = tab.dataset.type;
            });
        });

        browse.addEventListener("click", () => input.click());
        input.addEventListener("change", () => syncSelectedFile(input.files[0]));

        ["dragenter", "dragover"].forEach((eventName) => {
            zone.addEventListener(eventName, function (event) {
                event.preventDefault();
                zone.classList.add("dragover");
            });
        });

        ["dragleave", "drop"].forEach((eventName) => {
            zone.addEventListener(eventName, function (event) {
                event.preventDefault();
                zone.classList.remove("dragover");
            });
        });

        zone.addEventListener("drop", function (event) {
            const file = event.dataTransfer.files[0];
            if (!file) return;
            syncSelectedFile(file);
        });

        startButton.addEventListener("click", async function () {
            const file = currentFile;
            if (!file) {
                window.TruthLens.showToast("Choose a file before starting analysis.", "error");
                return;
            }

            const validExtensions = {
                video: [".mp4"],
                audio: [".mp3", ".wav"],
                image: [".jpg", ".jpeg", ".png"],
            };
            const lowerName = file.name.toLowerCase();
            const isValid = validExtensions[selectedType].some((extension) => lowerName.endsWith(extension));
            if (!isValid) {
                window.TruthLens.showToast(`Selected file does not match the ${selectedType} tab.`, "error");
                return;
            }

            const formData = new FormData();
            formData.append("file", file);
            formData.append("file_type", selectedType);
            activeController = new AbortController();

            if (realtimeTimer) clearInterval(realtimeTimer);
            realtimeTimer = window.TruthLensRealtime.simulateRealtime();

            try {
                const response = await fetch(window.truthlensConfig.urls.detect, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": window.truthlensConfig.csrfToken,
                    },
                    body: formData,
                    signal: activeController.signal,
                });

                if (!response.ok) {
                    throw new Error("Detection request failed.");
                }

                const data = await response.json();
                clearInterval(realtimeTimer);
                document.getElementById("progress-bar").style.width = "100%";
                window.TruthLensRealtime.appendLog("Forensic report generated successfully.");

                setVerdictBadge(badge, data.verdict);
                updateRing(data.confidence_score);
                updateMetric("metric-facial", data.facial_inconsistency);
                updateMetric("metric-audio", data.audio_sync_score);
                updateMetric("metric-compression", data.compression_artifacts);
                updateMetric("metric-gan", data.gan_fingerprint);
                explanation.textContent = data.ai_explanation;
                reportLink.href = data.detail_url;
                reportLink.onclick = function () {
                    window.open(data.detail_url, "_blank");
                };
                resultCard.classList.remove("hidden");
                window.TruthLens.showToast("Analysis complete. Result saved to history.", "success");
            } catch (error) {
                if (error.name === "AbortError") {
                    window.TruthLens.showToast("Upload aborted.", "error");
                } else {
                    window.TruthLens.showToast("Unable to complete analysis.", "error");
                }
            }
        });

        abortButton.addEventListener("click", function () {
            if (activeController) activeController.abort();
            if (realtimeTimer) clearInterval(realtimeTimer);
            window.TruthLensRealtime.resetProgress();
        });

        resetButton.addEventListener("click", resetDashboard);
    });
})();
