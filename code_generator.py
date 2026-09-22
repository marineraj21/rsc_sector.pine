import re

code = """// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/

// RSC Sector — RS rank table for INDEX STOCKS1.xlsx constituents

// Open on a stock or sector index (e.g. NSE:CNXAUTO / NSE:MARUTI) to see all names in that sector.

// Stock lists are exactly the 12 sector blocks of INDEX STOCKS1.xlsx (168 names), no additions.

//

// Column formulas, all on the chart timeframe against the benchmark, period = 22:

// RS(k) = ((close[k] / close[k + 22]) / (bench[k] / bench[k + 22]) - 1) * 100

// RS-0 = RS(0) RS-1 = RS(1) RS-2 = RS(2)

// %Change = stock only: week-over-week if chart TF <= D, month-over-month if chart TF >= W

// Rank = descending RS-0 (first column)

// Weightage = INDEX STOCKS1.xlsx Weightage* for that stock in this sector

// Average = arithmetic mean of the RS columns over every listed name

//@version=6

indicator(title='RSC Sector', shorttitle='RSC Sector', overlay=false, precision=2, max_bars_back=1000)

grpB = 'Benchmark Settings'

defaultBType = input.string(defval='Auto Sector', title='Benchmark Type', group=grpB, options=['Auto Sector', 'Custom Benchmark'], tooltip='Auto Sector maps the benchmark to the sector of the chart symbol.')

customBench = input.symbol('NSE:NIFTY', 'Custom Benchmark', group=grpB)

flagARS = input.bool(defval=false, title='Use Anchored RS (ARS)', group=grpB)

historyDateARS = input.time(timestamp('2024-09-26 00:00'), 'ARS Reference Date', group=grpB)

fromDate = input.time(timestamp('2026-08-01 00:00'), 'From Date', group=grpB, tooltip='Hides plotted lines before this date. Example: 1 Aug shows 1 Aug to today only.')

rsLen = input.int(22, 'RS Period', minval=1, group=grpB, tooltip='RS = ((stock / stock[period]) / (bench / bench[period]) - 1) * 100. Period is in chart bars.')

rsLb1 = input.int(1, 'RS-1 bars back', minval=1, group=grpB, tooltip='RS-1 = RS one chart bar ago.')

rsLb2 = input.int(2, 'RS-2 bars back', minval=1, group=grpB, tooltip='RS-2 = RS two chart bars ago.')

grpV = 'View'

viewMode = input.string('Auto', 'View Mode', options=['Auto', 'Sector Stocks', 'Compare Sectors', 'Nifty Stocks'], group=grpV, tooltip='Auto: NIFTY chart compares sectors. A stock or sector index chart lists all constituents of that sector.')

showPlots = input.bool(true, 'Show RS Lines', group=grpV)

showAbsolute = input.bool(false, 'Show Absolute? (%Change instead of RS line)', group=grpV)

showBenchmark = input.bool(false, 'Show Benchmark? (zero line)', group=grpV)

showDelta = input.bool(false, 'Show Delta? (RS minus group average)', group=grpV)

rankBy = input.string('RS-0', 'Rank By', options=['RS-0', '%Change'], group=grpV)

grpH = 'Highlight'

hlMode = input.string('By Slot/Color (Trace specific stock)', 'Highlight Mode', options=['By Slot/Color (Trace specific stock)', 'By Rank (Track Top Performers)'], group=grpH, tooltip='By Slot highlights the Nth stock in the raw list (e.g., Slot 1 is always the highest-weighted stock). By Rank highlights whichever stock is currently rank N on that specific bar.')

hlTargetStr = input.string('None', 'Highlight Target', options=['None', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20'], group=grpH)
hlTarget = hlTargetStr == 'None' ? 0 : str.tonumber(hlTargetStr)

grpT = 'Table'

showTable = input.bool(true, 'Show Table', group=grpT)

tblPos = input.string('Top Right', 'Table Position', options=['Top Right', 'Middle Right', 'Bottom Right', 'Top Left'], group=grpT)

tblSize = input.string('Small', 'Table Text Size', options=['Tiny', 'Small', 'Normal'], group=grpT)

grpC = 'Cell Colors'

colRsHi = input.color(#1a237e, 'RS strongest of the three', group=grpC, tooltip='Background for whichever of RS-0 / RS-1 / RS-2 is highest in that row.')

colRsMid = input.color(#1976d2, 'RS middle of the three', group=grpC)

colRsLo = input.color(#4dd0e1, 'RS weakest of the three', group=grpC)

colUp = input.color(#43a047, '%Change positive', group=grpC)

colDown = input.color(#e53935, '%Change negative', group=grpC)

colRankTop = input.color(#2e7d32, 'Rank best', group=grpC, tooltip='Rank column fades from this colour at rank 1 to the worst-rank colour at the bottom.')

colRankBot = input.color(#c62828, 'Rank worst', group=grpC)

colBlank = input.color(#111111, 'No data', group=grpC)

dummyId = 'NSE:NIFTY'

inRange = time >= fromDate

useTf = timeframe.period

weekPctMode = timeframe.in_seconds() < timeframe.in_seconds('W')

normTicker(string id) =>
    t = str.replace_all(id, 'NSE:', '')
    t := str.replace_all(t, 'BSE:', '')
    str.replace_all(t, ':', '')

var map<string, string> sectorOfStock = map.new<string, string>()

if bar_index == 0
    sectorOfStock.put('ABB', 'CNXENERGY')
    sectorOfStock.put('ABBOTINDIA', 'CNXPHARMA')
    sectorOfStock.put('ADANIENSOL', 'CNXENERGY')
    sectorOfStock.put('ADANIENT', 'CNXMETAL')
    sectorOfStock.put('ADANIGREEN', 'CNXENERGY')
    sectorOfStock.put('ADANIPOWER', 'CNXENERGY')
    sectorOfStock.put('AEGISLOG', 'NIFTY_OIL_AND_GAS')
    sectorOfStock.put('AEGISVOPAK', 'NIFTY_OIL_AND_GAS')
    sectorOfStock.put('ALKEM', 'CNXPHARMA')
    sectorOfStock.put('AMBER', 'NIFTY_CONSR_DURBL')
    sectorOfStock.put('APLAPOLLO', 'CNXMETAL')
    sectorOfStock.put('APOLLOHOSP', 'CNXPHARMA')
    sectorOfStock.put('ASHOKLEY', 'CNXAUTO')
    sectorOfStock.put('ATGL', 'NIFTY_OIL_AND_GAS')
    sectorOfStock.put('AUBANK', 'BANKNIFTY')
    sectorOfStock.put('AUROPHARMA', 'CNXPHARMA')
    sectorOfStock.put('AXISBANK', 'BANKNIFTY')
    sectorOfStock.put('BAJAJ_AUTO', 'CNXAUTO')
    sectorOfStock.put('BAJAJFINSV', 'CNXFINANCE')
    sectorOfStock.put('BAJFINANCE', 'CNXFINANCE')
    sectorOfStock.put('BANKBARODA', 'CNXPSUBANK')
    sectorOfStock.put('BANKINDIA', 'CNXPSUBANK')
    sectorOfStock.put('BATAINDIA', 'NIFTY_CONSR_DURBL')
    sectorOfStock.put('BEL', 'CNXPSE')
    sectorOfStock.put('BHARATFORG', 'CNXAUTO')
    sectorOfStock.put('BHEL', 'CNXENERGY')
    sectorOfStock.put('BIOCON', 'CNXPHARMA')
    sectorOfStock.put('BLUESTARCO', 'NIFTY_CONSR_DURBL')
    sectorOfStock.put('BOSCHLTD', 'CNXAUTO')
    sectorOfStock.put('BPCL', 'NIFTY_OIL_AND_GAS')
    sectorOfStock.put('BRITANNIA', 'CNXFMCG')
    sectorOfStock.put('BSE', 'CNXFINANCE')
    sectorOfStock.put('CANBK', 'CNXPSUBANK')
    sectorOfStock.put('CASTROLIND', 'NIFTY_OIL_AND_GAS')
    sectorOfStock.put('CENTRALBK', 'CNXPSUBANK')
    sectorOfStock.put('CGPOWER', 'CNXENERGY')
    sectorOfStock.put('CHENNPETRO', 'NIFTY_OIL_AND_GAS')
    sectorOfStock.put('CHOLAFIN', 'CNXFINANCE')
    sectorOfStock.put('CIPLA', 'CNXPHARMA')
    sectorOfStock.put('COALINDIA', 'CNXENERGY')
    sectorOfStock.put('COFORGE', 'CNXIT')
    sectorOfStock.put('COLPAL', 'CNXFMCG')
    sectorOfStock.put('CROMPTON', 'NIFTY_CONSR_DURBL')
    sectorOfStock.put('DABUR', 'CNXFMCG')
    sectorOfStock.put('DIVISLAB', 'CNXPHARMA')
    sectorOfStock.put('DIXON', 'NIFTY_CONSR_DURBL')
    sectorOfStock.put('DRREDDY', 'CNXPHARMA')
    sectorOfStock.put('EICHERMOT', 'CNXAUTO')
    sectorOfStock.put('EMAMILTD', 'CNXFMCG')
    sectorOfStock.put('EXIDEIND', 'CNXAUTO')
    sectorOfStock.put('FEDERALBNK', 'BANKNIFTY')
    sectorOfStock.put('FORTIS', 'CNXPHARMA')
    sectorOfStock.put('GAIL', 'NIFTY_OIL_AND_GAS')
    sectorOfStock.put('GLENMARK', 'CNXPHARMA')
    sectorOfStock.put('GODREJCP', 'CNXFMCG')
    sectorOfStock.put('HAL', 'CNXPSE')
    sectorOfStock.put('HAVELLS', 'NIFTY_CONSR_DURBL')
    sectorOfStock.put('HCLTECH', 'CNXIT')
    sectorOfStock.put('HDFCBANK', 'BANKNIFTY')
    sectorOfStock.put('HDFCLIFE', 'CNXFINANCE')
    sectorOfStock.put('HEROMOTOCO', 'CNXAUTO')
    sectorOfStock.put('HINDALCO', 'CNXMETAL')
    sectorOfStock.put('HINDCOPPER', 'CNXMETAL')
    sectorOfStock.put('HINDPETRO', 'NIFTY_OIL_AND_GAS')
    sectorOfStock.put('HINDUNILVR', 'CNXFMCG')
    sectorOfStock.put('HINDZINC', 'CNXMETAL')
    sectorOfStock.put('ICICIBANK', 'BANKNIFTY')
    sectorOfStock.put('IDFCFIRSTB', 'BANKNIFTY')
    sectorOfStock.put('IGL', 'NIFTY_OIL_AND_GAS')
    sectorOfStock.put('INDIANB', 'CNXPSUBANK')
    sectorOfStock.put('INDUSINDBK', 'BANKNIFTY')
    sectorOfStock.put('INFY', 'CNXIT')
    sectorOfStock.put('IOB', 'CNXPSUBANK')
    sectorOfStock.put('IOC', 'NIFTY_OIL_AND_GAS')
    sectorOfStock.put('IPCALAB', 'CNXPHARMA')
    sectorOfStock.put('IRFC', 'CNXPSE')
    sectorOfStock.put('ITC', 'CNXFMCG')
    sectorOfStock.put('JINDALSTEL', 'CNXMETAL')
    sectorOfStock.put('JIOFIN', 'CNXFINANCE')
    sectorOfStock.put('JSL', 'CNXMETAL')
    sectorOfStock.put('JSWSTEEL', 'CNXMETAL')
    sectorOfStock.put('KAJARIACER', 'NIFTY_CONSR_DURBL')
    sectorOfStock.put('KALYANKJIL', 'NIFTY_CONSR_DURBL')
    sectorOfStock.put('KOTAKBANK', 'BANKNIFTY')
    sectorOfStock.put('LAURUSLABS', 'CNXPHARMA')
    sectorOfStock.put('LLOYDSME', 'CNXMETAL')
    sectorOfStock.put('LTM', 'CNXIT')
    sectorOfStock.put('LUPIN', 'CNXPHARMA')
    sectorOfStock.put('M&M', 'CNXAUTO')
    sectorOfStock.put('M_M', 'CNXAUTO')
    sectorOfStock.put('MAHABANK', 'CNXPSUBANK')
    sectorOfStock.put('MANKIND', 'CNXPHARMA')
    sectorOfStock.put('MARICO', 'CNXFMCG')
    sectorOfStock.put('MARUTI', 'CNXAUTO')
    sectorOfStock.put('MAXHEALTH', 'CNXPHARMA')
    sectorOfStock.put('MOTHERSON', 'CNXAUTO')
    sectorOfStock.put('MPHASIS', 'CNXIT')
    sectorOfStock.put('MUTHOOTFIN', 'CNXFINANCE')
    sectorOfStock.put('NATIONALUM', 'CNXMETAL')
    sectorOfStock.put('NMDC', 'CNXMETAL')
    sectorOfStock.put('NTPC', 'CNXENERGY')
    sectorOfStock.put('OFSS', 'CNXIT')
    sectorOfStock.put('OIL', 'NIFTY_OIL_AND_GAS')
    sectorOfStock.put('ONGC', 'NIFTY_OIL_AND_GAS')
    sectorOfStock.put('PATANJALI', 'CNXFMCG')
    sectorOfStock.put('PERSISTENT', 'CNXIT')
    sectorOfStock.put('PETRONET', 'NIFTY_OIL_AND_GAS')
    sectorOfStock.put('PFC', 'CNXFINANCE')
    sectorOfStock.put('PGEL', 'NIFTY_CONSR_DURBL')
    sectorOfStock.put('PNB', 'CNXPSUBANK')
    sectorOfStock.put('POWERGRID', 'CNXENERGY')
    sectorOfStock.put('POWERINDIA', 'CNXENERGY')
    sectorOfStock.put('PPLPHARMA', 'CNXPHARMA')
    sectorOfStock.put('PSB', 'CNXPSUBANK')
    sectorOfStock.put('RADICO', 'CNXFMCG')
    sectorOfStock.put('RECLTD', 'CNXPSE')
    sectorOfStock.put('RELIANCE', 'NIFTY_OIL_AND_GAS')
    sectorOfStock.put('SAIL', 'CNXMETAL')
    sectorOfStock.put('SBILIFE', 'CNXFINANCE')
    sectorOfStock.put('SBIN', 'CNXPSUBANK')
    sectorOfStock.put('SHRIRAMFIN', 'CNXFINANCE')
    sectorOfStock.put('SIEMENS', 'CNXENERGY')
    sectorOfStock.put('SONACOMS', 'CNXAUTO')
    sectorOfStock.put('SUNPHARMA', 'CNXPHARMA')
    sectorOfStock.put('TATACONSUM', 'CNXFMCG')
    sectorOfStock.put('TATASTEEL', 'CNXMETAL')
    sectorOfStock.put('TCS', 'CNXIT')
    sectorOfStock.put('TECHM', 'CNXIT')
    sectorOfStock.put('TIINDIA', 'CNXAUTO')
    sectorOfStock.put('TITAN', 'NIFTY_CONSR_DURBL')
    sectorOfStock.put('TMPV', 'CNXAUTO')
    sectorOfStock.put('TORNTPHARM', 'CNXPHARMA')
    sectorOfStock.put('TVSMOTOR', 'CNXAUTO')
    sectorOfStock.put('UBL', 'CNXFMCG')
    sectorOfStock.put('UCOBANK', 'CNXPSUBANK')
    sectorOfStock.put('UNIONBANK', 'CNXPSUBANK')
    sectorOfStock.put('UNITDSPR', 'CNXFMCG')
    sectorOfStock.put('UNOMINDA', 'CNXAUTO')
    sectorOfStock.put('VBL', 'CNXFMCG')
    sectorOfStock.put('VEDL', 'CNXMETAL')
    sectorOfStock.put('VOLTAS', 'NIFTY_CONSR_DURBL')
    sectorOfStock.put('WHIRLPOOL', 'NIFTY_CONSR_DURBL')
    sectorOfStock.put('WIPRO', 'CNXIT')
    sectorOfStock.put('YESBANK', 'BANKNIFTY')
    sectorOfStock.put('ZYDUSLIFE', 'CNXPHARMA')

    // Sector index charts resolve to their own constituent list.
    sectorOfStock.put('CNXAUTO', 'CNXAUTO')
    sectorOfStock.put('NIFTY_CONSR_DURBL', 'NIFTY_CONSR_DURBL')
    sectorOfStock.put('CNXIT', 'CNXIT')
    sectorOfStock.put('CNXPHARMA', 'CNXPHARMA')
    sectorOfStock.put('CNXFMCG', 'CNXFMCG')
    sectorOfStock.put('CNXMETAL', 'CNXMETAL')
    sectorOfStock.put('CNXPSUBANK', 'CNXPSUBANK')
    sectorOfStock.put('BANKNIFTY', 'BANKNIFTY')
    sectorOfStock.put('CNXFINANCE', 'CNXFINANCE')
    sectorOfStock.put('NIFTY_OIL_AND_GAS', 'NIFTY_OIL_AND_GAS')
    sectorOfStock.put('CNXENERGY', 'CNXENERGY')
    sectorOfStock.put('CNXPSE', 'CNXPSE')
    sectorOfStock.put('NIFTY', 'SECTORS')
    sectorOfStock.put('NIFTY50', 'SECTORS')
    sectorOfStock.put('CNX500', 'SECTORS')
    sectorOfStock.put('NIFTYJR', 'SECTORS')

resolveSector() =>
    t = normTicker(syminfo.tickerid)
    string key = sectorOfStock.get(t)
    if na(key)
        key := sectorOfStock.get(str.replace_all(t, '_', '&'))
    if na(key)
        key := sectorOfStock.get(str.replace_all(t, '_', '-'))
    if na(key)
        key := sectorOfStock.get(str.replace_all(t, '-', '_'))

    if viewMode == 'Nifty Stocks'
        key := 'NIFTY_STOCKS'
    else if viewMode == 'Compare Sectors'
        key := 'SECTORS'
    else if viewMode == 'Sector Stocks' and (na(key) or key == 'SECTORS')
        key := 'CNXAUTO'
    else if na(key)
        key := 'SECTORS'
    key

loadSector(string sectorKey, string[] ids, string[] nms, float[] wts) =>
    // Lists mirror INDEX STOCKS1.xlsx exactly, in the sheet's descending-weightage order.
    array.clear(ids)
    array.clear(nms)
    array.clear(wts)

    if sectorKey == 'NIFTY_STOCKS'
        array.push(ids, 'NSE:HDFCBANK'), array.push(nms, 'HDFCBANK'), array.push(wts, 11.0)
        array.push(ids, 'NSE:RELIANCE'), array.push(nms, 'RELIANCE'), array.push(wts, 9.5)
        array.push(ids, 'NSE:ICICIBANK'), array.push(nms, 'ICICIBANK'), array.push(wts, 8.0)
        array.push(ids, 'NSE:INFY'), array.push(nms, 'INFY'), array.push(wts, 6.0)
        array.push(ids, 'NSE:ITC'), array.push(nms, 'ITC'), array.push(wts, 4.5)
        array.push(ids, 'NSE:TCS'), array.push(nms, 'TCS'), array.push(wts, 4.0)
        array.push(ids, 'NSE:LT'), array.push(nms, 'LT'), array.push(wts, 3.8)
        array.push(ids, 'NSE:AXISBANK'), array.push(nms, 'AXISBANK'), array.push(wts, 3.5)
        array.push(ids, 'NSE:KOTAKBANK'), array.push(nms, 'KOTAKBANK'), array.push(wts, 3.0)
        array.push(ids, 'NSE:BHARTIARTL'), array.push(nms, 'BHARTIARTL'), array.push(wts, 2.8)
        array.push(ids, 'NSE:SBIN'), array.push(nms, 'SBIN'), array.push(wts, 2.7)
        array.push(ids, 'NSE:HINDUNILVR'), array.push(nms, 'HINDUNILVR'), array.push(wts, 2.5)
        array.push(ids, 'NSE:BAJFINANCE'), array.push(nms, 'BAJFINANCE'), array.push(wts, 2.2)
        array.push(ids, 'NSE:M&M'), array.push(nms, 'M_M'), array.push(wts, 2.0)
        array.push(ids, 'NSE:MARUTI'), array.push(nms, 'MARUTI'), array.push(wts, 1.8)
        array.push(ids, 'NSE:ASIANPAINT'), array.push(nms, 'ASIANPAINT'), array.push(wts, 1.7)
        array.push(ids, 'NSE:HCLTECH'), array.push(nms, 'HCLTECH'), array.push(wts, 1.6)
        array.push(ids, 'NSE:SUNPHARMA'), array.push(nms, 'SUNPHARMA'), array.push(wts, 1.5)
        array.push(ids, 'NSE:TITAN'), array.push(nms, 'TITAN'), array.push(wts, 1.4)
        array.push(ids, 'NSE:TATAMOTORS'), array.push(nms, 'TATAMOTORS'), array.push(wts, 1.3)
    else if sectorKey == 'CNXAUTO'
        array.push(ids, 'NSE:MARUTI'), array.push(nms, 'MARUTI'), array.push(wts, 16.87)
        array.push(ids, 'NSE:M&M'), array.push(nms, 'M_M'), array.push(wts, 16.55)
        array.push(ids, 'NSE:BAJAJ_AUTO'), array.push(nms, 'BAJAJ_AUTO'), array.push(wts, 12.44)
        array.push(ids, 'NSE:EICHERMOT'), array.push(nms, 'EICHERMOT'), array.push(wts, 8.63)
        array.push(ids, 'NSE:TVSMOTOR'), array.push(nms, 'TVSMOTOR'), array.push(wts, 7.95)
        array.push(ids, 'NSE:MOTHERSON'), array.push(nms, 'MOTHERSON'), array.push(wts, 6.87)
        array.push(ids, 'NSE:BOSCHLTD'), array.push(nms, 'BOSCHLTD'), array.push(wts, 5.37)
        array.push(ids, 'NSE:TMPV'), array.push(nms, 'TMPV'), array.push(wts, 4.76)
        array.push(ids, 'NSE:HEROMOTOCO'), array.push(nms, 'HEROMOTOCO'), array.push(wts, 4.49)
        array.push(ids, 'NSE:ASHOKLEY'), array.push(nms, 'ASHOKLEY'), array.push(wts, 3.91)
        array.push(ids, 'NSE:BHARATFORG'), array.push(nms, 'BHARATFORG'), array.push(wts, 3.84)
        array.push(ids, 'NSE:UNOMINDA'), array.push(nms, 'UNOMINDA'), array.push(wts, 2.77)
        array.push(ids, 'NSE:TIINDIA'), array.push(nms, 'TIINDIA'), array.push(wts, 2.05)
        array.push(ids, 'NSE:SONACOMS'), array.push(nms, 'SONACOMS'), array.push(wts, 1.91)
        array.push(ids, 'NSE:EXIDEIND'), array.push(nms, 'EXIDEIND'), array.push(wts, 1.56)
    else if sectorKey == 'NIFTY_CONSR_DURBL'
        array.push(ids, 'NSE:TITAN'), array.push(nms, 'TITAN'), array.push(wts, 52.78)
        array.push(ids, 'NSE:DIXON'), array.push(nms, 'DIXON'), array.push(wts, 10.12)
        array.push(ids, 'NSE:HAVELLS'), array.push(nms, 'HAVELLS'), array.push(wts, 9.54)
        array.push(ids, 'NSE:KALYANKJIL'), array.push(nms, 'KALYANKJIL'), array.push(wts, 7.35)
        array.push(ids, 'NSE:VOLTAS'), array.push(nms, 'VOLTAS'), array.push(wts, 5.13)
        array.push(ids, 'NSE:BLUESTARCO'), array.push(nms, 'BLUESTARCO'), array.push(wts, 3.63)
        array.push(ids, 'NSE:AMBER'), array.push(nms, 'AMBER'), array.push(wts, 2.98)
        array.push(ids, 'NSE:KAJARIACER'), array.push(nms, 'KAJARIACER'), array.push(wts, 2.30)
        array.push(ids, 'NSE:PGEL'), array.push(nms, 'PGEL'), array.push(wts, 2.02)
        array.push(ids, 'NSE:CROMPTON'), array.push(nms, 'CROMPTON'), array.push(wts, 1.85)
        array.push(ids, 'NSE:WHIRLPOOL'), array.push(nms, 'WHIRLPOOL'), array.push(wts, 1.16)
        array.push(ids, 'NSE:BATAINDIA'), array.push(nms, 'BATAINDIA'), array.push(wts, 1.14)
    else if sectorKey == 'CNXIT'
        array.push(ids, 'NSE:TCS'), array.push(nms, 'TCS'), array.push(wts, 34.15)
        array.push(ids, 'NSE:INFY'), array.push(nms, 'INFY'), array.push(wts, 18.98)
        array.push(ids, 'NSE:HCLTECH'), array.push(nms, 'HCLTECH'), array.push(wts, 14.77)
        array.push(ids, 'NSE:WIPRO'), array.push(nms, 'WIPRO'), array.push(wts, 7.28)
        array.push(ids, 'NSE:TECHM'), array.push(nms, 'TECHM'), array.push(wts, 6.41)
        array.push(ids, 'NSE:LTM'), array.push(nms, 'LTM'), array.push(wts, 5.61)
        array.push(ids, 'NSE:OFSS'), array.push(nms, 'OFSS'), array.push(wts, 4.09)
        array.push(ids, 'NSE:PERSISTENT'), array.push(nms, 'PERSISTENT'), array.push(wts, 3.52)
        array.push(ids, 'NSE:COFORGE'), array.push(nms, 'COFORGE'), array.push(wts, 3.23)
        array.push(ids, 'NSE:MPHASIS'), array.push(nms, 'MPHASIS'), array.push(wts, 1.96)
    else if sectorKey == 'CNXPHARMA'
        array.push(ids, 'NSE:SUNPHARMA'), array.push(nms, 'SUNPHARMA'), array.push(wts, 22.18)
        array.push(ids, 'NSE:DIVISLAB'), array.push(nms, 'DIVISLAB'), array.push(wts, 10.83)
        array.push(ids, 'NSE:TORNTPHARM'), array.push(nms, 'TORNTPHARM'), array.push(wts, 8.84)
        array.push(ids, 'NSE:CIPLA'), array.push(nms, 'CIPLA'), array.push(wts, 5.62)
        array.push(ids, 'NSE:ZYDUSLIFE'), array.push(nms, 'ZYDUSLIFE'), array.push(wts, 5.46)
        array.push(ids, 'NSE:LUPIN'), array.push(nms, 'LUPIN'), array.push(wts, 4.91)
        array.push(ids, 'NSE:DRREDDY'), array.push(nms, 'DRREDDY'), array.push(wts, 4.82)
        array.push(ids, 'NSE:MANKIND'), array.push(nms, 'MANKIND'), array.push(wts, 4.80)
        array.push(ids, 'NSE:LAURUSLABS'), array.push(nms, 'LAURUSLABS'), array.push(wts, 4.71)
        array.push(ids, 'NSE:AUROPHARMA'), array.push(nms, 'AUROPHARMA'), array.push(wts, 4.58)
        array.push(ids, 'NSE:BIOCON'), array.push(nms, 'BIOCON'), array.push(wts, 3.25)
        array.push(ids, 'NSE:GLENMARK'), array.push(nms, 'GLENMARK'), array.push(wts, 3.17)
        array.push(ids, 'NSE:ALKEM'), array.push(nms, 'ALKEM'), array.push(wts, 3.10)
        array.push(ids, 'NSE:ABBOTINDIA'), array.push(nms, 'ABBOTINDIA'), array.push(wts, 2.76)
        array.push(ids, 'NSE:APOLLOHOSP'), array.push(nms, 'APOLLOHOSP'), array.push(wts, 5.73)
        array.push(ids, 'NSE:MAXHEALTH'), array.push(nms, 'MAXHEALTH'), array.push(wts, 4.39)
        array.push(ids, 'NSE:FORTIS'), array.push(nms, 'FORTIS'), array.push(wts, 3.15)
        array.push(ids, 'NSE:IPCALAB'), array.push(nms, 'IPCALAB'), array.push(wts, 1.96)
        array.push(ids, 'NSE:PPLPHARMA'), array.push(nms, 'PPLPHARMA'), array.push(wts, 1.23)
    else if sectorKey == 'CNXFMCG'
        array.push(ids, 'NSE:HINDUNILVR'), array.push(nms, 'HINDUNILVR'), array.push(wts, 26.87)
        array.push(ids, 'NSE:ITC'), array.push(nms, 'ITC'), array.push(wts, 19.04)
        array.push(ids, 'NSE:VBL'), array.push(nms, 'VBL'), array.push(wts, 8.08)
        array.push(ids, 'NSE:BRITANNIA'), array.push(nms, 'BRITANNIA'), array.push(wts, 7.32)
        array.push(ids, 'NSE:MARICO'), array.push(nms, 'MARICO'), array.push(wts, 6.16)
        array.push(ids, 'NSE:UNITDSPR'), array.push(nms, 'UNITDSPR'), array.push(wts, 6.05)
        array.push(ids, 'NSE:TATACONSUM'), array.push(nms, 'TATACONSUM'), array.push(wts, 5.86)
        array.push(ids, 'NSE:GODREJCP'), array.push(nms, 'GODREJCP'), array.push(wts, 5.24)
        array.push(ids, 'NSE:DABUR'), array.push(nms, 'DABUR'), array.push(wts, 3.96)
        array.push(ids, 'NSE:RADICO'), array.push(nms, 'RADICO'), array.push(wts, 3.41)
        array.push(ids, 'NSE:COLPAL'), array.push(nms, 'COLPAL'), array.push(wts, 2.95)
        array.push(ids, 'NSE:PATANJALI'), array.push(nms, 'PATANJALI'), array.push(wts, 2.10)
        array.push(ids, 'NSE:UBL'), array.push(nms, 'UBL'), array.push(wts, 1.99)
        array.push(ids, 'NSE:EMAMILTD'), array.push(nms, 'EMAMILTD'), array.push(wts, 0.96)
    else if sectorKey == 'CNXMETAL'
        array.push(ids, 'NSE:ADANIENT'), array.push(nms, 'ADANIENT'), array.push(wts, 18.89)
        array.push(ids, 'NSE:JSWSTEEL'), array.push(nms, 'JSWSTEEL'), array.push(wts, 14.22)
        array.push(ids, 'NSE:HINDZINC'), array.push(nms, 'HINDZINC'), array.push(wts, 10.90)
        array.push(ids, 'NSE:HINDALCO'), array.push(nms, 'HINDALCO'), array.push(wts, 10.67)
        array.push(ids, 'NSE:TATASTEEL'), array.push(nms, 'TATASTEEL'), array.push(wts, 10.51)
        array.push(ids, 'NSE:JINDALSTEL'), array.push(nms, 'JINDALSTEL'), array.push(wts, 5.15)
        array.push(ids, 'NSE:LLOYDSME'), array.push(nms, 'LLOYDSME'), array.push(wts, 4.96)
        array.push(ids, 'NSE:VEDL'), array.push(nms, 'VEDL'), array.push(wts, 4.84)
        array.push(ids, 'NSE:NMDC'), array.push(nms, 'NMDC'), array.push(wts, 3.41)
        array.push(ids, 'NSE:SAIL'), array.push(nms, 'SAIL'), array.push(wts, 3.21)
        array.push(ids, 'NSE:NATIONALUM'), array.push(nms, 'NATIONALUM'), array.push(wts, 3.17)
        array.push(ids, 'NSE:JSL'), array.push(nms, 'JSL'), array.push(wts, 2.79)
        array.push(ids, 'NSE:APLAPOLLO'), array.push(nms, 'APLAPOLLO'), array.push(wts, 2.67)
        array.push(ids, 'NSE:HINDCOPPER'), array.push(nms, 'HINDCOPPER'), array.push(wts, 2.35)
    else if sectorKey == 'CNXPSUBANK'
        array.push(ids, 'NSE:SBIN'), array.push(nms, 'SBIN'), array.push(wts, 51.84)
        array.push(ids, 'NSE:UNIONBANK'), array.push(nms, 'UNIONBANK'), array.push(wts, 7.51)
        array.push(ids, 'NSE:PNB'), array.push(nms, 'PNB'), array.push(wts, 7.10)
        array.push(ids, 'NSE:BANKBARODA'), array.push(nms, 'BANKBARODA'), array.push(wts, 6.75)
        array.push(ids, 'NSE:INDIANB'), array.push(nms, 'INDIANB'), array.push(wts, 6.37)
        array.push(ids, 'NSE:CANBK'), array.push(nms, 'CANBK'), array.push(wts, 6.26)
        array.push(ids, 'NSE:BANKINDIA'), array.push(nms, 'BANKINDIA'), array.push(wts, 3.44)
        array.push(ids, 'NSE:IOB'), array.push(nms, 'IOB'), array.push(wts, 3.40)
        array.push(ids, 'NSE:MAHABANK'), array.push(nms, 'MAHABANK'), array.push(wts, 3.24)
        array.push(ids, 'NSE:UCOBANK'), array.push(nms, 'UCOBANK'), array.push(wts, 1.71)
        array.push(ids, 'NSE:CENTRALBK'), array.push(nms, 'CENTRALBK'), array.push(wts, 1.49)
        array.push(ids, 'NSE:PSB'), array.push(nms, 'PSB'), array.push(wts, 0.88)
    else if sectorKey == 'BANKNIFTY'
        array.push(ids, 'NSE:HDFCBANK'), array.push(nms, 'HDFCBANK'), array.push(wts, 23.29)
        array.push(ids, 'NSE:ICICIBANK'), array.push(nms, 'ICICIBANK'), array.push(wts, 21.14)
        array.push(ids, 'NSE:SBIN'), array.push(nms, 'SBIN'), array.push(wts, 20.48)
        array.push(ids, 'NSE:KOTAKBANK'), array.push(nms, 'KOTAKBANK'), array.push(wts, 8.12)
        array.push(ids, 'NSE:AXISBANK'), array.push(nms, 'AXISBANK'), array.push(wts, 7.87)
        array.push(ids, 'NSE:UNIONBANK'), array.push(nms, 'UNIONBANK'), array.push(wts, 2.97)
        array.push(ids, 'NSE:PNB'), array.push(nms, 'PNB'), array.push(wts, 2.81)
        array.push(ids, 'NSE:BANKBARODA'), array.push(nms, 'BANKBARODA'), array.push(wts, 2.67)
        array.push(ids, 'NSE:CANBK'), array.push(nms, 'CANBK'), array.push(wts, 2.47)
        array.push(ids, 'NSE:FEDERALBNK'), array.push(nms, 'FEDERALBNK'), array.push(wts, 1.81)
        array.push(ids, 'NSE:AUBANK'), array.push(nms, 'AUBANK'), array.push(wts, 1.69)
        array.push(ids, 'NSE:INDUSINDBK'), array.push(nms, 'INDUSINDBK'), array.push(wts, 1.67)
        array.push(ids, 'NSE:IDFCFIRSTB'), array.push(nms, 'IDFCFIRSTB'), array.push(wts, 1.53)
        array.push(ids, 'NSE:YESBANK'), array.push(nms, 'YESBANK'), array.push(wts, 1.48)
    else if sectorKey == 'CNXFINANCE'
        array.push(ids, 'NSE:HDFCBANK'), array.push(nms, 'HDFCBANK'), array.push(wts, 17.31)
        array.push(ids, 'NSE:ICICIBANK'), array.push(nms, 'ICICIBANK'), array.push(wts, 15.71)
        array.push(ids, 'NSE:SBIN'), array.push(nms, 'SBIN'), array.push(wts, 15.22)
        array.push(ids, 'NSE:BAJFINANCE'), array.push(nms, 'BAJFINANCE'), array.push(wts, 10.46)
        array.push(ids, 'NSE:KOTAKBANK'), array.push(nms, 'KOTAKBANK'), array.push(wts, 6.04)
        array.push(ids, 'NSE:AXISBANK'), array.push(nms, 'AXISBANK'), array.push(wts, 5.85)
        array.push(ids, 'NSE:BAJAJFINSV'), array.push(nms, 'BAJAJFINSV'), array.push(wts, 5.02)
        array.push(ids, 'NSE:SHRIRAMFIN'), array.push(nms, 'SHRIRAMFIN'), array.push(wts, 4.08)
        array.push(ids, 'NSE:SBILIFE'), array.push(nms, 'SBILIFE'), array.push(wts, 2.80)
        array.push(ids, 'NSE:JIOFIN'), array.push(nms, 'JIOFIN'), array.push(wts, 2.55)
        array.push(ids, 'NSE:CHOLAFIN'), array.push(nms, 'CHOLAFIN'), array.push(wts, 2.51)
        array.push(ids, 'NSE:BSE'), array.push(nms, 'BSE'), array.push(wts, 2.17)
        array.push(ids, 'NSE:PFC'), array.push(nms, 'PFC'), array.push(wts, 1.92)
        array.push(ids, 'NSE:HDFCLIFE'), array.push(nms, 'HDFCLIFE'), array.push(wts, 1.80)
        array.push(ids, 'NSE:MUTHOOTFIN'), array.push(nms, 'MUTHOOTFIN'), array.push(wts, 1.00)
    else if sectorKey == 'NIFTY_OIL_AND_GAS'
        array.push(ids, 'NSE:RELIANCE'), array.push(nms, 'RELIANCE'), array.push(wts, 60.38)
        array.push(ids, 'NSE:ONGC'), array.push(nms, 'ONGC'), array.push(wts, 10.14)
        array.push(ids, 'NSE:IOC'), array.push(nms, 'IOC'), array.push(wts, 6.71)
        array.push(ids, 'NSE:BPCL'), array.push(nms, 'BPCL'), array.push(wts, 4.71)
        array.push(ids, 'NSE:GAIL'), array.push(nms, 'GAIL'), array.push(wts, 3.90)
        array.push(ids, 'NSE:HINDPETRO'), array.push(nms, 'HINDPETRO'), array.push(wts, 2.71)
        array.push(ids, 'NSE:OIL'), array.push(nms, 'OIL'), array.push(wts, 2.61)
        array.push(ids, 'NSE:ATGL'), array.push(nms, 'ATGL'), array.push(wts, 2.45)
        array.push(ids, 'NSE:AEGISLOG'), array.push(nms, 'AEGISLOG'), array.push(wts, 1.51)
        array.push(ids, 'NSE:PETRONET'), array.push(nms, 'PETRONET'), array.push(wts, 1.44)
        array.push(ids, 'NSE:AEGISVOPAK'), array.push(nms, 'AEGISVOPAK'), array.push(wts, 1.02)
        array.push(ids, 'NSE:IGL'), array.push(nms, 'IGL'), array.push(wts, 0.72)
        array.push(ids, 'NSE:CHENNPETRO'), array.push(nms, 'CHENNPETRO'), array.push(wts, 0.67)
        array.push(ids, 'NSE:CASTROLIND'), array.push(nms, 'CASTROLIND'), array.push(wts, 0.63)
    else if sectorKey == 'CNXENERGY'
        array.push(ids, 'NSE:RELIANCE'), array.push(nms, 'RELIANCE'), array.push(wts, 29.10)
        array.push(ids, 'NSE:ADANIPOWER'), array.push(nms, 'ADANIPOWER'), array.push(wts, 6.51)
        array.push(ids, 'NSE:NTPC'), array.push(nms, 'NTPC'), array.push(wts, 5.44)
        array.push(ids, 'NSE:ONGC'), array.push(nms, 'ONGC'), array.push(wts, 4.89)
        array.push(ids, 'NSE:COALINDIA'), array.push(nms, 'COALINDIA'), array.push(wts, 4.14)
        array.push(ids, 'NSE:POWERGRID'), array.push(nms, 'POWERGRID'), array.push(wts, 4.07)
        array.push(ids, 'NSE:ADANIGREEN'), array.push(nms, 'ADANIGREEN'), array.push(wts, 3.64)
        array.push(ids, 'NSE:ADANIENSOL'), array.push(nms, 'ADANIENSOL'), array.push(wts, 3.25)
        array.push(ids, 'NSE:IOC'), array.push(nms, 'IOC'), array.push(wts, 3.24)
        array.push(ids, 'NSE:ABB'), array.push(nms, 'ABB'), array.push(wts, 2.66)
        array.push(ids, 'NSE:POWERINDIA'), array.push(nms, 'POWERINDIA'), array.push(wts, 2.61)
        array.push(ids, 'NSE:BHEL'), array.push(nms, 'BHEL'), array.push(wts, 2.42)
        array.push(ids, 'NSE:CGPOWER'), array.push(nms, 'CGPOWER'), array.push(wts, 2.31)
        array.push(ids, 'NSE:SIEMENS'), array.push(nms, 'SIEMENS'), array.push(wts, 2.30)
    else if sectorKey == 'CNXPSE'
        array.push(ids, 'NSE:HAL'), array.push(nms, 'HAL'), array.push(wts, 10.75)
        array.push(ids, 'NSE:NTPC'), array.push(nms, 'NTPC'), array.push(wts, 10.59)
        array.push(ids, 'NSE:BEL'), array.push(nms, 'BEL'), array.push(wts, 9.61)
        array.push(ids, 'NSE:ONGC'), array.push(nms, 'ONGC'), array.push(wts, 9.53)
        array.push(ids, 'NSE:COALINDIA'), array.push(nms, 'COALINDIA'), array.push(wts, 8.06)
        array.push(ids, 'NSE:POWERGRID'), array.push(nms, 'POWERGRID'), array.push(wts, 7.94)
        array.push(ids, 'NSE:IOC'), array.push(nms, 'IOC'), array.push(wts, 6.31)
        array.push(ids, 'NSE:BHEL'), array.push(nms, 'BHEL'), array.push(wts, 4.71)
        array.push(ids, 'NSE:BPCL'), array.push(nms, 'BPCL'), array.push(wts, 4.42)
        array.push(ids, 'NSE:PFC'), array.push(nms, 'PFC'), array.push(wts, 3.99)
        array.push(ids, 'NSE:IRFC'), array.push(nms, 'IRFC'), array.push(wts, 3.67)
        array.push(ids, 'NSE:GAIL'), array.push(nms, 'GAIL'), array.push(wts, 3.67)
        array.push(ids, 'NSE:RECLTD'), array.push(nms, 'RECLTD'), array.push(wts, 2.83)
        array.push(ids, 'NSE:HINDPETRO'), array.push(nms, 'HINDPETRO'), array.push(wts, 2.54)
    else if sectorKey == 'SECTORS'
        array.push(ids, 'NSE:BANKNIFTY'), array.push(nms, 'BANKNIFTY'), array.push(wts, na)
        array.push(ids, 'NSE:CNXFINANCE'), array.push(nms, 'FINANCE'), array.push(wts, na)
        array.push(ids, 'NSE:CNXPSUBANK'), array.push(nms, 'PSU BANK'), array.push(wts, na)
        array.push(ids, 'NSE:CNXMETAL'), array.push(nms, 'METAL'), array.push(wts, na)
        array.push(ids, 'NSE:CNXFMCG'), array.push(nms, 'FMCG'), array.push(wts, na)
        array.push(ids, 'NSE:CNXAUTO'), array.push(nms, 'AUTO'), array.push(wts, na)
        array.push(ids, 'NSE:NIFTY_OIL_AND_GAS'), array.push(nms, 'OIL & GAS'), array.push(wts, na)
        array.push(ids, 'NSE:CNXPSE'), array.push(nms, 'PSE'), array.push(wts, na)
        array.push(ids, 'NSE:CNXIT'), array.push(nms, 'IT'), array.push(wts, na)
        array.push(ids, 'NSE:CNXENERGY'), array.push(nms, 'ENERGY'), array.push(wts, na)
        array.push(ids, 'NSE:CNXPHARMA'), array.push(nms, 'PHARMA'), array.push(wts, na)
        array.push(ids, 'NSE:NIFTY_CONSR_DURBL'), array.push(nms, 'CONSUMER DUR.'), array.push(wts, na)
    true

var string[] ids = array.new_string()
var string[] nms = array.new_string()
var float[] wts = array.new_float()
var string activeSector = na
sectorKey = resolveSector()

if bar_index == 0 or sectorKey != activeSector
    loadSector(sectorKey, ids, nms, wts)
    activeSector := sectorKey

nSym = math.min(array.size(ids), 20)
string finalBenchTicker = customBench

if defaultBType == 'Auto Sector'
    if sectorKey == 'SECTORS'
        finalBenchTicker := 'NSE:NIFTY'
    else
        finalBenchTicker := 'NSE:' + sectorKey

bmPx = request.security(finalBenchTicker, useTf, close, ignore_invalid_symbol=true, calc_bars_count=500)

swapStr(string[] arr, int i, int j) =>
    string tmp = array.get(arr, i)
    array.set(arr, i, array.get(arr, j))
    array.set(arr, j, tmp)
    true

swapFlt(float[] arr, int i, int j) =>
    float tmp = array.get(arr, i)
    array.set(arr, i, array.get(arr, j))
    array.set(arr, j, tmp)
    true

swapInt(int[] arr, int i, int j) =>
    int tmp = array.get(arr, i)
    array.set(arr, i, array.get(arr, j))
    array.set(arr, j, tmp)
    true

swapClr(color[] arr, int i, int j) =>
    color tmp = array.get(arr, i)
    array.set(arr, i, array.get(arr, j))
    array.set(arr, j, tmp)
    true

// Stock-only % change: last completed week on chart TF <= D, last completed month on TF >= W.
pctChg(string sym) =>
    string ptf = weekPctMode ? 'W' : 'M'
    request.security(sym, ptf, (close / close[1] - 1.0) * 100.0, ignore_invalid_symbol=true, calc_bars_count=500)

// Anchored RS calculation helper
calcRS(float stockPx, float benchPx) =>
    var float anchorStockPrice = na
    var float anchorBenchPrice = na

    bool isAnchorBar = time >= historyDateARS and time[1] < historyDateARS

    if flagARS
        if isAnchorBar
            anchorStockPrice := stockPx
            anchorBenchPrice := benchPx
    else
        anchorStockPrice := stockPx[rsLen]
        anchorBenchPrice := benchPx[rsLen]

    float ratioStock = stockPx / anchorStockPrice
    float ratioBench = benchPx / anchorBenchPrice

    float rs = ratioBench == 0 or na(ratioBench) or na(ratioStock) ? na : (ratioStock / ratioBench - 1.0) * 100.0
    rs

"""
with open('rsc_sector.pine', 'w') as f:
    f.write(code)
