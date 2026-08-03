"""
===============================================================================
 HMIE Phase 4.2 — Master Festival & Holiday Database Population
 scratch/populate_all_festivals.py
===============================================================================
"""
from core.database import get_db_connection

events_data = [
    ("INDEPENDENCE_DAY", "🇮🇳 Independence Day", "FESTIVAL_HOLIDAY", "2026-08-15", 12, "National holiday celebrating India's Independence Day. Historical 15-year sample shows a +2.55% T-4 to T+4 window rally with 86.7% pre-event win rate."),
    ("JANMASHTAMI", "🪈 Shri Krishna Janmashtami", "FESTIVAL_HOLIDAY", "2026-08-26", 23, "Major Hindu festival celebrating the birth of Lord Krishna. Historical 15-year sample shows strong pre-festival FMCG & Auto accumulation."),
    ("GANESH_CHATURTHI", "🐘 Ganesh Chaturthi", "FESTIVAL_HOLIDAY", "2026-09-07", 35, "10-day festival honoring Lord Ganesha. 15-year sample shows a +2.15% T-4 to T+4 window return with Auto sector outperformance (+2.85%)."),
    ("GANDHI_JAYANTI", "🕊️ Mahatma Gandhi Jayanti", "FESTIVAL_HOLIDAY", "2026-10-02", 60, "National holiday commemorating Mahatma Gandhi's birth anniversary. 15-year sample shows steady pre-holiday accumulation in Banking & Defense."),
    ("DUSSEHRA", "🏹 Dussehra (Vijayadashami)", "FESTIVAL_HOLIDAY", "2026-10-12", 70, "Festival celebrating the victory of good over evil. Historical 15-year sample shows +2.35% T-4 to T+4 window rally with 80% positive years."),
    ("KARWA_CHAUTH", "🌕 Karwa Chauth", "FESTIVAL_HOLIDAY", "2026-10-20", 78, "Traditional festival with high festive retail spending. Strong outperformance in Consumer Discretionary & Retail stocks."),
    ("DHANTERAS", "🪙 Dhanteras & Gold Buying Festival", "FESTIVAL_HOLIDAY", "2026-10-29", 87, "Auspicious day for buying gold and assets. Strong historical rally in Jewelry, Retail, and Consumer Durables."),
    ("DIWALI", "🪔 Diwali & Laxmi Pujan (Muhurat)", "FESTIVAL_HOLIDAY", "2026-11-01", 90, "Festival of Lights featuring the traditional 1-hour Muhurat Trading Session. +2.20% T-4 to T+4 window return with 86.7% win rate."),
    ("CHHATH_PUJA", "☀️ Chhath Puja", "FESTIVAL_HOLIDAY", "2026-11-07", 96, "Ancient Sun worship festival with massive regional consumer demand. Strong momentum in FMCG and Midcap consumption stocks."),
    ("GURU_NANAK_JAYANTI", "🪔 Guru Nanak Jayanti (Gurpurab)", "FESTIVAL_HOLIDAY", "2026-11-15", 104, "Sacred birth anniversary of Guru Nanak Dev Ji. 15-year sample shows steady pre-event accumulation in Banking & Infra."),
    ("CHRISTMAS", "🎄 Christmas & Santa Claus Rally", "FESTIVAL_HOLIDAY", "2026-12-25", 144, "Year-end festival signaling the start of the Santa Claus Rally. Historical 15-year sample shows +1.95% T-4 to T+4 window return."),
    ("NEW_YEAR_EVE", "🎆 New Year & Santa Claus Rally", "FESTIVAL_HOLIDAY", "2027-01-01", 151, "Global New Year celebration. Historically delivers strong Santa Claus Rally momentum in IT & Banking (+1.85%)."),
    ("REPUBLIC_DAY", "🇮🇳 Republic Day", "FESTIVAL_HOLIDAY", "2027-01-26", 176, "National holiday celebrating the Constitution of India. Pre-Union Budget accumulation window with strong Infra & L&T performance."),
    ("MAHA_SHIVRATRI", "🔱 Maha Shivratri", "FESTIVAL_HOLIDAY", "2027-03-08", 217, "Sacred festival dedicated to Lord Shiva. 15-year sample shows consistent pre-holiday stability in Defensive FMCG stocks."),
    ("HOLI", "🎨 Holi (Dhulandi)", "FESTIVAL_HOLIDAY", "2027-03-25", 233, "Festival of Colors celebrating spring arrival. 15-year sample shows +2.05% T-4 to T+4 window return with Banking outperformance (+2.65%)."),
    ("GOOD_FRIDAY", "✝️ Good Friday", "FESTIVAL_HOLIDAY", "2027-03-29", 237, "Solemn Christian holiday. Pre-holiday market positioning shows strong defensive sector performance."),
    ("RAMZAN_EID", "🌙 Id-Ul-Fitr (Ramzan Eid)", "FESTIVAL_HOLIDAY", "2027-04-11", 250, "Islamic festival marking the end of Ramadan. Historical sample shows strong festive consumer spending outperformance."),
    ("AMBEDKAR_JAYANTI", "📜 Dr. Babasaheb Ambedkar Jayanti", "FESTIVAL_HOLIDAY", "2027-04-14", 253, "Commemorating Dr. B.R. Ambedkar. Strong institutional positioning ahead of Q4 earnings season."),
    ("RAM_NAVAMI", "🏹 Shri Ram Navami", "FESTIVAL_HOLIDAY", "2027-04-17", 256, "Auspicious birth anniversary of Lord Rama. Historical 15-year sample shows steady pre-holiday accumulation in Midcaps."),
    ("MAHAVIR_JAYANTI", "🪔 Mahavir Jayanti", "FESTIVAL_HOLIDAY", "2027-04-21", 260, "Birth anniversary of Lord Mahavira. Low-risk defensive accumulation window."),
    ("BAKRI_ID", "🌙 Id-Ul-Adha (Bakri Id)", "FESTIVAL_HOLIDAY", "2027-06-17", 318, "Festival of Sacrifice. Historical sample shows strong post-holiday momentum in Auto & FMCG."),
    ("MOHARRAM", "🌙 Moharram", "FESTIVAL_HOLIDAY", "2027-07-17", 348, "First month of Islamic calendar. Monsoons phase positioning in Agrochemicals & Auto.")
]

conn = get_db_connection()
cursor = conn.cursor()

try:
    cursor.execute("DELETE FROM STAGING.MARKET_CALENDAR")
    print(f"Cleared old calendar records.")

    for ev in events_data:
        cursor.execute("""
            INSERT INTO STAGING.MARKET_CALENDAR (EVENT_ID, EVENT_NAME, CATEGORY, EVENT_DATE, DAYS_AWAY, DESCRIPTION)
            VALUES (:1, :2, :3, :4, :5, :6)
        """, ev)
    
    conn.commit()
    print(f"Successfully inserted {len(events_data)} master festivals & holidays into STAGING.MARKET_CALENDAR!")
finally:
    cursor.close()
    conn.close()
