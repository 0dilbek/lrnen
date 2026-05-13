import docx

def inspect_docx(file_path):
    doc = docx.Document(file_path)
    for i, para in enumerate(doc.paragraphs[:50]): # Inspect first 50 paragraphs
        if para.text.strip():
            print(f"P{i}: {para.text.strip()}")

if __name__ == "__main__":
    inspect_docx("Beginner vocabulary last one.docx")
