import pandas as pd

# 1. ตั้งค่าพื้นฐาน
input_file = 'Data_readt_to_use_add_fam.csv'  # เปลี่ยนเป็นชื่อไฟล์ของคุณ
TOLERANCE = 2.0  # เกณฑ์ความคลาดเคลื่อน +- 2

def calculate_detailed_errors(file_path):
    # อ่านไฟล์และลบช่องว่างในชื่อคอลัมน์
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    
    # ค้นหารายชื่อ Marker ทั้งหมด
    marker_cols = [c for c in df.columns if c.endswith('_1') or c.endswith('_2')]
    markers = sorted(list(set([c.rsplit('_', 1)[0] for c in marker_cols])))
    
    # ตัวแปรสำหรับเก็บสถิติ
    marker_err_counts = {m: 0 for m in markers}
    marker_valid_counts = {m: 0 for m in markers}
    family_mismatch_count = 0
    total_trios = 0
    
    # วนลูปตรวจสอบทีละครอบครัว (Fam_ID)
    families = df['Fam_ID'].unique()
    
    for fam in families:
        fam_df = df[df['Fam_ID'] == fam]
        child = fam_df[fam_df['Membership'] == 'C']
        father = fam_df[fam_df['Membership'] == 'F']
        mother = fam_df[fam_df['Membership'] == 'M']
        
        # ตรวจสอบเฉพาะครอบครัวที่มีข้อมูลครบ พ่อ-แม่-ลูก
        if child.empty or father.empty or mother.empty:
            continue
            
        total_trios += 1
        c_row, f_row, m_row = child.iloc[0], father.iloc[0], mother.iloc[0]
        
        any_marker_failed = False
        
        for m in markers:
            c_alleles = [c_row[f"{m}_1"], c_row[f"{m}_2"]]
            f_alleles = [f_row[f"{m}_1"], f_row[f"{m}_2"]]
            m_alleles = [m_row[f"{m}_1"], m_row[f"{m}_2"]]
            
            # ข้ามหากข้อมูลใน Marker นั้นไม่ครบ
            if any(pd.isna(c_alleles + f_alleles + m_alleles)):
                continue
            
            marker_valid_counts[m] += 1
            
            # ตรวจสอบกฎเมนเดล (ลูกต้องตรงกับพ่ออย่างน้อย 1 และแม่ 1 ภายในช่วง +-2)
            p_match = any(abs(c - f) <= TOLERANCE for c in c_alleles for f in f_alleles)
            m_match = any(abs(c - mo) <= TOLERANCE for c in c_alleles for mo in m_alleles)
            
            if not p_match or not m_match:
                marker_err_counts[m] += 1
                any_marker_failed = True
        
        # ถ้าใน 11 markers มีพลาดแม้แต่ที่เดียว ให้ถือว่าครอบครัวนี้เกิด Mismatch
        if any_marker_failed:
            family_mismatch_count += 1
            
    # --- สรุปผล ---
    print(f"สรุปการวิเคราะห์จากทั้งหมด {total_trios} ครอบครัว (พ่อ-แม่-ลูก)")
    print("-" * 50)
    print(f"{'Marker':<12} | {'Error Rate (%)':<15}")
    print("-" * 50)
    
    for m in markers:
        rate = (marker_err_counts[m] / marker_valid_counts[m] * 100)
        print(f"{m:<12} | {rate:>10.2f}%")
        
    overall_rate = (family_mismatch_count / total_trios * 100)
    print("-" * 50)
    print(f"โอกาสที่จะเกิด Mismatch อย่างน้อย 1 จุด (Combined 11 Markers): {overall_rate:.2f}%")
    print(f"จำนวนครอบครัวที่พบปัญหา: {family_mismatch_count} จาก {total_trios} ครอบครัว")

# รันโปรแกรม
calculate_detailed_errors(input_file)
