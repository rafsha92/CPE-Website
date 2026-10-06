# Pelan Effects & Scrolling Animation — Website CPE

Pelan ini menjadi rujukan untuk reka bentuk, pembangunan dan penyelenggaraan website CPE. Susunan seksyen mengikuti 11 imej reka bentuk yang telah dipersetujui.

**Arah visual:** navy, teal, putih hangat dan aksen amber.  
**Gaya pergerakan:** tenang, kemas dan membantu pembacaan.  
**Identiti:** CPE Patch dan Pasukan CPE.  
**Bahasa:** Bahasa Melayu sebagai lalai, dengan versi English yang setara.

## 1. Prinsip keseluruhan

- Gunakan scrolling semula jadi pelayar. Tiada scroll hijacking, section snapping atau skrin yang terkunci ketika animasi.
- Kandungan utama boleh dibaca tanpa menunggu animasi.
- Reveal dimainkan sekali apabila elemen masuk ke kawasan paparan. Scroll semula tidak mengulang animasi yang sama.
- Pergerakan biasa menggunakan jarak kecil, sekitar 12px.
- Gunakan transform dan opacity untuk reveal, hover, bar perbandingan dan parallax.
- Animasi tidak boleh menukar atau membesar-besarkan angka penjimatan.
- Navigasi dan tindakan penting mesti berfungsi melalui sentuhan, tetikus dan papan kekunci.
- Hormati pilihan sistem “Reduce Motion”.
- Foto di laman ini ialah ilustrasi, bukan bukti pemasangan atau hasil pelanggan.

## 2. Tetapan motion

| Elemen | Tempoh | Pergerakan | Easing |
|---|---:|---|---|
| Hero image | 700ms | Scale 1.02 → 1.00 | cubic-bezier(.16, 1, .3, 1) |
| Reveal teks / elemen | 350ms | Translate Y 12px → 0; opacity .55 → 1 | cubic-bezier(.16, 1, .3, 1) |
| Reveal melalui opacity | 250ms | Opacity .55 → 1 | cubic-bezier(.16, 1, .3, 1) |
| Reveal foto | 500ms | Clip-path dari kiri ke kanan | cubic-bezier(.16, 1, .3, 1) |
| Garis perbandingan | 450ms | Garis berkembang mengikut orientasi | cubic-bezier(.16, 1, .3, 1) |
| Bar contoh bil | 700ms | Scale X 0 → 1 | cubic-bezier(.16, 1, .3, 1) |
| Highlight pengiraan | 600ms | Warna latar lembut, kemudian kembali | cubic-bezier(.16, 1, .3, 1) |
| FAQ accordion | 220ms | Tinggi panel dan opacity | cubic-bezier(.16, 1, .3, 1) |
| Hover foto premis | 250ms | Scale 1.00 → 1.03 | cubic-bezier(.16, 1, .3, 1) |
| Hover butang / pautan | 150ms | Warna dan anak panah +4px | Ease |
| Header / floating contact | 200ms | Warna atau opacity | Ease |

Reveal menggunakan GSAP ScrollTrigger apabila sekitar 15% elemen memasuki viewport, dengan tetapan once. IntersectionObserver menjadi fallback jika GSAP tidak tersedia. Reveal yang telah dimainkan tidak diulang selepas perubahan saiz skrin.

## 3. Pelan mengikut seksyen

### Seksyen 01 — Hero & navigasi

**Tujuan:** Memperkenalkan CPE dan mengarahkan pelawat kepada semakan kesesuaian.

**Effects:**
- Foto hero bermula pada scale 1.02 dan kembali ke 1.00 dalam 700ms.
- Tajuk, penerangan dan butang kekal boleh dibaca sejak paparan pertama.
- Overlay navy memastikan tulisan jelas di atas foto.
- Header kekal di atas skrin.
- Selepas scroll melebihi kira-kira 30px, header mendapat latar navy solid.
- Anak panah pada butang bergerak 4px ketika hover.
- Butang utama membawa pelawat ke seksyen pertanyaan; pautan kedua ke penerangan produk.

**Mobile:**
- Gunakan crop foto yang mengekalkan suasana premis.
- Susun butang secara menegak.
- Menu dibuka melalui butang dengan keadaan expanded yang jelas.
- Escape menutup menu dan mengembalikan fokus kepada butang menu.
- Tiada parallax pada hero.

**Reduce Motion:** Tiada scale animation. Foto terus pada saiz akhir.

### Seksyen 02 — Situasi & penggunaan premis

**Tujuan:** Membantu prospek mengenali corak penggunaan peralatan.

**Effects:**
- Tiga penerangan masuk secara berurutan dari bawah sejauh 12px.
- Tempoh reveal: 350ms.
- Jarak masa antara elemen: sekitar 80ms.
- Ikon kekal statik untuk memudahkan imbasan.
- Foto ruang kedai menjadi pemisah visual yang tenang.

**Mobile:**
- Tiga penerangan disusun menegak.
- Reveal ringan digunakan mengikut urutan bacaan.
- Tiada elemen bergerak secara mendatar di luar skrin.

**Reduce Motion:** Semua penerangan dipaparkan terus.

### Seksyen 03 — Kenali CPE Patch

**Tujuan:** Menjelaskan aplikasi produk dan perkara yang perlu disemak.

**Effects:**
- Foto peralatan menggunakan reveal dari kiri ke kanan selama 500ms.
- Teks menggunakan reveal ringan.
- Tab “Aplikasi” dan “Semakan awal” menukar kandungan apabila dipilih.
- Tab aktif menggunakan warna dan garisan bawah.
- Pertukaran tab berlaku serta-merta supaya maklumat mudah dibaca.

**Interaksi:**
- Arrow Left / Right mengubah tab.
- Home / End memilih tab pertama / terakhir.
- Fokus papan kekunci jelas.

**Mobile:**
- Foto di atas, penerangan di bawah.
- Tab kekal ringkas dan mudah disentuh.

**Reduce Motion:** Foto terus dipaparkan; tab berfungsi seperti biasa.

### Seksyen 04 — Kesesuaian premis

**Tujuan:** Menunjukkan jenis premis dan faktor penilaian.

**Effects:**
- Foto premis mempunyai hover scale maksimum 1.03 selama 250ms.
- Pilihan aktif ditandakan dengan outline teal dan label yang jelas.
- Apabila kategori dipilih, nota kesesuaian dikemas kini.
- Jenis premis dalam borang pertanyaan turut dipilih.
- Checklist menggunakan reveal 350ms dengan sela sekitar 70ms.

**Mobile:**
- Susun foto secara kompak tanpa horizontal scrolling yang diperlukan.
- Pemilihan berlaku melalui tap; hover bukan syarat untuk memahami pilihan.
- Checklist ditampilkan di bawah foto.

**Reduce Motion:** Tiada scale atau stagger. Keadaan pilihan masih jelas melalui warna dan outline.

### Seksyen 05 — Pengukuran & maklumat penjimatan

**Tujuan:** Membezakan penggunaan compressor dengan jumlah bil premis.

**Effects:**
- Garis pemisah perbandingan berkembang dalam 450ms.
- Desktop menggunakan garis menegak; mobile menggunakan garis mendatar.
- Foto dan penerangan masuk secara ringan.
- Tiga langkah pengukuran menggunakan stagger sekitar 70ms.
- Setiap langkah boleh dipilih untuk membuka penerangan.
- Hanya satu penerangan langkah dibuka pada satu masa.

**Mobile:**
- Dua skop pengukuran disusun menegak.
- Foto diikuti penerangan langkah.
- Kawasan klik merangkumi satu baris langkah penuh.

**Reduce Motion:** Garis dipaparkan terus. Penerangan masih boleh dibuka dan ditutup.

### Seksyen 06 — Contoh konfigurasi kedai & bil

**Tujuan:** Membantu pelawat membaca contoh dalam brosur.

**Signature effect:**
- Dua bar bil berkembang serentak dalam 700ms.
- Bar sebelum mewakili RM4,500.00.
- Bar selepas mewakili RM4,236.75.
- Lebar akhir bar selepas ialah 94.15% daripada bar sebelum.
- Nombor dipaparkan sejak awal dan tidak menggunakan count-up.
- Persamaan menerima highlight latar lembut selama 600ms, bermula sekitar 650ms selepas reveal.

**Pengiraan yang dipaparkan:**

> RM263.25 penjimatan contoh − RM235.00 bayaran bulanan contoh = RM28.25 baki bulanan.

**Peraturan kandungan:**
- Labelkan sebagai contoh brosur.
- Baki ini tidak memasukkan bayaran awal.
- Perubahan bil keseluruhan ialah 5.85%.
- Jangan menyamakan perubahan jumlah bil dengan dakwaan pengukuran pada compressor.
- Jangan gunakan animasi untuk membayangkan penjimatan yang dijamin.

**Mobile:**
- Foto, bar dan pengiraan disusun menegak.
- Simbol tolak dan sama dengan kekal jelas.
- Angka tidak dipotong atau memerlukan sideways scrolling.

**Reduce Motion:** Bar terus pada lebar akhir; tiada highlight bergerak.

### Seksyen 07 — Pelan & pemilikan

**Tujuan:** Menjelaskan perkara yang perlu difahami sebelum menerima cadangan.

**Effects:**
- Jadual muncul melalui opacity selama 250ms.
- Hover baris menggunakan perubahan latar lembut.
- Penerangan bayaran awal, bayaran bulanan dan pemilikan menggunakan reveal ringan.
- Butang amber menjadi fokus tindakan seterusnya.

**Peraturan kandungan:**
- Jadual menunjukkan contoh konfigurasi, bukan pengesahan kelayakan.
- Jumlah bayaran dan tempoh pemilikan disahkan melalui cadangan rasmi.
- Terma yang bercanggah dalam lampiran tidak dimuktamadkan melalui reka bentuk.

**Mobile:**
- Dua kolum jadual kekal boleh dibaca.
- Penerangan tiga perkara disusun menegak.

**Reduce Motion:** Jadual dan penerangan terus kelihatan.

### Seksyen 08 — Semakan & proses seterusnya

**Tujuan:** Menjadikan proses pertanyaan mudah difahami.

**Effects:**
- Empat langkah dihubungkan oleh garis progress.
- Desktop: garis berkembang mendatar.
- Mobile: garis berkembang menegak.
- Progress mengikuti kedudukan seksyen semasa scroll.
- Marker langkah berubah keadaan mengikut progress.
- Setiap langkah juga boleh diklik untuk membaca penerangan khusus.
- Klik tidak mengunci scrolling; progress kembali mengikuti scroll seterusnya.

**Mobile:**
- Langkah disusun sebagai timeline menegak.
- Nombor, tajuk dan penerangan sejajar.
- Tiada pinned section atau scroll-lock.

**Reduce Motion:** Garis progress bergerak disembunyikan. Semua langkah dan interaksi klik kekal tersedia.

### Seksyen 09 — Pasukan CPE & pertanyaan rujukan

**Tujuan:** Membina keyakinan melalui akses kepada penjelasan dan bahan sokongan.

**Effects:**
- Foto latar mempunyai parallax kecil, maksimum sekitar ±20px.
- Teks kekal statik supaya mudah dibaca.
- Overlay navy membezakan kandungan daripada foto.
- Butang rujukan membuka mesej WhatsApp yang berkaitan.

**Peraturan kandungan:**
- Gunakan label Pasukan CPE.
- Foto mesti ditandakan sebagai ilustrasi.
- Rujukan diminta melalui pasukan; jangan cipta testimoni, pelanggan atau logo.

**Mobile:**
- Tiada parallax pada lebar 600px dan ke bawah.
- Teks disusun dalam satu kolum.

**Reduce Motion:** Tiada parallax.

### Seksyen 10 — FAQ

**Tujuan:** Menjawab kebimbangan sebelum prospek menghubungi pasukan.

**Effects:**
- FAQ menggunakan reveal melalui opacity.
- Panel jawapan dibuka / ditutup dalam 220ms.
- Animasi menggunakan tinggi panel dan opacity secara setempat.
- Simbol tambah / tolak mengikut keadaan panel.
- Hanya satu jawapan dibuka pada satu masa.
- Klik pantas tidak boleh menyebabkan panel tersangkut.

**Aksesibiliti:**
- Soalan ialah butang sebenar.
- Keadaan expanded dan hubungan dengan jawapan ditentukan melalui ARIA.
- Enter / Space membuka atau menutup jawapan.
- Fokus kelihatan.

**Mobile:** Seluruh baris soalan boleh disentuh; jawapan mengalir di bawah soalan.

**Reduce Motion:** Jawapan dibuka dan ditutup serta-merta.

### Seksyen 11 — Pertanyaan, WhatsApp & footer

**Tujuan:** Membolehkan pelawat menyediakan pertanyaan dengan selesa.

**Effects:**
- Borang menggunakan reveal 12px selama 350ms.
- Medan input menunjukkan keadaan fokus dan ralat yang jelas.
- Ralat dipaparkan di bawah medan berkaitan.
- Fokus bergerak ke medan tidak sah pertama.
- Floating WhatsApp disembunyikan apabila seksyen hubungan masuk ke kawasan paparan.
- Footer kekal statik.

**Aliran sebenar borang:**
1. Pelawat mengisi nama, telefon, lokasi dan jenis premis.
2. Nota peralatan adalah pilihan.
3. Borang menyemak medan wajib dan nombor telefon.
4. Website menyediakan mesej WhatsApp.
5. Pelawat menyemak dan menghantar mesej dalam WhatsApp.
6. Jika tetingkap baharu disekat, pautan untuk membuka mesej dipaparkan.

**Peraturan:**
- Website tidak menghantar mesej secara automatik.
- Jangan paparkan “pertanyaan telah diterima” kerana tiada pangkalan data submission.
- Input borang tidak disimpan oleh website.
- Kekalkan pautan telefon, e-mel dan WhatsApp sebagai saluran langsung.

**Mobile:** Maklumat hubungan di atas; borang satu kolum di bawah.

**Reduce Motion:** Borang terus dipaparkan; feedback dan validasi kekal berfungsi.

## 4. Peraturan mobile & responsive

| Saiz | Susunan utama |
|---|---|
| Desktop, melebihi 900px | Navigasi penuh, split layouts dan timeline mendatar |
| Tablet, 601–900px | Menu mobile; beberapa susunan dua kolum dikekalkan |
| Mobile, 600px dan ke bawah | Satu kolum, butang utama lebih mudah disentuh, timeline menegak, tiada parallax |
| Skrin kecil, 320px | Kandungan mengalir tanpa horizontal overflow |

Anchor mengambil kira ketinggian header tetap. Kekalkan margin di atas tajuk selepas navigasi ke sesuatu seksyen.

## 5. Aksesibiliti & prestasi

- Semua kandungan asas kekal tersedia jika JavaScript tidak berjalan.
- Dalam fallback tanpa JavaScript, maklumat tab, langkah pengukuran dan FAQ masih boleh dibaca.
- Borang penyediaan mesej dinyahaktifkan tanpa JavaScript; gunakan pautan hubungan langsung.
- Jangan bergantung pada warna sahaja untuk pilihan aktif atau ralat.
- Gunakan labels, alt text yang sesuai, aria-expanded dan fokus yang kelihatan.
- Sasarkan kontras minimum 4.5:1 untuk teks biasa dan 3:1 untuk sempadan kawalan penting.
- Gunakan foto WebP, dimensi imej yang tetap dan lazy loading di bawah hero.
- Jangan tambah video autoplay atau pustaka animasi besar untuk effects yang boleh dibuat dengan CSS.
- Kemaskan observers dan animasi apabila halaman ditutup.
- Uji perubahan pilihan Reduce Motion semasa website sedang dibuka.

## 6. Rujukan pelaksanaan

Pelan ini diterapkan dalam website semasa menggunakan:

- **dist/assets/site.css** — tokens visual, responsive layout, keyframes, hover dan reduced-motion rules.
- **dist/assets/site.js** — GSAP ScrollTrigger, header, process progress, parallax, menu, tabs, FAQ dan validasi pertanyaan.
- **dist/assets/vendor/** — GSAP 3.15.0 dan ScrollTrigger, disajikan secara lokal dengan notis lesen asal.
- **tools/build-site.py** — struktur seksyen, kandungan dwibahasa, semantic HTML dan metadata.

Website menggunakan GSAP 3.15.0 untuk motion yang ditetapkan dalam pelan ini, tanpa menukar struktur website kepada React. GSAP matchMedia memulihkan gaya asal apabila saiz skrin atau pilihan Reduce Motion berubah. ScrollTrigger mengendalikan progress timeline dan parallax; reveal, bar bil dan FAQ menggunakan GSAP timelines atau tweens. CSS dan IntersectionObserver menyediakan fallback jika pustaka tidak tersedia. Tiada pinning, scroll-lock, kad bertindih atau marquee kerana pelan ini menetapkan scrolling semula jadi.

## 7. Senarai semakan sebelum penerbitan

- [x] 11 seksyen mengikut urutan reka bentuk.
- [x] Desktop, tablet, phone dan lebar 320px diperiksa.
- [x] Tiada horizontal overflow pada halaman yang dijana.
- [x] Semua foto dimuatkan dan ditandakan sebagai ilustrasi.
- [x] Menu mobile dan Escape focus return diuji.
- [x] Navigasi tab melalui papan kekunci diuji.
- [x] Pemilihan premis mengemas kini borang.
- [x] Penerangan pengukuran dan proses boleh dibuka.
- [x] FAQ buka, tutup dan klik pantas diuji.
- [x] Validasi medan kosong dan nombor telefon diuji.
- [x] Mesej WhatsApp dan fallback pautan diuji tanpa menghantar mesej.
- [x] Versi BM / English serta pautan halaman setara diuji.
- [x] Reduce Motion dan fallback tanpa JavaScript diuji.
- [x] Kontras butang utama dan sempadan input diperiksa.
- [x] GSAP dan ScrollTrigger lokal dimuatkan; fallback diuji dengan fail pustaka disekat.
- [x] Kedua-dua bar bil bergerak serentak dan nisbah akhirnya kekal 94.15%.
- [x] Timeline mendatar / menegak, had parallax 20px dan reveal sekali sahaja diuji.
- [x] Perubahan Reduce Motion semasa sesi memulihkan kandungan tanpa trigger berganda.
- [x] Tajuk hero BM / English kekal dalam maksimum tiga baris pada 320px, 390px, 820px dan 1440px.
- [x] Pautan dalaman, metadata, sitemap dan aset diperiksa.

Semakan ini ialah bukti ujian untuk versi semasa, bukan pengesahan menyeluruh WCAG atau bukti prestasi pengguna sebenar.
