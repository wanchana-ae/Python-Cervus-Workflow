import pandas as pd
import numpy as np

# 1. โหลดและเตรียมข้อมูล
df = pd.read_csv('Data_readt_to_use_add_fam.csv')
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
        freqs = alleles.value_counts() / alleles.count()
        p = freqs.values
        
        # สูตร PE สำหรับ Trio (Jamieson & Taylor, 1997)
        s2, s3, s4 = np.sum(p**2), np.sum(p**3), np.sum(p**4)
        pe = 1 - 4*s2 + 2*(s2**2) + 4*s3 - 3*s4
        
        # เก็บค่า PNE (1-PE) เพื่อนำไปคูณสะสม
        pne = 1 - pe
        combined_pne *= pne
        
        results.append({'Marker': m, 'PE': pe})

    return pd.DataFrame(results), combined_pne

# ประมวลผล
pe_df, final_false_inclusion = calculate_exclusion_power(df, markers)

print(f"โอกาสเกิด False Inclusion (รวม 11 Markers): {final_false_inclusion:.10f}")
print(f"คิดเป็นความแม่นยำ: {(1 - final_false_inclusion)*100:.5f}%")
