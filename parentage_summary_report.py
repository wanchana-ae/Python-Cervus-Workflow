import pandas as pd

# 1. ตั้งค่าชื่อไฟล์และตัวแปร
input_filename = 'Data_readt_to_use_add_fam.csv'   # ชื่อไฟล์ข้อมูลของคุณ
output_filename = 'parentage_summary_report.csv' # ชื่อไฟล์ผลลัพธ์ที่จะสร้างขึ้น
TOLERANCE = 2.0  # ค่าความคลาดเคลื่อน +- ที่ยอมรับได้

def analyze_parentage():
    # 2. อ่านไฟล์ข้อมูล
    try:
        df = pd.read_csv(input_filename)
        # ลบช่องว่างที่อาจแอบซ่อนอยู่ในชื่อคอลัมน์
        df.columns = df.columns.str.strip()
    except FileNotFoundError:
        print(f"❌ ไม่พบไฟล์ชื่อ '{input_filename}' กรุณาตรวจสอบชื่อไฟล์ครับ")
        return

    # ตรวจสอบคอลัมน์สำคัญว่ามีครบไหม
    required_cols = ['Fam_ID', 'Membership', 'ID']
    for col in required_cols:
        if col not in df.columns:
            print(f"❌ ไฟล์ CSV ของคุณต้องมีคอลัมน์ชื่อ '{col}' ครับ")
            return

    # 3. ค้นหาคอลัมน์ Marker อัตโนมัติ (หาคอลัมน์ที่ลงท้ายด้วย _1 หรือ _2)
    marker_cols = [c for c in df.columns if c.endswith('_1') or c.endswith('_2')]
    markers = list(set([c.rsplit('_', 1)[0] for c in marker_cols]))
    print(f"🔍 พบ Marker ทั้งหมด {len(markers)} ตัว ได้แก่: {', '.join(markers)}\n")

    results = []

    # 4. วนลูปวิเคราะห์ทีละครอบครัว (Fam_ID)
    families = df['Fam_ID'].dropna().unique()
    
    for fam in families:
        fam_df = df[df['Fam_ID'] == fam]
        
        # แยกตัวลูก (C) กับ ตัวพ่อ/แม่ (F, M) ออกจากกัน
        offspring_rows = fam_df[fam_df['Membership'] == 'C']
        parent_rows = fam_df[fam_df['Membership'].isin(['F', 'M'])]
        
        # นำลูกแต่ละตัว ไปเทียบกับพ่อ/แม่ ในครอบครัวเดียวกัน
        for _, o_row in offspring_rows.iterrows():
            for _, p_row in parent_rows.iterrows():
                
                pass_count = 0
                fail_count = 0
                failed_markers_list = []
                
                # ตรวจสอบทีละ Marker
                for marker in markers:
                    o1, o2 = o_row[f"{marker}_1"], o_row[f"{marker}_2"]
                    p1, p2 = p_row[f"{marker}_1"], p_row[f"{marker}_2"]
                    
                    # ข้าม Marker นี้ถ้าข้อมูลแหว่ง (Missing data) หรือมีค่าเป็น 0
                    if pd.isna(o1) or pd.isna(p1) or o1 == 0 or p1 == 0:
                        continue
                        
                    o_alleles = [o1, o2]
                    p_alleles = [p1, p2]
                    
                    # เช็คว่าลูกมีอัลลีลอย่างน้อย 1 ตัว ที่ตรงกับพ่อ/แม่ ในช่วง +- TOLERANCE หรือไม่
                    is_match = False
                    for o in o_alleles:
                        for p in p_alleles:
                            if abs(o - p) <= TOLERANCE:
                                is_match = True
                                break
                        if is_match:
                            break
                            
                    if is_match:
                        pass_count += 1
                    else:
                        fail_count += 1
                        failed_markers_list.append(marker)
                
                # สรุปผลคู่นี้
                total_checked = pass_count + fail_count
                match_percent = (pass_count / total_checked * 100) if total_checked > 0 else 0
                
                # กำหนดสถานะ: ถ้ามี fail แม้แต่ 1 ตำแหน่ง จะถือว่า Mismatch
                status = "✅ Pass" if fail_count == 0 else f"❌ Mismatch ({fail_count})"
                
                # แปลงรหัส Membership ให้เข้าใจง่ายขึ้นในรีพอร์ต
                parent_role = "พ่อ (F)" if p_row['Membership'] == 'F' else "แม่ (M)"
                
                results.append({
                    'Fam_ID': fam,
                    'Offspring_ID': o_row['ID'],
                    'Parent_ID': p_row['ID'],
                    'Parent_Type': parent_role,
                    'Total_Checked': total_checked,
                    'Passed': pass_count,
                    'Failed': fail_count,
                    'Match_%': f"{match_percent:.1f}%",
                    'Failed_Markers': ", ".join(failed_markers_list) if failed_markers_list else "-",
                    'Status': status
                })

    # 5. สรุปผลออกมาเป็นตารางและบันทึกเป็นไฟล์
    if results:
        report_df = pd.DataFrame(results)
        print("--- ตัวอย่างผลการวิเคราะห์ (10 รายการแรก) ---")
        print(report_df[['Fam_ID', 'Offspring_ID', 'Parent_ID', 'Parent_Type', 'Passed', 'Failed', 'Status']].head(10).to_string(index=False))
        
        # บันทึกเป็นไฟล์ CSV (รองรับภาษาไทย)
        report_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
        
        print(f"\n✅ ตรวจสอบครอบครัวทั้งหมด: {len(families)} ครอบครัว")
        print(f"✅ ตรวจสอบคู่สายเลือดทั้งหมด: {len(report_df)} คู่")
        print(f"🎉 [สำเร็จ] บันทึกรายงานสรุปผลลงในไฟล์ '{output_filename}' เรียบร้อยแล้วครับ!")
    else:
        print("\n⚠️ ไม่พบข้อมูลที่เข้าคู่กันได้ กรุณาตรวจสอบคอลัมน์ Membership ว่ามี C, F, M หรือไม่")

# สั่งรันฟังก์ชัน
analyze_parentage()