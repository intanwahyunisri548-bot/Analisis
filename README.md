# Analisis Dinamis Komoditas vs Cuaca

### Deskripsi

Proyek ini bertujuan untuk menganalisis hubungan antara harga komoditas (seperti gula, cabai, beras) dan faktor cuaca, khususnya curah hujan. Dengan menggunakan data dari **Bank Indonesia (BI)** untuk harga komoditas dan **MSN Weather API** untuk data cuaca, program ini menggabungkan kedua set data untuk menghitung statistik terkait harga komoditas dan dampaknya terhadap curah hujan. Hasil analisis ini ditampilkan dalam grafik yang memperlihatkan korelasi antara harga dan curah hujan, serta analisis statistik lainnya seperti uji T untuk perbedaan harga pada hari hujan dan tidak hujan.

### Fitur

- **Pengambilan Data Harga Komoditas**: Mengambil data harga komoditas dari API BI berdasarkan provinsi dan kabupaten yang ditentukan.
- **Pengambilan Data Cuaca**: Mengambil data curah hujan dan tren cuaca dari MSN Weather API berdasarkan koordinat geografis.
- **Pembersihan dan Penggabungan Data**: Data harga dan cuaca digabungkan dan dibersihkan untuk analisis lebih lanjut.
- **Analisis Statistik**: Menghitung statistik deskriptif, uji T, dan korelasi antara harga komoditas dan curah hujan.
- **Visualisasi**: Membuat grafik yang menampilkan harga komoditas dan curah hujan serta analisis korelasi dan T-statistik.

### Cara Penggunaan

1. **Instalasi Dependensi**

   Pastikan Anda telah menginstal Python 3.x dan pip. Kemudian, instal semua dependensi yang diperlukan dengan menjalankan perintah berikut:

   ```bash
   pip install -r requirements.txt


Menjalankan Program

Anda dapat menjalankan program ini dengan menggunakan perintah berikut:

python main.py --komoditas <komoditas> --province_id <provinsi_id> --regency_id <kabupaten_id> --lat <latitude> --lon <longitude> --ndays <jumlah_hari> --lokasi_label <label_lokasi> --output <output_file>

Parameter:

--komoditas: Pilih komoditas (gula, cabai, beras).

--province_id: ID Provinsi (default: 27).

--regency_id: ID Kabupaten (default: 72).

--lat: Latitude untuk data cuaca (default: -4.04).

--lon: Longitude untuk data cuaca (default: 122.49).

--ndays: Jumlah hari yang ingin dianalisis (default: 365).

--lokasi_label: Label lokasi yang akan ditampilkan di grafik.

--output: Nama file output untuk grafik.

Contoh Penggunaan :
python main.py --komoditas gula --province_id 27 --regency_id 72 --lat -4.04 --lon 122.49 --ndays 365 --lokasi_label Kendari --output analisis_gula_vs_cuaca.png

Hasil Output

Program ini akan menghasilkan grafik yang menunjukkan hubungan antara harga komoditas dan curah hujan, serta statistik lainnya seperti korelasi dan uji T.<img width="1200" height="600" alt="analisis_komoditas_vs_cuaca" src="https://github.com/user-attachments/assets/b03a304c-c746-4b94-aee0-beed5f2df069" />

Struktur Proyek

main.py: File utama yang menjalankan seluruh alur pengambilan dan analisis data.

requirements.txt: Daftar dependensi yang dibutuhkan untuk menjalankan proyek ini.

analisis_komoditas_vs_cuaca.png: Contoh output grafik analisis.

Dependensi

requests: Untuk mengambil data dari API.

pandas: Untuk pengolahan data.

numpy: Untuk perhitungan statistik.

matplotlib: Untuk visualisasi grafik.

seaborn: Untuk tampilan grafik yang lebih baik.

scipy: Untuk perhitungan statistik lebih lanjut seperti uji T dan korelasi.

argparse: Untuk parsing argumen dari command line.

Kontribusi

Jika Anda ingin berkontribusi pada proyek ini, silakan fork repositori ini dan buat pull request dengan perubahan Anda. Pastikan untuk mengikuti pedoman kontribusi yang baik dan melakukan pengujian terhadap perubahan yang Anda buat.

Lisensi

Proyek ini dilisensikan di bawah MIT License
.

Let me know if you need additional changes!

