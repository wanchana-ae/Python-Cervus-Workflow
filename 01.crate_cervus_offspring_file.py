import pandas as pd

# 1. อ่านข้อมูลเดิม
df = pd.read_csv('Data_ready_to_use_add_fam.csv')
df.columns = df.columns.str.strip()

# 2. ดึง ID ของแม่วัวทั้งหมด (Membership == 'M')
candidate_mothers = df[df['Membership'] == 'M']['ID'].unique()

# 3. ดึง ID ของพ่อวัวทั้งหมด (Membership == 'F')
candidate_fathers = df[df['Membership'] == 'F']['ID'].unique()

# 4. บันทึกเป็นไฟล์สำหรับ Cervus (ไม่มี Header)
pd.Series(candidate_mothers).to_csv('Candidate_Mothers.txt', index=False, header=False)
pd.Series(candidate_fathers).to_csv('Candidate_Fathers.txt', index=False, header=False)

print(f"✅ สร้างไฟล์ Candidate_Mothers.txt (จำนวน {len(candidate_mothers)} ตัว)")
print(f"✅ สร้างไฟล์ Candidate_Fathers.txt (จำนวน {len(candidate_fathers)} ตัว)")
