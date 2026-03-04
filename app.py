import streamlit as st
import random
import pandas as pd
import os
from datetime import datetime

# ==========================================
# 1. กำหนดพฤติกรรมตัวละครทั้ง 8 ตัว (เพิ่ม Opportunist)
# ==========================================
def char_always_cooperate(history): return "Cooperate"
def char_always_cheat(history): return "Cheat"
def char_tit_for_tat(history): return "Cooperate" if not history else history[-1]
def char_suspicious_tft(history): return "Cheat" if not history else history[-1]
def char_grudger(history): return "Cheat" if "Cheat" in history else "Cooperate"
def char_tit_for_two_tats(history): 
    return "Cheat" if len(history) >= 2 and history[-1] == "Cheat" and history[-2] == "Cheat" else "Cooperate"
def char_alternator(history): return "Cooperate" if len(history) % 2 == 0 else "Cheat"
def char_opportunist(history): 
    # ถ้านิสิตยอม Cooperate ติดต่อกัน 2 ครั้งล่าสุด แอบแทงข้างหลัง (Cheat) เพื่อฉวยโอกาส
    if len(history) >= 2 and history[-1] == "Cooperate" and history[-2] == "Cooperate":
        return "Cheat"
    # ถ้าไม่ใช่ ให้ทำตัวเหมือนคนเลียนแบบ (Tit-for-Tat)
    return "Cooperate" if not history else history[-1]

CHARACTERS = {
    "Angel (คนใจดี)": char_always_cooperate, 
    "Devil (คนเห็นแก่ตัว)": char_always_cheat, 
    "Copycat (คนเลียนแบบ)": char_tit_for_tat,
    "Skeptic (คนขี้ระแวง)": char_suspicious_tft, 
    "Grudger (คนเจ้าคิดเจ้าแค้น)": char_grudger, 
    "Tolerant (คนใจเย็น)": char_tit_for_two_tats,
    "Alternator (คนโลเล)": char_alternator,
    "Opportunist (นักฉวยโอกาส)": char_opportunist
}
TOTAL_CHARS = len(CHARACTERS) # ตัวแปรเก็บจำนวนตัวละครทั้งหมด (ตอนนี้คือ 8)

# ==========================================
# 2. ฟังก์ชันตรวจสอบการเล่นซ้ำและเตรียม Session
# ==========================================
def check_already_played(student_id):
    if os.path.exists("game_results.csv"):
        df = pd.read_csv("game_results.csv")
        played_ids = df['Student_ID'].astype(str).tolist()
        if str(student_id).strip() in played_ids:
            return True
    return False

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def init_game_session():
    if 'total_rounds' not in st.session_state:
        st.session_state.total_rounds = 0
        st.session_state.player_history = []
        st.session_state.score = 0
        chars = list(CHARACTERS.keys())
        random.shuffle(chars)
        st.session_state.sequence = chars
        st.session_state.game_over = False
        st.session_state.last_result = ""
        st.session_state.saved = False

# ==========================================
# 3. หน้าจอการทำงานหลัก (UI)
# ==========================================
st.title("🎭 Game Theory: The Repeated Game")

# โค้ดสำหรับซ่อนเมนูและแถบด้านบนของ Streamlit
st.markdown("""
    <style>
    .stApp header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ปรับปรุงตาราง Payoff ให้เจ็บปวดขึ้น
with st.expander("📊 ดูตารางผลตอบแทน (Payoff Matrix) กติกาการให้คะแนน", expanded=True):
    st.markdown("""
    | การตัดสินใจ (นิสิต \ คู่แข่ง) | 🤝 คู่แข่งเลือก Cooperate | 🗡️ คู่แข่งเลือก Cheat |
    | :---: | :---: | :---: |
    | **🤝 นิสิตเลือก Cooperate** | **2**, 2 | **-3** , 4 |
    | **🗡️ นิสิตเลือก Cheat** | **4** , -3 | **0** , 0 |
    """)

# --- ส่วนหน้า Login ---
if not st.session_state.logged_in:
    st.subheader("📝 เข้าสู่ระบบเพื่อเริ่มเล่น")
    
    col1, col2 = st.columns(2)
    with col1:
        student_id = st.text_input("รหัสนิสิต (Student ID):")
    with col2:
        student_name = st.text_input("ชื่อ-นามสกุล (Name-Surname):")
        
    high_school = st.text_input("ชื่อโรงเรียนระดับมัธยมศึกษา (เพื่อยืนยันตัวตน):")
        
    if st.button("เริ่มเกม", type="primary", use_container_width=True):
        if student_id.strip() == "" or student_name.strip() == "" or high_school.strip() == "":
            st.error("⚠️ กรุณากรอกข้อมูล รหัสนิสิต ชื่อ-นามสกุล และชื่อโรงเรียนมัธยม ให้ครบถ้วนครับ!")
        elif check_already_played(student_id):
            st.error("❌ นิสิตรหัสนี้ได้ทำการเล่นและบันทึกคะแนนไปแล้ว ไม่สามารถเล่นซ้ำได้ครับ")
        else:
            st.session_state.student_id = student_id
            st.session_state.student_name = student_name
            st.session_state.high_school = high_school
            st.session_state.logged_in = True
            init_game_session()
            st.rerun()
            
    # --- ส่วนจัดการข้อมูลสำหรับอาจารย์ (ป้องกันด้วยรหัสผ่าน) ---
    st.markdown("---")
    with st.expander("🔒 สำหรับอาจารย์ผู้สอน (Instructor Area)"):
        admin_password = st.text_input("ใส่รหัสผ่านเพื่อเข้าถึงข้อมูล:", type="password")
        
        # รหัสผ่านคือ 123456 (คุณสามารถเปลี่ยนตัวเลขนี้ในโค้ดได้เลย)
        if admin_password == st.secrets["admin_password"]: 
            if os.path.exists("game_results.csv"):
                with open("game_results.csv", "rb") as file:
                    st.download_button(
                        label="📥 ดาวน์โหลดผลคะแนนทั้งหมด (CSV)", 
                        data=file, 
                        file_name="game_results.csv", 
                        mime="text/csv"
                    )
                
                st.markdown("<hr>", unsafe_allow_html=True)
                st.warning("⚠️ ระวัง: การกดปุ่มด้านล่างจะลบข้อมูลผลการเล่นของทุกคนทิ้งอย่างถาวร")
                if st.button("🗑️ ล้างข้อมูลทั้งหมด (Reset Data)", type="secondary"):
                    os.remove("game_results.csv")
                    st.success("✅ ลบข้อมูลเก่าทิ้งเรียบร้อยแล้ว!")
                    st.rerun()
            else:
                st.info("📂 ยังไม่มีนิสิตเข้ามาเล่นเกม (ไม่มีข้อมูลให้ดาวน์โหลดหรือลบ)")
        elif admin_password != "":
            st.error("❌ รหัสผ่านไม่ถูกต้อง")

# --- ส่วนหน้าเล่นเกม ---
else:
    if st.session_state.game_over:
        st.success(f"🎉 จบเกมแล้วครับ! ขอบคุณที่ร่วมสนุก")
        st.info(f"**ผู้เล่น:** {st.session_state.student_name} ({st.session_state.student_id})")
        st.metric("คะแนนรวมของคุณคือ", st.session_state.score)
        
        # บันทึกข้อมูลลง CSV
        if not st.session_state.saved:
            file_name = "game_results.csv"
            new_data = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Student_ID": st.session_state.student_id,
                "Name": st.session_state.student_name,
                "High_School": st.session_state.high_school,
                "Total_Score": st.session_state.score,
                "History": ",".join(st.session_state.player_history)
            }])
            
            if os.path.exists(file_name):
                existing_data = pd.read_csv(file_name)
                updated_data = pd.concat([existing_data, new_data], ignore_index=True)
            else:
                updated_data = new_data
                
            updated_data.to_csv(file_name, index=False)
            st.session_state.saved = True
            st.info("✅ ระบบได้บันทึกคะแนนของคุณเรียบร้อยแล้ว สามารถกดปุ่มด้านล่างเพื่อออกจากระบบ")
            
        if st.button("กลับหน้าหลัก (Log out)", type="primary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    else:
        ROUNDS_PER_CHAR = 6
        char_index = st.session_state.total_rounds // ROUNDS_PER_CHAR
        current_char = st.session_state.sequence[char_index]
        current_round_with_char = (st.session_state.total_rounds % ROUNDS_PER_CHAR) + 1

        st.write(f"👤 **ผู้เล่น:** {st.session_state.student_name} ({st.session_state.student_id})")
        st.markdown("---")
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            # ปรับตัวเลข 7 เป็นตัวแปร TOTAL_CHARS อัตโนมัติ
            st.info(f"🎭 **กำลังเผชิญหน้ากับ:**\n\n### ผู้เล่นปริศนาคนที่ {char_index + 1}/{TOTAL_CHARS}")
        with col_info2:
            st.success(f"⚔️ **สถานะการแข่งขัน:**\n\n### รอบที่ {current_round_with_char} / {ROUNDS_PER_CHAR}")
            
        st.progress(current_round_with_char / ROUNDS_PER_CHAR)
        st.markdown("<br>", unsafe_allow_html=True)

        def play(player_choice):
            start_idx = char_index * ROUNDS_PER_CHAR
            history_with_char = st.session_state.player_history[start_idx:]
            bot_choice = CHARACTERS[current_char](history_with_char)
            
            # ปรับปรุงคะแนน Payoff ตามกติกาใหม่
            p_score = 0
            if player_choice == "Cheat" and bot_choice == "Cheat": p_score = 0
            elif player_choice == "Cheat" and bot_choice == "Cooperate": p_score = 4 # ได้ 4 ถ้าหลอกคนดี
            elif player_choice == "Cooperate" and bot_choice == "Cooperate": p_score = 2
            elif player_choice == "Cooperate" and bot_choice == "Cheat": p_score = -3 # เสีย 3 ถ้าโดนหลอก
                
            st.session_state.score += p_score
            st.session_state.player_history.append(player_choice)
            st.session_state.total_rounds += 1
            st.session_state.last_result = f"คุณเลือก **{player_choice}** | คู่แข่งเลือก **{bot_choice}** ➡️ คุณได้คะแนน **{p_score}** แต้ม"
            
            if st.session_state.total_rounds >= TOTAL_CHARS * ROUNDS_PER_CHAR:
                st.session_state.game_over = True

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🤝 เลือก Cooperate (ร่วมมือ)", use_container_width=True):
                play("Cooperate")
                st.rerun()
        with col_btn2:
            if st.button("🗡️ เลือก Cheat (หักหลัง)", use_container_width=True):
                play("Cheat")
                st.rerun()
                
        st.markdown("---")
        if st.session_state.last_result:
            st.warning(st.session_state.last_result)
            
        st.metric("🏆 คะแนนสะสมของคุณตอนนี้", st.session_state.score)
