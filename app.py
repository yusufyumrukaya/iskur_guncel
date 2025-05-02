from flask import Flask, request, send_file, render_template
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

# A4 boyutları (piksel cinsinden)
a4_width_mm = 210
a4_height_mm = 297
dpi = 300
a4_width_pixels = int(a4_width_mm / 25.4 * dpi)
a4_height_pixels = int(a4_height_mm / 25.4 * dpi)

# Türkçe büyük harf dönüşümü için fonksiyon
def turkish_upper(text):
    tr_map = {
        'i': 'İ',
        'ı': 'I',
        'ğ': 'Ğ',
        'ü': 'Ü',
        'ş': 'Ş',
        'ö': 'Ö',
        'ç': 'Ç',
    }
    result = ''
    for char in text:
        result += tr_map.get(char, char.upper())
    return result

# Uzun metni ikiye bölmek için yardımcı fonksiyon
def split_long_text(text, max_length=30):
    if len(text) <= max_length:
        return [text]
    words = text.split()
    if len(words) == 1:
        mid = len(text) // 2
        return [text[:mid].strip(), text[mid:].strip()]
    first_half = ''
    second_half = ''
    current_length = 0
    for word in words:
        if current_length + len(word) < max_length and not second_half:
            first_half += word + ' '
            current_length += len(word) + 1
        else:
            second_half += word + ' '
    return [first_half.strip(), second_half.strip()]


def create_petition(ad_soyad, ogrenci_no, cep_telefonu, eposta, egitim_yili, yariyil, dersler, bolum):
    a4_image = Image.new('RGB', (a4_width_pixels, a4_height_pixels), 'white')
    draw = ImageDraw.Draw(a4_image)
    font_path = 'arialuni.ttf'
    font_bold_path = 'arialbd.ttf'
    font_size_baslik = 47
    font_size = 45
    font_baslik = ImageFont.truetype(font_path, font_size_baslik)
    font = ImageFont.truetype(font_path, font_size)
    font_bold = ImageFont.truetype(font_bold_path, font_size)
    text_color = (0, 0, 0)
    y_offset = 60

    def draw_centered_text(text, y, font, fill):
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x = (a4_width_pixels - text_width) // 2
        draw.text((x, y), text, font=font, fill=fill)

    draw_centered_text(turkish_upper('YILDIZ TEKNİK ÜNİVERSİTESİ'), 200, font_baslik, text_color)
    draw_centered_text(turkish_upper('FEN-EDEBİYAT FAKÜLTESİ'), 200 + y_offset, font_baslik, text_color)
    draw_centered_text(turkish_upper(f'{bolum} BÖLÜM BAŞKANLIĞI\'NA'), 200 + 2 * y_offset, font_baslik, text_color)
    draw_centered_text(turkish_upper('ÇAKIŞAN DERS EKLEME DİLEKÇESİ'), 200 + 3 * y_offset, font_baslik, text_color)

    # Öğrenci bilgileri tablosu
    table_x = 300
    table_y = 600
    cell_width = 1800
    cell_height = 75
    row_labels = ['Adı Soyadı', 'Öğrenci Numarası', 'Cep Telefonu', 'e-posta']
    values = [ad_soyad, ogrenci_no, cep_telefonu, eposta]
    line_x = table_x + 390
    line_start_y = table_y
    line_end_y = table_y + len(row_labels) * cell_height
    for i, (label, value) in enumerate(zip(row_labels, values)):
        y = table_y + i * cell_height
        draw.rectangle([(table_x, y), (table_x + cell_width, y + cell_height)], outline='black')
        draw.text((table_x + 10, y + 15), label, font=font, fill='black')
        draw.text((table_x + 410, y + 15), ':', font=font, fill='black')
        draw.text((table_x + 450, y + 15), value, font=font, fill='black')
    draw.line([(line_x, line_start_y), (line_x, line_end_y)], fill='black', width=1)

    # Dilekçe metni
    metin_x = 300
    metin_y = table_y + len(row_labels) * cell_height + 200
    metin_font = ImageFont.truetype(font_path, 45)
    metin = (
        f"{egitim_yili} Eğitim-Öğretim yılı {yariyil} Yarıyılında daha önce alıp, F0 dışında bir not ile başarısız"
        f"\nolduğum  ders  ile  ilk  defa  alacağım  ders  çakışmaktadır.  Aşağıda  belirtilen  dersin öğrenci   "
        f"\notomasyon sistemine işlenmesi için gereğini arz ederim."
    )
    draw.text((metin_x, metin_y), metin, font=metin_font, fill='black')
    draw.text((metin_x, metin_y + 370), 'Ek 1: Öğrenci transkripti', font=metin_font, fill='black')
    draw.text((metin_x, metin_y + 450), 'Ek 2: OBS ders programı', font=metin_font, fill='black')

    # Dersler tablosu
    ders_table_x = 300
    ders_table_y = metin_y + 800
    ders_cell_height = 120  # İki satırlık metin için artırıldı
    kodu_width = 250
    adi_width = 650
    grubu_width = 200
    x_positions = [
        ders_table_x,
        ders_table_x + kodu_width,
        ders_table_x + kodu_width + adi_width,
        ders_table_x + kodu_width * 2 + adi_width,
        ders_table_x + kodu_width * 2 + adi_width * 2
    ]
    widths = [kodu_width, adi_width, kodu_width, adi_width, grubu_width]
    ders_row_labels = ['Kodu', 'Adı', 'Kodu', 'Adı', 'Grubu']

    # Başlık blokları
    draw.rectangle([
        (ders_table_x, ders_table_y - ders_cell_height),
        (ders_table_x + kodu_width + adi_width, ders_table_y)
    ], outline='black')
    draw.text(
        (ders_table_x + 10, ders_table_y - ders_cell_height + 15),
        "                 OBS'den seçtiğim dersin",
        font=font_bold,
        fill='black'
    )
    draw.rectangle([
        (ders_table_x + kodu_width + adi_width, ders_table_y - ders_cell_height),
        (ders_table_x + kodu_width * 2 + adi_width * 2 + grubu_width, ders_table_y)
    ], outline='black')
    draw.text(
        (ders_table_x + kodu_width + adi_width + 10, ders_table_y - ders_cell_height + 15),
        "              Çakışma nedeniyle eklenecek ders",
        font=font_bold,
        fill='black'
    )

    # Header row
    for i, (x, width, label) in enumerate(zip(x_positions, widths, ders_row_labels)):
        draw.rectangle([
            (x, ders_table_y),
            (x + width, ders_table_y + ders_cell_height)
        ], outline='black')
        text_bbox = draw.textbbox((0, 0), label, font=font_bold)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = x + (width - text_width) // 2
        text_y = ders_table_y + (ders_cell_height - (text_bbox[3] - text_bbox[1])) // 2
        draw.text((text_x, text_y), label, font=font_bold, fill='black')

    # Ders satırları
    for i, ders in enumerate(dersler):
        y = ders_table_y + (i + 1) * ders_cell_height
        values = [ders['kodu1'], ders['adi1'], ders['kodu2'], ders['adi2'], ders['grubu']]
        for j, (x, width, value) in enumerate(zip(x_positions, widths, values)):
            draw.rectangle([(x, y), (x + width, y + ders_cell_height)], outline='black')
            if value:
                if j in [1, 3]:  # adi1 ve adi2 sütunları
                    text_parts = split_long_text(value)
                    if len(text_parts) == 1:
                        # Tek satırlık metin
                        bbox = draw.textbbox((0, 0), text_parts[0], font=font)
                        text_w = bbox[2] - bbox[0]
                        text_h = bbox[3] - bbox[1]
                        text_x = x + (width - text_w) // 2
                        text_y = y + (ders_cell_height - text_h) // 2
                        draw.text((text_x, text_y), text_parts[0], font=font, fill='black')
                    else:
                        # İki satırlık metin, her satırı kendi yarısında ortala
                        # Birinci satır
                        part = text_parts[0]
                        bbox = draw.textbbox((0, 0), part, font=font)
                        text_w = bbox[2] - bbox[0]
                        text_h = bbox[3] - bbox[1]
                        center_y = y + ders_cell_height * 1 / 4
                        text_x = x + (width - text_w) // 2
                        text_y = int(center_y - text_h / 2)
                        draw.text((text_x, text_y), part, font=font, fill='black')
                        # İkinci satır
                        part = text_parts[1]
                        bbox = draw.textbbox((0, 0), part, font=font)
                        text_w = bbox[2] - bbox[0]
                        text_h = bbox[3] - bbox[1]
                        center_y = y + ders_cell_height * 3 / 4
                        text_x = x + (width - text_w) // 2
                        text_y = int(center_y - text_h / 2)
                        draw.text((text_x, text_y), part, font=font, fill='black')
                else:
                    # Ders kodu ve grup için normal tek satırlık metin
                    text_bbox = draw.textbbox((0, 0), value, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_x = x + (width - text_width) // 2
                    text_y = y + (ders_cell_height - (text_bbox[3] - text_bbox[1])) // 2
                    draw.text((text_x, text_y), value, font=font, fill='black')

    output_path = 'Dilekce_a4_formati.pdf'
    a4_image.save(output_path, format='PDF', resolution=300)
    return output_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form-gonder', methods=['POST'])
def form_gonder():
    ad_soyad = request.form.get('adSoyad', '')
    ogrenci_no = request.form.get('ogrenciNo', '')
    cep_telefonu = request.form.get('cepTelefonu', '')
    eposta = request.form.get('eposta', '')
    egitim_yili = request.form.get('egitimYili', '')
    yariyil = request.form.get('yariyil', '')
    bolum = request.form.get('bolum', 'MATEMATİK')
    dersler = []
    max_dersler = 5
    for i in range(1, max_dersler + 1):
        kodu1 = request.form.get(f'dersler[{i}][kodu1]', '')
        adi1 = request.form.get(f'dersler[{i}][adi1]', '')
        kodu2 = request.form.get(f'dersler[{i}][kodu2]', '')
        adi2 = request.form.get(f'dersler[{i}][adi2]', '')
        grubu = request.form.get(f'dersler[{i}][grubu]', '')
        if any([kodu1, adi1, kodu2, adi2, grubu]):
            dersler.append({"kodu1": kodu1, "adi1": adi1, "kodu2": kodu2, "adi2": adi2, "grubu": grubu})
    output_path = create_petition(ad_soyad, ogrenci_no, cep_telefonu, eposta, egitim_yili, yariyil, dersler, bolum)
    return send_file(output_path, as_attachment=True, download_name=ad_soyad + ".pdf")

if __name__ == '__main__':
    app.run(debug=True)
