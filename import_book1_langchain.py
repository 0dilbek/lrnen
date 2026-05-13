import os
import sys
import time
import json
import base64
import django
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'englishLMS.settings')
django.setup()

from django.conf import settings
from decouple import config
from courses.models import Category, Lesson
from quiz.models import Exercise

# Import LangChain modules
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def find_audio_path(track_str):
    """
    Audio 1 papkasi ichidan berilgan trek raqami (masalan, '1.2', '1.3') bo'yicha
    tegishli mp3 faylni topadi va uning statik URL manzilini qaytaradi.
    """
    if not track_str:
        return None
    
    # Formatni normallashtirish: "1.2" -> "1_2"
    norm = track_str.replace('.', '_').strip()
    parts = norm.split('_')
    if not parts or not parts[0].isdigit():
        return None
        
    unit_folder = parts[0]
    base_audio_dir = os.path.join(settings.BASE_DIR, 'static', 'audio', unit_folder)
    
    if not os.path.exists(base_audio_dir):
        return None
        
    # Asosiy nomzodni qidirish (masalan, "1_2.mp3")
    main_candidate = f"{norm}.mp3"
    if os.path.exists(os.path.join(base_audio_dir, main_candidate)):
        return f"/static/audio/{unit_folder}/{main_candidate}"
        
    # Variant yoki qism audiolarini qidirish (masalan, "1_2_1.mp3" yoki "1_2a.mp3")
    for fname in sorted(os.listdir(base_audio_dir)):
        fname_norm = fname.lower().replace('.', '_')
        if fname_norm.startswith(f"{norm}_") or fname_norm.startswith(norm):
            return f"/static/audio/{unit_folder}/{fname}"
            
    return None


def process_page(page_num, category, llm):
    filename = f"English_for_Everyone_-_Level_1_Beginner_-_Practice_Book_page-{page_num:04d}.jpg"
    img_path = os.path.join(settings.BASE_DIR, 'static', 'book', filename)
    
    if not os.path.exists(img_path):
        print(f"❌ Sahifa rasmi topilmadi: {img_path}")
        return

    print(f"\n📄 Sahifa {page_num} tahlil qilinmoqda ({filename})...")
    base64_image = encode_image(img_path)
    
    prompt_text = """
You are an expert English language curriculum extractor. Analyze the provided page image from an English Practice Book.
Extract all distinct learning exercises found on this page and format them strictly as a JSON object.

### DATABASE EXERCISE TYPES WE SUPPORT:
1. "choose_correct" (To'g'ri so'zni tanlash): For multiple choice questions or crossing out incorrect words.
   Expected content format: {"questions": [{"question": "...", "options": ["A", "B"], "correct": 0}]}
2. "fill_blank" (Bo'sh joy to'ldirish): For gap-fills, rewriting sentences, or complete the sentence tasks.
   Expected content format: {"items": [{"sentence": "...", "answer": "..."}]}
3. "matching" (Moslashtirish): For matching beginnings to endings or pairing items.
   Expected content format: {"pairs": [{"left": "...", "right": "..."}]}
4. "listening" (Listening tasks): Exercises with a headphone icon indicating an audio track to listen to.
   Expected content format: {"questions": [{"question": "...", "options": ["A", "B"], "correct": 0}]} (can be an empty list [] if there are no specific questions).

### CRITICAL FILTERING RULES:
- If an exercise relies on a visual diagram/picture to be solved (has_linked_image is true) AND it is NOT a listening exercise (is_listening is false), YOU MUST SKIP/IGNORE IT COMPLETELY. Do not include it in the output array.
- If an exercise relies on a picture/diagram AND it IS a listening exercise, DO NOT SKIP IT. Set has_linked_image to true, and we will automatically attach the page image to this listening task in the database.

### AUDIO TRACK EXTRACTION:
- For listening exercises, ALWAYS locate the track number next to the headphone icon (e.g., "1.2", "1.3", "2.4").
- Look very closely at the page; the numbers are often small and located near the instruction or a headphone symbol.
- If the instruction says "Listen to...", it MUST be a listening exercise. Try your best to find the track number.
- Provide this exact string in the "audio_track" field.

### OUTPUT FORMAT:
Return ONLY a valid JSON object enclosed in ```json ... ``` blocks adhering to this exact structure:
{
  "lesson_title": "Unit 01 - Talking about yourself (extract appropriate title from page header)",
  "exercises": [
    {
      "type": "choose_correct",
      "instruction": "Cross out the incorrect word",
      "has_linked_image": false,
      "is_listening": false,
      "audio_track": null,
      "content": {
        "questions": [
          {
            "question": "Jack ___ 27 years old.",
            "options": ["are", "is"],
            "correct": 1
          }
        ]
      }
    }
  ]
}
"""

    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt_text},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            }
        ]
    )

    max_retries = 5
    data = None
    for attempt in range(max_retries):
        try:
            response = llm.invoke([message])
            text_resp = response.content.strip()
            
            # Extract JSON block
            if "```json" in text_resp:
                json_str = text_resp.split("```json")[1].split("```")[0].strip()
            elif "```" in text_resp:
                json_str = text_resp.split("```")[1].split("```")[0].strip()
            else:
                json_str = text_resp
                
            data = json.loads(json_str)
            break  # Muvaffaqiyatli bo'lsa, tsikldan chiqish
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "exceeded" in err_str:
                wait_sec = 60
                print(f"⏳ Kvota chekloviga yetildi (429). {wait_sec} soniya kutilmoqda (Urinish {attempt + 1}/{max_retries})...")
                time.sleep(wait_sec)
            else:
                print(f"❌ LangChain/Gemini tahlilida xatolik yuz berdi: {e}")
                return

    if not data:
        print("❌ Barcha urinishlardan so'ng ham ma'lumotni olish imkoni bo'lmadi.")
        return

    lesson_title = data.get('lesson_title', f"Practice Book Page {page_num}")
    exercises = data.get('exercises', [])
    
    if not exercises:
        print("⚠️ Bu sahifada bazaga qo'shish uchun mos topshiriqlar topilmadi yoki rasmli bo'lgani uchun o'tkazib yuborildi.")
        return

    # Kategoriya ichida darsni yaratish yoki olish
    lesson, created = Lesson.objects.get_or_create(
        title=f"[Book 1] {lesson_title}",
        category=category,
        defaults={'description': f"Automated extraction from Practice Book Page {page_num}"}
    )
    if created:
        print(f"🆕 Yangi dars yaratildi: {lesson.title}")

    added_count = 0
    for ex_data in exercises:
        ex_type = ex_data.get('type')
        is_listening = ex_data.get('is_listening', False) or (ex_type == 'listening')
        has_linked_image = ex_data.get('has_linked_image', False)
        
        # Rasm bog'langan bo'lsa va listening bo'lmasa, tashlab ketamiz
        if has_linked_image and not is_listening:
            print(f"⏩ Rasm bog'langan oddiy topshiriq o'tkazib yuborildi: '{ex_data.get('instruction')}'")
            continue
            
        content = ex_data.get('content', {})
        audio_url = None
        
        # Agar listening topshirig'i bo'lsa va rasm bog'langan bo'lsa, rasmni saqlaymiz
        if is_listening:
            ex_type = 'listening'
            track = ex_data.get('audio_track')
            audio_url = find_audio_path(track)
            if audio_url:
                print(f"🎵 Audio ulandi (Trek {track}): {audio_url}")
            else:
                print(f"⚠️ Audio topilmadi (Trek {track})")
                
            # Rasmni content ichiga saqlaymiz
            image_static_url = f"/static/book/{filename}"
            if isinstance(content, list):
                content = {"items": content}
            content['image_url'] = image_static_url
            print(f"🖼️ Listening topshirig'iga rasm ulandi: {image_static_url}")

        # Topshiriqni bazaga saqlash
        Exercise.objects.create(
            lesson=lesson,
            type=ex_type,
            instruction=ex_data.get('instruction', 'Topshiriq'),
            content=content,
            has_audio=bool(audio_url),
            audio_url=audio_url,
            order=added_count + 1
        )
        added_count += 1
        print(f"✅ Topshiriq saqlandi: [{ex_type}] {ex_data.get('instruction')[:50]}...")

    print(f"🎉 Sahifa {page_num} yakunlandi. {added_count} ta topshiriq qo'shildi.")


def main():
    # Load API Key from .env (handle typo GEMINI_API_KRY as specified by user)
    api_key = config('GEMINI_API_KRY', default=None) or config('GEMINI_API_KEY', default=None)
    if not api_key:
        print("❌ GEMINI_API_KRY topilmadi .env faylini tekshiring.")
        sys.exit(1)

    # Initialize LangChain LLM (bepul kvotasi ko'proq bo'lgan gemini-1.5-flash yoki atrof-muhit o'zgaruvchisi orqali belgilangan model)
    model_name = config('GEMINI_MODEL', default='gemini-2.5-flash')
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0.1
    )

    # Yangi kategoriya yaratish
    category_name = "Book 1 Practice Exercises (LangChain)"
    category, created = Category.objects.get_or_create(
        name=category_name,
        defaults={'description': "LangChain va Gemini yordamida avtomatik ajratib olingan kitob topshiriqlari."}
    )
    if created:
        print(f"📁 Yangi kategoriya yaratildi: '{category.name}'")
    else:
        print(f"📁 Kategoriya tanlandi: '{category.name}'")

    # Qaysi sahifalarni tahlil qilishni belgilash (sukut bo'yicha 12 dan 15 gacha bo'lgan sahifalar namunasi)
    start_page = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    end_page = int(sys.argv[2]) if len(sys.argv) > 2 else 15

    print(f"🚀 LangChain avtomatlashtirish jarayoni boshlandi (Sahifalar: {start_page} - {end_page})...")
    for p in range(start_page, end_page + 1):
        process_page(p, category, llm)
        if p < end_page:
            time.sleep(5)  # Sahifalar orasida qisqa pauza (breather)

    print("\n✨ Barcha belgilangan sahifalar muvaffaqiyatli qayta ishlandi!")


if __name__ == '__main__':
    main()
