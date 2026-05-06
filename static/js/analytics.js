(function () {
    let charts = {};

    function createOrUpdateChart(id, config) {
        const canvas = document.getElementById(id);
        if (!canvas) return;
        if (charts[id]) charts[id].destroy();
        charts[id] = new Chart(canvas, config);
    }

    async function refreshLiveStats() {
        const response = await fetch(window.truthlensConfig.urls.analyticsLive);
        const data = await response.json();
        window.TruthLens.animateCounter(document.getElementById("stat-total"), data.total_scans || 0);
        window.TruthLens.animateCounter(document.getElementById("stat-fakes"), data.deepfakes_found || 0);
        window.TruthLens.animateCounter(document.getElementById("stat-real"), data.authentics || 0);
        window.TruthLens.animateCounter(document.getElementById("stat-accuracy"), data.accuracy_rate || 0, "%");

        const feed = document.getElementById("analytics-feed");
        if (feed) {
            feed.innerHTML = data.live_feed.length
                ? data.live_feed
                      .map(
                          (item) =>
                              `<div class="live-feed-entry">${item.file_name} | ${item.file_type} | ${item.verdict} | ${Math.round(item.confidence_score)}%</div>`
                      )
                      .join("")
                : `<div class="live-feed-entry">No scan activity yet.</div>`;
        }
    }

    async function refreshCharts() {
        const response = await fetch(window.truthlensConfig.urls.analyticsChart);
        const data = await response.json();
        const textColor = "#edf4ff";
        const gridColor = "rgba(255,255,255,0.08)";

        const baseOptions = {
            responsive: true,
            plugins: {
                legend: { labels: { color: textColor } },
            },
            scales: {
                x: { ticks: { color: textColor }, grid: { color: gridColor } },
                y: { ticks: { color: textColor }, grid: { color: gridColor } },
            },
        };

        createOrUpdateChart("line-chart", {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [{
                    label: "Detections",
                    data: data.detections_over_time,
                    borderColor: "#00f5a0",
                    backgroundColor: "rgba(0,245,160,0.16)",
                    tension: 0.35,
                    fill: true,
                }],
            },
            options: baseOptions,
        });

        createOrUpdateChart("doughnut-chart", {
            type: "doughnut",
            data: {
                labels: Object.keys(data.type_breakdown),
                datasets: [{
                    data: Object.values(data.type_breakdown),
                    backgroundColor: ["#00f5a0", "#ff3b5c", "#9cb3ff"],
                }],
            },
            options: { responsive: true, plugins: { legend: { labels: { color: textColor } } } },
        });

        createOrUpdateChart("bar-chart", {
            type: "bar",
            data: {
                labels: Object.keys(data.confidence_distribution),
                datasets: [{
                    label: "Confidence buckets",
                    data: Object.values(data.confidence_distribution),
                    backgroundColor: ["#16353f", "#237c67", "#ff7c59", "#ff3b5c"],
                }],
            },
            options: baseOptions,
        });

        createOrUpdateChart("area-chart", {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: "Deepfake",
                        data: data.fake_series,
                        borderColor: "#ff3b5c",
                        backgroundColor: "rgba(255,59,92,0.18)",
                        fill: true,
                        tension: 0.35,
                    },
                    {
                        label: "Authentic",
                        data: data.real_series,
                        borderColor: "#00f5a0",
                        backgroundColor: "rgba(0,245,160,0.14)",
                        fill: true,
                        tension: 0.35,
                    },
                ],
            },
            options: baseOptions,
        });

        const map = document.getElementById("threat-map");
        if (map) {
            const max = Math.max(...data.threat_map.map((item) => item.intensity), 1);
            map.innerHTML = data.threat_map
                .map(
                    (item) => `
                    <div class="threat-row">
                        <div>${item.label}</div>
                        <div class="threat-bar"><span style="width:${(item.intensity / max) * 100}%"></span></div>
                    </div>
                `
                )
                .join("");
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        if (document.body.dataset.page !== "analytics") return;
        refreshLiveStats();
        refreshCharts();
        setInterval(refreshLiveStats, 5000);
        setInterval(refreshCharts, 5000);
    });
})();
