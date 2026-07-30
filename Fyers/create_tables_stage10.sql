-- ============================================================================
--  HMIE Stage 10: Research Plausibility Engine — Oracle DDL
--  Tables: STAGING.STRATEGY_MONTHLY_UNIVERSE
--           STAGING.PLAUSIBILITY_AUDIT
--  Compliance: HMIE Constitution Laws 1-11 (QG3 Extension)
--  Version: 1.0.0
-- ============================================================================

-- ============================================================================
--  Table 1: STRATEGY_MONTHLY_UNIVERSE
--  Records the dynamic symbol selection for each strategy for each month.
--  Enables universe overlap calculation for Quality Gate 3.
-- ============================================================================
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE STAGING.STRATEGY_MONTHLY_UNIVERSE';
EXCEPTION WHEN OTHERS THEN
    IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

CREATE TABLE STAGING.STRATEGY_MONTHLY_UNIVERSE (
    ID              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    STRATEGY_CODE   VARCHAR2(50)    NOT NULL,   -- e.g. 'TOP_STOCK_MOMENTUM_95P'
    MONTH_KEY       VARCHAR2(7)     NOT NULL,   -- 'YYYY-MM' format
    SYMBOL          VARCHAR2(30)    NOT NULL,   -- Selected stock symbol
    MOMENTUM_RANK   NUMBER(5)       NOT NULL,   -- Rank within eligible universe (1 = highest momentum)
    MOMENTUM_PCT    NUMBER(10, 4)   NOT NULL,   -- 6-month trailing return used for ranking (%)
    UNIVERSE_SIZE   NUMBER(5)       NOT NULL,   -- Total eligible symbols that month
    PERCENTILE_CUT  NUMBER(5, 2)    NOT NULL,   -- Percentile threshold applied (e.g. 95.0)
    BASKET_SIZE     NUMBER(5)       NOT NULL    -- Number of symbols selected that month
);

CREATE INDEX IDX_SMU_STRAT_MONTH ON STAGING.STRATEGY_MONTHLY_UNIVERSE (STRATEGY_CODE, MONTH_KEY);
CREATE INDEX IDX_SMU_SYMBOL      ON STAGING.STRATEGY_MONTHLY_UNIVERSE (SYMBOL);

COMMENT ON TABLE STAGING.STRATEGY_MONTHLY_UNIVERSE IS 
    'Dynamic monthly symbol selection log for algorithmic strategies. '
    'Enables universe overlap auditing in Quality Gate 3.';

-- ============================================================================
--  Table 2: PLAUSIBILITY_AUDIT
--  Stores the output of the Research Plausibility Engine (Quality Gate 3).
--  Each row is one rule evaluation for one strategy-benchmark pair.
-- ============================================================================
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE STAGING.PLAUSIBILITY_AUDIT';
EXCEPTION WHEN OTHERS THEN
    IF SQLCODE != -942 THEN RAISE; END IF;
END;
/

CREATE TABLE STAGING.PLAUSIBILITY_AUDIT (
    AUDIT_ID            NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    RUN_TIMESTAMP       TIMESTAMP   DEFAULT SYSTIMESTAMP NOT NULL,
    STRATEGY_CODE       VARCHAR2(50)    NOT NULL,
    BENCHMARK_CODE      VARCHAR2(50),           -- NULL for non-benchmark rules
    RULE_CODE           VARCHAR2(50)    NOT NULL,   -- e.g. 'UNIVERSE_IDENTICAL'
    RULE_DESCRIPTION    VARCHAR2(500)   NOT NULL,   -- Human-readable rule explanation
    OBSERVED_VALUE      VARCHAR2(200)   NOT NULL,   -- What was actually measured
    THRESHOLD_VALUE     VARCHAR2(200)   NOT NULL,   -- Limit that determines severity
    SEVERITY            VARCHAR2(10)    NOT NULL,   -- 'PASS', 'WARNING', 'FAIL'
    RECOMMENDATION      VARCHAR2(500)   NOT NULL    -- What to do about it
);

CREATE INDEX IDX_PA_STRATEGY    ON STAGING.PLAUSIBILITY_AUDIT (STRATEGY_CODE);
CREATE INDEX IDX_PA_SEVERITY    ON STAGING.PLAUSIBILITY_AUDIT (SEVERITY);
CREATE INDEX IDX_PA_RULE        ON STAGING.PLAUSIBILITY_AUDIT (RULE_CODE);
CREATE INDEX IDX_PA_TIMESTAMP   ON STAGING.PLAUSIBILITY_AUDIT (RUN_TIMESTAMP);

COMMENT ON TABLE STAGING.PLAUSIBILITY_AUDIT IS 
    'Quality Gate 3: Research Plausibility Engine output. '
    'Each row represents one rule evaluation per strategy-benchmark pair. '
    'FAIL severity blocks research publication. WARNING requires disclosure.';

-- Confirm creation
SELECT TABLE_NAME, NUM_ROWS 
FROM USER_TABLES 
WHERE TABLE_NAME IN ('STRATEGY_MONTHLY_UNIVERSE', 'PLAUSIBILITY_AUDIT')
ORDER BY TABLE_NAME;
