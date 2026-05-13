import docx
from docx.document import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

def iter_block_items(parent):
    if isinstance(parent, Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("something's wrong")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)

def inspect_structure(file_path):
    doc = docx.Document(file_path)
    current_section = "Unknown"
    for item in iter_block_items(doc):
        if isinstance(item, Paragraph):
            text = item.text.strip()
            if text:
                print(f"P: {text}")
        elif isinstance(item, Table):
            print(f"T: Table with {len(item.rows)} rows")
            # Print first row to identify
            if item.rows:
                cells = [cell.text.strip() for cell in item.rows[0].cells]
                print(f"   Sample: {cells}")

if __name__ == "__main__":
    inspect_structure("Beginner vocabulary last one.docx")
