import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="i4.0 Analysis System", layout="wide")

st.title("ระบบวิเคราะห์ความพร้อมอุตสาหกรรม 4.0")
st.write("สำหรับใช้งานในองค์กร (EECi)")

# =========================
# STEP 1: UPLOAD FILE
# =========================
uploaded_file = st.file_uploader("Upload Excel (ไฟล์ประเมินบริษัท)", type=["xlsx"])

# =========================
# STEP 2: COMPANY NAME
# =========================
def extract_company_name(file):
    raw = pd.read_excel(file, sheet_name="Summary", header=None)
    raw = raw.astype(str)

    keywords = ["บริษัท", "Company", "Co.", "Ltd"]

    for i in range(raw.shape[0]):
        for j in range(raw.shape[1]):
            cell = raw.iloc[i, j]

            if any(k in cell for k in keywords):
                return cell.strip()

    return "ไม่พบชื่อบริษัท"

# =========================
# STEP 3: EXTRACT DATA (SAFE VERSION)
# =========================
def extract_data(file):
    raw = pd.read_excel(file, sheet_name="Summary", header=None)

    metrics = [
        "Production Automation","Enterprise Automation","Facility Automation",
        "Production Network","Enterprise Network","Facility Network",
        "Smart Production","Smart Enterprise","Smart Facility",
        "Internal Integration","External Integration","Market Analysis",
        "Product Life Cycle","Top-down Management","i4.0 Strategy",
        "Inter-company Collaboration","Workforce Learning"
    ]

    scores = []

    for metric in metrics:
        found = False

        for i in range(raw.shape[0]):
            for j in range(raw.shape[1]):

                # 🔥 แปลงเป็น string แบบ safe
                cell = str(raw.iloc[i, j])

                if metric in cell:

                    for k in range(1, 6):
                        try:
                            val = raw.iloc[i, j+k]
                            val_str = str(val)

                            # 🔥 กัน NaN + กันค่าประหลาด
                            if val_str.replace('.', '', 1).isdigit():
                                scores.append(float(val_str))
                                found = True
                                break

                        except:
                            continue

                    if found:
                        break
            if found:
                break

        if not found:
            scores.append(None)

    df = pd.DataFrame({"Metric": metrics, "Score": scores})

    # 🔥 ลบค่า None
    df = df.dropna()

    # 🔥 แปลงเป็น float แบบปลอดภัย
    df["Score"] = pd.to_numeric(df["Score"], errors="coerce")

    # 🔥 ลบค่าที่ยังผิดพลาด
    df = df.dropna()

    # 🔥 ทศนิยม 1 ตำแหน่ง (ของที่นายต้องการ)
    df["Score"] = df["Score"].round(1)

    return df

# =========================
# STEP 4: INDUSTRY LIST
# =========================
industry_list = [
"กลุ่มอุตสาหกรรมก๊าซ","กลุ่มอุตสาหกรรมการพิมพ์และบรรจุภัณฑ์","กลุ่มอุตสาหกรรมชิ้นส่วนและอะไหล่ยานยนต์",
"กลุ่มอุตสาหกรรมดิจิทัล","กลุ่มอุตสาหกรรมต่อเรือ ซ่อมเรือและก่อสร้างงานเหล็ก",
"กลุ่มอุตสาหกรรมเทคโนโลยีชีวภาพ","กลุ่มอุตสาหกรรมน้ำตาล","กลุ่มอุตสาหกรรมน้ำมันปาล์ม",
"กลุ่มอุตสาหกรรมป้องกันประเทศ","กลุ่มอุตสาหกรรมปิโตรเคมี","กลุ่มอุตสาหกรรมปูนซีเมนต์",
"กลุ่มอุตสาหกรรมผลิตภัณฑ์เสริมอาหาร","กลุ่มอุตสาหกรรมผู้ผลิตเครื่องมือแพทย์",
"กลุ่มอุตสาหกรรมผู้ผลิตไฟฟ้า","กลุ่มอุตสาหกรรมพลังงานหมุนเวียน","กลุ่มอุตสาหกรรมพลาสติก",
"กลุ่มอุตสาหกรรมเฟอร์นิเจอร์","กลุ่มอุตสาหกรรมไฟฟ้าและอิเล็กทรอนิกส์",
"กลุ่มอุตสาหกรรมไม้อัด ไม้บาง และวัสดุแผ่น","กลุ่มอุตสาหกรรมยาง","กลุ่มอุตสาหกรรมยา",
"กลุ่มอุตสาหกรรมยานยนต์","กลุ่มอุตสาหกรรมเยื่อและกระดาษ","กลุ่มอุตสาหกรรมรองเท้า",
"กลุ่มอุตสาหกรรมโรงกลั่นน้ำมันปิโตรเลียม","กลุ่มอุตสาหกรรมโรงเลื่อยและโรงอบไม้",
"กลุ่มอุตสาหกรรมสมุนไพร","กลุ่มอุตสาหกรรมสิ่งทอ","กลุ่มอุตสาหกรรมสำรวจและผลิตปิโตรเลียม",
"กลุ่มอุตสาหกรรมหัตถกรรมสร้างสรรค์","กลุ่มอุตสาหกรรมหล่อโลหะ","กลุ่มอุตสาหกรรมหนังและผลิตภัณฑ์หนัง",
"กลุ่มอุตสาหกรรมหลังคาและอุปกรณ์","กลุ่มอุตสาหกรรมเหล็ก","กลุ่มอุตสาหกรรมอลูมิเนียม",
"กลุ่มอุตสาหกรรมอัญมณีและเครื่องประดับ","กลุ่มอุตสาหกรรมอาหารและเครื่องดื่ม",
"กลุ่มอุตสาหกรรมเครื่องจักรกล","กลุ่มอุตสาหกรรมเครื่องปรับอากาศและเครื่องทำความเย็น",
"กลุ่มอุตสาหกรรมเซรามิก","กลุ่มอุตสาหกรรมแก้วและกระจก","กลุ่มอุตสาหกรรมเคมี",
"กลุ่มอุตสาหกรรมเครื่องสำอาง","กลุ่มอุตสาหกรรมกระดาษและวัสดุการพิมพ์",
"กลุ่มอุตสาหกรรมโลจิสติกส์และซัพพลายเชน","กลุ่มอุตสาหกรรมระบบราง",
"กลุ่มอุตสาหกรรมอากาศยาน","กลุ่มอุตสาหกรรมหุ่นยนต์และระบบอัตโนมัติ"
]

# =========================
# STEP 5: CLASSIFY INDUSTRY
# =========================
def classify_industry_auto(text):

    text = text.lower()
    text = re.sub(r'[^a-zA-Zก-๙]', ' ', text)

    rules = {

"กลุ่มอุตสาหกรรมก๊าซ": ["ก๊าซ","แก๊ส","gas","LPG","NGV","ออกซิเจน","ไนโตรเจน","ไฮโดรเจน","โรงบรรจุก๊าซ","ท่อก๊าซ","ถังก๊าซ","ก๊าซอุตสาหกรรม","ก๊าซหุงต้ม","พลังงานก๊าซ","สถานีแก๊ส"],

"กลุ่มอุตสาหกรรมการพิมพ์และบรรจุภัณฑ์": ["พิมพ์","บรรจุภัณฑ์","แพคเกจ","กล่อง","ซอง","ฉลาก","สติ๊กเกอร์","โรงพิมพ์","แพ็คสินค้า","หีบห่อ","ฟิล์มห่อ","กล่องกระดาษ","บรรจุสินค้า","ถุงพลาสติก","กล่องสินค้า"],

"กลุ่มอุตสาหกรรมชิ้นส่วนและอะไหล่ยานยนต์": ["อะไหล่","ชิ้นส่วนรถ","อะไหล่รถ","ชิ้นส่วนยานยนต์","auto parts","เครื่องยนต์","เกียร์","เพลา","ระบบเบรก","ช่วงล่าง","อะไหล่รถยนต์","ชิ้นส่วนเครื่องยนต์","โรงงานอะไหล่","ชิ้นส่วนรถบรรทุก","parts"],

"กลุ่มอุตสาหกรรมดิจิทัล": ["ไอที","ซอฟต์แวร์","software","ดิจิทัล","แอป","ระบบ","โปรแกรม","เว็บไซต์","data","AI","cloud","ระบบสารสนเทศ","แพลตฟอร์ม","เทคโนโลยี","ไอทีโซลูชัน"],

"กลุ่มอุตสาหกรรมต่อเรือ ซ่อมเรือและก่อสร้างงานเหล็ก": ["เรือ","ต่อเรือ","ซ่อมเรือ","ship","ท่าเรือ","โครงสร้างเหล็ก","งานเหล็ก","อู่เรือ","โครงสร้าง","เหล็กโครงสร้าง","งานประกอบเหล็ก","อุตสาหกรรมเรือ","dock","marine","steel structure"],

"กลุ่มอุตสาหกรรมเทคโนโลยีชีวภาพ": ["ชีวภาพ","biotech","เอนไซม์","จุลินทรีย์","พันธุกรรม","ชีววิทยา","การหมัก","biotechnology","อาหารชีวภาพ","วิจัยชีวภาพ","สารชีวภาพ","เพาะเลี้ยง","ชีววิศวกรรม","bio","lab"],

"กลุ่มอุตสาหกรรมน้ำตาล": ["น้ำตาล","อ้อย","โรงงานน้ำตาล","sugar","น้ำตาลทราย","น้ำเชื่อม","อ้อยโรงงาน","น้ำตาลดิบ","น้ำตาลขาว","น้ำตาลทรายขาว","น้ำตาลทรายแดง","โรงงานอ้อย","น้ำตาลอุตสาหกรรม","syrup","refine sugar"],

"กลุ่มอุตสาหกรรมน้ำมันปาล์ม": ["ปาล์ม","น้ำมันปาล์ม","palm oil","โรงงานปาล์ม","ปาล์มดิบ","ปาล์มสกัด","น้ำมันพืช","ผลปาล์ม","โรงสกัดปาล์ม","ปาล์มอุตสาหกรรม","น้ำมันพืช","สกัดน้ำมัน","ปาล์มดิบ","refinery palm","oil palm"],

"กลุ่มอุตสาหกรรมป้องกันประเทศ": ["ทหาร","defense","ยุทโธปกรณ์","อาวุธ","ระบบป้องกัน","ทหารบก","ทหารเรือ","ทหารอากาศ","ยุทธศาสตร์","ความมั่นคง","อุปกรณ์ทหาร","ระบบเรดาร์","โดรนทหาร","security","military"],

"กลุ่มอุตสาหกรรมปิโตรเคมี": ["ปิโตร","petro","เคมี","น้ำมัน","สารเคมี","โรงงานเคมี","ปิโตรเคมี","พลาสติกขั้นต้น","สารตั้งต้น","อุตสาหกรรมเคมี","สารอินทรีย์","chemical","refinery","gas","polymer"],

"กลุ่มอุตสาหกรรมปูนซีเมนต์": ["ปูน","cement","ซีเมนต์","คอนกรีต","ปูนผสม","โรงปูน","ปูนสำเร็จรูป","คอนกรีตผสมเสร็จ","วัสดุก่อสร้าง","ปูนปอร์ตแลนด์","ซีเมนต์ผง","ปูนก่อสร้าง","โรงงานปูน","cement plant","construction material"],

"กลุ่มอุตสาหกรรมผลิตภัณฑ์เสริมอาหาร": ["อาหารเสริม","วิตามิน","supplement","สุขภาพ","แคปซูล","ผงอาหาร","โปรตีน","ผลิตภัณฑ์สุขภาพ","วิตามินรวม","อาหารเสริมสุขภาพ","สารอาหาร","nutraceutical","อาหารสุขภาพ","dietary","nutrition"],

"กลุ่มอุตสาหกรรมผู้ผลิตเครื่องมือแพทย์": ["เครื่องมือแพทย์","medical","อุปกรณ์แพทย์","เครื่องมือผ่าตัด","อุปกรณ์โรงพยาบาล","เครื่องตรวจ","เครื่องวัด","เครื่องมือสุขภาพ","health device","เครื่องช่วยหายใจ","เครื่องมือแพทย์","diagnostic","device","hospital equipment"],

"กลุ่มอุตสาหกรรมผู้ผลิตไฟฟ้า": ["ไฟฟ้า","power","โรงไฟฟ้า","ผลิตไฟฟ้า","generator","พลังงานไฟฟ้า","ไฟฟ้าอุตสาหกรรม","โรงผลิตไฟฟ้า","electricity","grid","ไฟฟ้าแรงสูง","ผลิตพลังงาน","โรงงานไฟฟ้า","energy plant","power generation"],

"กลุ่มอุตสาหกรรมพลังงานหมุนเวียน": ["solar","แสงอาทิตย์","ลม","พลังงานหมุนเวียน","renewable","พลังงานสะอาด","กังหันลม","solar cell","พลังงานชีวมวล","biomass","พลังงานน้ำ","green energy","clean energy","energy renewable","solar panel"],

"กลุ่มอุตสาหกรรมพลาสติก": ["พลาสติก","plastic","PET","poly","เม็ดพลาสติก","ฉีดพลาสติก","ขึ้นรูป","ถุงพลาสติก","ฟิล์ม","บรรจุภัณฑ์","พลาสติกแข็ง","พลาสติกอ่อน","โรงงานพลาสติก","plastic molding","resin"],

"กลุ่มอุตสาหกรรมเฟอร์นิเจอร์": ["เฟอร์นิเจอร์","โต๊ะ","เก้าอี้","ตู้","bed","sofa","ไม้","furniture","ตกแต่ง","งานไม้","built-in","เฟอร์นิเจอร์ไม้","เฟอร์นิเจอร์เหล็ก","home decor","interior"],

"กลุ่มอุตสาหกรรมไฟฟ้าและอิเล็กทรอนิกส์": ["ไฟฟ้า","electronic","วงจร","PCB","อุปกรณ์ไฟฟ้า","สายไฟ","ปลั๊ก","chip","sensor","control","ไฟฟ้าอุตสาหกรรม","เครื่องใช้ไฟฟ้า","อิเล็กทรอนิกส์","component","electrical"],

"กลุ่มอุตสาหกรรมไม้อัด ไม้บาง และวัสดุแผ่น": ["ไม้","ไม้อัด","plywood","แผ่นไม้","ไม้บาง","ไม้แปรรูป","แผ่นวัสดุ","ไม้ MDF","particle board","ไม้แผ่น","โรงไม้","วัสดุไม้","ไม้ก่อสร้าง","wood panel","wood"],

"กลุ่มอุตสาหกรรมยาง": ["ยาง","rubber","ยางรถยนต์","latex","ยางดิบ","ยางพารา","ผลิตภัณฑ์ยาง","ยางอุตสาหกรรม","ซีลยาง","ท่อยาง","ยางสังเคราะห์","rubber part","ยางธรรมชาติ","elastic","rubber goods"],

"กลุ่มอุตสาหกรรมยา": ["ยา","pharma","medicine","เภสัช","ผลิตยา","ยาเม็ด","ยาแคปซูล","ยา liquid","ยาโรงงาน","drug","healthcare","ยาเคมี","ยาแผนปัจจุบัน","pharmaceutical","medical"],

"กลุ่มอุตสาหกรรมยานยนต์": ["รถ","car","auto","motor","รถยนต์","รถบรรทุก","รถจักรยานยนต์","vehicle","EV","รถไฟฟ้า","assembly","ประกอบรถ","automotive","transport vehicle","engine"],

"กลุ่มอุตสาหกรรมเยื่อและกระดาษ": ["กระดาษ","paper","pulp","เยื่อกระดาษ","โรงกระดาษ","กระดาษอุตสาหกรรม","กระดาษพิมพ์","กระดาษแข็ง","paper mill","รีไซเคิลกระดาษ","กระดาษบรรจุ","paper packaging","cellulose","paper product"],

"กลุ่มอุตสาหกรรมรองเท้า": ["รองเท้า","shoe","footwear","รองเท้าหนัง","รองเท้ากีฬา","รองเท้าแฟชั่น","ผลิตรองเท้า","พื้นรองเท้า","shoe factory","รองเท้าแตะ","รองเท้าอุตสาหกรรม","footwear manufacturing","shoe sole","รองเท้าเด็ก"],

"กลุ่มอุตสาหกรรมโรงกลั่นน้ำมันปิโตรเลียม": ["โรงกลั่น","refinery","น้ำมัน","oil refinery","กลั่นน้ำมัน","ปิโตรเลียม","น้ำมันดิบ","refined oil","petroleum","fuel","น้ำมันเชื้อเพลิง","gasoline","diesel","energy refinery"],

"กลุ่มอุตสาหกรรมโรงเลื่อยและโรงอบไม้": ["เลื่อยไม้","อบไม้","โรงเลื่อย","ไม้แปรรูป","ไม้แห้ง","kiln","wood drying","โรงอบไม้","ไม้ดิบ","ไม้ท่อน","ไม้แปรรูป","wood processing","timber","sawmill"],

"กลุ่มอุตสาหกรรมสมุนไพร": ["สมุนไพร","herb","ยาสมุนไพร","ผลิตภัณฑ์สมุนไพร","พืชสมุนไพร","natural medicine","สารสกัด","herbal","extract","สุขภาพธรรมชาติ","organic","สมุนไพรไทย","plant extract"],

"กลุ่มอุตสาหกรรมสิ่งทอ": ["ผ้า","textile","garment","เสื้อผ้า","ตัดเย็บ","ด้าย","fabric","ทอผ้า","เสื้อ","โรงงานเสื้อผ้า","เครื่องแต่งกาย","fashion","woven","knit","apparel"],

"กลุ่มอุตสาหกรรมสำรวจและผลิตปิโตรเลียม": ["สำรวจน้ำมัน","oil exploration","drilling","ขุดเจาะ","ปิโตรเลียม","offshore","แท่นขุดเจาะ","energy exploration","gas exploration","production oil","well","rig","petroleum"],

"กลุ่มอุตสาหกรรมหัตถกรรมสร้างสรรค์": ["หัตถกรรม","craft","งานฝีมือ","งานศิลป์","ของ handmade","ผลิตภัณฑ์ชุมชน","OTOP","งานไม้","งานผ้า","creative","art","handmade","decor","local product"],

"กลุ่มอุตสาหกรรมหล่อโลหะ": ["หล่อ","casting","foundry","โลหะ","หล่อเหล็ก","หล่ออลูมิเนียม","แม่พิมพ์","metal casting","โรงหล่อ","die casting","metal part","หล่อชิ้นงาน"],

"กลุ่มอุตสาหกรรมหนังและผลิตภัณฑ์หนัง": ["หนัง","leather","กระเป๋าหนัง","รองเท้าหนัง","belt","ผลิตภัณฑ์หนัง","leather goods","หนังแท้","synthetic leather","bag","wallet"],

"กลุ่มอุตสาหกรรมหลังคาและอุปกรณ์": ["หลังคา","roof","กระเบื้อง","แผ่นหลังคา","metal sheet","วัสดุมุงหลังคา","roofing","หลังคาเหล็ก","หลังคาเมทัลชีท","tile","หลังคาบ้าน"],

"กลุ่มอุตสาหกรรมเหล็ก": ["เหล็ก","steel","เหล็กแผ่น","เหล็กเส้น","steel structure","โรงเหล็ก","rolling","metal","iron","เหล็กกล้า","steel mill","structure"],

"กลุ่มอุตสาหกรรมอลูมิเนียม": ["อลูมิเนียม","aluminum","extrusion","profile","aluminium","แผ่นอลูมิเนียม","window frame","อลูมิเนียมก่อสร้าง","aluminum part"],

"กลุ่มอุตสาหกรรมอัญมณีและเครื่องประดับ": ["อัญมณี","jewelry","ทอง","เงิน","เพชร","พลอย","เครื่องประดับ","gem","gold","silver","jewel","ornament"],

"กลุ่มอุตสาหกรรมอาหารและเครื่องดื่ม": ["อาหาร","เครื่องดื่ม","food","drink","โรงงานอาหาร","processing","อาหารสำเร็จรูป","beverage","ผลิตอาหาร","โรงงานเครื่องดื่ม"],

"กลุ่มอุตสาหกรรมเครื่องจักรกล": ["เครื่องจักร","machine","engineering","machinery","เครื่องมือ","เครื่องกล","โรงงานเครื่องจักร","automation machine","industrial machine"],

"กลุ่มอุตสาหกรรมเครื่องปรับอากาศและเครื่องทำความเย็น": ["แอร์","air conditioner","cooling","เครื่องทำความเย็น","chiller","refrigeration","เครื่องปรับอากาศ","HVAC"],

"กลุ่มอุตสาหกรรมเซรามิก": ["เซรามิก","ceramic","กระเบื้อง","ดินเผา","porcelain","tile","ceramic ware"],

"กลุ่มอุตสาหกรรมแก้วและกระจก": ["แก้ว","glass","กระจก","glassware","window glass","bottle","glass product"],

"กลุ่มอุตสาหกรรมเคมี": ["เคมี","chemical","สารเคมี","industrial chemical","lab chemical","compound","solution"],

"กลุ่มอุตสาหกรรมเครื่องสำอาง": ["เครื่องสำอาง","cosmetic","beauty","skincare","makeup","ผลิตภัณฑ์ความงาม","cosmetic product"],

"กลุ่มอุตสาหกรรมกระดาษและวัสดุการพิมพ์": ["กระดาษพิมพ์","printing material","ink","หมึก","paper print","วัสดุพิมพ์"],

"กลุ่มอุตสาหกรรมโลจิสติกส์และซัพพลายเชน": ["ขนส่ง","logistic","transport","warehouse","คลังสินค้า","distribution","delivery","supply chain"],

"กลุ่มอุตสาหกรรมระบบราง": ["รถไฟ","rail","metro","train","railway","ขนส่งทางราง"],

"กลุ่มอุตสาหกรรมอากาศยาน": ["เครื่องบิน","aircraft","aviation","airline","สนามบิน","aerospace"],

"กลุ่มอุตสาหกรรมหุ่นยนต์และระบบอัตโนมัติ": ["หุ่นยนต์","robot","automation","อัตโนมัติ","robotic","แขนกล","system automation","industrial robot"]

}

    best = None
    score = 0

    for ind, kws in rules.items():
        s = sum([1 for k in kws if k in text])

        if s > score:
            score = s
            best = ind

    if best:
        return best, score*30
    else:
        return "ไม่สามารถระบุได้", 0

# =========================
# STEP 6: SIZE
# =========================
def classify_size(df):
    avg = df["Score"].mean()

    if avg < 2:
        return "ขนาดเล็ก"
    elif avg < 3:
        return "ขนาดกลาง"
    else:
        return "ขนาดใหญ่"

# =========================
# STEP 7: WEAKNESS
# =========================
def find_weakness(df):
    weak = df[df["Score"] <= 2].sort_values(by="Score").head(5)

    # 🔥 เพิ่ม: ทศนิยม 1 ตำแหน่ง
    weak["Score"] = weak["Score"].round(1)

    return weak

# =========================
# STEP 8: RECOMMENDATION (FULL COMPLETE)
# =========================
def recommendation(metric):

    mapping = {

        # ================= PRODUCTION =================
        "Production Automation":
        "ควรเพิ่มระดับ Automation ในกระบวนการผลิต โดยเริ่มจากงานที่เป็น manual และซ้ำ ๆ "
        "เช่น การลำเลียง ตรวจสอบ และบรรจุสินค้า และพัฒนาไปสู่การใช้เครื่องจักรอัตโนมัติเต็มรูปแบบ "
        "รวมถึงเชื่อมต่อเครื่องจักรให้สามารถทำงานร่วมกันได้แบบ real-time",

        "Enterprise Automation":
        "ควรนำระบบ ERP หรือระบบสารสนเทศองค์กรมาใช้ เพื่อเชื่อมโยงข้อมูลระหว่างฝ่าย เช่น บัญชี คลังสินค้า และจัดซื้อ "
        "ลดการใช้ Excel แยกส่วน และพัฒนาไปสู่ระบบอัตโนมัติทั้งองค์กร",

        "Facility Automation":
        "ควรติดตั้งระบบ Building Automation เช่น ระบบควบคุมพลังงาน แสง และ HVAC "
        "เพื่อเพิ่ม efficiency และลดการควบคุมแบบ manual",

        # ================= NETWORK =================
        "Production Network":
        "ควรพัฒนาเครือข่ายเครื่องจักรให้สามารถสื่อสารกันได้ (Machine-to-Machine) "
        "และรองรับการแลกเปลี่ยนข้อมูลแบบ real-time",

        "Enterprise Network":
        "ควรเชื่อมต่อระบบ IT ภายในองค์กรให้สามารถแลกเปลี่ยนข้อมูลได้อย่างรวดเร็ว "
        "ลดการทำงานแบบแยกส่วน (silo)",

        "Facility Network":
        "ควรเชื่อมระบบ Facility เช่น ไฟฟ้า น้ำ HVAC เข้ากับระบบกลาง "
        "เพื่อ monitor และควบคุมแบบ real-time",

        # ================= SMART =================
        "Smart Production":
        "ควรนำ Data Analytics และ AI มาใช้ในกระบวนการผลิต เช่น predictive maintenance "
        "และการวิเคราะห์ประสิทธิภาพการผลิต",

        "Smart Enterprise":
        "ควรใช้ Business Intelligence (BI) และ Data Analytics เพื่อสนับสนุนการตัดสินใจ "
        "จากเดิมที่ใช้ประสบการณ์ไปสู่ data-driven",

        "Smart Facility":
        "ควรใช้ IoT และ Data Analytics ในการวิเคราะห์การใช้พลังงาน "
        "และเพิ่ม efficiency ของ facility",

        # ================= INTEGRATION =================
        "Internal Integration":
        "ควรเชื่อมระบบ OT (เครื่องจักร) กับ IT (ERP, Database) "
        "เพื่อให้ข้อมูลไหลแบบ end-to-end",

        "External Integration":
        "ควรเชื่อมข้อมูลกับ supplier และลูกค้า เช่น order, logistics "
        "เพื่อให้ supply chain เป็น digital",

        # ================= BUSINESS =================
        "Market Analysis":
        "ควรใช้ Big Data และ Analytics ในการวิเคราะห์ตลาดและพฤติกรรมลูกค้า "
        "เพื่อเพิ่มความแม่นยำในการตัดสินใจ",

        "Product Life Cycle":
        "ควรใช้ระบบ PLM (Product Lifecycle Management) "
        "เพื่อบริหารข้อมูลสินค้าตลอดวงจรชีวิต",

        # ================= MANAGEMENT =================
        "Top-down Management":
        "ผู้บริหารควรกำหนด vision และสนับสนุนการเปลี่ยนผ่านสู่ Industry 4.0 "
        "รวมถึงกำหนด KPI ที่ชัดเจน",

        "i4.0 Strategy":
        "องค์กรควรกำหนดกลยุทธ์ Industry 4.0 อย่างเป็นระบบ "
        "โดยมี roadmap ระยะสั้น กลาง และยาว "
        "เชื่อมโยงกับเป้าหมายทางธุรกิจ และติดตามผลอย่างต่อเนื่อง",

        # ================= COLLAB =================
        "Inter-company Collaboration":
        "ควรพัฒนาความร่วมมือกับ partner และ supplier "
        "ผ่าน digital platform เพื่อเพิ่มความเร็วของ supply chain",

        # ================= PEOPLE =================
        "Workforce Learning":
        "ควรพัฒนาทักษะบุคลากรด้าน digital, automation และ data analytics "
        "รวมถึง reskill และ upskill อย่างต่อเนื่อง"
    }

    return mapping.get(metric, "ควรวิเคราะห์เพิ่มเติมและกำหนด roadmap เฉพาะด้าน")

# =========================
# MAIN
# =========================
if uploaded_file:

    company_name = extract_company_name(uploaded_file)
    df = extract_data(uploaded_file)

    st.subheader(f"บริษัท: {company_name}")

    business_desc = st.text_input("คำอธิบายธุรกิจ")

    if business_desc:
        auto_industry, confidence = classify_industry_auto(business_desc)
    else:
        auto_industry, confidence = "ยังไม่ได้วิเคราะห์", 0

    st.write(f"ระบบแนะนำ: {auto_industry} ({confidence}%)")

    search = st.text_input("ค้นหาอุตสาหกรรม")

    filtered_list = [i for i in industry_list if search in i]

    if not filtered_list:
        filtered_list = industry_list

    default_index = 0
    if auto_industry in filtered_list:
        default_index = filtered_list.index(auto_industry)

    industry = st.selectbox(
        "ยืนยันหรือแก้ไขอุตสาหกรรม",
        filtered_list,
        index=default_index
    )

    size = classify_size(df)

    weak = find_weakness(df)
    weak["Recommendation"] = weak["Metric"].apply(recommendation)

    st.header("Dashboard")

    c1, c2, c3 = st.columns(3)

    # 🔥 KPI: 1 decimal
    c1.metric("คะแนนเฉลี่ย", f"{df['Score'].mean():.1f}")
    c2.write(f"ขนาด: {size}")
    c3.write(f"อุตสาหกรรม: {industry}")

    fig = px.line_polar(df, r="Score", theta="Metric", line_close=True)
    fig.update_traces(fill='toself')

    # 🔥 Radar: 1 decimal
    fig.update_layout(
        polar=dict(
            radialaxis=dict(tickformat=".1f")
        )
    )

    st.plotly_chart(fig)

    st.subheader("จุดอ่อน")
    st.dataframe(weak)

    st.subheader("คำแนะนำ")
    for i, r in weak.iterrows():
        st.write(f"{r['Metric']} : {r['Recommendation']}")

    fig2 = px.bar(df, x="Metric", y="Score")

    # 🔥 Bar: 1 decimal
    fig2.update_layout(yaxis_tickformat=".1f")

    st.plotly_chart(fig2)

#=========================================================================================

# =========================
# PHASE 2: ADVANCED ANALYSIS (FULL + HEATMAP)
# =========================
if uploaded_file:

    if df is None:
        st.stop()

    st.header("รายงานวิเคราะห์เชิงผู้บริหาร")

    # =========================
    # STEP 1: BENCHMARK
    # =========================
    benchmark = {
        "Production Automation": 3,
        "Enterprise Automation": 3,
        "Facility Automation": 3,
        "Production Network": 3,
        "Enterprise Network": 3,
        "Facility Network": 3,
        "Smart Production": 3,
        "Smart Enterprise": 3,
        "Smart Facility": 3,
        "Internal Integration": 3,
        "External Integration": 3,
        "Market Analysis": 3,
        "Product Life Cycle": 3,
        "Top-down Management": 3,
        "i4.0 Strategy": 3,
        "Inter-company Collaboration": 3,
        "Workforce Learning": 3
    }

    df["Benchmark"] = df["Metric"].map(benchmark).fillna(3)

    # 🔥 FIX: ไม่ใช้ค่าติดลบแล้ว
    df["Gap"] = df["Benchmark"] - df["Score"]

    # =========================
    # STEP 2: จุดแข็ง / จุดอ่อน
    # =========================
    strength = df[df["Score"] >= 3].sort_values(by="Score", ascending=False).head(5)
    weakness = df[df["Score"] <= 2].sort_values(by="Score").head(5)

    # =========================
    # STEP 3: Executive Summary
    # =========================
    avg_score = df["Score"].mean()

    if avg_score >= 3:
        level = "อยู่ในระดับค่อนข้างสูง"
    elif avg_score >= 2:
        level = "อยู่ในระดับปานกลาง"
    else:
        level = "อยู่ในระดับเริ่มต้น"

    st.subheader("Executive Summary")

    st.write(f"""
    บริษัท {company_name} อยู่ในกลุ่มอุตสาหกรรม {industry}
    มีระดับความพร้อม {level} (คะแนนเฉลี่ย {round(avg_score,2)})

    จุดแข็ง: {', '.join(strength['Metric'].tolist())}
    จุดอ่อน: {', '.join(weakness['Metric'].tolist())}
    """)

    # =========================
    # STEP 4: GAP TABLE
    # =========================
    st.subheader("Gap Analysis")

    gap_df = df.sort_values(by="Gap", ascending=False)
    st.dataframe(gap_df)

    # =========================
    # STEP 5: HEATMAP (🔥 สำคัญ)
    # =========================
    st.subheader("Heatmap แสดงจุดที่ต้องพัฒนา")

    heat_df = df[["Metric", "Gap"]].copy()

    fig_heat = px.imshow(
        [heat_df["Gap"].values],
        labels=dict(x="Metric", y="", color="Gap"),
        x=heat_df["Metric"],
        y=["Gap"],
        color_continuous_scale="Reds"
    )

    st.plotly_chart(fig_heat, use_container_width=True)

    # =========================
    # STEP 6: GAP BAR
    # =========================
    st.subheader("Gap Chart")

    fig_gap = px.bar(
        gap_df,
        x="Metric",
        y="Gap",
        color="Gap",
        color_continuous_scale="Reds"
    )

    st.plotly_chart(fig_gap, use_container_width=True)

    # =========================
    # STEP 7: STRATEGY
    # =========================
    st.subheader("ข้อเสนอเชิงกลยุทธ์")

    def strategic_recommendation(metric):

        strategy_map = {
            "Production Automation": "ลงทุนระบบ Automation เพื่อลดต้นทุน",
            "Enterprise Automation": "นำ ERP มาใช้ทั้งองค์กร",
            "Facility Automation": "ใช้ SCADA/IoT",
            "Production Network": "เชื่อมเครื่องจักร",
            "Smart Production": "ใช้ AI วิเคราะห์",
            "Internal Integration": "เชื่อมระบบทั้งหมด",
            "External Integration": "เชื่อม Supplier",
            "Market Analysis": "ใช้ Data วิเคราะห์ลูกค้า",
            "Product Life Cycle": "ใช้ PLM",
            "Top-down Management": "กำหนดนโยบายชัดเจน",
            "i4.0 Strategy": "สร้าง roadmap",
            "Workforce Learning": "Upskill พนักงาน"
        }

        return strategy_map.get(metric, "ควรพัฒนาเพิ่มเติม")

    for i, row in weakness.iterrows():
        st.write(f"- {row['Metric']} → {strategic_recommendation(row['Metric'])}")

    # =========================
    # STEP 8: PRIORITY
    # =========================
    st.subheader("Priority")

    def priority_level(x):
        if x >= 2:
            return "High"
        elif x == 1:
            return "Medium"
        else:
            return "Low"

    priority_df = df.copy()
    priority_df["Priority"] = priority_df["Gap"].apply(priority_level)

    st.dataframe(priority_df[["Metric","Score","Gap","Priority"]])

    # =========================
    # STEP 9: DISTRIBUTION
    # =========================
    st.subheader("Distribution คะแนน")

    fig_hist = px.histogram(df, x="Score", nbins=5)
    st.plotly_chart(fig_hist, use_container_width=True)

    # =========================
    # STEP 10: EXPORT
    # =========================
    st.subheader("Export")

    export_df = df.copy()
    export_df["Industry"] = industry
    export_df["Company"] = company_name

    csv = export_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "ดาวน์โหลดรายงาน (CSV)",
        csv,
        "i40_report.csv",
        "text/csv"
    )

#================================================================================

# =========================
# PHASE 3: EXECUTIVE REPORT (CLEAN VERSION)
# =========================
if uploaded_file:

    st.header("รายงานสำหรับผู้บริหาร (Executive Report)")

    # =========================
    # STEP 1: Executive Insight
    # =========================
    st.subheader("Executive Insight")

    top_weak = df.sort_values(by="Gap", ascending=False).head(3)

    insight_text = f"""
    บริษัท {company_name} อยู่ในกลุ่มอุตสาหกรรม {industry}
    มีช่องว่างสำคัญในด้าน {', '.join(top_weak['Metric'].tolist())}

    หากไม่ปรับปรุง อาจส่งผลต่อ:
    - ความสามารถการแข่งขัน
    - ประสิทธิภาพการผลิต
    - การปรับตัวสู่ Industry 4.0
    """

    st.write(insight_text)

    # =========================
    # STEP 2: KPI SUMMARY
    # =========================
    st.subheader("KPI Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("คะแนนเฉลี่ย", round(df["Score"].mean(),2))
    col2.metric("Gap สูงสุด", int(df["Gap"].max()))
    col3.metric("จำนวนจุดอ่อน", len(df[df["Score"] <= 2]))

    # =========================
    # STEP 3: VISUALIZATION
    # =========================
    st.subheader("Visualization")

    c1, c2 = st.columns(2)

    # Radar
    fig_radar = px.line_polar(
        df,
        r="Score",
        theta="Metric",
        line_close=True
    )
    fig_radar.update_traces(fill='toself')

    c1.plotly_chart(fig_radar, use_container_width=True, key="radar_phase3_clean")

    # Gap
    fig_gap = px.bar(
        df.sort_values(by="Gap", ascending=False),
        x="Metric",
        y="Gap",
        color="Gap",
        color_continuous_scale="Reds"
    )

    c2.plotly_chart(fig_gap, use_container_width=True, key="gap_phase3_clean")

    # =========================
    # STEP 4: EXPERT COMMENT
    # =========================
    st.subheader("คำวิเคราะห์จากระบบ")

    for i, row in top_weak.iterrows():
        st.write(f"- {row['Metric']} มีช่องว่าง {row['Gap']} ระดับ ควรเร่งพัฒนา")
    
#=================================================

# =========================
# PHASE 4: MULTI-COMPANY ANALYSIS
# =========================
if uploaded_file:

    st.header("เปรียบเทียบบริษัท (Multi-Company Analysis)")

    # =========================
    # STEP 1: INIT DATABASE (🔥 แก้ตรงนี้)
    # =========================
    if "database" not in st.session_state:
        st.session_state.database = pd.DataFrame(
            columns=["Company", "Industry", "Metric", "Score"]
        )

    db = st.session_state.database

    # =========================
    # STEP 2: PREP DATA
    # =========================
    temp_df = df.copy()
    temp_df["Company"] = company_name
    temp_df["Industry"] = industry

    # =========================
    # STEP 3: ADD COMPANY
    # =========================
    if st.button("เพิ่มบริษัทนี้เข้า Database"):

        # 🔥 เช็คก่อนว่ามีคอลัมน์ไหม
        if "Company" not in db.columns:
            db = pd.DataFrame(columns=["Company", "Industry", "Metric", "Score"])

        existing = db[db["Company"] == company_name]

        if len(existing) == 0:
            st.session_state.database = pd.concat(
                [db, temp_df],
                ignore_index=True
            )
            st.success("เพิ่มบริษัทเรียบร้อย")
        else:
            st.warning("บริษัทนี้มีอยู่แล้ว")

    db = st.session_state.database

    # =========================
    # STEP 4: CHECK EMPTY
    # =========================
    if db.empty:
        st.info("ยังไม่มีข้อมูลหลายบริษัท")
        st.stop()

    # =========================
    # STEP 5: SUMMARY
    # =========================
    st.subheader("สรุปคะแนนแต่ละบริษัท")

    summary = db.groupby("Company").agg({
        "Score": "mean",
        "Industry": "first"
    }).reset_index()

    summary.rename(columns={"Score": "AvgScore"}, inplace=True)

    st.dataframe(summary)

    # =========================
    # STEP 6: RANKING
    # =========================
    st.subheader("Ranking บริษัท")

    summary = summary.sort_values(by="AvgScore", ascending=False)
    summary["Rank"] = range(1, len(summary) + 1)

    st.dataframe(summary)

    fig_rank = px.bar(
        summary,
        x="Company",
        y="AvgScore",
        color="AvgScore",
        title="Ranking บริษัท"
    )

    st.plotly_chart(fig_rank, use_container_width=True, key="rank_chart_fix")

    # =========================
    # STEP 7: COMPARE
    # =========================
    st.subheader("เปรียบเทียบบริษัท")

    companies = summary["Company"].tolist()

    selected = st.multiselect(
        "เลือกบริษัท",
        companies,
        default=companies[:2]
    )

    compare_df = db[db["Company"].isin(selected)]

    if not compare_df.empty:

        fig_compare = px.line(
            compare_df,
            x="Metric",
            y="Score",
            color="Company",
            markers=True
        )

        st.plotly_chart(fig_compare, use_container_width=True, key="compare_fix")

    # =========================
    # STEP 8: INDUSTRY
    # =========================
    st.subheader("Insight อุตสาหกรรม")

    industry_avg = db.groupby("Industry")["Score"].mean().reset_index()

    st.dataframe(industry_avg)

    fig_industry = px.bar(
        industry_avg,
        x="Industry",
        y="Score",
        color="Score"
    )

    st.plotly_chart(fig_industry, use_container_width=True, key="industry_fix")

    # =========================
    # STEP 9: BEST / WORST
    # =========================
    st.subheader("Best / Worst")

    best = summary.iloc[0]
    worst = summary.iloc[-1]

    st.success(f"ดีที่สุด: {best['Company']} ({round(best['AvgScore'],2)})")
    st.error(f"ต้องปรับปรุง: {worst['Company']} ({round(worst['AvgScore'],2)})")

# ================================================================================================

# =========================
# PHASE 5: SHAREABLE + PERMISSION (NO LOGIN)
# =========================
import os
from datetime import datetime

st.header("โหมดใช้งานจริง (Share Mode)")

DATA_PATH = "database.csv"

# =========================
# STEP 1: LOAD DATABASE
# =========================
if "database" not in st.session_state:

    if os.path.exists(DATA_PATH):
        try:
            st.session_state.database = pd.read_csv(DATA_PATH)
        except:
            st.session_state.database = pd.DataFrame(columns=["Company","Industry","Metric","Score"])
    else:
        st.session_state.database = pd.DataFrame(columns=["Company","Industry","Metric","Score"])

db = st.session_state.database

# =========================
# STEP 2: ROLE SELECT (🔥 แทน login)
# =========================
st.subheader("สิทธิ์การใช้งาน")

role = st.selectbox(
    "เลือกโหมด",
    ["viewer", "editor", "admin"]
)

st.info(f"Current Mode: {role}")

# =========================
# STEP 3: SAVE FUNCTION
# =========================
def save_database():
    st.session_state.database.to_csv(DATA_PATH, index=False)

# =========================
# STEP 4: CONTROL PANEL
# =========================
st.subheader("Control Panel")

c1, c2, c3 = st.columns(3)

# SAVE
if role in ["editor", "admin"]:
    if c1.button("บันทึกข้อมูล"):
        save_database()
        st.success("บันทึกเรียบร้อย")

# RELOAD
if c2.button("โหลดข้อมูลใหม่"):
    if os.path.exists(DATA_PATH):
        st.session_state.database = pd.read_csv(DATA_PATH)
        st.success("โหลดสำเร็จ")

# RESET (admin only)
if role == "admin":
    if c3.button("ล้างข้อมูลทั้งหมด"):
        st.session_state.database = pd.DataFrame(columns=["Company","Industry","Metric","Score"])
        save_database()
        st.warning("ล้างข้อมูลแล้ว")

# =========================
# STEP 5: DELETE COMPANY
# =========================
st.subheader("ลบบริษัท")

if role in ["editor", "admin"]:

    companies = db["Company"].unique().tolist() if not db.empty else []

    if len(companies) > 0:
        del_company = st.selectbox("เลือกบริษัท", companies)

        if st.button("ลบ"):
            st.session_state.database = db[db["Company"] != del_company]
            save_database()
            st.success(f"ลบ {del_company} แล้ว")
    else:
        st.info("ไม่มีข้อมูล")

else:
    st.warning("Viewer ไม่สามารถลบข้อมูลได้")

# =========================
# STEP 6: EXPORT DATABASE
# =========================
st.subheader("Export")

csv = db.to_csv(index=False).encode("utf-8")

st.download_button(
    "ดาวน์โหลดฐานข้อมูล",
    csv,
    "database.csv",
    "text/csv"
)

# =========================
# STEP 7: DASHBOARD SUMMARY
# =========================
st.subheader("ภาพรวมระบบ")

if not db.empty:

    summary = db.groupby("Company")["Score"].mean().reset_index()
    summary.rename(columns={"Score": "AvgScore"}, inplace=True)

    col1, col2 = st.columns(2)

    fig1 = px.bar(
        summary.sort_values(by="AvgScore", ascending=False),
        x="Company",
        y="AvgScore",
        color="AvgScore",
        title="Ranking บริษัท"
    )

    col1.plotly_chart(fig1, use_container_width=True, key="phase5_rank")

    industry_avg = db.groupby("Industry")["Score"].mean().reset_index()

    fig2 = px.bar(
        industry_avg,
        x="Industry",
        y="Score",
        color="Score",
        title="ค่าเฉลี่ยอุตสาหกรรม"
    )

    col2.plotly_chart(fig2, use_container_width=True, key="phase5_industry")

else:
    st.info("ยังไม่มีข้อมูล")

# =========================
# STEP 8: SHARE GUIDE
# =========================
st.subheader("วิธีแชร์ให้ทีมใช้")

st.code("""
วิธีง่ายสุด:

1. อัปขึ้น GitHub
2. ไป https://streamlit.io/cloud
3. Deploy app.py
4. ได้ URL เช่น:
   https://your-app.streamlit.app

แชร์ลิงก์ให้หัวหน้าใช้ได้เลย

--------------------------------

ถ้าใช้ในองค์กร:
- วางใน Server
- รัน streamlit run app.py
- ให้เข้า IP:8501
""")

# ==========================================================

# =========================
# PHASE 6: EXECUTIVE DASHBOARD (FINAL PRO)
# =========================
st.header("Executive Dashboard (สรุปภาพรวมองค์กร)")

# =========================
# LOAD DATABASE
# =========================
db = st.session_state.get("database", pd.DataFrame())

if db.empty or "Company" not in db.columns:
    st.warning("ยังไม่มีข้อมูลในระบบ กรุณาเพิ่มบริษัทก่อน (Phase 4)")
    st.stop()

# =========================
# PREP DATA
# =========================
summary = db.groupby("Company")["Score"].mean().reset_index()
summary.rename(columns={"Score": "AvgScore"}, inplace=True)

industry_avg = db.groupby("Industry")["Score"].mean().reset_index()
metric_avg = db.groupby("Metric")["Score"].mean().reset_index()

if summary.empty:
    st.warning("ไม่มีข้อมูลสำหรับสรุป")
    st.stop()

# =========================
# SAFE BEST / WORST
# =========================
best_row = summary.loc[summary["AvgScore"].idxmax()] if not summary["AvgScore"].isna().all() else None
worst_row = summary.loc[summary["AvgScore"].idxmin()] if not summary["AvgScore"].isna().all() else None

best_name = best_row["Company"] if best_row is not None else "-"
worst_name = worst_row["Company"] if worst_row is not None else "-"

# =========================
# KPI
# =========================
st.subheader("Key Metrics")

c1, c2, c3, c4 = st.columns(4)

c1.metric("จำนวนบริษัท", int(summary.shape[0]))
c2.metric("คะแนนเฉลี่ยทั้งหมด", f"{summary['AvgScore'].mean():.1f}")
c3.metric("บริษัทดีที่สุด", best_name)
c4.metric("ต้องปรับปรุง", worst_name)

# =========================
# OVERVIEW CHART
# =========================
st.subheader("Overview")

col1, col2 = st.columns(2)

fig_rank = px.bar(
    summary.sort_values(by="AvgScore", ascending=False),
    x="Company",
    y="AvgScore",
    color="AvgScore",
    title="Company Ranking"
)

fig_rank.update_layout(yaxis_tickformat=".1f")
col1.plotly_chart(fig_rank, use_container_width=True)

if not industry_avg.empty:
    fig_industry = px.bar(
        industry_avg,
        x="Industry",
        y="Score",
        color="Score",
        title="Industry Average"
    )
    fig_industry.update_layout(yaxis_tickformat=".1f")
    col2.plotly_chart(fig_industry, use_container_width=True)

# =========================
# HEATMAP
# =========================
st.subheader("Heatmap (ภาพรวมทุกบริษัท)")

try:
    pivot = db.pivot_table(
        index="Company",
        columns="Metric",
        values="Score",
        aggfunc="mean"
    )

    if not pivot.empty:
        fig_heatmap = px.imshow(
            pivot,
            aspect="auto",
            color_continuous_scale="RdYlGn_r"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

except:
    st.warning("ไม่สามารถสร้าง Heatmap ได้")

# =========================
# GAP ANALYSIS (🔥 เพิ่ม)
# =========================
st.subheader("Gap Analysis (ช่องว่างจากเป้าหมาย)")

benchmark = 3
db["Gap"] = benchmark - db["Score"]

gap_df = db.groupby("Metric")["Gap"].mean().reset_index()

fig_gap = px.bar(
    gap_df.sort_values(by="Gap", ascending=False),
    x="Metric",
    y="Gap",
    color="Gap",
    title="Gap Analysis"
)

fig_gap.update_layout(yaxis_tickformat=".1f")
st.plotly_chart(fig_gap, use_container_width=True)

# =========================
# TOP WEAKNESS
# =========================
st.subheader("Top จุดอ่อนของทั้งระบบ")

if not metric_avg.empty:
    weak = metric_avg.sort_values(by="Score").head(5)

    fig_weak = px.bar(
        weak,
        x="Metric",
        y="Score",
        color="Score",
        title="Top Weak Areas"
    )

    fig_weak.update_layout(yaxis_tickformat=".1f")
    st.plotly_chart(fig_weak, use_container_width=True)

else:
    weak = pd.DataFrame()

# =========================
# DISTRIBUTION
# =========================
st.subheader("Score Distribution")

if "Score" in db.columns and not db["Score"].empty:
    fig_hist = px.histogram(
        db,
        x="Score",
        nbins=5,
        title="Distribution of Scores"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# =========================
# BOX PLOT (🔥 เพิ่ม)
# =========================
st.subheader("Score Variability by Metric")

fig_box = px.box(
    db,
    x="Metric",
    y="Score",
    title="Score Spread"
)

st.plotly_chart(fig_box, use_container_width=True)

# =========================
# COMPARE RADAR (🔥 เพิ่ม)
# =========================
st.subheader("เปรียบเทียบบริษัท (Radar)")

companies = summary["Company"].tolist()
selected = st.multiselect("เลือกบริษัท", companies)

if len(selected) > 0:
    compare_df = db[db["Company"].isin(selected)]

    fig_compare = px.line_polar(
        compare_df,
        r="Score",
        theta="Metric",
        color="Company",
        line_close=True
    )

    fig_compare.update_layout(
        polar=dict(
            radialaxis=dict(tickformat=".1f")
        )
    )

    st.plotly_chart(fig_compare, use_container_width=True)

# =========================
# EXECUTIVE INSIGHT
# =========================
st.subheader("Executive Insight")

avg_score = summary["AvgScore"].mean()

if avg_score >= 3:
    level = "สูง"
elif avg_score >= 2:
    level = "ปานกลาง"
else:
    level = "ต่ำ"

top_weak_text = ", ".join(weak["Metric"].tolist()) if not weak.empty else "-"

st.info(f"""
ภาพรวมองค์กรอยู่ในระดับ {level} (คะแนนเฉลี่ย {avg_score:.1f})

จุดที่ควรพัฒนาเร่งด่วน:
{top_weak_text}

ข้อแนะนำ:
- เพิ่ม Automation ในกระบวนการผลิต
- เชื่อมระบบข้อมูล (Integration)
- พัฒนาทักษะบุคลากร
- วางกลยุทธ์ Industry 4.0 ระยะยาว
""")
