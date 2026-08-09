-- ===============================================================================
-- HMIE Stage 9: Fee & Slippage Stress Test Tables (create_tables_stage9.sql)
-- Oracle 23c XE DDL for Strategy Transaction Fee Sensitivity & Survival Points
-- Compliance: HMIE Constitution Laws 1-11
-- ===============================================================================

CREATE TABLE STAGING.STRATEGY_FEE_SENSITIVITY (
    STRATEGY_CODE VARCHAR2(50) NOT NULL,
    FEE_LEVEL_PCT NUMBER(6, 2) NOT NULL,
    NET_TOTAL_RETURN_PCT NUMBER(10, 2) NOT NULL,
    NET_CAGR_PCT NUMBER(8, 2) NOT NULL,
    NET_MAX_DRAWDOWN_PCT NUMBER(8, 2) NOT NULL,
    NET_SHARPE_RATIO NUMBER(8, 2) NOT NULL,
    NET_PROFIT_FACTOR NUMBER(8, 2) NOT NULL,
    CAGR_DRAG_PCT NUMBER(8, 2) NOT NULL,
    BREAK_EVEN_FEE_PCT NUMBER(6, 3),
    MAX_SUSTAINABLE_COST_PCT NUMBER(6, 3),
    ROBUSTNESS_CLASSIFICATION VARCHAR2(30),
    CONSTRAINT PK_STRAT_FEE_SENS PRIMARY KEY (STRATEGY_CODE, FEE_LEVEL_PCT)
);
