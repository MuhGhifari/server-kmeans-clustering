import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Intelijen Armada Server",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.kpi-card {
    background: #ffffff;
    padding: 18px 20px;
    border-radius: 10px;
    border: 1px solid #e8ecf0;
    border-left: 4px solid #2e6c80;
    margin-bottom: 4px;
}
.kpi-title { font-size: 0.78rem; color: #6c757d; font-weight: 600;
             text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }
.kpi-value { font-size: 1.75rem; color: #1a2332; font-weight: 700; line-height: 1.1; }
.kpi-sub   { font-size: 0.78rem; color: #9ca3af; margin-top: 2px; }

.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.badge-red    { background: #fee2e2; color: #991b1b; }
.badge-blue   { background: #dbeafe; color: #1e40af; }
.badge-gray   { background: #f1f5f9; color: #475569; }
.badge-off    { background: #f3f4f6; color: #6b7280; }
.badge-purple { background: #ede9fe; color: #5b21b6; }
.badge-amber  { background: #fef3c7; color: #92400e; }
.badge-green  { background: #dcfce7; color: #166534; }

.callout {
    background: #f0f9ff;
    border-left: 4px solid #0ea5e9;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    font-size: 0.88rem;
    color: #0c4a6e;
    margin: 10px 0 18px;
    line-height: 1.6;
}
.callout-warn {
    background: #fffbeb;
    border-left: 4px solid #f59e0b;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    font-size: 0.88rem;
    color: #78350f;
    margin: 10px 0 18px;
    line-height: 1.6;
}

.insight-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 16px 18px;
    margin-top: 14px;
    font-size: 0.85rem;
    color: #374151;
    line-height: 1.7;
}
.insight-box strong { color: #1a2332; }

.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #94a3b8;
    margin-bottom: 6px;
}

.stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid #e8ecf0; }
.stTabs [data-baseweb="tab"] { padding: 10px 18px; font-size: 0.9rem; }
.stTabs [aria-selected="true"] { border-bottom: 2px solid #2e6c80; color: #2e6c80; font-weight: 600; }

.savings-card {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    border: 1px solid #bbf7d0;
    border-radius: 12px;
    padding: 32px;
    text-align: center;
}
.savings-label { font-size: 0.85rem; color: #166534; font-weight: 600; text-transform: uppercase;
                 letter-spacing: 0.05em; margin-bottom: 8px; }
.savings-value { font-size: 3.2rem; color: #15803d; font-weight: 800; line-height: 1; }
.savings-sub   { font-size: 0.85rem; color: #4ade80; margin-top: 8px; }

.risk-high   { color: #dc2626; font-weight: 600; }
.risk-med    { color: #d97706; font-weight: 600; }
.risk-low    { color: #16a34a; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# METADATA KLASTER
# ==========================================
CLUSTER_META = {
    0: {
        "label": "Produksi Kritis",
        "badge": "badge-red",
        "icon": "🔴",
        "examples": "Database, server navigasi",
        "action": "Pantau ketat. Tidak perlu tindakan.",
        "risk": "high",
        "risk_label": "Tinggi — jangan pernah dinonaktifkan",
        "color": "#ef4444",
        "description": (
            "Server-server ini berjalan dengan utilisasi CPU dan memori tinggi sepanjang waktu dengan uptime 100%. "
            "Koefisien variasi yang rendah (CV ≈ 0,16) menunjukkan bahwa bebannya stabil dan dapat diprediksi — "
            "tidak melonjak-lonjak. Ini adalah inti infrastruktur Anda: database, layanan autentikasi, atau apa pun "
            "yang harus selalu aktif dan tidak boleh mengalami downtime."
        ),
    },
    1: {
        "label": "Produksi Aktif",
        "badge": "badge-blue",
        "icon": "🔵",
        "examples": "Web server, backend API",
        "action": "Pertimbangkan right-sizing jika CPU konsisten < 50%.",
        "risk": "med",
        "risk_label": "Sedang — kandidat right-sizing",
        "color": "#3b82f6",
        "description": (
            "CPU sedang (≈40%) dan memori (≈38%) dengan uptime 100%. Sedikit lebih variatif dibanding klaster kritis "
            "(CV ≈ 0,21), menunjukkan server-server ini menangani trafik nyata yang berfluktuasi sepanjang hari. "
            "Web server dan backend API cocok dengan profil ini. Kondisinya sehat, namun jika utilisasi terus "
            "di bawah 50%, kemungkinan over-provisioned dan bisa dikecilkan spesifikasinya."
        ),
    },
    2: {
        "label": "Burst / Idle",
        "badge": "badge-green",
        "icon": "🟢",
        "examples": "Job backup, tugas terjadwal",
        "action": "Konsolidasi ke infrastruktur bersama atau jadwalkan ulang.",
        "risk": "low",
        "risk_label": "Rendah — kandidat konsolidasi",
        "color": "#22c55e",
        "description": (
            "Rata-rata CPU sangat rendah (≈2,3%) namun dengan rasio puncak-terhadap-rata-rata yang tinggi (≈10×) "
            "dan CV tinggi (≈1,32). Artinya server-server ini hampir selalu idle, tetapi melonjak tajam saat "
            "dipicu — pola khas job batch atau backup. Mereka menyala 24/7 hanya untuk pekerjaan berkala. "
            "Kandidat kuat untuk dikonsolidasi ke infrastruktur penjadwalan job bersama."
        ),
    },
    3: {
        "label": "Dimatikan",
        "badge": "badge-gray",
        "icon": "⚪",
        "examples": "VM cadangan / tidak terpakai",
        "action": "Nonaktifkan segera — tidak ada ROI.",
        "risk": "low",
        "risk_label": "Tidak ada — aman dinonaktifkan",
        "color": "#94a3b8",
        "description": (
            "CPU nol, memori nol, uptime nol. VM-VM ini sepenuhnya mati dan tidak mengonsumsi sumber daya komputasi. "
            "Namun demikian, mereka masih menempati kapasitas lisensi, penyimpanan, dan overhead manajemen. "
            "Jika bukan bagian dari strategi warm-standby, sebaiknya segera dinonaktifkan."
        ),
    },
    4: {
        "label": "Intensif Memori",
        "badge": "badge-purple",
        "icon": "🟣",
        "examples": "Cache, database in-memory, analitik",
        "action": "Tinjau alokasi memori; periksa apakah cache bisa di-tuning.",
        "risk": "med",
        "risk_label": "Sedang — tinjau ukuran memori",
        "color": "#8b5cf6",
        "description": (
            "CPU rendah-sedang (≈29%) namun utilisasi memori sangat tinggi (≈63%) dengan uptime 100%. "
            "Ketidaksesuaian antara CPU dan memori menunjukkan beban kerja in-memory: cache (Redis, Memcached), "
            "mesin analitik in-memory, atau database dengan dataset besar. Server-server ini tidak idle — "
            "mereka bekerja keras, hanya saja bukan pekerjaan yang membutuhkan banyak CPU."
        ),
    },
    5: {
        "label": "Intermiten",
        "badge": "badge-amber",
        "icon": "🟡",
        "examples": "Dev/test, lab, on-demand",
        "action": "Terapkan auto-shutdown di luar jam kerja.",
        "risk": "low",
        "risk_label": "Rendah — kandidat shutdown terjadwal",
        "color": "#f59e0b",
        "description": (
            "Uptime hanya 66% — server ini mati sekitar ⅓ dari total waktu. Saat aktif, CPU rendah (≈9%) "
            "dan perilakunya tidak beraturan (CV tinggi). Ini adalah mesin development atau testing: dipakai "
            "saat jam kerja, kadang lupa dimatikan saat akhir pekan. Menerapkan jadwal auto-shutdown bisa "
            "memangkas biaya operasionalnya 30–40% tanpa dampak bisnis sama sekali."
        ),
    },
}

FEATURE_MAP = {
    'cpu_mean':         'Rata-rata CPU (%)',
    'cpu_median':       'Median CPU (%)',
    'cpu_p25':          'CPU P25 (%)',
    'cpu_p75':          'CPU P75 (%)',
    'cpu_max':          'CPU Maksimum (%)',
    'cpu_std':          'Volatilitas CPU (σ)',
    'mem_mean':         'Rata-rata Memori (%)',
    'mem_median':       'Median Memori (%)',
    'mem_p25':          'Memori P25 (%)',
    'mem_p75':          'Memori P75 (%)',
    'mem_max':          'Memori Maksimum (%)',
    'mem_std':          'Volatilitas Memori (σ)',
    'uptime_ratio':     'Rasio Uptime',
    'cpu_cv':           'Lonjakan CPU (CV)',
    'mem_cv':           'Lonjakan Memori (CV)',
    'cpu_peak_to_mean': 'Rasio Puncak-ke-Rata CPU',
    'mem_peak_to_mean': 'Rasio Puncak-ke-Rata Memori',
    'cpu_iqr':          'Sebaran CPU (IQR)',
    'mem_iqr':          'Sebaran Memori (IQR)',
}

# ==========================================
# MUAT DATA
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_csv("server_cluster_profiles.csv")
    hist = pd.read_csv("historical_server_data.csv", parse_dates=["date"])

    df = df.rename(columns=FEATURE_MAP)
    meta_cols = ['server', 'cluster', 'samples_count']
    metrics = [c for c in df.columns if c not in meta_cols and pd.api.types.is_numeric_dtype(df[c])]

    df["Label Klaster"] = df["cluster"].map(lambda c: CLUSTER_META[c]["label"])
    df["Warna Klaster"] = df["cluster"].map(lambda c: CLUSTER_META[c]["color"])

    cluster_means = df.groupby("cluster")[metrics].mean()
    profile_t = cluster_means.T
    range_diff = (profile_t.max(axis=1) - profile_t.min(axis=1)).replace(0, 1e-9)
    normalized_matrix = (profile_t.subtract(profile_t.min(axis=1), axis=0)).divide(range_diff, axis=0)

    cluster_map = df[["server", "cluster", "Label Klaster"]].drop_duplicates()
    hist = hist.merge(cluster_map, on="server", how="left")
    hist["bulan"] = hist["date"].dt.to_period("M").astype(str)

    return df, metrics, normalized_matrix, hist


df, metrics, normalized_matrix, hist = load_data()
n_servers  = len(df)
n_clusters = df["cluster"].nunique()
fleet_cpu  = df["Rata-rata CPU (%)"].mean()
fleet_mem  = df["Rata-rata Memori (%)"].mean()

# ==========================================
# HEADER
# ==========================================
st.markdown("## 🖥️ Segmentasi Server Berdasarkan Pemakaian")
st.markdown(
    "Data ini dihasilkan dari histori telemetri server perusahaan selama 6 bulan terakhir dari awal tahun 2026. "
)
st.markdown("---")

# ==========================================
# TAB
# ==========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Ringkasan",
    "🏷️ Profil Cluster",
    "📈 Contoh Pemakaian",
    "📉 Tren Penggunaan",
    "🔥 Heatmap Perilaku",
    "💰 Estimasi Penghematan",
])

# ──────────────────────────────────────────
# TAB 1 · RINGKASAN ARMADA
# ──────────────────────────────────────────
with tab1:
    k1, k2, k3, k4 = st.columns(4)
    kpi_data = [
        ("Total Server", f"{n_servers}", "di semua klaster"),
        ("Klaster Perilaku", f"{n_clusters}", "jenis beban kerja berbeda"),
        ("Rata-rata CPU Armada", f"{fleet_cpu:.1f}%", "dari server aktif"),
        ("Rata-rata Memori Armada", f"{fleet_mem:.1f}%", "dari server aktif"),
    ]
    for col, (title, value, sub) in zip([k1, k2, k3, k4], kpi_data):
        col.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-title">{title}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-sub">{sub}</div>'
            f'</div>', unsafe_allow_html=True
        )

    st.markdown("")

    col_pie, col_bar = st.columns([1, 1.3])

    with col_pie:
        st.markdown('<div class="section-label">Distribusi server per klaster</div>', unsafe_allow_html=True)
        counts = df.groupby(["cluster", "Label Klaster"]).size().reset_index(name="Jumlah")
        counts["label_str"] = counts.apply(
            lambda r: f"{CLUSTER_META[r['cluster']]['icon']} {r['Label Klaster']}", axis=1
        )
        colors = [CLUSTER_META[c]["color"] for c in counts["cluster"]]
        fig_pie = px.pie(
            counts, names="label_str", values="Jumlah", hole=0.45,
            color_discrete_sequence=colors,
        )
        fig_pie.update_traces(textposition="outside", textinfo="percent+label",
                              marker=dict(line=dict(color="#ffffff", width=2)))
        fig_pie.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=330)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_bar:
        st.markdown('<div class="section-label">Rata-rata CPU vs Memori per klaster</div>', unsafe_allow_html=True)
        bar_data = df.groupby(["cluster", "Label Klaster"])[
            ["Rata-rata CPU (%)", "Rata-rata Memori (%)"]
        ].mean().reset_index()
        bar_data["label_str"] = bar_data.apply(
            lambda r: f"{CLUSTER_META[r['cluster']]['icon']} {r['Label Klaster']}", axis=1
        )
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="CPU", x=bar_data["label_str"], y=bar_data["Rata-rata CPU (%)"],
            marker_color="#3b82f6", text=bar_data["Rata-rata CPU (%)"].round(1),
            texttemplate="%{text}%", textposition="outside"
        ))
        fig_bar.add_trace(go.Bar(
            name="Memori", x=bar_data["label_str"], y=bar_data["Rata-rata Memori (%)"],
            marker_color="#8b5cf6", text=bar_data["Rata-rata Memori (%)"].round(1),
            texttemplate="%{text}%", textposition="outside"
        ))
        fig_bar.update_layout(
            barmode="group", height=330,
            yaxis=dict(title="Utilisasi (%)", range=[0, 110]),
            xaxis=dict(tickangle=-20),
            legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
            margin=dict(t=30, b=10, l=0, r=0),
            plot_bgcolor="#f8fafc",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown(
        '<div class="callout">💡 <strong>Cara membaca grafik ini:</strong> Klaster 0 (Produksi Kritis) berjalan '
        'pada ~60% CPU dan memori — tinggi namun normal. Klaster 4 (Intensif Memori) menunjukkan perbedaan '
        'mencolok: CPU rendah, memori tinggi. Klaster 2 dan 3 mendekati nol — ini adalah target konsolidasi Anda.'
        '</div>', unsafe_allow_html=True)

    # 3D scatter
    st.markdown("---")
    st.markdown('<div class="section-label">Scatter 3D — CPU × Memori × Lonjakan</div>', unsafe_allow_html=True)
    st.markdown("Setiap titik mewakili satu server. Warna = klaster. Semakin rapat klasternya, semakin "
                "konsisten perilaku server-server di dalamnya.")

    z_options = [m for m in metrics if m not in ["Rata-rata CPU (%)", "Rata-rata Memori (%)"]]
    z_col, _ = st.columns([1, 2])
    z_metric = z_col.selectbox("Metrik sumbu Z:", z_options,
                                index=z_options.index("Lonjakan CPU (CV)") if "Lonjakan CPU (CV)" in z_options else 0)
    fig_3d = px.scatter_3d(
        df, x="Rata-rata CPU (%)", y="Rata-rata Memori (%)", z=z_metric,
        color="Label Klaster",
        hover_name="server" if "server" in df.columns else None,
        opacity=0.75,
        color_discrete_map={CLUSTER_META[c]["label"]: CLUSTER_META[c]["color"] for c in CLUSTER_META},
    )
    fig_3d.update_layout(margin=dict(l=0, r=0, b=0, t=0), height=520,
                         legend=dict(title="Klaster", orientation="v"))
    st.plotly_chart(fig_3d, use_container_width=True)

# ──────────────────────────────────────────
# TAB 2 · PROFIL KLASTER
# ──────────────────────────────────────────
with tab2:
    st.markdown("Setiap klaster mengelompokkan server yang berperilaku serupa. Gunakan tab ini untuk memahami "
                "apa arti setiap klaster secara operasional dan tindakan apa yang perlu diambil.")
    st.markdown("")

    for cid, meta in CLUSTER_META.items():
        count = len(df[df["cluster"] == cid])
        if count == 0:
            continue
        jumlah_label = f"{count} server"
        with st.expander(f"{meta['icon']} Klaster {cid} — **{meta['label']}** ({jumlah_label})", expanded=(cid == 0)):
            left, right = st.columns([1.8, 1])
            with left:
                st.markdown(f'<span class="badge {meta["badge"]}">{meta["label"]}</span>', unsafe_allow_html=True)
                st.markdown(f"**Jenis server:** {meta['examples']}")
                st.markdown(meta["description"])
                risk_cls = f"risk-{meta['risk']}"
                st.markdown(f'**Rekomendasi tindakan:** {meta["action"]}  \n'
                            f'**Risiko dekomisi:** <span class="{risk_cls}">{meta["risk_label"]}</span>',
                            unsafe_allow_html=True)
            with right:
                c_data = df[df["cluster"] == cid]
                stats = {
                    "Rata-rata CPU":       f'{c_data["Rata-rata CPU (%)"].mean():.1f}%',
                    "Rata-rata Memori":    f'{c_data["Rata-rata Memori (%)"].mean():.1f}%',
                    "Uptime":              f'{c_data["Rasio Uptime"].mean():.0%}',
                    "Lonjakan CPU (CV)":   f'{c_data["Lonjakan CPU (CV)"].mean():.2f}',
                    "Rasio Puncak-ke-Rata": f'{c_data["Rasio Puncak-ke-Rata CPU"].mean():.1f}×',
                    "Jumlah server":       str(count),
                }
                for k, v in stats.items():
                    st.markdown(
                        f'<div style="display:flex; justify-content:space-between; '
                        f'padding:6px 0; border-bottom:1px solid #f1f5f9; font-size:0.85rem;">'
                        f'<span style="color:#6b7280;">{k}</span>'
                        f'<span style="font-weight:600; color:#1a2332;">{v}</span></div>',
                        unsafe_allow_html=True
                    )

# ──────────────────────────────────────────
# TAB 3 · SIMULASI LIVE
# ──────────────────────────────────────────
with tab3:
    st.markdown("Simulasi ini menghasilkan rekaman performa 60 detik yang representatif berdasarkan "
                "sidik jari statistik setiap klaster — rata-rata, volatilitas, dan perilaku puncak. "
                "Ini bukan telemetri real-time, namun mencerminkan dengan akurat bagaimana setiap *tipe* klaster berperilaku.")

    st.markdown('<div class="callout-warn">ℹ️ Ini adalah sinyal <strong>simulasi</strong> yang dibangkitkan dari '
                'statistik klaster (rata-rata, std dev, maks). Fungsinya untuk menggambarkan bentuk perilaku — '
                'gunakan tab Tren Penggunaan untuk data historis nyata.</div>', unsafe_allow_html=True)

    sim_col, _ = st.columns([1, 2])
    target_cluster = sim_col.selectbox(
        "Pilih klaster yang akan disimulasikan:",
        options=sorted(df["cluster"].unique()),
        format_func=lambda c: f"Klaster {c} — {CLUSTER_META[c]['label']}"
    )

    c_data = df[df["cluster"] == target_cluster]
    c_cpu_mean = c_data["Rata-rata CPU (%)"].mean()
    c_cpu_max  = c_data["CPU Maksimum (%)"].mean()
    c_cpu_std  = c_data["Volatilitas CPU (σ)"].mean()
    c_mem_mean = c_data["Rata-rata Memori (%)"].mean()
    c_mem_max  = c_data["Memori Maksimum (%)"].mean()
    c_mem_std  = c_data["Volatilitas Memori (σ)"].mean()

    np.random.seed(42)
    t = np.arange(60)

    def gen_wave(mean, std, max_val):
        base = np.sin(t * 0.2) * (std * 0.8) + np.random.normal(0, std * 0.3, 60) + mean
        base = np.clip(base, 0, 100)
        pk = np.random.randint(10, 50)
        if max_val > mean:
            base[pk] = min(max_val, 100)
            if pk > 0:  base[pk-1] = (base[pk-1] + max_val) / 2
            if pk < 59: base[pk+1] = (base[pk+1] + max_val) / 2
        return base

    cpu_w = gen_wave(c_cpu_mean, c_cpu_std, c_cpu_max)
    mem_w = gen_wave(c_mem_mean, c_mem_std, c_mem_max)

    meta = CLUSTER_META[target_cluster]
    fig_sim = go.Figure()
    fig_sim.add_trace(go.Scatter(
        x=t, y=cpu_w, fill="tozeroy", mode="lines",
        line=dict(color="#3b82f6", width=2), fillcolor="rgba(59,130,246,0.12)",
        name=f"CPU  (rata-rata {c_cpu_mean:.1f}%)"
    ))
    fig_sim.add_trace(go.Scatter(
        x=t, y=mem_w, fill="tozeroy", mode="lines",
        line=dict(color="#8b5cf6", width=2), fillcolor="rgba(139,92,246,0.12)",
        name=f"Memori  (rata-rata {c_mem_mean:.1f}%)"
    ))
    fig_sim.add_hline(y=c_cpu_mean, line=dict(color="#3b82f6", width=1, dash="dot"))
    fig_sim.add_hline(y=c_mem_mean, line=dict(color="#8b5cf6", width=1, dash="dot"))
    fig_sim.update_layout(
        plot_bgcolor="#f8fafc",
        xaxis=dict(showgrid=False, showticklabels=False, title="Jendela 60 detik"),
        yaxis=dict(gridcolor="#e8ecf0", range=[0, 105], title="Utilisasi (%)"),
        height=380, hovermode="x unified",
        legend=dict(orientation="h", y=1.08, x=0, xanchor="left"),
        margin=dict(t=40, b=20, l=0, r=0),
        title=dict(text=f"{meta['icon']} Klaster {target_cluster} — pola perilaku {meta['label']}",
                   font=dict(size=13), x=0)
    )
    st.plotly_chart(fig_sim, use_container_width=True)

    st.markdown(
        f'<div class="insight-box">'
        f'<strong>Yang sedang Anda lihat:</strong> {meta["description"]}'
        f'</div>', unsafe_allow_html=True
    )

# ──────────────────────────────────────────
# TAB 4 · TREN PENGGUNAAN
# ──────────────────────────────────────────
with tab4:
    st.markdown("Data harian historis nyata dari Jan–Jun 2026 yang diagregasi per klaster. "
                "Gunakan ini untuk mendeteksi musiman, creep kapasitas, atau pergeseran beban kerja yang tidak terduga.")

    trend_metric = st.radio(
        "Metrik:", ["Utilisasi CPU", "Utilisasi Memori"],
        horizontal=True
    )
    col_key = "cpu_avg" if "CPU" in trend_metric else "mem_avg"
    y_label = "Rata-rata CPU (%)" if "CPU" in trend_metric else "Rata-rata Memori (%)"

    active_hist = hist[(hist["power_state"] == 1) & hist[col_key].notna()].copy()
    active_hist["cluster"] = active_hist["cluster"].astype("Int64")

    daily_cluster = (
        active_hist
        .groupby(["date", "cluster", "Label Klaster"])[col_key]
        .mean()
        .reset_index()
        .rename(columns={col_key: y_label})
    )

    fig_trend = px.line(
        daily_cluster, x="date", y=y_label, color="Label Klaster",
        color_discrete_map={CLUSTER_META[c]["label"]: CLUSTER_META[c]["color"] for c in CLUSTER_META},
        labels={"date": "Tanggal", "Label Klaster": "Klaster"},
    )
    fig_trend.update_traces(line=dict(width=1.8))
    fig_trend.update_layout(
        height=380, plot_bgcolor="#f8fafc",
        xaxis=dict(gridcolor="#e8ecf0", title=""),
        yaxis=dict(gridcolor="#e8ecf0", title=y_label, range=[0, 105]),
        legend=dict(orientation="h", y=-0.25, x=0, xanchor="left", title=""),
        margin=dict(t=20, b=20, l=0, r=0),
        hovermode="x unified",
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown('<div class="section-label">Rata-rata bulanan per klaster</div>', unsafe_allow_html=True)
    monthly = (
        active_hist
        .groupby(["bulan", "Label Klaster"])[col_key]
        .mean()
        .unstack("Label Klaster")
        .round(1)
    )
    st.dataframe(
        monthly.style.background_gradient(cmap="Blues", axis=None),
        use_container_width=True
    )

    st.markdown(
        '<div class="callout">💡 <strong>Yang perlu diperhatikan:</strong> '
        'Tren naik pada Produksi Kritis (merah) bisa menjadi sinyal tekanan kapasitas. '
        'Server Burst/Idle yang terus rendah dari bulan ke bulan mengkonfirmasi bahwa konsolidasi aman dilakukan. '
        'Klaster Intermiten (amber) terkadang tidak muncul pada bulan-bulan ketika servernya sepenuhnya mati.'
        '</div>', unsafe_allow_html=True
    )

# ──────────────────────────────────────────
# TAB 5 · HEATMAP PERILAKU
# ──────────────────────────────────────────
with tab5:
    st.markdown("Setiap metrik dinormalisasi dari **0,00 (terendah di armada)** hingga **1,00 (tertinggi di armada)** "
                "sehingga kita dapat membandingkan CPU, memori, uptime, dan lonjakan secara visual pada skala yang sama — "
                "meskipun diukur dalam satuan yang berbeda.")

    st.markdown('<div class="callout">💡 <strong>Cara membaca heatmap ini:</strong> '
                'Merah gelap = klaster ini tertinggi pada metrik ini dibanding armada. '
                'Biru gelap = terendah. Klaster yang merah terang pada "Rasio Puncak-ke-Rata CPU" '
                'tapi biru gelap pada "Rata-rata CPU" adalah profil burst/idle — lonjakan tinggi, baseline rendah.'
                '</div>', unsafe_allow_html=True)

    col_labels = {c: f"{CLUSTER_META[c]['icon']} {c}: {CLUSTER_META[c]['label']}" for c in CLUSTER_META}
    heatmap_data = normalized_matrix.copy()
    heatmap_data.columns = [col_labels.get(c, str(c)) for c in heatmap_data.columns]

    fig_heat, ax = plt.subplots(figsize=(13, 10))
    sns.heatmap(
        heatmap_data, annot=True, fmt=".2f", cmap="vlag", square=True, ax=ax,
        cbar_kws={"label": "Intensitas relatif (0 = terendah, 1 = tertinggi)", "shrink": 0.6},
        linewidths=0.5, linecolor="#f1f5f9",
    )
    ax.set_ylabel("Metrik telemetri", fontsize=11, labelpad=10)
    ax.set_xlabel("")
    ax.tick_params(axis="y", rotation=0, labelsize=9)
    ax.tick_params(axis="x", rotation=15, labelsize=8)
    plt.tight_layout()
    st.pyplot(fig_heat)

# ──────────────────────────────────────────
# TAB 6 · ESTIMASI PENGHEMATAN
# ──────────────────────────────────────────
with tab6:
    st.markdown("Estimasi dampak biaya tahunan dari keputusan operasional: menonaktifkan server idle, "
                "menjadwalkan auto-shutdown untuk server intermiten, atau mengecilkan spesifikasi mesin yang over-provisioned.")

    st.markdown('<div class="callout-warn">'
                '⚠️ <strong>Ini adalah estimasi.</strong> Penghematan aktual bergantung pada model lisensi Anda, '
                'biaya penyimpanan, dan apakah server yang dinonaktifkan membebaskan perangkat keras fisik. '
                'Gunakan angka ini sebagai dasar diskusi dengan tim keuangan dan infrastruktur Anda.'
                '</div>', unsafe_allow_html=True)

    scenario = st.radio(
        "Skenario optimasi:",
        [
            "🔴 Nonaktifkan satu klaster sepenuhnya",
            "🟡 Auto-shutdown server intermiten (di luar jam kerja)",
            "🔵 Right-size server produksi yang over-provisioned",
        ],
        index=0
    )

    st.markdown("---")
    sim_left, sim_right = st.columns([1.1, 1])

    with sim_left:
        hourly_cost = st.slider(
            "Estimasi biaya per server per jam (USD):",
            min_value=0.05, max_value=10.0, value=0.45, step=0.05,
            help="Biaya gabungan termasuk komputasi, penyimpanan, lisensi, dan overhead operasional."
        )

        if "Nonaktifkan" in scenario:
            all_c = sorted(df["cluster"].unique())
            target = st.selectbox(
                "Pilih klaster yang akan dinonaktifkan:",
                all_c,
                format_func=lambda c: f"Klaster {c} — {CLUSTER_META[c]['label']} ({CLUSTER_META[c]['risk_label']})"
            )
            n = len(df[df["cluster"] == target])
            hours_saved = 24 * 365
            saving_pct  = 1.0
            explanation = (
                f"Menonaktifkan semua **{n}** server di Klaster {target} "
                f"({CLUSTER_META[target]['label']}) menghilangkan biaya operasional mereka sepenuhnya. "
                f"Penghematan tahunan = {n} server × ${hourly_cost:.2f}/jam × 8.760 jam."
            )
            if CLUSTER_META[target]["risk"] == "high":
                st.markdown('<div class="callout-warn">⚠️ Ini adalah klaster <strong>berisiko tinggi</strong> '
                            '(Produksi Kritis). Menonaktifkannya kemungkinan besar akan menyebabkan gangguan layanan. '
                            'Angka yang ditampilkan hanya bersifat teoritis.</div>', unsafe_allow_html=True)

        elif "Auto-shutdown" in scenario:
            st.markdown("Auto-shutdown menghemat biaya selama jam-jam ketika server intermiten/dev sedang mati. "
                        "Jam kerja tipikal adalah pukul 08.00–20.00 pada hari kerja.")
            off_hours = st.slider("Jam tidak aktif per hari (jam server dimatikan):", 6, 18, 12)
            off_days_pct = st.slider("Hari per minggu server mati (mis. 2 = akhir pekan):", 0, 7, 2) / 7
            intermittent = df[df["cluster"] == 5]
            n = len(intermittent)
            weekday_saving = (off_hours / 24) * (5/7)
            weekend_saving = 1.0 * off_days_pct
            saving_pct = weekday_saving + weekend_saving
            hours_saved = saving_pct * 24 * 365
            explanation = (
                f"Mematikan **{n}** server intermiten selama {off_hours} jam/hari pada hari kerja "
                f"dan {int(off_days_pct*7)} hari/minggu di akhir pekan menghemat "
                f"~{saving_pct:.0%} dari biaya operasionalnya."
            )

        else:  # Right-size
            st.markdown("Right-sizing berarti mengganti server yang over-provisioned dengan tier instance yang lebih kecil. "
                        "Penghematan tipikal saat turun satu tier instance: 30–50%.")
            rightsized_clusters = [c for c in sorted(df["cluster"].unique()) if CLUSTER_META[c]["risk"] == "med"]
            target = st.selectbox(
                "Pilih klaster yang akan di-right-size:",
                rightsized_clusters,
                format_func=lambda c: f"Klaster {c} — {CLUSTER_META[c]['label']}"
            )
            size_reduction = st.slider("Estimasi pengurangan biaya per server setelah resize:", 0.1, 0.6, 0.35,
                                       format="%.0f%%",
                                       help="Beralih dari instance 4vCPU ke 2vCPU biasanya menghemat ~35–40%.")
            n = len(df[df["cluster"] == target])
            saving_pct = size_reduction
            hours_saved = saving_pct * 24 * 365
            explanation = (
                f"Right-sizing **{n}** server di Klaster {target} "
                f"({CLUSTER_META[target]['label']}) dengan mengecilkan tier instance menghemat "
                f"~{saving_pct:.0%} dari biaya saat ini."
            )

    with sim_right:
        annual  = n * hourly_cost * hours_saved
        monthly = annual / 12

        st.markdown(
            f'<div class="savings-card">'
            f'<div class="savings-label">Estimasi penghematan tahunan</div>'
            f'<div class="savings-value">${annual:,.0f}</div>'
            f'<p style="color:#15803d; font-size:0.85rem; margin-top:6px;">'
            f'≈ ${monthly:,.0f} / bulan dari {n} server'
            f'</p></div>', unsafe_allow_html=True
        )

        st.markdown("")
        st.markdown(
            f'<div class="insight-box"><strong>Cara perhitungan ini:</strong><br>{explanation}<br><br>'
            f'<strong>Rumus:</strong> {n} server × ${hourly_cost:.2f}/jam × '
            f'{hours_saved:,.0f} jam dihemat = <strong>${annual:,.0f}/tahun</strong>'
            f'</div>', unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown('<div class="section-label">Ringkasan biaya seluruh armada (pada tarif per jam saat ini)</div>',
                unsafe_allow_html=True)

    rows = []
    for cid, meta in CLUSTER_META.items():
        cnt = len(df[df["cluster"] == cid])
        if cnt == 0:
            continue
        full_annual = cnt * hourly_cost * 24 * 365
        rows.append({
            "Klaster": f"{meta['icon']} {cid}: {meta['label']}",
            "Server": cnt,
            "Estimasi Biaya Tahunan": f"${full_annual:,.0f}",
            "Rekomendasi Tindakan": meta["action"],
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)