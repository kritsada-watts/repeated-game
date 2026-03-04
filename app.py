import streamlit as st
import random
import pandas as pd
import os
from datetime import datetime

# ==========================================
# 1. กำหนดพฤติกรรมตัวละครทั้ง 7 ตัว
# ==========================================
def char_always_cooperate(history): return "Cooperate"
def char_always_cheat(history): return "Cheat"
def char_tit_for_tat(history): return "Cooperate" if not history else history[-1]
def char_suspicious_tft(history): return "Cheat" if not history else history[-1]
def char_grudger(history): return "Cheat" if "Cheat" in history else "Cooperate"
def char_tit_for_two_tats(history): 
    return "Cheat" if len(history) >= 2 and history[-1] == "Cheat" and history[-2] == "Cheat" else "Cooperate"
def char_alternator(history): return "Cooperate" if len(history) % 2 == 0 else "Cheat"

CHARACTERS = {
    "Angel (คนใจดี)": char_always_cooperate, "Devil (คนเห็นแก่ตัว)": char_always_cheat, "Copycat (คนเลียนแบบ)": char_tit_for_tat,
    "Skeptic (คนขี้ระแวง)": char_suspicious_tft, "Grudger (คนเจ้าคิดเจ้าแค้น)": char_grudger, "Tolerant (คนใจเย็น)": char_tit_for_two_tats,
    "Alternator (คนโลเล)": char_alternator
}

# ==========================================
# 2. ฟังก์ชันตรวจสอบการเล่นซ้ำและเตรียม Session
# ==========================================
def check_already_played(student_id):
    if os.path.exists("game_results.csv"):
        df = pd.read_csv("game_results.csv")
        # แปลงเป็น string เพื่อป้องกันปัญหาตอนเทียบข้อมูล
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

# --- แสดง Payoff Matrix ให้นิสิตดูเป็นกติกา ---
with st.expander("📊 ดูตารางผลตอบแทน (Payoff Matrix) กติกาการให้คะแนน", expanded=True):
    st.markdown("""
    | การตัดสินใจ (คุณ \ คู่แข่ง) | 🤝 คู่แข่งเลือก Cooperate | 🗡️ คู่แข่งเลือก Cheat |
    | :--- | :--- | :--- |
    | **🤝 คุณเลือก Cooperate** | คุณได้ **2** , คู่แข่งได้ 2 | คุณเสีย **-1** , คู่แข่งได้ 3 |
    | **🗡️ คุณเลือก Cheat** | คุณได้ **3** , คู่แข่งเสีย -1 | คุณได้ **0** , คู่แข่งได้ 0 |
    """)

# --- ส่วนหน้า Login ---
if not st.session_state.logged_in:
    st.subheader("📝 เข้าสู่ระบบเพื่อเริ่มเล่น")
    
    col1, col2 = st.columns(2)
    with col1:
        student_id = st.text_input("รหัสนิสิต (Student ID):")
    with col2:
        student_name = st.text_input("ชื่อ-นามสกุล (Name-Surname):")
        
    if st.button("เริ่มเกม", type="primary", use_container_width=True):
        if student_id.strip() == "" or student_name.strip() == "":
            st.error("⚠️ กรุณากรอกรหัสนิสิตและชื่อ-นามสกุลให้ครบถ้วนครับ!")
        elif check_already_played(student_id):
            st.error("❌ นิสิตรหัสนี้ได้ทำการเล่นและบันทึกคะแนนไปแล้ว ไม่สามารถเล่นซ้ำได้ครับ")
        else:
            st.session_state.student_id = student_id
            st.session_state.student_name = student_name
            st.session_state.logged_in = True
            init_game_session()
            st.rerun()
            
    # ปุ่มลับสำหรับอาจารย์โหลดข้อมูล
    st.markdown("---")
    if os.path.exists("game_results.csv"):
        with open("game_results.csv", "rb") as file:
            st.download_button(
                label="📥 (สำหรับอาจารย์) ดาวน์โหลดผลคะแนน CSV", 
                data=file, 
                file_name="game_results.csv", 
                mime="text/csv"
            )

# --- ส่วนหน้าเล่นเกม ---
else:
    if st.session_state.game_over:
        st.success(f"🎉 จบเกมแล้วครับ! ขอบคุณที่ร่วมสนุก")
        st.info(f"**ผู้เล่น:** {st.session_state.student_name} ({st.session_state.student_id})")
        st.metric("คะแนนรวมของคุณคือ", st.session_state.score)
        
        # บันทึกข้อมูล
        if not st.session_state.saved:
            file_name = "game_results.csv"
            new_data = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Student_ID": st.session_state.student_id,
                "Name": st.session_state.student_name,
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
        
        # ทำให้กล่องข้อมูลตัวละครและรอบโดดเด่นขึ้น
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.info(f"🎭 **กำลังเผชิญหน้ากับ:**\n\n### ผู้เล่นปริศนาคนที่ {char_index + 1}/7")
        with col_info2:
            st.success(f"⚔️ **สถานะการแข่งขัน:**\n\n### รอบที่ {current_round_with_char} / {ROUNDS_PER_CHAR}")
            
        st.progress(current_round_with_char / ROUNDS_PER_CHAR)
        st.markdown("<br>", unsafe_allow_html=True) # เว้นบรรทัดนิดหน่อยให้ดูสบายตา

        def play(player_choice):
            start_idx = char_index * ROUNDS_PER_CHAR
            history_with_char = st.session_state.player_history[start_idx:]
            bot_choice = CHARACTERS[current_char](history_with_char)
            
            p_score = 0
            if player_choice == "Cheat" and bot_choice == "Cheat": p_score = 0
            elif player_choice == "Cheat" and bot_choice == "Cooperate": p_score = 3
            elif player_choice == "Cooperate" and bot_choice == "Cooperate": p_score = 2
            elif player_choice == "Cooperate" and bot_choice == "Cheat": p_score = -1
                
            st.session_state.score += p_score
            st.session_state.player_history.append(player_choice)
            st.session_state.total_rounds += 1
            st.session_state.last_result = f"คุณเลือก **{player_choice}** | คู่แข่งเลือก **{bot_choice}** ➡️ คุณได้คะแนน **{p_score}** แต้ม"
            
            if st.session_state.total_rounds >= len(CHARACTERS) * ROUNDS_PER_CHAR:
                st.session_state.game_over = True

        # ปุ่มกดตัดสินใจ
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🤝 เลือก Cooperate (ร่วมมือ)", use_container_width=True):
                play("Cooperate")
                st.rerun()
        with col_btn2:
            if st.button("🗡️ เลือก Cheat (หักหลัง)", use_container_width=True):
                play("Cheat")
                st.rerun()
                
        # แสดงผลลัพธ์ของตาล่าสุด และคะแนนสะสม
        st.markdown("---")
        if st.session_state.last_result:
            st.warning(st.session_state.last_result)
            
        st.metric("🏆 คะแนนสะสมของคุณตอนนี้", st.session_state.score)
