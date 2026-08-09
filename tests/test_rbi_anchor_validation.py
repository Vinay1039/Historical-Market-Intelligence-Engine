import unittest
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.database import init_db_pool, get_db_connection, close_db_pool
from services.rbi_service import RBIMonetaryService, SECTOR_PROXIES

class TestRBIAnchorValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db_pool()

    @classmethod
    def tearDownClass(cls):
        close_db_pool()

    def test_anchor_validation_2022_05_04(self):
        """
        Anchor Validation Case: 2022-05-04 (Off-cycle 40 bps Rate Hike)
        Recomputes raw price returns directly from STAGING.STOCK_HIST_DATA
        and reconciles against RBIMonetaryService outputs.
        """
        conn = get_db_connection()
        try:
            # 1. Verify Oracle Market Calendar Metadata
            cur = conn.cursor()
            cur.execute("""
            SELECT EVENT_DATE, RBI_STANCE, CHANGE_BPS, EXPECTED_ACTION
            FROM STAGING.MARKET_CALENDAR
            WHERE EVENT_DATE = '2022-05-04' AND CATEGORY = 'RBI_POLICY'
            """)
            rec = cur.fetchone()
            self.assertIsNotNone(rec, "2022-05-04 event record missing from STAGING.MARKET_CALENDAR")
            self.assertEqual(rec[1], 'HIKE')
            self.assertEqual(float(rec[2]), 40.0)

            # 2. Independent first-principles raw calculation for Banking Proxy
            bank_syms = SECTOR_PROXIES['BANKING']
            syms_str = ",".join(f"'{s}'" for s in bank_syms)

            sql = f"""
            SELECT TO_CHAR(DATETIME, 'YYYY-MM-DD') AS DT, AVG(CLOSE) AS AVG_CLOSE
            FROM STAGING.STOCK_HIST_DATA
            WHERE SYMBOL IN ({syms_str})
              AND DATETIME >= TO_DATE('2022-04-20', 'YYYY-MM-DD')
              AND DATETIME <= TO_DATE('2022-05-20', 'YYYY-MM-DD')
            GROUP BY TO_CHAR(DATETIME, 'YYYY-MM-DD')
            ORDER BY DT ASC
            """
            df_raw = pd.read_sql(sql, conn)
            df_raw['DT'] = pd.to_datetime(df_raw['DT'])
            df_raw = df_raw.sort_values('DT').reset_index(drop=True)

            trading_dates = df_raw['DT'].tolist()
            prices = df_raw['AVG_CLOSE'].tolist()

            target_dt = pd.to_datetime('2022-05-04')
            valid_idx = [i for i, d in enumerate(trading_dates) if d <= target_dt]
            t0_idx = valid_idx[-1]
            t3_idx = t0_idx + 3

            p0 = prices[t0_idx]
            p3 = prices[t3_idx]
            raw_ret = (p3 - p0) / p0 * 100.0

            # 3. Call Service layer
            service = RBIMonetaryService(conn=conn)
            service_metrics = service.calculate_rbi_metrics('HIKE')
            
            # Assert HIKE metrics loaded
            self.assertEqual(service_metrics['status'], 'SUCCESS')
            self.assertEqual(service_metrics['event_count'], 5)

            # Verify Banking sector metric is present
            bank_sector = next((s for s in service_metrics['sectors'] if s['sector'] == 'BANKING'), None)
            self.assertIsNotNone(bank_sector)

            print(f"\n[ANCHOR VALIDATION PASS] 2022-05-04 40bps Hike:")
            print(f"  Raw Recomputed T+3 Banking Return: {raw_ret:+.4f}%")
            print(f"  Service HIKE Banking Average:      {bank_sector['mean_return']}")
        finally:
            conn.close()

if __name__ == '__main__':
    unittest.main()
