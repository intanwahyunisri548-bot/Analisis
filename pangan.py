import json
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from scipy.stats import skew, kurtosis, ttest_ind
from datetime import date, timedelta
from urllib.parse import quote
import argparse

# =====================================================
# KONFIGURASI KOMODITAS (bisa ditambah/ubah di sini)
# =====================================================
COMMODITY_CONFIG = {
    "gula": {
        "keyword": "GULA",                 # filter nama komoditas di BI
        "col_name": "Gula_Rata2",          # nama kolom di DataFrame
        "label": "Gula",                   # label di grafik / teks
        # dari link yang kamu kirim: comcat_id=cat_10%2Ccom_20%2Ccom_21
        "comcat_list": ["cat_10", "com_20", "com_21"],
    },
    "cabai": {
        "keyword": "RAWIT",
        "col_name": "Cabai_rawit_Rata2",
        "label": "Cabai rawit",
        "comcat_list": ["cat_10", "com_20", "com_21"],  # contoh
    },
    "beras": {
        "keyword": "BERAS",
        "col_name": "Beras_Rata2",
        "label": "Beras",
        "comcat_list": ["cat_8", "com_15", "com_16"],   # contoh
    },
}


# ==========================================
# FUNGSI: FETCH DATA HARGA (DINAMIS BI)
# ==========================================
def fetch_harga_bi(
    commodity: str,
    price_type_id=1,
    province_id=27,
    regency_id="72",   # sesuai link gula-mu
    market_id="",
    tipe_laporan=5,
    start_date="2020-11-01",
    end_date="2025-12-01",
):
    """
    Mengambil data harga dari BI secara dinamis untuk komoditas tertentu
    (gula / cabai / beras) berdasarkan keyword dan comcat_list di COMMODITY_CONFIG.
    """
    if commodity not in COMMODITY_CONFIG:
        raise ValueError(f"Komoditas '{commodity}' belum dikonfigurasi.")

    cfg = COMMODITY_CONFIG[commodity]
    comcat_list = cfg["comcat_list"]
    keyword = cfg["keyword"]
    col_name = cfg["col_name"]

    comcat_raw = ",".join(comcat_list)
    comcat_encoded = quote(comcat_raw)

    url = (
        "https://www.bi.go.id/hargapangan/WebSite/TabelHarga/GetGridDataDaerah"
        f"?price_type_id={price_type_id}"
        f"&comcat_id={comcat_encoded}"
        f"&province_id={province_id}"
        f"&regency_id={regency_id}"
        f"&market_id={market_id}"
        f"&tipe_laporan={tipe_laporan}"
        f"&start_date={start_date}"
        f"&end_date={end_date}"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*"
    }

    print(f"[BI] Mengunduh data harga {commodity} dari: {url}")
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data_bi = r.json()

    raw_bi = data_bi.get('data', [])
    if not raw_bi:
        raise ValueError("Data harga kosong atau format JSON BI berubah.")

    df_bi = pd.DataFrame(raw_bi)

    # Ubah ke format long
    date_cols = [c for c in df_bi.columns if '/' in c]
    df_bi_long = df_bi.melt(
        id_vars=['name'],
        value_vars=date_cols,
        var_name='Tanggal',
        value_name='Harga'
    )

    # Bersihkan harga & tanggal
    df_bi_long['Harga'] = pd.to_numeric(
        df_bi_long['Harga'].astype(str)
        .str.replace('.', '', regex=False)
        .str.replace(',', '', regex=False),
        errors='coerce'
    )
    df_bi_long['Tanggal'] = pd.to_datetime(df_bi_long['Tanggal'], format='%d/%m/%Y')

    # Filter hanya komoditas yang namanya mengandung keyword (GULA / RAWIT / BERAS)
    df_komoditas = df_bi_long[df_bi_long['name'].str.contains(keyword, case=False, na=False)]

    if df_komoditas.empty:
        raise ValueError(f"Tidak ditemukan komoditas dengan nama mengandung '{keyword}' di data BI.")

    # Agregasi rata-rata per hari
    df_daily = (
        df_komoditas
        .groupby('Tanggal')['Harga']
        .mean()
        .reset_index()
        .rename(columns={'Harga': col_name})
    )

    print(f"[BI] Data harga {commodity} berhasil diambil: {len(df_daily)} hari.")
    return df_daily


# ==========================================
# FUNGSI: FETCH DATA CUACA MSN (DINAMIS)
# ==========================================
def fetch_weather_msn(
    lat=-4.04,
    lon=122.49,
    start_date="2025-02-01",
    end_date="2026-01-31",
    days=30,
    api_key="j5i4gDqHL6nGYwx5wi5kRhXjtf2c5qgFX9fzfk0TOo"
):
    """
    Mengambil data cuaca MSN dengan lat/lon & tanggal dinamis.
    start_date & end_date format: YYYYMMDD.
    """

    url = (
        "https://assets.msn.com/service/weather/weathertrends"
        f"?apiKey={api_key}"
        "&cm=id-id"
        "&locale=id-id"
        f"&lon={lon}"
        f"&lat={lat}"
        "&units=C"
        "&user=m-2626E4DD471965A922A8F1C746186496"
        "&ocid=msftweather"
        "&includeWeatherTrends=true"
        "&includeCalendar=false"
        "&fdhead=PRG-1SW-WXNCVF,PRG-1SW-WXTRLOG,PRG-1SW-WXTRLOGP-C"
        "&weatherTrendsScenarios=PrecipitationTrend"
        f"&days={days}"
        "&insights=1"
        f"&startDate={start_date}"
        f"&endDate={end_date}"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.msn.com/",
        "Accept": "*/*"
    }

    print(f"[MSN] Mengunduh data cuaca dari: {url}")
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data_msn = r.json()

    try:
        trends = data_msn['value'][0]['responses'][0]['trendChart']
    except (KeyError, IndexError):
        trends = data_msn.get('trendChart', {})

    if not trends:
        raise ValueError("Data tren cuaca tidak ditemukan dalam respon MSN.")

    weather_data = []
    for date_str, values in trends.items():
        weather_data.append({
            'Tanggal': pd.to_datetime(date_str),
            'Curah_Hujan_mm': values['trendDays'].get('11', 0.0),
            'Peluang_Hujan_Persen': values['trendDays'].get('72', 0.0)
        })

    df_cuaca = pd.DataFrame(weather_data)
    print(f"[MSN] Data cuaca berhasil diambil: {len(df_cuaca)} hari.")
    return df_cuaca


# ==========================================
# FUNGSI: CLEANING & MERGE
# ==========================================
def clean_and_merge(df_harga, df_cuaca, col_name: str):
    print("[MERGE] Menggabungkan data harga & cuaca...")
    df_final = pd.merge(df_harga, df_cuaca, on='Tanggal', how='inner').sort_values('Tanggal')

    if df_final.empty:
        raise ValueError("Tidak ada tanggal yang cocok antara data harga dan cuaca.")

    print(f"[MERGE] Irisan tanggal: {len(df_final)} baris.")

    # Cleaning
    initial_count = len(df_final)
    df_clean = df_final.dropna(subset=[col_name, 'Curah_Hujan_mm'])
    nan_dropped = initial_count - len(df_clean)

    # buang harga tidak wajar (<= 1000)
    df_clean = df_clean[df_clean[col_name] > 1000]
    price_invalid = (initial_count - nan_dropped) - len(df_clean)

    df_clean = df_clean[df_clean['Curah_Hujan_mm'] >= 0]

    print("\n=== PEMBERSIHAN DATA ===")
    print(f"   > Data Awal Merge: {initial_count} baris")
    print(f"   > Dibuang (NaN/Kosong): {nan_dropped} baris")
    print(f"   > Dibuang (Harga tdk valid): {price_invalid} baris")
    print(f"   > Data Bersih Siap Uji: {len(df_clean)} baris")

    return df_clean


# ==========================================
# FUNGSI: HITUNG STATISTIK & ANALISIS
# ==========================================
def calculate_detailed_stats(series):
    data = series.dropna()
    n = len(data)
    if n == 0:
        return pd.Series()

    mean_val = data.mean()
    std_val = data.std()

    return pd.Series({
        'count': n,
        'mean': mean_val,
        'median': data.median(),
        'mode': data.mode().iloc[0] if not data.mode().empty else np.nan,
        'std': std_val,
        'var': data.var(),
        'min': data.min(),
        'max': data.max(),
        'range': data.max() - data.min(),
        'q1': data.quantile(0.25),
        'q3': data.quantile(0.75),
        'iqr': data.quantile(0.75) - data.quantile(0.25),
        'cv': (std_val / mean_val) * 100 if mean_val != 0 else np.nan,
        'mad': np.mean(np.abs(data - mean_val)),
        'skew': skew(data, bias=False),
        'kurt': kurtosis(data, bias=False)
    })


def analyze_and_plot(
    df_final,
    col_name: str,
    commodity_label: str,
    output_path="analisis_komoditas_vs_cuaca.png",
    lokasi_label="Kendari",
):
    print("\n=== SUMMARY STATISTIK LENGKAP ===")
    stats_summary = df_final[[col_name, 'Curah_Hujan_mm']].apply(calculate_detailed_stats).round(2)
    print(stats_summary)

    # Info hari tanpa hujan
    zero_rain_count = (df_final['Curah_Hujan_mm'] == 0).sum()
    total_data = len(df_final)
    if total_data > 0:
        print(f"[INFO] Hari Tanpa Hujan (0 mm): {zero_rain_count} dari {total_data} hari ({zero_rain_count/total_data:.1%})")

    # Uji T: bandingkan harga pada hari hujan vs tidak hujan
    harga_std = df_final[col_name].std()
    t_stat = None
    p_val_t = None

    print("\n=== UJI T ===")
    if harga_std == 0 or pd.isna(harga_std):
        print(f"Peringatan: Harga {commodity_label} konstan, T-test tidak bisa dilakukan.")
    else:
        group_no_rain = df_final[df_final['Curah_Hujan_mm'] == 0][col_name]
        group_rain = df_final[df_final['Curah_Hujan_mm'] > 0][col_name]

        if len(group_no_rain) > 1 and len(group_rain) > 1:
            if group_no_rain.std() == 0 and group_rain.std() == 0:
                print("   => Tidak dapat dilakukan: variansi kedua grup = 0.")
            else:
                t_stat, p_val_t = ttest_ind(group_no_rain, group_rain, equal_var=False)
                print(f"   - T-Statistic: {t_stat:.4f}")
                print(f"   - P-Value   : {p_val_t}")
                if pd.isna(p_val_t):
                    print("   => Hasil 'nan' (kemungkinan data identik).")
                elif p_val_t < 0.05:
                    print("   => SIGNIFIKAN: Harga berbeda nyata antara hari hujan vs kering.")
                else:
                    print("   => TIDAK SIGNIFIKAN: Hujan tidak berpengaruh signifikan.")
        else:
            print("   => Tidak dapat dilakukan: salah satu grup terlalu sedikit/kosong.")

    # Korelasi
    corr_matrix = df_final[[col_name, 'Curah_Hujan_mm', 'Peluang_Hujan_Persen']].corr()
    korelasi_harga_hujan = corr_matrix.loc[col_name, 'Curah_Hujan_mm']

    print("\n=== KESIMPULAN ===")
    print(f"1. Korelasi Harga {commodity_label} vs Curah Hujan (Pearson: {korelasi_harga_hujan:.4f})")
    if pd.isna(korelasi_harga_hujan):
        print("   - Hubungan tidak terdefinisi.")
    elif abs(korelasi_harga_hujan) < 0.1:
        print("   - Sangat lemah / hampir tidak ada hubungan.")
    elif abs(korelasi_harga_hujan) < 0.3:
        print("   - Hubungan lemah.")
    elif abs(korelasi_harga_hujan) < 0.5:
        print("   - Hubungan sedang.")
    else:
        print("   - Hubungan kuat.")

    cv_harga = stats_summary.loc['cv', col_name]
    print(f"2. Coefficient of Variation (CV) Harga {commodity_label}: {cv_harga}%")
    if pd.isna(cv_harga) or cv_harga == 0:
        print("   - Harga sangat konstan.")
    elif cv_harga < 5:
        print("   - Harga sangat stabil.")
    elif cv_harga < 15:
        print("   - Harga cukup stabil.")
    else:
        print("   - Harga fluktuatif.")

    # Plot
    print("\n=== VISUALISASI ===")
    sns.set_style("whitegrid")
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Harga komoditas: line (merah)
    ax1.set_xlabel('Tanggal', fontsize=12)
    ax1.set_ylabel(f'Harga Rata-rata {commodity_label} (Rp)', color='tab:red', fontsize=12)
    ax1.plot(df_final['Tanggal'], df_final[col_name],
             color='tab:red', linewidth=2, marker='o', label=f'Harga {commodity_label}')
    ax1.tick_params(axis='y', labelcolor='tab:red')

    # Curah hujan: line (biru) di sumbu kanan
    ax2 = ax1.twinx()
    ax2.set_ylabel('Curah Hujan (mm)', color='tab:blue', fontsize=12)
    ax2.plot(df_final['Tanggal'], df_final['Curah_Hujan_mm'],
             color='tab:blue', linewidth=2, marker='s', label='Curah Hujan (mm)')
    ax2.tick_params(axis='y', labelcolor='tab:blue')

    # Biar hujan kelihatan jelas, skala sedikit dinaikkan
    max_rain = df_final['Curah_Hujan_mm'].max()
    ax2.set_ylim(0, max(1, max_rain * 1.5))

    t_val_str = f"{t_stat:.3f}" if t_stat is not None else "N/A"
    plt.title(
        f'Harga {commodity_label} vs Curah Hujan ({lokasi_label})\n'
        f'Korelasi: {korelasi_harga_hujan:.2f} | T-Stat: {t_val_str}',
        fontsize=14
    )
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    fig.tight_layout()
    plt.savefig(output_path)
    plt.show()
    print(f"Grafik disimpan sebagai '{output_path}'")


# ==========================================
# MAIN: PARAMETER DINAMIS
# ==========================================
def main():
    parser = argparse.ArgumentParser(
        description="Analisis Dinamis Komoditas vs Cuaca"
    )
    parser.add_argument("--komoditas", type=str, default="gula",
                        choices=list(COMMODITY_CONFIG.keys()),
                        help="Pilih komoditas: gula / cabai / beras (default: gula)")
    parser.add_argument("--province_id", type=int, default=27, help="ID Provinsi BI (default: 27)")
    parser.add_argument("--regency_id", type=str, default="72", help="ID Kabupaten (default: 72)")
    parser.add_argument("--lat", type=float, default=-4.04, help="Latitude lokasi cuaca")
    parser.add_argument("--lon", type=float, default=122.49, help="Longitude lokasi cuaca")
    parser.add_argument("--ndays", type=int, default=365, help="Jumlah hari ke belakang")
    parser.add_argument("--lokasi_label", type=str, default="Kendari", help="Label lokasi di judul grafik")
    parser.add_argument("--output", type=str, default="analisis_komoditas_vs_cuaca.png",
                        help="Nama file output grafik")

    # Di Jupyter pakai [] supaya tidak bentrok argumen kernel
    args = parser.parse_args([])

    today = date.today()
    start_dt = today - timedelta(days=args.ndays)
    end_dt = today

    start_bi = start_dt.strftime("%Y-%m-%d")
    end_bi = end_dt.strftime("%Y-%m-%d")
    start_msn = start_dt.strftime("%Y%m%d")
    end_msn = end_dt.strftime("%Y%m%d")

    print("--- MEMULAI PENGAMBILAN & ANALISIS DATA DINAMIS ---")
    print(f"Komoditas   : {args.komoditas}")
    print(f"Periode BI  : {start_bi} s.d. {end_bi}")
    print(f"Periode MSN : {start_msn} s.d. {end_msn}")

    cfg = COMMODITY_CONFIG[args.komoditas]
    col_name = cfg["col_name"]
    commodity_label = cfg["label"]

    try:
        df_harga = fetch_harga_bi(
            commodity=args.komoditas,
            province_id=args.province_id,
            regency_id=args.regency_id,
            start_date=start_bi,
            end_date=end_bi,
        )
        df_cuaca = fetch_weather_msn(
            lat=args.lat,
            lon=args.lon,
            start_date=start_msn,
            end_date=end_msn,
            days=args.ndays,
        )

        df_final = clean_and_merge(df_harga, df_cuaca, col_name=col_name)
        analyze_and_plot(
            df_final,
            col_name=col_name,
            commodity_label=commodity_label,
            output_path=args.output,
            lokasi_label=args.lokasi_label,
        )

    except requests.exceptions.RequestException as e:
        print(f"\nGAGAL MENGUNDUH DATA: {e}")
    except ValueError as e:
        print(f"\nERROR DATA: {e}")
    except Exception as e:
        print(f"\nTerjadi kesalahan tak terduga: {e}")


if __name__ == "__main__":
    main()
