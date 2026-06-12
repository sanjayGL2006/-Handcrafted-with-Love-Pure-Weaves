# ============================================================
#  Pure Weaves - Invoice Generator Utility
#  File: invoice_generator.py
#  Description: High-fidelity invoice generation in PDF (fpdf2)
#               and Word Document (docx zip schema).
# ============================================================

import io
import zipfile
import datetime
from fpdf import FPDF
from typing import Any

class InvoicePDF(FPDF):
    def __init__(self, invoice_no: Any, date: Any, customer: Any, subtotal: Any, tax: Any, discount: Any, total: Any) -> None:
        super().__init__()
        self.invoice_no = invoice_no
        self.date = date
        self.customer = customer
        self.subtotal = float(subtotal)
        self.tax = float(tax)
        self.discount = float(discount)
        self.total = float(total)

    def header(self) -> None:
        # Premium Maroon Color Palette Top Bar
        self.set_fill_color(123, 26, 46) # #7B1A2E Maroon
        self.rect(0, 0, 210, 35, 'F')
        
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 20)
        self.cell(0, 5, "PURE WEAVES", ln=True)
        self.set_font('Helvetica', '', 9)
        self.cell(0, 8, "Handcrafted Saree Kuchu & Bunches", ln=True)
        
        # Company Info Right Aligned
        self.set_xy(110, 10)
        self.set_text_color(245, 230, 211) # #F5E6D3 Cream
        self.set_font('Helvetica', 'B', 9)
        self.cell(90, 4, "Pure Weaves Shivamogga", align='R', ln=True)
        self.set_font('Helvetica', '', 8)
        self.cell(90, 4, "Latha & Gangadhar", align='R', ln=True)
        self.cell(90, 4, "Mobile: +91 8088744654", align='R', ln=True)
        self.cell(90, 4, "Email: pureweaves@gmail.com", align='R', ln=True)
        self.set_y(40)

    def footer(self) -> None:
        self.set_y(-25)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(123, 26, 46)
        self.cell(0, 4, "Thank you for shopping with Pure Weaves!", align='C', ln=True)
        self.set_text_color(138, 106, 112)
        self.cell(0, 4, "Facebook: facebook.com/pureweaves | Instagram: @pureweaves_sareesbunches", align='C', ln=True)
        self.cell(0, 4, "Copyright 2026 Pure Weaves Shivamogga. All rights reserved.", align='C', ln=True)


def generate_pdf_invoice(invoice_no: Any, date: Any, customer: Any, items: Any, subtotal: Any, tax: Any, discount: Any, total: Any) -> Any:
    pdf = InvoicePDF(invoice_no, date, customer, subtotal, tax, discount, total)
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(True, margin=30)
    
    pdf.set_y(42)
    
    # Invoice Metadata & Customer Metadata Layout Columns
    pdf.set_text_color(42, 10, 18) # #2A0A12 Deep Red
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(100, 6, "BILL TO:", ln=False)
    pdf.cell(80, 6, "INVOICE DETAILS:", ln=True)
    
    pdf.set_font('Helvetica', '', 9)
    # Row 1
    pdf.cell(100, 5, f"Customer: {customer['name']}", ln=False)
    pdf.cell(80, 5, f"Invoice #: {invoice_no}", ln=True)
    # Row 2
    pdf.cell(100, 5, f"Mobile: +91 {customer['mobile']}", ln=False)
    pdf.cell(80, 5, f"Date: {date}", ln=True)
    # Row 3
    pdf.cell(100, 5, f"Email: {customer.get('email') or 'N/A'}", ln=False)
    pdf.cell(80, 5, "Status: PAID", ln=True)
    # Address (handles wrap if needed)
    pdf.cell(100, 5, f"Address: {customer.get('address') or 'N/A'}", ln=True)
    
    pdf.ln(6)
    
    # Table Header
    pdf.set_fill_color(123, 26, 46) # Maroon
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(100, 7, "  Product / Design Description", fill=True, ln=False)
    pdf.cell(20, 7, "Qty", fill=True, align='C', ln=False)
    pdf.cell(30, 7, "Unit Price", fill=True, align='R', ln=False)
    pdf.cell(30, 7, "Total Price  ", fill=True, align='R', ln=True)
    
    # Table Rows
    pdf.set_text_color(58, 26, 34)
    pdf.set_font('Helvetica', '', 9)
    bg_toggle = False
    
    for item in items:
        if bg_toggle:
            pdf.set_fill_color(253, 246, 236) # #FDF6EC Cream light
        else:
            pdf.set_fill_color(255, 255, 255)
        bg_toggle = not bg_toggle
        
        pdf.cell(100, 7, f"  {item['name']}", border='B', fill=True, ln=False)
        pdf.cell(20, 7, f"{item['qty']}", border='B', fill=True, align='C', ln=False)
        pdf.cell(30, 7, f"INR {float(item['price']):.2f}", border='B', fill=True, align='R', ln=False)
        total_price = float(item['qty']) * float(item['price'])
        pdf.cell(30, 7, f"INR {total_price:.2f}  ", border='B', fill=True, align='R', ln=True)
        
    pdf.ln(5)
    
    # Financial Summary Right Aligned
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(120, 5, "", ln=False)
    pdf.cell(30, 5, "Subtotal:", align='R', ln=False)
    pdf.cell(30, 5, f"INR {float(subtotal):.2f}", align='R', ln=True)
    
    pdf.cell(120, 5, "", ln=False)
    pdf.cell(30, 5, "GST (5%):", align='R', ln=False)
    pdf.cell(30, 5, f"INR {float(tax):.2f}", align='R', ln=True)
    
    pdf.cell(120, 5, "", ln=False)
    pdf.cell(30, 5, "Discount:", align='R', ln=False)
    pdf.cell(30, 5, f"-INR {float(discount):.2f}", align='R', ln=True)
    
    pdf.ln(2)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(123, 26, 46)
    pdf.cell(120, 6, "", ln=False)
    pdf.cell(30, 6, "Grand Total:", align='R', ln=False)
    pdf.cell(30, 6, f"INR {float(total):.2f}", align='R', ln=True)
    
    return pdf.output()


def generate_docx_invoice(invoice_no: Any, date: Any, customer: Any, items: Any, subtotal: Any, tax: Any, discount: Any, total: Any) -> Any:
    """
    Generates a Microsoft Word document (.docx) using manual OpenXML packaging.
    Avoids compiled lxml/Cython dependencies for full compatibility.
    """
    subtotal = float(subtotal)
    tax = float(tax)
    discount = float(discount)
    total = float(total)
    
    # Create the zip package in memory
    docx_buffer = io.BytesIO()
    with zipfile.ZipFile(docx_buffer, 'w', zipfile.ZIP_DEFLATED) as docx:
        
        # 1. [Content_Types].xml
        content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""
        docx.writestr("[Content_Types].xml", content_types)

        # 2. _rels/.rels
        rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
        docx.writestr("_rels/.rels", rels)

        # 3. word/document.xml
        # Coupon details must NOT appear in this document
        document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:jc w:val="center"/></w:pPr>
      <w:r>
        <w:rPr>
          <w:b/><w:sz w:val="42"/><w:color w:val="7B1A2E"/>
        </w:rPr>
        <w:t>PURE WEAVES</w:t>
      </w:r>
    </w:p>
    <w:p>
      <w:pPr><w:jc w:val="center"/></w:pPr>
      <w:r>
        <w:rPr><w:sz w:val="18"/><w:color w:val="8A6A70"/></w:rPr>
        <w:t>Shivamogga, Karnataka | Email: pureweaves@gmail.com | Phone: +91 8088744654</w:t>
      </w:r>
    </w:p>
    
    <w:p><w:r><w:t></w:t></w:r></w:p>
    
    <w:p>
      <w:r>
        <w:rPr><w:b/><w:sz w:val="24"/><w:color w:val="7B1A2E"/></w:rPr>
        <w:t>INVOICE DETAILS</w:t>
      </w:r>
    </w:p>
    <w:p><w:r><w:t>Invoice Number: {invoice_no}</w:t></w:r></w:p>
    <w:p><w:r><w:t>Date: {date}</w:t></w:r></w:p>
    
    <w:p><w:r><w:t></w:t></w:r></w:p>
    
    <w:p>
      <w:r>
        <w:rPr><w:b/><w:sz w:val="24"/><w:color w:val="7B1A2E"/></w:rPr>
        <w:t>CUSTOMER DETAILS</w:t>
      </w:r>
    </w:p>
    <w:p><w:r><w:t>Name: {customer['name']}</w:t></w:r></w:p>
    <w:p><w:r><w:t>Mobile: +91 {customer['mobile']}</w:t></w:r></w:p>
    <w:p><w:r><w:t>Email: {customer.get('email') or 'N/A'}</w:t></w:r></w:p>
    <w:p><w:r><w:t>Address: {customer.get('address') or 'N/A'}</w:t></w:r></w:p>
    
    <w:p><w:r><w:t></w:t></w:r></w:p>
    
    <!-- Table -->
    <w:tbl>
      <w:tblPr>
        <w:tblBorders>
          <w:top w:val="single" w:sz="6" w:space="0" w:color="7B1A2E"/>
          <w:left w:val="none"/>
          <w:bottom w:val="single" w:sz="6" w:space="0" w:color="7B1A2E"/>
          <w:right w:val="none"/>
          <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E8CFA8"/>
          <w:insideV w:val="none"/>
        </w:tblBorders>
      </w:tblPr>
      <w:tr>
        <w:tc><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Product Name</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Quantity</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Unit Price</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:rPr><w:b/></w:rPr><w:t>Total Price</w:t></w:r></w:p></w:tc>
      </w:tr>
"""
        for item in items:
            document_xml += f"""
      <w:tr>
        <w:tc><w:p><w:r><w:t>{item['name']}</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:t>{item['qty']}</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:t>₹{float(item['price']):.2f}</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:t>₹{(float(item['qty']) * float(item['price'])):.2f}</w:t></w:r></w:p></w:tc>
      </w:tr>
"""
        document_xml += f"""
    </w:tbl>
    
    <w:p><w:r><w:t></w:t></w:r></w:p>
    
    <w:p>
      <w:pPr><w:jc w:val="right"/></w:pPr>
      <w:r><w:t>Subtotal: ₹{subtotal:.2f}</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:jc w:val="right"/></w:pPr>
      <w:r><w:t>GST (5%): ₹{tax:.2f}</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:jc w:val="right"/></w:pPr>
      <w:r><w:t>Discount: -₹{discount:.2f}</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:jc w:val="right"/></w:pPr>
      <w:r>
        <w:rPr><w:b/><w:sz w:val="28"/><w:color w:val="7B1A2E"/></w:rPr>
        <w:t>Grand Total: ₹{total:.2f}</w:t>
      </w:r>
    </w:p>
    
    <w:p><w:r><w:t></w:t></w:r></w:p>
    
    <w:p>
      <w:pPr><w:jc w:val="center"/></w:pPr>
      <w:r>
        <w:rPr><w:b/><w:color w:val="7B1A2E"/></w:rPr>
        <w:t>Thank you for shopping with Pure Weaves!</w:t>
      </w:r>
    </w:p>
    <w:p>
      <w:pPr><w:jc w:val="center"/></w:pPr>
      <w:r>
        <w:rPr><w:color w:val="8A6A70"/></w:rPr>
        <w:t>Instagram: @pureweaves_sareesbunches | YouTube: @pureweaves</w:t>
      </w:r>
    </w:p>
  </w:body>
</w:document>"""
        docx.writestr("word/document.xml", document_xml)

    docx_buffer.seek(0)
    return docx_buffer.getvalue()
