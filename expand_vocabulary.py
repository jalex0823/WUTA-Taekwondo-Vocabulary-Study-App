import json

# Load current terms
with open('/Users/jalex0823/Documents/GitHub/WUTA-Taekwondo-Vocabulary-Study-App/data/terms.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Define moves and positions for each belt level
moves_by_belt = {
    "white": [
        {"id": "ap_kubi", "hangul": "앞굽이", "romanization": "ap kubi", "english": "Front Stance", "category": "Stance"},
        {"id": "juchum_seogi", "hangul": "주춤서기", "romanization": "juchum seogi", "english": "Walking Stance", "category": "Stance"},
        {"id": "arae_makgi", "hangul": "아래막기", "romanization": "arae makgi", "english": "Low Block", "category": "Block"},
        {"id": "momtong_makgi", "hangul": "몸통막기", "romanization": "momtong makgi", "english": "Middle Block", "category": "Block"},
        {"id": "ap_chagi", "hangul": "앞차기", "romanization": "ap chagi", "english": "Front Kick", "category": "Kick"},
    ],
    "white_black_tip": [
        {"id": "momtong_jireugi", "hangul": "몸통지르기", "romanization": "momtong jireugi", "english": "Middle Punch", "category": "Strike"},
        {"id": "eolgul_makgi", "hangul": "얼굴막기", "romanization": "eolgul makgi", "english": "High Block", "category": "Block"},
        {"id": "pyojeok_jireugi", "hangul": "표적지르기", "romanization": "pyojeok jireugi", "english": "Target Punch", "category": "Strike"},
        {"id": "juchum_ap_chagi", "hangul": "주춤앞차기", "romanization": "juchum ap chagi", "english": "Walking Stance Front Kick", "category": "Kick"},
    ],
    "yellow": [
        {"id": "yeop_seogi", "hangul": "옆서기", "romanization": "yeop seogi", "english": "Side Stance", "category": "Stance"},
        {"id": "sonnal_mokchigi", "hangul": "손날목치기", "romanization": "sonnal mokchigi", "english": "Knife Hand Strike", "category": "Strike"},
        {"id": "yeop_chagi", "hangul": "옆차기", "romanization": "yeop chagi", "english": "Side Kick", "category": "Kick"},
        {"id": "batangson_makgi", "hangul": "바탕손막기", "romanization": "batangson makgi", "english": "Palm Block", "category": "Block"},
        {"id": "taeguk_1_jang", "hangul": "태극1장", "romanization": "Taegeuk 1 Jang", "english": "Taegeuk Form 1", "category": "Form"},
    ],
    "yellow_black_tip": [
        {"id": "dwi_kubi", "hangul": "뒤굽이", "romanization": "dwi kubi", "english": "Back Stance", "category": "Stance"},
        {"id": "sonnal_makgi", "hangul": "손날막기", "romanization": "sonnal makgi", "english": "Knife Hand Block", "category": "Block"},
        {"id": "dolgae_chagi", "hangul": "돌개차기", "romanization": "dolgae chagi", "english": "Roundhouse Kick", "category": "Kick"},
        {"id": "dubeon_jireugi", "hangul": "두번지르기", "romanization": "dubeon jireugi", "english": "Double Punch", "category": "Strike"},
    ],
    "orange": [
        {"id": "beom_seogi", "hangul": "범서기", "romanization": "beom seogi", "english": "Tiger Stance", "category": "Stance"},
        {"id": "biteureo_makgi", "hangul": "비틀어막기", "romanization": "biteureo makgi", "english": "Twisting Block", "category": "Block"},
        {"id": "naeryo_chagi", "hangul": "내려차기", "romanization": "naeryo chagi", "english": "Axe Kick", "category": "Kick"},
        {"id": "jipge_sonkkeut", "hangul": "집게손끝", "romanization": "jipge sonkkeut", "english": "Spear Hand", "category": "Strike"},
        {"id": "taeguk_2_jang", "hangul": "태극2장", "romanization": "Taegeuk 2 Jang", "english": "Taegeuk Form 2", "category": "Form"},
    ],
    "orange_black_tip": [
        {"id": "hakdari_seogi", "hangul": "학다리서기", "romanization": "hakdari seogi", "english": "Crane Stance", "category": "Stance"},
        {"id": "palkup_chigi", "hangul": "팔굽치기", "romanization": "palkup chigi", "english": "Elbow Strike", "category": "Strike"},
        {"id": "dwi_chagi", "hangul": "뒤차기", "romanization": "dwi chagi", "english": "Back Kick", "category": "Kick"},
        {"id": "geodeur_makgi", "hangul": "걷어막기", "romanization": "geodeur makgi", "english": "Scooping Block", "category": "Block"},
    ],
    "green": [
        {"id": "juchumbal_seogi", "hangul": "주춤발서기", "romanization": "juchumbal seogi", "english": "Diagonal Stance", "category": "Stance"},
        {"id": "godeureo_chagi", "hangul": "고들어차기", "romanization": "godeureo chagi", "english": "Hook Kick", "category": "Kick"},
        {"id": "deung_jumeok", "hangul": "등주먹", "romanization": "deung jumeok", "english": "Backfist Strike", "category": "Strike"},
        {"id": "hecheo_makgi", "hangul": "헤쳐막기", "romanization": "hecheo makgi", "english": "Wedge Block", "category": "Block"},
        {"id": "taeguk_3_jang", "hangul": "태극3장", "romanization": "Taegeuk 3 Jang", "english": "Taegeuk Form 3", "category": "Form"},
    ],
    "green_black_tip": [
        {"id": "mal_seogi", "hangul": "말서기", "romanization": "mal seogi", "english": "Horse Stance", "category": "Stance"},
        {"id": "momdollyo_chagi", "hangul": "몸돌려차기", "romanization": "momdollyo chagi", "english": "Spinning Hook Kick", "category": "Kick"},
        {"id": "sudo_mokchigi", "hangul": "수도목치기", "romanization": "sudo mokchigi", "english": "Knife Hand Strike to Neck", "category": "Strike"},
        {"id": "sonbadak_makgi", "hangul": "손바닥막기", "romanization": "sonbadak makgi", "english": "Palm Heel Block", "category": "Block"},
    ],
    "blue": [
        {"id": "goa_seogi", "hangul": "꼬아서기", "romanization": "goa seogi", "english": "Cross Stance", "category": "Stance"},
        {"id": "meori_wiro_chagi", "hangul": "머리위로차기", "romanization": "meori wiro chagi", "english": "Jumping Front Kick", "category": "Kick"},
        {"id": "pyonsonkeut_tzireugi", "hangul": "편손끝찌르기", "romanization": "pyonsonkeut tzireugi", "english": "Flat Finger Thrust", "category": "Strike"},
        {"id": "dung_jumeok_chigi", "hangul": "등주먹치기", "romanization": "dung jumeok chigi", "english": "Backfist Strike", "category": "Strike"},
        {"id": "taeguk_4_jang", "hangul": "태극4장", "romanization": "Taegeuk 4 Jang", "english": "Taegeuk Form 4", "category": "Form"},
    ],
    "blue_black_tip": [
        {"id": "bam_seogi", "hangul": "밤서기", "romanization": "bam seogi", "english": "Cat Stance", "category": "Stance"},
        {"id": "momdollyo_yeop_chagi", "hangul": "몸돌려옆차기", "romanization": "momdollyo yeop chagi", "english": "Spinning Side Kick", "category": "Kick"},
        {"id": "mejumeok_chigi", "hangul": "메주먹치기", "romanization": "mejumeok chigi", "english": "Hammer Fist", "category": "Strike"},
        {"id": "batangson_yeop_makgi", "hangul": "바탕손옆막기", "romanization": "batangson yeop makgi", "english": "Palm Heel Side Block", "category": "Block"},
    ],
    "purple": [
        {"id": "ap_seogi", "hangul": "앞서기", "romanization": "ap seogi", "english": "Forward Stance", "category": "Stance"},
        {"id": "twieo_yeop_chagi", "hangul": "뛰어옆차기", "romanization": "twieo yeop chagi", "english": "Jumping Side Kick", "category": "Kick"},
        {"id": "sonnal_deung_chigi", "hangul": "손날등치기", "romanization": "sonnal deung chigi", "english": "Reverse Knife Hand Strike", "category": "Strike"},
        {"id": "oe_santeul_makgi", "hangul": "외산틀막기", "romanization": "oe santeul makgi", "english": "Outside Forearm Block", "category": "Block"},
        {"id": "taeguk_5_jang", "hangul": "태극5장", "romanization": "Taegeuk 5 Jang", "english": "Taegeuk Form 5", "category": "Form"},
    ],
    "purple_black_tip": [
        {"id": "moa_seogi", "hangul": "모아서기", "romanization": "moa seogi", "english": "Closed Stance", "category": "Stance"},
        {"id": "momdollyo_naeryo_chagi", "hangul": "몸돌려내려차기", "romanization": "momdollyo naeryo chagi", "english": "Spinning Axe Kick", "category": "Kick"},
        {"id": "palkup_dollyo_chigi", "hangul": "팔굽돌려치기", "romanization": "palkup dollyo chigi", "english": "Spinning Elbow Strike", "category": "Strike"},
        {"id": "gawi_makgi", "hangul": "가위막기", "romanization": "gawi makgi", "english": "Scissors Block", "category": "Block"},
    ],
    "brown": [
        {"id": "ogeum_seogi", "hangul": "오금서기", "romanization": "ogeum seogi", "english": "Crouching Stance", "category": "Stance"},
        {"id": "twieo_momdollyo_chagi", "hangul": "뛰어몸돌려차기", "romanization": "twieo momdollyo chagi", "english": "Jumping Spinning Kick", "category": "Kick"},
        {"id": "agwison_jireugi", "hangul": "아귀손지르기", "romanization": "agwison jireugi", "english": "Arc Hand Strike", "category": "Strike"},
        {"id": "doo_palmok_makgi", "hangul": "두팔목막기", "romanization": "doo palmok makgi", "english": "Double Forearm Block", "category": "Block"},
        {"id": "taeguk_6_jang", "hangul": "태극6장", "romanization": "Taegeuk 6 Jang", "english": "Taegeuk Form 6", "category": "Form"},
    ],
    "brown_black_tip": [
        {"id": "naranhi_seogi", "hangul": "나란히서기", "romanization": "naranhi seogi", "english": "Parallel Stance", "category": "Stance"},
        {"id": "ieo_chagi", "hangul": "이어차기", "romanization": "ieo chagi", "english": "Double Kick", "category": "Kick"},
        {"id": "mejumeok_naeryo_chigi", "hangul": "메주먹내려치기", "romanization": "mejumeok naeryo chigi", "english": "Downward Hammer Fist", "category": "Strike"},
        {"id": "noollo_makgi", "hangul": "눌러막기", "romanization": "noollo makgi", "english": "Pressing Block", "category": "Block"},
    ],
    "red": [
        {"id": "gyotdari_seogi", "hangul": "겹다리서기", "romanization": "gyotdari seogi", "english": "Cross-Leg Stance", "category": "Stance"},
        {"id": "540_dolyo_chagi", "hangul": "540돌려차기", "romanization": "540 dolyo chagi", "english": "540 Degree Kick", "category": "Kick"},
        {"id": "pyon_jumeok_jireugi", "hangul": "편주먹지르기", "romanization": "pyon jumeok jireugi", "english": "Flat Fist Punch", "category": "Strike"},
        {"id": "danggyeo_makgi", "hangul": "당겨막기", "romanization": "danggyeo makgi", "english": "Pulling Block", "category": "Block"},
        {"id": "taeguk_7_jang", "hangul": "태극7장", "romanization": "Taegeuk 7 Jang", "english": "Taegeuk Form 7", "category": "Form"},
        {"id": "samjae_chagi", "hangul": "삼재차기", "romanization": "samjae chagi", "english": "Triple Kick Combination", "category": "Kick"},
    ],
    "red_black_tip": [
        {"id": "poom_seogi", "hangul": "품서기", "romanization": "poom seogi", "english": "Attention Stance with Fists", "category": "Stance"},
        {"id": "twieo_dwi_chagi", "hangul": "뛰어뒤차기", "romanization": "twieo dwi chagi", "english": "Jumping Back Kick", "category": "Kick"},
        {"id": "mureup_chigi", "hangul": "무릎치기", "romanization": "mureup chigi", "english": "Knee Strike", "category": "Strike"},
        {"id": " geodeur_chagi", "hangul": "걷어차기", "romanization": "geodeur chagi", "english": "Crescent Kick", "category": "Kick"},
        {"id": "taeguk_8_jang", "hangul": "태극8장", "romanization": "Taegeuk 8 Jang", "english": "Taegeuk Form 8", "category": "Form"},
    ],
    "black": [
        {"id": "jaebi_poom_seogi", "hangul": "제비품서기", "romanization": "jaebi poom seogi", "english": "Swallow Stance", "category": "Stance"},
        {"id": "twieo_540_chagi", "hangul": "뛰어540차기", "romanization": "twieo 540 chagi", "english": "Jumping 540 Kick", "category": "Kick"},
        {"id": "batang_jumeok", "hangul": "바탕주먹", "romanization": "batang jumeok", "english": "Bottom Fist", "category": "Strike"},
        {"id": "hanseonuro_makgi", "hangul": "한선으로막기", "romanization": "hanseonuro makgi", "english": "Single Line Block", "category": "Block"},
        {"id": "koryo_poomsae", "hangul": "고려품새", "romanization": "Koryo Poomsae", "english": "Koryo Form", "category": "Form"},
        {"id": "yeonsu_chagi", "hangul": "연수차기", "romanization": "yeonsu chagi", "english": "Consecutive Kick Drill", "category": "Kick"},
        {"id": "jabeu_makgi", "hangul": "잡어막기", "romanization": "jabeu makgi", "english": "Grabbing Block", "category": "Block"},
    ],
}

# Add moves to each belt
for belt in data['belts']:
    belt_id = belt['belt_id']
    if belt_id in moves_by_belt:
        # Add the new terms to existing terms
        belt['terms'].extend(moves_by_belt[belt_id])
        print(f"Added {len(moves_by_belt[belt_id])} moves/positions to {belt['belt_name']}")

# Save updated data
with open('/Users/jalex0823/Documents/GitHub/WUTA-Taekwondo-Vocabulary-Study-App/data/terms.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("\n✅ Successfully expanded vocabulary with moves and positions!")
print(f"Total belt levels: {len(data['belts'])}")

# Count total terms
total_terms = sum(len(belt['terms']) for belt in data['belts'])
print(f"Total terms now: {total_terms}")
