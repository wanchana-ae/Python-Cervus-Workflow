import pandas as pd
import numpy as np

# 1. โหลดข้อมูลเดิมของคุณ
df = pd.read_csv('Data_ready_to_use_add_fam.csv')
df.columns = df.columns.str.strip()

# ระบุรายชื่อ Marker
marker_cols = [c for c in df.columns if c.endswith('_1') or c.endswith('_2')]
markers = sorted(list(set([c.rsplit('_', 1)[0] for c in marker_cols])))

# 2. ขั้นตอนการทำ Binning (แปลงทศนิยมเป็นจำนวนเต็ม)
df_binned = df.copy()
tolerance = 1.5

for marker in markers:
    cols = [f"{marker}_1", f"{marker}_2"]
    all_vals = pd.concat([df[cols[0]], df[cols[1]]]).dropna().sort_values().values
    
    if len(all_vals) == 0: continue
        
    clusters = []
    current_cluster = [all_vals[0]]
    for val in all_vals[1:]:
        if val - current_cluster[0] <= tolerance:
            current_cluster.append(val)
        else:
            clusters.append(current_cluster)
            current_cluster = [val]
    clusters.append(current_cluster)
    
    mapping = {val: int(round(np.mean(cluster))) for cluster in clusters for val in cluster}
    df_binned[cols[0]] = df_binned[cols[0]].map(mapping)
    df_binned[cols[1]] = df_binned[cols[1]].map(mapping)

# 3. สร้างไฟล์ Genotypes สำหรับ Cervus
cervus_genotypes = df_binned[['ID'] + marker_cols].copy()
cervus_genotypes[marker_cols] = cervus_genotypes[marker_cols].fillna(0).astype(int)
cervus_genotypes.to_csv('Cervus_Genotypes.csv', index=False)

# 4. สร้างไฟล์ความสัมพันธ์แม่-ลูก (Offspring File)
offspring_data = []
for fam in df['Fam_ID'].unique():
    fam_subset = df[df['Fam_ID'] == fam]
    children = fam_subset[fam_subset['Membership'] == 'C']['ID'].tolist()
    mother = fam_subset[fam_subset['Membership'] == 'M']['ID'].tolist()
    for c in children:
        offspring_data.append({'Offspring_ID': c, 'Known_Mother_ID': mother[0] if mother else "0"})

pd.DataFrame(offspring_data).to_csv('Cervus_Offspring_File.csv', index=False)

print("✅ สร้างไฟล์ 'Cervus_Genotypes.csv' และ 'Cervus_Offspring_File.csv' เรียบร้อย!")
