(function () {
    function showToast(message, type) {
        const container = document.getElementById("toast-container");
        if (!container) return;
        const toast = document.createElement("div");
        toast.className = `toast ${type || ""}`.trim();
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 3500);
    }

    function animateCounter(element, value, suffix = "") {
        if (!element) return;
        const target = Number(value) || 0;
        const start = Number(element.dataset.value || 0);
        const duration = 600;
        const startTime = performance.now();

        function frame(now) {
            const progress = Math.min((now - startTime) / duration, 1);
            const current = start + (target - start) * progress;
            element.textContent = `${Math.round(current)}${suffix}`;
            if (progress < 1) {
                requestAnimationFrame(frame);
            } else {
                element.dataset.value = target;
            }
        }

        requestAnimationFrame(frame);
    }

    window.TruthLens = {
        showToast,
        animateCounter,
    };

    document.addEventListener("DOMContentLoaded", async function () {
        const page = document.body.dataset.page;
        if (page === "index") {
            try {
                const response = await fetch(window.truthlensConfig.urls.analyticsLive);
                const data = await response.json();
                animateCounter(document.getElementById("today-counter"), data.today_count || 0);
            } catch (error) {
                showToast("Unable to load live scan count.", "error");
            }
        }
    });
})();
