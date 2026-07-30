import oracledb
oracledb.init_oracle_client(lib_dir=r'C:\instantclient_23_0')
conn = oracledb.connect(user='analysis', password='hr', dsn='localhost:1521/XE')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM HR.STOCKS WHERE EXCHANGE='NSE' AND MARKET_CAP IS NOT NULL")
total = cursor.fetchone()[0]
print(f"NSE Stocks with Market Cap: {total}")

cursor.execute("SELECT COUNT(DISTINCT SECTOR) FROM HR.STOCKS WHERE EXCHANGE='NSE' AND MARKET_CAP IS NOT NULL")
print(f"Distinct Sectors: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(DISTINCT INDUSTRY) FROM HR.STOCKS WHERE EXCHANGE='NSE' AND MARKET_CAP IS NOT NULL")
print(f"Distinct Industries: {cursor.fetchone()[0]}")

cursor.execute("""
    SELECT * FROM (
        SELECT SECTOR, COUNT(*) as CNT, ROUND(SUM(MARKET_CAP)/1e9, 2) as TOTAL_MCAP_B
        FROM HR.STOCKS 
        WHERE EXCHANGE='NSE' AND MARKET_CAP IS NOT NULL AND SECTOR IS NOT NULL
        GROUP BY SECTOR 
        ORDER BY CNT DESC
    ) WHERE ROWNUM <= 15
""")
print("\nTop 15 Sectors (by stock count):")
for r in cursor.fetchall(): print(f"  {r[0][:40]:<40} | Stocks: {r[1]:>4} | MCap(B): {r[2]}")

cursor.execute("""
    SELECT * FROM (
        SELECT SECTOR, INDUSTRY, COUNT(*) as CNT
        FROM HR.STOCKS 
        WHERE EXCHANGE='NSE' AND MARKET_CAP IS NOT NULL AND SECTOR IS NOT NULL
        GROUP BY SECTOR, INDUSTRY
        ORDER BY CNT DESC
    ) WHERE ROWNUM <= 20
""")
print("\nTop 20 Sector-Industry combos:")
for r in cursor.fetchall(): print(f"  {r[0][:25]:<25} | {r[1][:40]:<40} | {r[2]}")

cursor.execute("SELECT COUNT(*) FROM HR.STOCKS WHERE EXCHANGE='NSE' AND MARKET_CAP IS NOT NULL AND SECTOR IS NULL")
print(f"\nStocks with NULL Sector: {cursor.fetchone()[0]}")

cursor.close()
conn.close()
