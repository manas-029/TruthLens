(function () {
    function debounce(fn, wait) {
        let timer;
        return function (...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), wait);
        };
    }

    function verdictPill(verdict) {
        const label = verdict === "fake" ? "Deepfake" : verdict === "real" ? "Authentic" : "Uncertain";
        return `<span class="history-pill verdict-badge ${verdict}">${label}</span>`;
    }

    async function loadHistory(page = 1) {
        const list = document.getElementById("history-list");
        const pagination = document.getElementById("history-pagination");
        const search = document.getElementById("history-search");
        const type = document.getElementById("history-type");
        const verdict = document.getElementById("history-verdict");
        const params = new URLSearchParams({
            page,
            q: search.value,
            type: type.value,
            verdict: verdict.value,
        });

        const response = await fetch(`${window.truthlensConfig.urls.history}?${params.toString()}`);
        const data = await response.json();
        list.innerHTML = data.results.length
            ? data.results
                  .map(
                      (item) => `
                <article class="history-row">
                    <div class="history-row-top">
                        <div class="history-thumb"></div>
                        <div>
                            <strong>${item.file_name}</strong>
                            <div class="history-meta">${new Date(item.created_at).toLocaleString()}</div>
                        </div>
                        <div>${item.file_type}</div>
                        <div>${verdictPill(item.verdict)}</div>
                        <div>${Math.round(item.confidence_score)}%</div>
                        <a class="button button-secondary" href="/result/${item.id}/">Open</a>
                    </div>
                    <div class="history-row-bottom">
                        <div>${item.ai_explanation}</div>
                        <div class="history-meta">Processing time: ${item.processing_time_ms} ms</div>
                    </div>
                </article>
            `
                  )
                  .join("")
            : `<div class="live-feed-entry">No detection records match the current filters.</div>`;

        pagination.innerHTML = `
            <button class="button button-secondary" ${!data.pagination.has_previous ? "disabled" : ""} data-page="${page - 1}">Previous</button>
            <span>Page ${data.pagination.page} of ${data.pagination.pages || 1}</span>
            <button class="button button-secondary" ${!data.pagination.has_next ? "disabled" : ""} data-page="${page + 1}">Next</button>
        `;

        pagination.querySelectorAll("button[data-page]").forEach((button) => {
            button.addEventListener("click", () => loadHistory(button.dataset.page));
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        if (document.body.dataset.page !== "history") return;
        const search = document.getElementById("history-search");
        const type = document.getElementById("history-type");
        const verdict = document.getElementById("history-verdict");
        const rerender = debounce(() => loadHistory(1), 250);
        [search, type, verdict].forEach((element) => element.addEventListener("input", rerender));
        [type, verdict].forEach((element) => element.addEventListener("change", rerender));
        loadHistory();
    });
})();
