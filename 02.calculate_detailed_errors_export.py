import pandas as pd

# 1. ตั้งค่าพื้นฐาน
input_file = 'Data_readt_to_use_add_fam.csv'  # เปลี่ยนเป็นชื่อไฟล์ของคุณ
TOLERANCE = 2.0  # เกณฑ์ความคลาดเคลื่อน +- 2

def calculate_detailed_errors(file_path):
    # อ่านไฟล์และลบช่องว่างในชื่อคอลัมน์
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"ไม่พบไฟล์: {file_path}")
        return
        
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
        
        if any_marker_failed:
            family_mismatch_count += 1
            
    # --- เตรียมข้อมูลสำหรับ Save เป็น CSV ---
    
    # 1. ข้อมูลราย Marker
    marker_results = []
    for m in markers:
        valid = marker_valid_counts[m]
        err = marker_err_counts[m]
        rate = (err / valid * 100) if valid > 0 else 0
        marker_results.append({
            'Marker': m,
            'Valid_Trios': valid,
            'Error_Count': err,
            'Error_Rate_Percent': round(rate, 2)
        })
    
    df_marker_report = pd.DataFrame(marker_results)
    df_marker_report.to_csv('marker_error_report.csv', index=False, encoding='utf-8-sig')
    
    # 2. ข้อมูลสรุปภาพรวม
    overall_rate = (family_mismatch_count / total_trios * 100) if total_trios > 0 else 0
    summary_data = {
        'Total_Trios': [total_trios],
        'Mismatch_Families': [family_mismatch_count],
        'Overall_Mismatch_Rate_Percent': [round(overall_rate, 2)]
    }
    df_summary = pd.DataFrame(summary_data)
    df_summary.to_csv('overall_summary.csv', index=False, encoding='utf-8-sig')

    # --- สรุปผลทางหน้าจอ (Print) ---
    print(f"วิเคราะห์เสร็จสิ้น! บันทึกไฟล์ CSV เรียบร้อยแล้ว")
    print("-" * 50)
    print(df_marker_report.to_string(index=False))
    print("-" * 50)
    print(f"Combined Mismatch Rate: {overall_rate:.2f}%")
    print(f"บันทึกไฟล์: 'marker_error_report.csv' และ 'overall_summary.csv'")

# รันโปรแกรม
calculate_detailed_errors(input_file)
