import streamlit as st
import random

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
    "Angel": char_always_cooperate, "Devil": char_always_cheat, "Copycat": char_tit_for_tat,
    "Skeptic": char_suspicious_tft, "Grudger": char_grudger, "Tolerant": char_tit_for_two_tats,
    "Alternator": char_alternator
}

# ==========================================
# 2. ฟังก์ชันเตรียม "สมุดจด" ให้ผู้เล่นใหม่
# ==========================================
def init_session():
    if 'total_rounds' not in st.session_state:
        st.session_state.total_rounds = 0
        st.session_state.player_history = []
        st.session_state.score = 0
        
        # สุ่มลำดับตัวละครให้นิสิตคนนี้
        chars = list(CHARACTERS.keys())
        random.shuffle(chars)
        st.session_state.sequence = chars
        
        st.session_state.game_over = False
        st.session_state.last_result = ""

init_session()

# ==========================================
# 3. หน้าตาของ Web App (User Interface)
# ==========================================
st.title("Game Theory: The Repeated Game")

# ถ้าเกมจบแล้ว
if st.session_state.game_over:
    st.success(f"จบเกมแล้วครับ! 🎉")
    st.metric("คะแนนรวมของคุณคือ", st.session_state.score)
    st.info("สามารถบันทึกภาพหน้าจอนี้ หรือกด Refresh หน้าเว็บเพื่อเริ่มใหม่")

# ถ้าเกมยังไม่จบ
else:
    ROUNDS_PER_CHAR = 6
    char_index = st.session_state.total_rounds // ROUNDS_PER_CHAR
    current_char = st.session_state.sequence[char_index]
    current_round_with_char = (st.session_state.total_rounds % ROUNDS_PER_CHAR) + 1

    st.subheader(f"กำลังเผชิญหน้ากับ: ผู้เล่นปริศนาคนที่ {char_index + 1}/7")
    st.write(f"รอบที่ {current_round_with_char} / {ROUNDS_PER_CHAR}")

    # ฟังก์ชันประมวลผลเมื่อกดปุ่ม
    def play(player_choice):
        start_idx = char_index * ROUNDS_PER_CHAR
        history_with_char = st.session_state.player_history[start_idx:]
        
        # ให้บอทตัดสินใจ
        bot_choice = CHARACTERS[current_char](history_with_char)
        
        # คำนวณ Payoff
        p_score = 0
        if player_choice == "Cheat" and bot_choice == "Cheat": p_score = 0
        elif player_choice == "Cheat" and bot_choice == "Cooperate": p_score = 3
        elif player_choice == "Cooperate" and bot_choice == "Cooperate": p_score = 2
        elif player_choice == "Cooperate" and bot_choice == "Cheat": p_score = -1
            
        # บันทึกข้อมูลลงสมุดจด
        st.session_state.score += p_score
        st.session_state.player_history.append(player_choice)
        st.session_state.total_rounds += 1
        st.session_state.last_result = f"คุณเลือก {player_choice} | คู่แข่งเลือก {bot_choice} ➡️ คุณได้ {p_score} คะแนน"
        
        # เช็คว่าจบเกมหรือยัง
        if st.session_state.total_rounds >= len(CHARACTERS) * ROUNDS_PER_CHAR:
            st.session_state.game_over = True

    # แสดงผลปุ่มและคะแนน
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🤝 Cooperate", use_container_width=True):
            play("Cooperate")
            st.rerun() # สั่งให้เว็บโหลดข้อมูลใหม่ทันที
    with col2:
        if st.button("🗡️ Cheat", use_container_width=True):
            play("Cheat")
            st.rerun()
            
    if st.session_state.last_result:
        st.warning(st.session_state.last_result)
        
    st.metric("คะแนนสะสมของคุณ", st.session_state.score)
