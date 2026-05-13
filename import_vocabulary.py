import os
import django
import docx
import re
from docx.document import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'englishLMS.settings')
django.setup()

from courses.models import Lesson, Vocabulary, Category

def iter_block_items(parent):
    if isinstance(parent, Document):
        parent_elm = parent.element.body
    elif hasattr(parent, '_tc'):
        parent_elm = parent._tc
    else:
        raise ValueError("something's wrong")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)

def extract_unit_number(text):
    # Match patterns like "1.1", "3", "5-6", "14-15 VOCABULARY"
    match = re.search(r'(\d+)(?:\.\d+)?(?:-(\d+))?', text)
    if match:
        return int(match.group(1))
    return None

def main():
    file_path = "Beginner vocabulary last one.docx"
    if not os.path.exists(file_path):
        print(f"❌ Fayl topilmadi: {file_path}")
        return

    doc = docx.Document(file_path)
    
    vocab_data = {} # unit_num -> list of (word, translation, example)
    current_unit = None
    
    print("🔍 Hujjat tahlil qilinmoqda...")
    
    for item in iter_block_items(doc):
        if isinstance(item, Paragraph):
            text = item.text.strip()
            if not text:
                continue
            
            unit_num = extract_unit_number(text)
            # Agar matnda raqam bo'lsa va u sarlavhaga o'xshasa (odatda qisqa bo'ladi)
            if unit_num is not None and len(text) < 50:
                current_unit = unit_num
                if current_unit not in vocab_data:
                    vocab_data[current_unit] = []
                print(f"📌 Bo'lim aniqlandi: '{text}' -> Unit {current_unit}")
        
        elif isinstance(item, Table):
            if current_unit is None:
                continue
                
            added_in_table = 0
            for row in item.rows:
                cells = [cell.text.strip() for cell in row.cells]
                # Keraksiz sarlavha qatorlarini tashlab ketish (agar bo'lsa)
                if not cells or not cells[0] or cells[0].lower() in ['word', 'vocabulary', 'english']:
                    continue
                
                word = cells[0]
                translation = ""
                example = ""
                
                if len(cells) == 2:
                    translation = cells[1]
                elif len(cells) >= 3:
                    # Tekshiruv natijasida: [Word, Example, Translation] ekanligi aniqlandi
                    example = cells[1]
                    translation = cells[2]
                
                if word and translation:
                    vocab_data[current_unit].append((word, translation, example))
                    added_in_table += 1
            
            if added_in_table > 0:
                print(f"   📊 Jadvaldan {added_in_table} ta so'z olindi (Unit {current_unit})")

    print("\n🚀 Ma'lumotlar bazasiga saqlash boshlandi...")
    
    total_added = 0
    for unit_num, words in vocab_data.items():
        if not words:
            continue
            
        # Lesson'ni qidirish
        unit_str = f"Unit {unit_num:02d}"
        lesson = Lesson.objects.filter(title__icontains=unit_str).first()
        
        if not lesson:
            unit_str_alt = f"Unit {unit_num}"
            lesson = Lesson.objects.filter(title__icontains=unit_str_alt).first()
            
        if not lesson:
            # Agar topilmasa, vaqtinchalik "Book 1" darslaridan birini tanlaymiz yoki xabar beramiz
            print(f"⚠️ Unit {unit_num} uchun dars topilmadi. O'tkazib yuborildi.")
            continue
            
        print(f"✅ {lesson.title} darsiga {len(words)} ta so'z qo'shilmoqda...")
        
        # Avvalgi vocabularylarni o'chirib tashlash (takrorlanishning oldini olish uchun)
        # Agar user xohlasa buni o'chirib qo'yish mumkin
        # Vocabulary.objects.filter(lesson=lesson).delete()
        
        start_order = Vocabulary.objects.filter(lesson=lesson).count()
        
        for i, (word, trans, example) in enumerate(words):
            Vocabulary.objects.create(
                lesson=lesson,
                word=word,
                translation=trans,
                example=example,
                order=start_order + i
            )
            total_added += 1

    print(f"\n✨ Jarayon yakunlandi! Jami {total_added} ta so'z bazaga qo'shildi.")

if __name__ == "__main__":
    main()
