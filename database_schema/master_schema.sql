-- ===============================================================================
--  HMIE v1.0.0 — AUTHORITATIVE ORACLE DDL SCHEMA DEFINITION SCRIPT
--  Database: Oracle 11g / 21c / 23c XE
--  Schema: STAGING & ANALYSIS
-- ===============================================================================

-- -------------------------------------------------------------------------------
-- 1. BASE RAW HISTORICAL MARKET DATA (STOCK_HIST_DATA & FYERS_HIST_DATA)
-- -------------------------------------------------------------------------------

CREATE TABLE STAGING.RAW_STOCK_HISTORY 
(
    SYMBOL       VARCHAR2(50) NOT NULL, 
    DATETIME     DATE NOT NULL, 
    OPEN         NUMBER(12,4), 
    HIGH         NUMBER(12,4), 
    LOW          NUMBER(12,4), 
    CLOSE        NUMBER(12,4), 
    VOLUME       NUMBER(15,0),
    CREATED_AT   DATE DEFAULT SYSDATE,
    CONSTRAINT PK_RAW_STOCK_HISTORY PRIMARY KEY (SYMBOL, DATETIME)
);

CREATE TABLE STAGING.STOCK_HIST_DATA 
(
    SYMBOL                      VARCHAR2(50) NOT NULL, 
    DATETIME                    DATE NOT NULL, 
    OPEN                        NUMBER(12,4), 
    HIGH                        NUMBER(12,4), 
    LOW                         NUMBER(12,4), 
    CLOSE                       NUMBER(12,4), 
    CHANGE                      NUMBER(12,4), 
    CHANGE_PERCENT              NUMBER(8,4), 
    TOTAL_LOW_HIGH              NUMBER(12,4), 
    GAP                         VARCHAR2(20), 
    GAP_PERCENT                 NUMBER(8,4), 
    TOTAL_PREV_LOW_HIGH         NUMBER(12,4), 
    TOTAL_PREV_LOW_HIGH_PERCENT NUMBER(8,4), 
    UPPER_WICK                  NUMBER(12,4), 
    LOWER_WICK                  NUMBER(12,4), 
    VOLUME                      NUMBER(15,0), 
    LOW_CLOSE                   NUMBER(12,4), 
    HIGH_CLOSE                  NUMBER(12,4), 
    PREVIOUS_CLOSE              NUMBER(12,4), 
    HIGH_52W                    NUMBER(12,4), 
    LOW_52W                     NUMBER(12,4), 
    DIST_HIGH52                 NUMBER(12,4), 
    DIST_LOW52                  NUMBER(12,4), 
    DAY_NAME                    VARCHAR2(20), 
    MONTH                       NUMBER(2,0), 
    QUARTER                     NUMBER(1,0), 
    WEEK                        NUMBER(2,0), 
    RSI_14                      NUMBER(8,4), 
    VWAP                        NUMBER(12,4), 
    EMA_20                      NUMBER(12,4), 
    EMA_50                      NUMBER(12,4), 
    EMA_100                     NUMBER(12,4), 
    EMA_200                     NUMBER(12,4), 
    EMA_400                     NUMBER(12,4), 
    EMA_500                     NUMBER(12,4), 
    MACD                        NUMBER(12,4), 
    MACD_SIGNAL                 NUMBER(12,4), 
    MACD_HIST                   NUMBER(12,4), 
    MACD_CROSS                  VARCHAR2(30), 
    MACD_TREND                  VARCHAR2(30), 
    CONSTRAINT PK_STOCK_HIST_DATA PRIMARY KEY (SYMBOL, DATETIME)
);

-- -------------------------------------------------------------------------------
-- 2. SECTOR & THEMATIC ROTATION ENGINE (STAGE 3)
-- -------------------------------------------------------------------------------

CREATE TABLE STAGING.SECTOR_MASTER (
    SECTOR_CODE       VARCHAR2(30) PRIMARY KEY,
    SECTOR_NAME       VARCHAR2(100) NOT NULL,
    INDEX_SYMBOL      VARCHAR2(50) NOT NULL,
    SECTOR_CATEGORY   VARCHAR2(30) DEFAULT 'CYCLICAL',
    WEIGHT_PCT        NUMBER(5,2),
    MEMBER_COUNT      NUMBER(4,0)
);

CREATE TABLE STAGING.SECTOR_ROTATION (
    DATETIME               DATE NOT NULL,
    SECTOR_CODE            VARCHAR2(30) NOT NULL,
    CLOSE_PRICE            NUMBER(12,4),
    RETURN_1M              NUMBER(8,4),
    RETURN_3M              NUMBER(8,4),
    RETURN_6M              NUMBER(8,4),
    RELATIVE_STRENGTH_3M   NUMBER(8,4),
    SECTOR_RANK_3M         NUMBER(3,0),
    RANK_DELTA_3M          NUMBER(3,0),
    ROTATION_STATUS        VARCHAR2(30), -- LEADING, WEAKENING, LAGGING, IMPROVING
    PRIMARY KEY (DATETIME, SECTOR_CODE)
);

CREATE TABLE STAGING.MARKET_REGIMES (
    DATETIME              DATE PRIMARY KEY,
    REGIME_NAME           VARCHAR2(50) NOT NULL, -- BULL_EXPANSION, BEAR_CAPITULATION, LATERAL_RANGE
    REGIME_DURATION_DAYS  NUMBER(5,0),
    PCT_ABOVE_EMA20       NUMBER(5,2),
    PCT_ABOVE_EMA50       NUMBER(5,2),
    PCT_ABOVE_EMA200      NUMBER(5,2),
    BREADTH_RATIO         NUMBER(6,3),
    NET_ADVANCES          NUMBER(5,0),
    AVG_MARKET_RETURN_PCT NUMBER(6,2)
);

-- -------------------------------------------------------------------------------
-- 3. HISTORICAL EVIDENCE ENGINE & MACRO EVENT TABLES (STAGE 4)
-- -------------------------------------------------------------------------------

CREATE TABLE STAGING.EVIDENCE_CORRECTIONS (
    EVENT_ID               NUMBER(6,0) PRIMARY KEY,
    EVENT_NAME             VARCHAR2(80) NOT NULL,
    PEAK_DATE              DATE NOT NULL,
    TROUGH_DATE            DATE NOT NULL,
    RECOVERY_DATE          DATE,
    MAX_DRAWDOWN_PCT       NUMBER(6,2),
    CORRECTION_DAYS        NUMBER(6,0),
    RECOVERY_DAYS          NUMBER(6,0),
    RECOVERY_TYPE          VARCHAR2(30), -- V_SHAPED, U_SHAPED, L_SHAPED_CONSOLIDATION
    TOP_SECTOR_30D         VARCHAR2(50),
    TOP_SECTOR_60D         VARCHAR2(50),
    TOP_THEME_60D          VARCHAR2(50)
);

CREATE TABLE STAGING.EVIDENCE_MACRO_EVENTS (
    EVENT_ID               NUMBER(6,0) PRIMARY KEY,
    EVENT_NAME             VARCHAR2(100) NOT NULL,
    EVENT_CATEGORY         VARCHAR2(30) NOT NULL, -- BUDGET, RBI_POLICY, FESTIVAL, ELECTION
    EVENT_DATE             DATE NOT NULL,
    REGIME_AT_EVENT        VARCHAR2(30),
    PRE_30D_MARKET_RETURN  NUMBER(6,2),
    POST_30D_MARKET_RETURN NUMBER(6,2),
    TOP_SECTOR_POST_30D    VARCHAR2(50),
    TOP_THEME_POST_30D     VARCHAR2(50)
);

-- -------------------------------------------------------------------------------
-- 4. ANALOG CASE MATCHER ENGINE
-- -------------------------------------------------------------------------------

CREATE TABLE ANALYSIS.EVENT_ANALOG_CASES (
    CASE_ID                NUMBER(6,0) PRIMARY KEY,
    TARGET_DATE            DATE NOT NULL,
    HISTORICAL_EVENT_ID    NUMBER(6,0) NOT NULL,
    HISTORICAL_EVENT_NAME  VARCHAR2(100) NOT NULL,
    SIMILARITY_SCORE       NUMBER(5,2), -- Percentage match 0-100%
    DRAWDOWN_MATCH_PCT     NUMBER(5,2),
    DURATION_MATCH_PCT     NUMBER(5,2),
    BREADTH_MATCH_PCT      NUMBER(5,2),
    MATCH_RATIONALE        VARCHAR2(500)
);

-- -------------------------------------------------------------------------------
-- 5. PIPELINE SYNC LOGS & SYSTEM INTEGRITY LOGS
-- -------------------------------------------------------------------------------

CREATE TABLE STAGING.SYNC_LOGS (
    LOG_ID                 NUMBER(10,0) GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    SYNC_TIME              DATE DEFAULT SYSDATE,
    STATUS                 VARCHAR2(20) NOT NULL, -- PASS, FAIL, WARNING
    SYMBOLS_UPDATED        VARCHAR2(50),
    TOTAL_RECORDS          NUMBER(10,0),
    REPORT_JSON            VARCHAR2(4000)
);
