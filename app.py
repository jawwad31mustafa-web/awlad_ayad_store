import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
import arabic_reshaper
from bidi.algorithm import get_display
import os
from datetime import datetime

# تسجيل الخط العربي (Amiri)
pdfmetrics.registerFont(TTFont("Amiri", "Amiri-Regular.ttf"))

# 🔹 دالة تهيئة النص العربي
def ar(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text))

# 🔹 دالة إنشاء الفاتورة PDF
def save_invoice_pdf(name, phone, address, cart, total, discount, after_discount):
    os.makedirs("invoices", exist_ok=True)
    invoice_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"invoices/invoice_{invoice_id}.pdf"

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    c.setFont("Amiri", 16)

    # عنوان الفاتورة
    c.drawRightString(width - 40, height - 50, ar("🧾 متجر أولاد عياد — فاتورة شراء"))

    c.setFont("Amiri", 12)
    # بيانات العميل
    c.drawRightString(width - 40, height - 100, ar(f"الاسم: {name}"))
    c.drawRightString(width - 40, height - 120, ar(f"الهاتف: {phone}"))
    c.drawRightString(width - 40, height - 140, ar(f"العنوان: {address}"))
    c.drawRightString(width - 40, height - 160, ar(f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"))

    # جدول الطلبات
    y = height - 200
    for item in cart:
        line = f"{item['name']} × {item['qty']} = {item['price']*item['qty']} ج.م"
        c.drawRightString(width - 40, y, ar(line))
        y -= 20

    # الإجمالي
    y -= 20
    c.drawRightString(width - 40, y, ar(f"الإجمالي: {total} ج.م"))
    y -= 20
    c.drawRightString(width - 40, y, ar(f"الخصم: {discount} ج.م"))
    y -= 20
    c.drawRightString(width - 40, y, ar(f"المطلوب دفعه: {after_discount} ج.م"))

    # رسالة شكر
    y -= 40
    c.setFont("Amiri", 14)
    c.drawCentredString(width / 2, y, ar("🎉 شكراً لتسوقكم من أولاد عياد 🎉"))

    c.save()
    return filename


# ================== واجهة Streamlit ==================

st.set_page_config(page_title="متجر أولاد عياد", page_icon="🛍️")

st.title("🛍️ متجر أولاد عياد")
st.write("مرحباً بكم! اختر الملابس وأضفها إلى سلة المشتريات 👕👗")

# منتجات
products = [
     {"name": "تيشيرت رجالي أسود", "price": 250, "img": "https://media-art.net/wp-content/uploads/2024/10/unisex-classic-tee-black-front-6702c2bda9757.jpg"},
    {"name": "تيشيرت رجالي أبيض", "price": 230, "img": "https://images.unsplash.com/photo-1520974735194-6c07f7c9e7b6"},
    {"name": "بنطال جينز رجالي", "price": 400, "img": "https://images.unsplash.com/photo-1503341455253-b2e723bb3dbb"},
    {"name": "جاكيت شتوي", "price": 650, "img": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab"},
    {"name": "هودي كاجوال", "price": 500, "img": "https://images.unsplash.com/photo-1602810318383-eed6f34f24d6"},
    {"name": "قميص كلاسيك", "price": 300, "img": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246"},
    {"name": "تيشيرت أطفال", "price": 180, "img": "https://images.unsplash.com/photo-1620799139504-3f81d3a7a4a0"},
    {"name": "فستان صيفي", "price": 550, "img": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c"},
    {"name": "بنطال رياضي", "price": 270, "img": "https://images.unsplash.com/photo-1618354691330-37d315f3a4b2"},
    {"name": "حذاء رياضي", "price": 600, "img": "https://images.unsplash.com/photo-1528701800489-20be9c1e88cd"}
]


# سلة المشتريات
if "cart" not in st.session_state:
    st.session_state.cart = []

# عرض المنتجات
cols = st.columns(2)
for idx, p in enumerate(products):
    with cols[idx % 2]:
        st.image(p["img"], width=200)
        st.write(f"**{p['name']}** — {p['price']} ج.م")
        qty = st.number_input(f"الكمية ({p['name']})", min_value=0, max_value=10, step=1, key=p["name"])
        if st.button(f"إضافة {p['name']}"):
            if qty > 0:
                st.session_state.cart.append({"name": p["name"], "price": p["price"], "qty": qty})
                st.success(f"تمت إضافة {p['name']} × {qty} للسلة")

st.divider()

# عرض السلة
st.subheader("🛒 سلة المشتريات")
if len(st.session_state.cart) == 0:
    st.info("السلة فارغة.")
else:
    total = sum(item["price"] * item["qty"] for item in st.session_state.cart)
    discount = total * 0.1 if total >= 500 else 0
    after_discount = total - discount

    for item in st.session_state.cart:
        st.write(f"- {item['name']} × {item['qty']} = {item['price']*item['qty']} ج.م")

    st.write(f"**الإجمالي:** {total} ج.م")
    st.write(f"**الخصم:** {discount} ج.م")
    st.write(f"**المطلوب دفعه:** {after_discount} ج.م")

    # بيانات العميل
    st.subheader("📋 بيانات العميل")
    name = st.text_input("الاسم الكامل")
    phone = st.text_input("رقم الهاتف")
    address = st.text_area("العنوان")

    if st.button("✅ تأكيد الطلب وحفظ الفاتورة PDF"):
        if not name or not phone or not address:
            st.error("الرجاء إدخال جميع بيانات العميل")
        else:
            path = save_invoice_pdf(name, phone, address, st.session_state.cart, total, discount, after_discount)
            st.success("تم حفظ الفاتورة بنجاح ✅")

            # زر لتحميل الفاتورة مباشرة
            with open(path, "rb") as f:
                st.download_button("⬇️ تحميل الفاتورة PDF", f, file_name=os.path.basename(path))
