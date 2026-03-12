import pandas as pd
import numpy as np

# 1. โหลดและเตรียมข้อมูล
input_file = 'Data_readt_to_use_add_fam.csv'
try:
    df = pd.read_csv(input_file)
except FileNotFoundError:
    print(f"ไม่พบไฟล์: {input_file}")
    exit()

df.columns = df.columns.str.strip()

# รายชื่อ Marker
marker_cols = [c for c in df.columns if c.endswith('_1') or c.endswith('_2')]
markers = sorted(list(set([c.rsplit('_', 1)[0] for c in marker_cols])))

def calculate_exclusion_power(df, markers):
    combined_pne = 1.0  # Probability of Non-Exclusion (โอกาสที่แยกไม่ออก)
    results = []

    for m in markers:
        # รวมอัลลีลทั้งหมดในประชากรเพื่อหาความถี่ (pi)
        alleles = pd.concat([df[f"{m}_1"], df[f"{m}_2"]]).dropna().round().astype(int)
        
        if len(alleles) == 0:
            continue
            
        freqs = alleles.value_counts() / alleles.count()
        p = freqs.values
        
        # สูตร PE สำหรับ Trio (Jamieson & Taylor, 1997)
        # PE = 1 - 4Σpi² + 2(Σpi²)² + 4Σpi³ - 3Σpi⁴
        s2, s3, s4 = np.sum(p**2), np.sum(p**3), np.sum(p**4)
        pe = 1 - 4*s2 + 2*(s2**2) + 4*s3 - 3*s4
        
        # เก็บค่า PNE (1-PE) เพื่อนำไปคูณสะสม
        pne = 1 - pe
        combined_pne *= pne
        
        results.append({
            'Marker': m, 
            'Power_of_Exclusion_PE': round(pe, 6),
            'Prob_Non_Exclusion_PNE': round(pne, 6)
        })

    return pd.DataFrame(results), combined_pne

# ประมวลผล
pe_df, final_false_inclusion = calculate_exclusion_power(df, markers)
accuracy = (1 - final_false_inclusion) * 100

# --- การบันทึกข้อมูลเป็น CSV ---

# 1. บันทึกค่า PE ราย Marker
pe_df.to_csv('marker_exclusion_report.csv', index=False, encoding='utf-8-sig')

# 2. บันทึกสรุปภาพรวม
summary_data = {
    'Metric': ['Combined False Inclusion (PNE)', 'Accuracy (%)'],
    'Value': [f"{final_false_inclusion:.10f}", f"{accuracy:.5f}"]
}
df_summary = pd.DataFrame(summary_data)
df_summary.to_csv('false_inclusion_summary.csv', index=False, encoding='utf-8-sig')

# --- แสดงผลทางหน้าจอ ---
print("วิเคราะห์และบันทึกข้อมูลเรียบร้อยแล้ว!")
print("-" * 50)
print(f"โอกาสเกิด False Inclusion (รวม 11 Markers): {final_false_inclusion:.10f}")
print(f"คิดเป็นความแม่นยำ: {accuracy:.5f}%")
print("-" * 50)
print("ไฟล์ที่สร้าง: 'marker_exclusion_report.csv' และ 'false_inclusion_summary.csv'")
