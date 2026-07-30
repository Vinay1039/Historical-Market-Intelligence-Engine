-- Oracle DDL Script for STAGING.FYERS_HIST_DATA
-- Matches exact 40-column order and data types of HIST_DATA.csv

-- Drop table statement if replacing existing structure:
-- DROP TABLE "STAGING"."FYERS_HIST_DATA" CASCADE CONSTRAINTS;

CREATE TABLE "STAGING"."FYERS_HIST_DATA" 
(
    "SYMBOL"                      VARCHAR2(50), 
    "DATETIME"                    DATE, 
    "OPEN"                        NUMBER(12,4), 
    "HIGH"                        NUMBER(12,4), 
    "LOW"                         NUMBER(12,4), 
    "CLOSE"                       NUMBER(12,4), 
    "CHANGE"                      NUMBER(12,4), 
    "CHANGE_PERCENT"              NUMBER(8,4), 
    "TOTAL_LOW_HIGH"              NUMBER(12,4), 
    "GAP"                         VARCHAR2(20), 
    "GAP_PERCENT"                 NUMBER(8,4), 
    "TOTAL_PREV_LOW_HIGH"         NUMBER(12,4), 
    "TOTAL_PREV_LOW_HIGH_PERCENT" NUMBER(8,4), 
    "UPPER_WICK"                  NUMBER(12,4), 
    "LOWER_WICK"                  NUMBER(12,4), 
    "VOLUME"                      NUMBER(15,0), 
    "LOW_CLOSE"                   NUMBER(12,4), 
    "HIGH_CLOSE"                  NUMBER(12,4), 
    "PREVIOUS_CLOSE"              NUMBER(12,4), 
    "HIGH_52W"                    NUMBER(12,4), 
    "LOW_52W"                     NUMBER(12,4), 
    "DIST_HIGH52"                 NUMBER(12,4), 
    "DIST_LOW52"                  NUMBER(12,4), 
    "DAY_NAME"                    VARCHAR2(20), 
    "MONTH"                       NUMBER(2,0), 
    "QUARTER"                     NUMBER(1,0), 
    "WEEK"                        NUMBER(2,0), 
    "RSI_14"                      NUMBER(8,4), 
    "VWAP"                        NUMBER(12,4), 
    "EMA_20"                      NUMBER(12,4), 
    "EMA_50"                      NUMBER(12,4), 
    "EMA_100"                     NUMBER(12,4), 
    "EMA_200"                     NUMBER(12,4), 
    "EMA_400"                     NUMBER(12,4), 
    "EMA_500"                     NUMBER(12,4), 
    "MACD"                        NUMBER(12,4), 
    "MACD_SIGNAL"                 NUMBER(12,4), 
    "MACD_HIST"                   NUMBER(12,4), 
    "MACD_CROSS"                  VARCHAR2(30), 
    "MACD_TREND"                  VARCHAR2(30), 
    CONSTRAINT "PK_FYERS_HIST_DATA" PRIMARY KEY ("SYMBOL", "DATETIME")
);
