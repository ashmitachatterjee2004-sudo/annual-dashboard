
import json
import re
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Annual Report Dashboard",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_CSS = """
<style>
:root{
  --bg1:#f7fafc;
  --bg2:#eef7f0;
  --card:#ffffff;
  --text:#1f2937;
  --muted:#6b7280;
  --border:#d9e3d6;
  --green:#cfe3c7;
  --green-dark:#5a7d4d;
  --nav:#0f172a;
  --nav2:#163047;
  --accent:#7a1f5c;
  --accent2:#b88746;
  --shadow:0 12px 28px rgba(15,23,42,.08);
}
.stApp{
  background:
    radial-gradient(1200px 500px at 0% 0%, rgba(90,125,77,.08), rgba(255,255,255,0) 60%),
    linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 100%);
}
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, var(--nav) 0%, var(--nav2) 100%);
  border-right: 1px solid rgba(255,255,255,.06);
}
section[data-testid="stSidebar"] *{ color: rgba(255,255,255,.95) !important; }
.hero{
  position:relative;
  overflow:hidden;
  border-radius:24px;
  padding:24px 24px 20px;
  margin-bottom:16px;
  color:white;
  background:
    radial-gradient(280px 180px at 100% 0%, rgba(255,255,255,.16), rgba(255,255,255,0) 70%),
    linear-gradient(135deg, #274e3d 0%, #5a7d4d 52%, #7a1f5c 100%);
  box-shadow:0 16px 36px rgba(15,23,42,.18);
}
.hero h1{ margin:0; font-size:34px; line-height:1.1; font-weight:900; }
.hero p{ margin:8px 0 0 0; font-size:14px; color:rgba(255,255,255,.90); }
.hero-meta{ margin-top:12px; display:flex; flex-wrap:wrap; gap:8px; }
.hero-chip{
  display:inline-flex; align-items:center; gap:6px;
  padding:7px 10px; border-radius:999px;
  background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.18);
  font-size:12px; font-weight:800;
}
.kpi{
  background:rgba(255,255,255,.94);
  border:1px solid var(--border);
  border-radius:18px;
  box-shadow:var(--shadow);
  padding:14px 16px;
  min-height:96px;
}
.kpi-label{ font-size:12px; text-transform:uppercase; letter-spacing:.4px; color:var(--muted); font-weight:800; margin-bottom:6px; }
.kpi-value{ font-size:24px; line-height:1.05; font-weight:900; color:var(--text); word-break:break-word; }
.kpi-sub{ margin-top:6px; font-size:12px; color:var(--muted); font-weight:700; }
.section-title{ font-size:20px; font-weight:900; color:var(--text); margin:4px 0 10px; }
.note{ color:var(--muted); font-size:12.5px; font-weight:600; }
.block{
  background:rgba(255,255,255,.88);
  border:1px solid var(--border);
  border-radius:18px;
  box-shadow:var(--shadow);
  padding:14px 16px;
}
.report-band{
  background:linear-gradient(90deg, #d9ead3 0%, #eef7ea 100%);
  border:1px solid #c8dcc2;
  color:#254117;
  border-radius:14px;
  padding:10px 14px;
  font-size:15px;
  font-weight:900;
  margin:4px 0 10px;
}
.small-gap{ height:10px; }
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)

RAW = r"""{
  "annual_trends": [
    {
      "year": "2017-18",
      "exports_bn": 43.2,
      "imports_bn": 28.7993357850424,
      "bot_bn": 14.400664214957605,
      "export_growth_pct": null,
      "import_growth_pct": null
    },
    {
      "year": "2018-19",
      "exports_bn": 41.01,
      "imports_bn": 31.6897748334721,
      "bot_bn": 9.320225166527898,
      "export_growth_pct": -5.06944444444446,
      "import_growth_pct": 10.036478167426765
    },
    {
      "year": "2019-20",
      "exports_bn": 39.76,
      "imports_bn": 26.5688527934214,
      "bot_bn": 13.191147206578599,
      "export_growth_pct": -3.048037064130704,
      "import_growth_pct": -16.159540630884393
    },
    {
      "year": "2020-21",
      "exports_bn": 35.65,
      "imports_bn": 24.52,
      "bot_bn": 11.129999999999999,
      "export_growth_pct": -10.33702213279678,
      "import_growth_pct": -7.711483854239686
    },
    {
      "year": "2021-22",
      "exports_bn": 25.51,
      "imports_bn": 16.49,
      "bot_bn": 9.020000000000003,
      "export_growth_pct": -28.443197755960725,
      "import_growth_pct": -32.74877650897228
    },
    {
      "year": "2022-23",
      "exports_bn": 39.58,
      "imports_bn": 26.87057,
      "bot_bn": 12.709429999999998,
      "export_growth_pct": 55.15484123872989,
      "import_growth_pct": 62.95069739235903
    },
    {
      "year": "2023-24",
      "exports_bn": 37.77,
      "imports_bn": 25.904345000000003,
      "bot_bn": 11.865655,
      "export_growth_pct": -4.5730166750884145,
      "import_growth_pct": -3.5958485435924836
    },
    {
      "year": "2024-25",
      "exports_bn": 32.33,
      "imports_bn": 22.31,
      "bot_bn": 10.02,
      "export_growth_pct": -14.402965316388682,
      "import_growth_pct": -13.875452168352464
    },
    {
      "year": "2025-26",
      "exports_bn": 28.72,
      "imports_bn": 19.71,
      "bot_bn": 9.009999999999998,
      "export_growth_pct": -11.166099597896684,
      "import_growth_pct": -11.65396683101747
    },
    {
      "year": "2026-27 (p)",
      "exports_bn": 27.62,
      "imports_bn": 22.83,
      "bot_bn": 4.790000000000003,
      "export_growth_pct": -3.8300835654596077,
      "import_growth_pct": 15.829528158295258
    }
  ],
  "gross_net_exports": [
    {
      "metric": "Gross Exports",
      "fy2024_mn": 32327.94599571961,
      "fy2025_mn": 28715.64027581346,
      "fy2026p_mn": 27616.39,
      "growth_fy25_vs_fy24_pct": -11.17394133355839
    },
    {
      "metric": "Return Consignment",
      "fy2024_mn": 6237.86380742037,
      "fy2025_mn": 5197.42058235703,
      "fy2026p_mn": null,
      "growth_fy25_vs_fy24_pct": -16.6794796613812
    },
    {
      "metric": "Net Exports",
      "fy2024_mn": 26090.08218829924,
      "fy2025_mn": 23518.21969345643,
      "fy2026p_mn": null,
      "growth_fy25_vs_fy24_pct": -9.857625117011803
    }
  ],
  "monthly_exports": [
  {
    "month": "April",
    "fy2025_mn": 2268.090061840444,
    "fy2026_mn": 2571.711077551109,
    "growth_pct": 13.386638424062024
  },
  {
    "month": "May",
    "fy2025_mn": 2688.51190640103,
    "fy2026_mn": 2289.793061078913,
    "growth_pct": -14.830466042304458
  },
  {
    "month": "June",
    "fy2025_mn": 1965.3493866889594,
    "fy2026_mn": 1749.186115254912,
    "growth_pct": -10.998719764439413
  },
  {
    "month": "July",
    "fy2025_mn": 1878.1118959396003,
    "fy2026_mn": 2341.385867954898,
    "growth_pct": 24.66700589122921
  },
  {
    "month": "August",
    "fy2025_mn": 2062.5061689857944,
    "fy2026_mn": 2228.9306237141536,
    "growth_pct": 8.069040336989431
  },
  {
    "month": "September",
    "fy2025_mn": 2735.382320252486,
    "fy2026_mn": 2915.660643206169,
    "growth_pct": 6.590607887567357
  },
  {
    "month": "October",
    "fy2025_mn": 3159.209888212982,
    "fy2026_mn": 2259.8983717473225,
    "growth_pct": -28.466342797323875
  },
  {
    "month": "November",
    "fy2025_mn": 2098.594761267675,
    "fy2026_mn": 2528.6129035786507,
    "growth_pct": 20.490766023413663
  },
  {
    "month": "December",
    "fy2025_mn": 2103.887462434016,
    "fy2026_mn": 2080.5707990090536,
    "growth_pct": -1.1082657148394737
  },
  {
    "month": "January",
    "fy2025_mn": 2376.018947495949,
    "fy2026_mn": 2287.185203035232,
    "growth_pct": -3.7387641438776154
  },
  {
    "month": "February",
    "fy2025_mn": 2581.4485698010935,
    "fy2026_mn": 2580.6878691774514,
    "growth_pct": -0.029467975172592364
  },
  {
    "month": "March",
    "fy2025_mn": 2753.9489649176726,
    "fy2026_mn": 1783.673806152366,
    "growth_pct": -35.23214014223072
  }
],
  "overall_target": {
    "target_bn": 35.15,
    "actual_bn": 28.72,
    "achieved_pct": 81.70697012802276
  },
  "region_targets": [
    {
      "region": "ASEAN",
      "target_mn": 1717.8,
      "actual_mn": 1293.16,
      "deficit_surplus_mn": -424.6399999999999,
      "achieved_pct": 75.28000931423915
    },
    {
      "region": "WANA",
      "target_mn": 10176.5,
      "actual_mn": 8876.26,
      "deficit_surplus_mn": -1300.2399999999998,
      "achieved_pct": 87.22311207193043
    },
    {
      "region": "AFRICA",
      "target_mn": 95.8,
      "actual_mn": 167.59,
      "deficit_surplus_mn": 71.79,
      "achieved_pct": 174.937369519833
    },
    {
      "region": "NEA",
      "target_mn": 7123.3,
      "actual_mn": 4928.47,
      "deficit_surplus_mn": -2194.83,
      "achieved_pct": 69.18801678997094
    },
    {
      "region": "OCEANIA",
      "target_mn": 330.8,
      "actual_mn": 343.94,
      "deficit_surplus_mn": 13.139999999999986,
      "achieved_pct": 103.97218863361547
    },
    {
      "region": "EUROPE",
      "target_mn": 4447.5,
      "actual_mn": 4015.1,
      "deficit_surplus_mn": -432.4000000000001,
      "achieved_pct": 90.27768409218662
    },
    {
      "region": "SOUTH ASIA",
      "target_mn": 73.7,
      "actual_mn": 55.27,
      "deficit_surplus_mn": -18.43,
      "achieved_pct": 74.9932157394844
    },
    {
      "region": "NAFTA",
      "target_mn": 11120.3,
      "actual_mn": 10193.82,
      "deficit_surplus_mn": -926.4799999999996,
      "achieved_pct": 91.66857009253347
    },
    {
      "region": "LAC",
      "target_mn": 18.6,
      "actual_mn": 23.11,
      "deficit_surplus_mn": 4.509999999999998,
      "achieved_pct": 124.24731182795699
    },
    {
      "region": "CIS",
      "target_mn": 49.3,
      "actual_mn": 45.21,
      "deficit_surplus_mn": -4.089999999999996,
      "achieved_pct": 91.70385395537525
    },
    {
      "region": "TOTAL",
      "target_mn": 35153.6,
      "actual_mn": 29941.93,
      "deficit_surplus_mn": -5211.669999999998,
      "achieved_pct": 85.17457671476038
    }
  ],
  "country_targets": [
    {
      "country": "U S A",
      "target_mn": 10897.8,
      "actual_mn": 9973.78,
      "deficit_surplus_mn": -924.0199999999986,
      "achieved_pct": 91.52104094404376
    },
    {
      "country": "HONG KONG",
      "target_mn": 6726.8,
      "actual_mn": 4567.91,
      "deficit_surplus_mn": -2158.8900000000003,
      "achieved_pct": 67.90613664744008
    },
    {
      "country": "U ARAB EMTS",
      "target_mn": 8839.9,
      "actual_mn": 7758.91,
      "deficit_surplus_mn": -1080.9899999999998,
      "achieved_pct": 87.7714680030317
    },
    {
      "country": "BELGIUM",
      "target_mn": 2308.8,
      "actual_mn": 1608.39,
      "deficit_surplus_mn": -700.4100000000001,
      "achieved_pct": 69.66346153846153
    },
    {
      "country": "U.K.",
      "target_mn": 594.0,
      "actual_mn": 982.36,
      "deficit_surplus_mn": 388.36,
      "achieved_pct": 165.3804713804714
    },
    {
      "country": "ISRAEL",
      "target_mn": 854.8,
      "actual_mn": 612.82,
      "deficit_surplus_mn": -241.9799999999999,
      "achieved_pct": 71.6916237716425
    },
    {
      "country": "SINGAPORE",
      "target_mn": 735.7,
      "actual_mn": 554.54,
      "deficit_surplus_mn": -181.16000000000008,
      "achieved_pct": 75.37583254043767
    },
    {
      "country": "THAILAND",
      "target_mn": 795.6,
      "actual_mn": 527.44,
      "deficit_surplus_mn": -268.15999999999997,
      "achieved_pct": 66.29462041226748
    },
    {
      "country": "SWITZERLAND",
      "target_mn": 588.1,
      "actual_mn": 467.0,
      "deficit_surplus_mn": -121.10000000000002,
      "achieved_pct": 79.40826390069716
    },
    {
      "country": "France",
      "target_mn": 325.5,
      "actual_mn": 326.87,
      "deficit_surplus_mn": 1.3700000000000045,
      "achieved_pct": 100.42089093701998
    },
    {
      "country": "Sub Total",
      "target_mn": 32667.0,
      "actual_mn": 27380.02,
      "deficit_surplus_mn": -5286.98,
      "achieved_pct": 83.81553249456638
    }
  ],
  "commodity_targets": [
    {
      "commodity": "Cut & Polished Diamonds",
      "target_mn": 16432.928,
      "actual_mn": 13292.43,
      "deficit_surplus_mn": -3140.4979999999996,
      "share_pct": 46.30568076240959,
      "achieved_pct": 80.88899312404946
    },
    {
      "commodity": "Plain Gold Jewellery including articles of Gold",
      "target_mn": 6906.7332,
      "actual_mn": 5235.58,
      "deficit_surplus_mn": -1671.1531999999997,
      "share_pct": 18.238734082937157,
      "achieved_pct": 75.80399949429058
    },
    {
      "commodity": "Studded Gold Jewellery",
      "target_mn": 5746.1421,
      "actual_mn": 6136.0,
      "deficit_surplus_mn": 389.8579,
      "share_pct": 21.37544881997838,
      "achieved_pct": 106.78468950498107
    },
    {
      "commodity": "Platinum Jewellery",
      "target_mn": 342.27845,
      "actual_mn": 172.94,
      "deficit_surplus_mn": -169.33845000000002,
      "share_pct": 0.6024560167742928,
      "achieved_pct": 50.52611404545042
    },
    {
      "commodity": "Silver Jewellery including articles of silver",
      "target_mn": 1868.5821,
      "actual_mn": 978.74,
      "deficit_surplus_mn": -889.8421000000001,
      "share_pct": 3.4095513002062643,
      "achieved_pct": 52.3787528522295
    },
    {
      "commodity": "Lab Grown Diamonds, unworked & worked",
      "target_mn": 1519.6069,
      "actual_mn": 1323.34,
      "deficit_surplus_mn": -196.26690000000008,
      "share_pct": 4.61000430922917,
      "achieved_pct": 87.08436372590832
    },
    {
      "commodity": "Colored gemstones & Articles of Precious/Semi Precious Stones",
      "target_mn": 628.33215,
      "actual_mn": 475.54,
      "deficit_surplus_mn": -152.79214999999994,
      "share_pct": 1.6565972835483243,
      "achieved_pct": 75.68290115347432
    },
    {
      "commodity": "Pearls worked & Articles of pearls",
      "target_mn": 7.2762549,
      "actual_mn": 5.36,
      "deficit_surplus_mn": -1.9162548999999993,
      "share_pct": 0.018672165201284896,
      "achieved_pct": 73.66426923828632
    },
    {
      "commodity": "Synthetic Stones, unworked & worked",
      "target_mn": 19.090754,
      "actual_mn": 12.1,
      "deficit_surplus_mn": -6.990754000000001,
      "share_pct": 0.04215171621931851,
      "achieved_pct": 63.3814672799199
    },
    {
      "commodity": "Imitation Jewellery",
      "target_mn": 237.45668,
      "actual_mn": 65.7,
      "deficit_surplus_mn": -171.75668000000002,
      "share_pct": 0.22887336823216747,
      "achieved_pct": 27.66820457525137
    },
    {
      "commodity": "Others",
      "target_mn": 1455.66,
      "actual_mn": 1008.1,
      "deficit_surplus_mn": -447.56000000000006,
      "share_pct": 3.511830175264049,
      "achieved_pct": 69.2538092686479
    }
  ],
  "export_key_commodities": [
    {
      "commodity": "Cut & Polished Diamonds",
      "fy2024_mn": 15967.0155910242,
      "fy2025_mn": 13292.4306358316,
      "growth_pct": -16.750687941308872
    },
    {
      "commodity": "Polished Lab Grown Diamonds",
      "fy2024_mn": 1402.43621641437,
      "fy2025_mn": 1267.27774263363,
      "growth_pct": -9.637406122205094
    },
    {
      "commodity": "Coloured Gemstones",
      "fy2024_mn": 478.70955814074,
      "fy2025_mn": 440.443629575932,
      "growth_pct": -7.99355849785599
    },
    {
      "commodity": "Polished Synthetic Stones",
      "fy2024_mn": 13.8914534588718,
      "fy2025_mn": 11.5249714561311,
      "growth_pct": -17.0355248264489
    },
    {
      "commodity": "Pearls - Worked",
      "fy2024_mn": 8.28190903357442,
      "fy2025_mn": 4.86980026125159,
      "growth_pct": -41.19954419313617
    },
    {
      "commodity": "Plain Gold Jewellery",
      "fy2024_mn": 5873.20414936061,
      "fy2025_mn": 5231.76813682332,
      "growth_pct": -10.921398204881417
    },
    {
      "commodity": "Studded Gold Jewellery",
      "fy2024_mn": 5356.96795570596,
      "fy2025_mn": 6136.00223949568,
      "growth_pct": 14.542448083153726
    },
    {
      "commodity": "Total Gold Jewellery",
      "fy2024_mn": 11230.17210506657,
      "fy2025_mn": 11367.770376319,
      "growth_pct": 1.225255231755118
    },
    {
      "commodity": "Silver Jewellery",
      "fy2024_mn": 1618.97495959602,
      "fy2025_mn": 964.658801921387,
      "growth_pct": -40.41545879362479
    },
    {
      "commodity": "Platinum Jewellery",
      "fy2024_mn": 163.478501392917,
      "fy2025_mn": 182.752189075454,
      "growth_pct": 11.789738417171503
    },
    {
      "commodity": "Imitation Jewellery",
      "fy2024_mn": 66.4145726296881,
      "fy2025_mn": 65.6984476877835,
      "growth_pct": -1.0782647746565233
    },
    {
      "commodity": "Articles of Gold, Silver & Others",
      "fy2024_mn": 54.2792947092569,
      "fy2025_mn": 56.3682473007683,
      "growth_pct": 3.848525672083114
    },
    {
      "commodity": "Gold Medallions & Coin",
      "fy2024_mn": 200.779907648462,
      "fy2025_mn": 120.404896159701,
      "growth_pct": -40.03140176231508
    },
    {
      "commodity": "Sales to Foreign Tourist",
      "fy2024_mn": 42.1,
      "fy2025_mn": 44.58,
      "growth_pct": 5.890736342042757
    },
    {
      "commodity": "Sub - Total",
      "fy2024_mn": 31246.534069114667,
      "fy2025_mn": 27818.779738222638,
      "growth_pct": -10.970030542619957
    },
    {
      "commodity": "Exports of Rough-Diamonds",
      "fy2024_mn": 917.315951412623,
      "fy2025_mn": 416.51,
      "growth_pct": -54.594706506673695
    },
    {
      "commodity": "Rgh Lab Grown Syn. Diamonds",
      "fy2024_mn": 83.4393338400182,
      "fy2025_mn": 56.06,
      "growth_pct": -32.81346168524518
    },
    {
      "commodity": "Others",
      "fy2024_mn": 80.65664135228872,
      "fy2025_mn": 424.2905960150638,
      "growth_pct": 426.0454550318616
    },
    {
      "commodity": "Gross Exports",
      "fy2024_mn": 32327.945995719598,
      "fy2025_mn": 28715.6403342377,
      "growth_pct": -11.173941152834722
    },
    {
      "commodity": "Return Consignment Others",
      "fy2024_mn": 5386.992857197,
      "fy2025_mn": 4446.76281811982,
      "growth_pct": -17.453708664585232
    },
    {
      "commodity": "Return Consignment CPD",
      "fy2024_mn": 850.870950223379,
      "fy2025_mn": 750.657764237216,
      "growth_pct": -11.777718578810815
    },
    {
      "commodity": "Net Exports",
      "fy2024_mn": 26090.082188299217,
      "fy2025_mn": 23518.219751880664,
      "growth_pct": -9.857624893078999
    }
  ],
  "export_basket": [
    {
      "commodity": "Cut & Polished Diamonds",
      "fy2020_mn": 18664.8946511777,
      "fy2025_mn": 13292.4306358316,
      "fy2020_share_pct": 52.361232019766824,
      "fy2025_share_pct": 46.28986322823877,
      "change_mn": -5372.464015346099
    },
    {
      "commodity": "Gold Jewellery",
      "fy2020_mn": 12039.7981328207,
      "fy2025_mn": 11367.7703763189,
      "fy2020_share_pct": 33.77563470276553,
      "fy2025_share_pct": 39.587382499581906,
      "change_mn": -672.0277565018005
    },
    {
      "commodity": "Silver Jewellery",
      "fy2020_mn": 1686.83457248375,
      "fy2025_mn": 964.658801921386,
      "fy2020_share_pct": 4.732131527097196,
      "fy2025_share_pct": 3.359349785319681,
      "change_mn": -722.1757705623639
    },
    {
      "commodity": "Polished Lab Grown Diamonds ",
      "fy2020_mn": 421.092310567775,
      "fy2025_mn": 1267.27774263363,
      "fy2020_share_pct": 1.1813038641494693,
      "fy2025_share_pct": 4.413196877670364,
      "change_mn": 846.1854320658549
    },
    {
      "commodity": "Coloured Gem Stone",
      "fy2020_mn": 320.82,
      "fy2025_mn": 440.44,
      "fy2020_share_pct": 0.9000067115579276,
      "fy2025_share_pct": 1.533798288575382,
      "change_mn": 119.62
    },
    {
      "commodity": "Imitation Jewellery",
      "fy2020_mn": 59.97,
      "fy2025_mn": 65.7,
      "fy2020_share_pct": 0.16823577860522698,
      "fy2025_share_pct": 0.22879517654936565,
      "change_mn": 5.730000000000004
    },
    {
      "commodity": "Gold Medallions",
      "fy2020_mn": 831.99,
      "fy2025_mn": 120.4,
      "fy2020_share_pct": 2.334008428243502,
      "fy2025_share_pct": 0.4192837025349106,
      "change_mn": -711.59
    },
    {
      "commodity": "Others",
      "fy2020_mn": 1621.001174189907,
      "fy2025_mn": 1196.962777532186,
      "fy2020_share_pct": 4.547446967814343,
      "fy2025_share_pct": 4.168330441529613,
      "change_mn": -424.038396657721
    },
    {
      "commodity": "Total Exports",
      "fy2020_mn": 35646.400841239825,
      "fy2025_mn": 28715.6403342377,
      "fy2020_share_pct": 100.0,
      "fy2025_share_pct": 100.0,
      "change_mn": -6930.760507002124
    }
  ],
  "export_regions": [
    {
      "region": "USA & Canada",
      "fy2020_mn": 9245.02,
      "fy2025_mn": 9393.74,
      "fy2020_share_pct": 25.935353920732535,
      "fy2025_share_pct": 32.71297415158049,
      "growth_pct": 1.6086498460792908
    },
    {
      "region": "Europe",
      "fy2020_mn": 3264.0499999999997,
      "fy2025_mn": 3624.2999999999997,
      "fy2020_share_pct": 9.156745141164325,
      "fy2025_share_pct": 12.621344876223226,
      "growth_pct": 11.0369020082413
    },
    {
      "region": "Asia",
      "fy2020_mn": 11429.7,
      "fy2025_mn": 6214.14,
      "fy2020_share_pct": 32.06410745545133,
      "fy2025_share_pct": 21.64026268496918,
      "growth_pct": -45.63164387516733
    },
    {
      "region": "Middle East",
      "fy2020_mn": 11263.73,
      "fy2025_mn": 8933.76,
      "fy2020_share_pct": 31.59850644104314,
      "fy2025_share_pct": 31.111129321912646,
      "growth_pct": -20.685598820284213
    },
    {
      "region": "East Asia (Oceania)",
      "fy2020_mn": 204.65,
      "fy2025_mn": 275.74,
      "fy2020_share_pct": 0.574111270703353,
      "fy2025_share_pct": 0.9602432569516299,
      "growth_pct": 34.73735646225262
    },
    {
      "region": "Africa",
      "fy2020_mn": 162.54,
      "fy2025_mn": 177.81,
      "fy2020_share_pct": 0.4559787243592621,
      "fy2025_share_pct": 0.6192095942502694,
      "growth_pct": 9.394610557401272
    },
    {
      "region": "LAC",
      "fy2020_mn": 7.88,
      "fy2025_mn": 8.81,
      "fy2020_share_pct": 0.022106019121145477,
      "fy2025_share_pct": 0.03068014467884188,
      "growth_pct": 11.802030456852798
    },
    {
      "region": "Other CIS Countries",
      "fy2020_mn": 15.68,
      "fy2025_mn": 31.8,
      "fy2020_share_pct": 0.043987611652228566,
      "fy2025_share_pct": 0.1107410443572272,
      "growth_pct": 102.80612244897962
    },
    {
      "region": "Others ",
      "fy2020_mn": 53.14999999999418,
      "fy2025_mn": 55.60033423769579,
      "fy2020_share_pct": 0.14910341577268443,
      "fy2025_share_pct": 0.19362387044318644,
      "growth_pct": 4.610224341866198
    },
    {
      "region": "TOTAL",
      "fy2020_mn": 35646.399999999994,
      "fy2025_mn": 28715.6403342377,
      "fy2020_share_pct": 100.0,
      "fy2025_share_pct": 100.0,
      "growth_pct": null
    }
  ],
  "top_export_destinations": {
    "fy2020": [
      {
        "country": "U.A.E",
        "amount_mn": 9492.984321490425,
        "share_pct": 26.630976259847905
      },
      {
        "country": "Hongkong",
        "amount_mn": 9489.359852446765,
        "share_pct": 26.62080841949472
      },
      {
        "country": "U.S.A",
        "amount_mn": 9175.938365387541,
        "share_pct": 25.7415569745824
      },
      {
        "country": "Belgium",
        "amount_mn": 1899.7608981285093,
        "share_pct": 5.329460753760574
      },
      {
        "country": "Israel",
        "amount_mn": 911.1611355157959,
        "share_pct": 2.556109833014823
      },
      {
        "country": "Thailand",
        "amount_mn": 637.4435912230606,
        "share_pct": 1.7882411441914488
      },
      {
        "country": "Turkey",
        "amount_mn": 636.0927139287014,
        "share_pct": 1.784451484381877
      },
      {
        "country": "Singapore",
        "amount_mn": 618.607983830036,
        "share_pct": 1.7354010049543178
      },
      {
        "country": "United kingdom",
        "amount_mn": 446.55689089266457,
        "share_pct": 1.2527405036487964
      },
      {
        "country": "Japan",
        "amount_mn": 391.7879709318789,
        "share_pct": 1.0990954792963072
      },
      {
        "country": "Others",
        "amount_mn": 1946.7062762246132,
        "share_pct": 5.461158142826802
      },
      {
        "country": "Total",
        "amount_mn": 35646.399999999994,
        "share_pct": 99.99999999999997
      }
    ],
    "fy2025": [
      {
        "country": "U.S.A",
        "amount_mn": 9236.455445361626,
        "share_pct": 32.165242835796995
      },
      {
        "country": "U.A.E",
        "amount_mn": 7868.164367768049,
        "share_pct": 27.40027481952692
      },
      {
        "country": "Hongkong",
        "amount_mn": 4559.14445804418,
        "share_pct": 15.876868511298023
      },
      {
        "country": "Belgium",
        "amount_mn": 1189.9955640207957,
        "share_pct": 4.144067658494671
      },
      {
        "country": "United Kingdom",
        "amount_mn": 777.6862218453056,
        "share_pct": 2.7082322135023715
      },
      {
        "country": "Israel",
        "amount_mn": 548.2704669628273,
        "share_pct": 1.9093095629461678
      },
      {
        "country": "Singapore",
        "amount_mn": 529.390290464284,
        "share_pct": 1.8435608062449895
      },
      {
        "country": "Thailand",
        "amount_mn": 525.5566076295394,
        "share_pct": 1.8302103018156188
      },
      {
        "country": "Switzerland",
        "amount_mn": 517.7381933243774,
        "share_pct": 1.8029832777473447
      },
      {
        "country": "Netherland",
        "amount_mn": 414.8931236810223,
        "share_pct": 1.444833264561907
      },
      {
        "country": "Others",
        "amount_mn": 2548.3455951356955,
        "share_pct": 8.874416748064988
      },
      {
        "country": "Total",
        "amount_mn": 28715.6403342377,
        "share_pct": 100.0
      }
    ]
  },
  "export_port_performance": [
    {
      "region": "Western Region",
      "port": "Mumbai",
      "fy2024_port_mn": 22186.7438282117,
      "fy2024_region_total_mn": 22186.7438282117,
      "fy2025_port_mn": 19653.24,
      "fy2025_region_total_mn": 19653.24,
      "growth_pct": -11.42
    },
    {
      "region": "Northern Region",
      "port": "Delhi",
      "fy2024_port_mn": 3116.53885376124,
      "fy2024_region_total_mn": 3116.53885376124,
      "fy2025_port_mn": 1675.8,
      "fy2025_region_total_mn": 1675.8,
      "growth_pct": -46.23
    },
    {
      "region": "Rajasthan Region",
      "port": "Jaipur",
      "fy2024_port_mn": 1360.80137526203,
      "fy2024_region_total_mn": 1360.80137526203,
      "fy2025_port_mn": 2104.53,
      "fy2025_region_total_mn": 2104.53,
      "growth_pct": 54.65
    },
    {
      "region": "Eastern Region",
      "port": "Kolkata",
      "fy2024_port_mn": 1262.62253911334,
      "fy2024_region_total_mn": 1262.62253911334,
      "fy2025_port_mn": 1650.5,
      "fy2025_region_total_mn": 1650.5,
      "growth_pct": 30.72
    },
    {
      "region": "Gujarat Region",
      "port": "Surat",
      "fy2024_port_mn": 2715.29122198328,
      "fy2024_region_total_mn": null,
      "fy2025_port_mn": 1684.6200000000001,
      "fy2025_region_total_mn": null,
      "growth_pct": -37.96
    },
    {
      "region": null,
      "port": "Ahmedabad",
      "fy2024_port_mn": 519.334575739811,
      "fy2024_region_total_mn": null,
      "fy2025_port_mn": 295.28,
      "fy2025_region_total_mn": null,
      "growth_pct": -43.14
    },
    {
      "region": "Gujarat Region Total",
      "port": null,
      "fy2024_port_mn": null,
      "fy2024_region_total_mn": 3234.625797723091,
      "fy2025_port_mn": null,
      "fy2025_region_total_mn": 1979.9,
      "growth_pct": -38.79
    },
    {
      "region": "Southern Region",
      "port": "Bangalore",
      "fy2024_port_mn": 181.288272538332,
      "fy2024_region_total_mn": null,
      "fy2025_port_mn": 238.28,
      "fy2025_region_total_mn": null,
      "growth_pct": 31.44
    },
    {
      "region": null,
      "port": "Chennai",
      "fy2024_port_mn": 582.116615868315,
      "fy2024_region_total_mn": null,
      "fy2025_port_mn": 910.68,
      "fy2025_region_total_mn": null,
      "growth_pct": 56.44
    },
    {
      "region": null,
      "port": "Cochin",
      "fy2024_port_mn": 164.032273763715,
      "fy2024_region_total_mn": null,
      "fy2025_port_mn": 164.56,
      "fy2025_region_total_mn": null,
      "growth_pct": 0.32
    },
    {
      "region": null,
      "port": "Hyderabad",
      "fy2024_port_mn": 184.631865015629,
      "fy2024_region_total_mn": null,
      "fy2025_port_mn": 231.5,
      "fy2025_region_total_mn": null,
      "growth_pct": 25.38
    },
    {
      "region": null,
      "port": "Vishakhapatnam",
      "fy2024_port_mn": 12.4445744621706,
      "fy2024_region_total_mn": null,
      "fy2025_port_mn": 62.07,
      "fy2025_region_total_mn": null,
      "growth_pct": 398.77
    },
    {
      "region": "Souther Region Total",
      "port": null,
      "fy2024_port_mn": null,
      "fy2024_region_total_mn": 1124.5136016481615,
      "fy2025_port_mn": null,
      "fy2025_region_total_mn": 1607.09,
      "growth_pct": 42.91
    },
    {
      "region": "Sub Total",
      "port": null,
      "fy2024_port_mn": 32285.845995719563,
      "fy2024_region_total_mn": 32285.845995719566,
      "fy2025_port_mn": 28671.059999999998,
      "fy2025_region_total_mn": 28671.06,
      "growth_pct": -11.2
    }
  ],
  "monthly_imports": [
  {
    "month": "April",
    "fy2025_mn": 1919.760326261807,
    "fy2026_mn": 2102.858826693236,
    "growth_pct": 9.537570806453832
  },
  {
    "month": "May",
    "fy2025_mn": 1968.1410081055126,
    "fy2026_mn": 1755.1172733409799,
    "growth_pct": -10.823601250480753
  },
  {
    "month": "June",
    "fy2025_mn": 1606.532543081222,
    "fy2026_mn": 1612.8852247872476,
    "growth_pct": 0.39542813703863366
  },
  {
    "month": "July",
    "fy2025_mn": 1492.8940860475795,
    "fy2026_mn": 2088.9222463380847,
    "growth_pct": 39.924343318184285
  },
  {
    "month": "August",
    "fy2025_mn": 1476.3697118691432,
    "fy2026_mn": 1606.851209997645,
    "growth_pct": 8.837996138738635
  },
  {
    "month": "September",
    "fy2025_mn": 1537.98127377417,
    "fy2026_mn": 1766.0043336150297,
    "growth_pct": 14.826127192127414
  },
  {
    "month": "October",
    "fy2025_mn": 1614.9714744524174,
    "fy2026_mn": 1369.01788677644,
    "growth_pct": -15.229593312747024
  },
  {
    "month": "November",
    "fy2025_mn": 1422.1717348804102,
    "fy2026_mn": 2432.7103743207726,
    "growth_pct": 71.05602049708422
  },
  {
    "month": "December",
    "fy2025_mn": 1678.310189563283,
    "fy2026_mn": 1835.3763195113054,
    "growth_pct": 9.358587639207073
  },
  {
    "month": "January",
    "fy2025_mn": 1422.0375324021545,
    "fy2026_mn": 2119.6580513069603,
    "growth_pct": 49.05781338459902
  },
  {
    "month": "February",
    "fy2025_mn": 1532.495405432457,
    "fy2026_mn": 1830.419913769761,
    "growth_pct": 19.44048297183849
  },
  {
    "month": "March",
    "fy2025_mn": 2035.1197170643024,
    "fy2026_mn": 2319.987623322263,
    "growth_pct": 13.997599446822107
  },
  {
    "month": "Total (US$million)",
    "fy2025_mn": 19706.78500293446,
    "fy2026_mn": 22839.809283779727,
    "growth_pct": 15.898200951493301
  }
],
  "import_commodities": [
    {
      "commodity": "Rough Diamonds",
      "fy2024_mn": 14266.7536394915,
      "fy2025_mn": 10804.5375349213,
      "growth_pct": -24.267721950328713
    },
    {
      "commodity": "Rgh Lab Grown Diamonds",
      "fy2024_mn": 1176.04871388233,
      "fy2025_mn": 863.356411530287,
      "growth_pct": -26.588380112231434
    },
    {
      "commodity": "Rough Coloured Gemstones",
      "fy2024_mn": 417.277128609126,
      "fy2025_mn": 411.544351570017,
      "growth_pct": -1.3738536445114025
    },
    {
      "commodity": "Rough Synthetic Stone",
      "fy2024_mn": 5.02069532882782,
      "fy2025_mn": 7.19533054196089,
      "growth_pct": 43.31342713920028
    },
    {
      "commodity": "Raw Pearls",
      "fy2024_mn": 14.7062343621231,
      "fy2025_mn": 7.6160466257243,
      "growth_pct": -48.21212257204371
    },
    {
      "commodity": "Gold Bar",
      "fy2024_mn": 2909.63767336812,
      "fy2025_mn": 4237.10279112523,
      "growth_pct": 45.62303856275244
    },
    {
      "commodity": "Silver Bar",
      "fy2024_mn": 61.021837202719,
      "fy2025_mn": 87.9395920134765,
      "growth_pct": 44.11167549959985
    },
    {
      "commodity": "Platinum Bar",
      "fy2024_mn": 75.6715022115217,
      "fy2025_mn": 754.187956858712,
      "growth_pct": 896.6604795958178
    },
    {
      "commodity": "Sub - Total",
      "fy2024_mn": 18926.13742445627,
      "fy2025_mn": 17173.480015186713,
      "growth_pct": -9.260512961322894
    },
    {
      "commodity": "Imports of Cut & Pol. Diamonds",
      "fy2024_mn": 1911.00062642254,
      "fy2025_mn": 1211.65842727982,
      "growth_pct": -36.595602820492694
    },
    {
      "commodity": "Pol. Lab Grown Diamonds",
      "fy2024_mn": 115.186159953726,
      "fy2025_mn": 93.4685367797253,
      "growth_pct": -18.85436860012121
    },
    {
      "commodity": "Col. Gemstones",
      "fy2024_mn": 126.066839905222,
      "fy2025_mn": 132.844986499771,
      "growth_pct": 5.376629254485062
    },
    {
      "commodity": "Pol. Synthetic Stone",
      "fy2024_mn": 13.3761810433192,
      "fy2025_mn": 9.796611634493,
      "growth_pct": -26.760772729029657
    },
    {
      "commodity": "Pearls worked",
      "fy2024_mn": 7.34033077793385,
      "fy2025_mn": 10.138752363077,
      "growth_pct": 38.123916616341475
    },
    {
      "commodity": "Gold Jewellery",
      "fy2024_mn": 1041.01903658822,
      "fy2025_mn": 956.150586193204,
      "growth_pct": -8.152439812547444
    },
    {
      "commodity": "Silver Jewellery",
      "fy2024_mn": 130.259624724799,
      "fy2025_mn": 62.5534183988703,
      "growth_pct": -51.97789143717586
    },
    {
      "commodity": "Imitation Jewellery",
      "fy2024_mn": 3.29540174956586,
      "fy2025_mn": 2.54262685878182,
      "growth_pct": -22.843190238738305
    },
    {
      "commodity": "Others",
      "fy2024_mn": 39.918138877839,
      "fy2025_mn": 54.1510417400317,
      "growth_pct": 35.655226576944095
    },
    {
      "commodity": "Sub Total",
      "fy2024_mn": 3387.462340043165,
      "fy2025_mn": 2533.3049877477742,
      "growth_pct": -25.21525751588154
    },
    {
      "commodity": "Gross Imports",
      "fy2024_mn": 22313.599764499435,
      "fy2025_mn": 19706.795002934487,
      "growth_pct": -11.682582770496454
    }
  ],
  "top_import_countries": {
    "fy2020": [
      {
        "country": "Switzerland",
        "amount_mn": 6366.1580592115315,
        "share_pct": 25.953778327631973
      },
      {
        "country": "U.A.E",
        "amount_mn": 5134.785105314928,
        "share_pct": 20.93367351923329
      },
      {
        "country": "Belgium",
        "amount_mn": 3912.451166247067,
        "share_pct": 15.950419286171158
      },
      {
        "country": "Hongkong",
        "amount_mn": 2334.351549516654,
        "share_pct": 9.51676695605373
      },
      {
        "country": "Russia",
        "amount_mn": 1295.2761704616219,
        "share_pct": 5.28062770175527
      },
      {
        "country": "South Africa",
        "amount_mn": 987.6436242127048,
        "share_pct": 4.026460457170982
      },
      {
        "country": "Canada",
        "amount_mn": 807.0147627955333,
        "share_pct": 3.290066326646606
      },
      {
        "country": "USA",
        "amount_mn": 649.4492745499465,
        "share_pct": 2.647697771550199
      },
      {
        "country": "Israel",
        "amount_mn": 435.43995255416087,
        "share_pct": 1.7752169987725657
      },
      {
        "country": "Botswana",
        "amount_mn": 401.150334108211,
        "share_pct": 1.6354238695715784
      },
      {
        "country": "Others",
        "amount_mn": 2205.10959511311,
        "share_pct": 8.989868785442658
      },
      {
        "country": "TOTAL",
        "amount_mn": 24528.829594085466,
        "share_pct": 100.0
      }
    ],
    "fy2025": [
      {
        "country": "U.A.E",
        "amount_mn": 11051.382303659355,
        "share_pct": 56.07907277627344
      },
      {
        "country": "Belgium",
        "amount_mn": 1820.0250193378708,
        "share_pct": 9.235524815777197
      },
      {
        "country": "Hongkong",
        "amount_mn": 1641.1992457795477,
        "share_pct": 8.328092306965155
      },
      {
        "country": "USA",
        "amount_mn": 879.4511146132611,
        "share_pct": 4.462681835125848
      },
      {
        "country": "Russia",
        "amount_mn": 426.0819639754667,
        "share_pct": 2.1621079435941506
      },
      {
        "country": "Indonesia",
        "amount_mn": 419.61116840710395,
        "share_pct": 2.129272574621489
      },
      {
        "country": "Canada",
        "amount_mn": 390.23580059334745,
        "share_pct": 1.98021037188582
      },
      {
        "country": "South Africa",
        "amount_mn": 344.6769658886851,
        "share_pct": 1.7490268749436333
      },
      {
        "country": "Tanzaia",
        "amount_mn": 295.3362125781909,
        "share_pct": 1.4986524313032976
      },
      {
        "country": "Israel",
        "amount_mn": 259.2672894852481,
        "share_pct": 1.3156244889597246
      },
      {
        "country": "Others",
        "amount_mn": 2179.517918616384,
        "share_pct": 11.059733580550256
      },
      {
        "country": "TOTAL",
        "amount_mn": 19706.78500293446,
        "share_pct": 100.0
      }
    ],
    "fy2026": []
  },
  "import_regions": [
    {
      "region": "USA & Canada",
      "fy2020_mn": 1456.56301523921,
      "fy2025_mn": 1271.69842382496,
      "fy2020_share_pct": 5.93816761477453,
      "fy2025_share_pct": 6.453099395135229
    },
    {
      "region": "Europe",
      "fy2020_mn": 4190.26438396504,
      "fy2025_mn": 2036.58761655645,
      "fy2020_share_pct": 17.083018037580693,
      "fy2025_share_pct": 10.334448852277
    },
    {
      "region": "Europe Others",
      "fy2020_mn": 6366.2256187783,
      "fy2025_mn": 140.352368340368,
      "fy2020_share_pct": 25.95405375686322,
      "fy2025_share_pct": 0.7122032757726291
    },
    {
      "region": "Asia",
      "fy2020_mn": 2672.4017571577,
      "fy2025_mn": 2329.67154318789,
      "fy2020_share_pct": 10.894941998382558,
      "fy2025_share_pct": 11.821672296323296
    },
    {
      "region": "Middle East",
      "fy2020_mn": 5590.75504517557,
      "fy2025_mn": 11320.0645452247,
      "fy2020_share_pct": 22.7925878963408,
      "fy2025_share_pct": 57.44247244560241
    },
    {
      "region": "CIS Countries",
      "fy2020_mn": 1295.39238044944,
      "fy2025_mn": 426.590697728168,
      "fy2020_share_pct": 5.281101470743618,
      "fy2025_share_pct": 2.1646894593138724
    },
    {
      "region": "East Asia (Oceania)",
      "fy2020_mn": 51.7501230360978,
      "fy2025_mn": 8.88076595183915,
      "fy2020_share_pct": 0.21097673183956656,
      "fy2025_share_pct": 0.045064509256668585
    },
    {
      "region": "Africa",
      "fy2020_mn": 2189.76489676035,
      "fy2025_mn": 1124.50919648048,
      "fy2020_share_pct": 8.92731097650238,
      "fy2025_share_pct": 5.706203200131514
    },
    {
      "region": "LAC",
      "fy2020_mn": 19.109575757131,
      "fy2025_mn": 82.8195283182534,
      "fy2020_share_pct": 0.07790659429481651,
      "fy2025_share_pct": 0.42025895297442645
    },
    {
      "region": "Others",
      "fy2020_mn": 696.6027977665617,
      "fy2025_mn": 965.6103173212905,
      "fy2020_share_pct": 2.839934922677813,
      "fy2025_share_pct": 4.899887613212953
    },
    {
      "region": "TOTAL",
      "fy2020_mn": 24528.8295940854,
      "fy2025_mn": 19706.7850029344,
      "fy2020_share_pct": 100.0,
      "fy2025_share_pct": 100.0
    }
  ],
  "dta_sez_recent": [
    {
      "year": "FY2024",
      "dta_mn": 25875.6147318508,
      "sez_mn": 6410.2312638688,
      "total_mn": 32285.8459957196,
      "dta_share_pct": 80.145382392276,
      "sez_share_pct": 19.854617607724006,
      "dta_growth_pct": null,
      "sez_growth_pct": null
    },
    {
      "year": "FY2025",
      "dta_mn": 21914.34,
      "sez_mn": 6801.31,
      "total_mn": 28715.65,
      "dta_share_pct": 76.31497110460673,
      "sez_share_pct": 23.68502889539328,
      "dta_growth_pct": -15.308910620680983,
      "sez_growth_pct": 6.100852216292285
    }
  ],
  "dta_sez_long": [
    {
      "year": "FY2011",
      "dta_mn": 27238.888691130196,
      "sez_mn": 18347.7706909998,
      "total_mn": 45586.65938213,
      "dta_share_pct": 59.75188588135032,
      "sez_share_pct": 40.248114118649674
    },
    {
      "year": "FY2012",
      "dta_mn": 28315.8872995743,
      "sez_mn": 18537.3367374183,
      "total_mn": 46853.2240369926,
      "dta_share_pct": 60.4353016928306,
      "sez_share_pct": 39.56469830716941
    },
    {
      "year": "FY2013",
      "dta_mn": 23763.544244389206,
      "sez_mn": 19867.2885206635,
      "total_mn": 43630.832765052706,
      "dta_share_pct": 54.465025621567456,
      "sez_share_pct": 45.534974378432544
    },
    {
      "year": "FY2014",
      "dta_mn": 30254.069262796995,
      "sez_mn": 9986.1714677987,
      "total_mn": 40240.240730595695,
      "dta_share_pct": 75.18361896824848,
      "sez_share_pct": 24.816381031751522
    },
    {
      "year": "FY2015",
      "dta_mn": 34182.45442914094,
      "sez_mn": 5845.50302462847,
      "total_mn": 40027.957453769406,
      "dta_share_pct": 85.39644939070456,
      "sez_share_pct": 14.60355060929546
    },
    {
      "year": "FY2016",
      "dta_mn": 31415.874983862905,
      "sez_mn": 7870.70701904959,
      "total_mn": 39286.582002912495,
      "dta_share_pct": 79.96591554219174,
      "sez_share_pct": 20.03408445780826
    },
    {
      "year": "FY2017",
      "dta_mn": 34097.78824115565,
      "sez_mn": 9101.63802960985,
      "total_mn": 43199.4262707655,
      "dta_share_pct": 78.93111363895767,
      "sez_share_pct": 21.06888636104233
    },
    {
      "year": "FY2018",
      "dta_mn": 31199.7731904304,
      "sez_mn": 9813.5159712227,
      "total_mn": 41013.2891616531,
      "dta_share_pct": 76.07235076283955,
      "sez_share_pct": 23.927649237160455
    },
    {
      "year": "FY2019",
      "dta_mn": 30072.70500494739,
      "sez_mn": 9684.40631217351,
      "total_mn": 39757.1113171209,
      "dta_share_pct": 75.64107151818386,
      "sez_share_pct": 24.35892848181614
    },
    {
      "year": "FY2020",
      "dta_mn": 25025.366559697693,
      "sez_mn": 10621.0342815421,
      "total_mn": 35646.400841239796,
      "dta_share_pct": 70.2044693688837,
      "sez_share_pct": 29.795530631116296
    },
    {
      "year": "FY2021",
      "dta_mn": 20500.972270113798,
      "sez_mn": 5004.61,
      "total_mn": 25505.5822701138,
      "dta_share_pct": 80.37837385165616,
      "sez_share_pct": 19.62162614834384
    },
    {
      "year": "FY2022",
      "dta_mn": 32569.19782536869,
      "sez_mn": 7000.02652229301,
      "total_mn": 39569.2243476617,
      "dta_share_pct": 82.30941688219706,
      "sez_share_pct": 17.690583117802937
    },
    {
      "year": "FY2023",
      "dta_mn": 30542.8691834261,
      "sez_mn": 7194.1819227896,
      "total_mn": 37737.0511062157,
      "dta_share_pct": 80.93602517446139,
      "sez_share_pct": 19.063974825538608
    },
    {
      "year": "FY2024",
      "dta_mn": 25875.6147318508,
      "sez_mn": 6410.2312638688,
      "total_mn": 32285.8459957196,
      "dta_share_pct": 80.145382392276,
      "sez_share_pct": 19.854617607724006
    },
    {
      "year": "FY2025",
      "dta_mn": 21914.34,
      "sez_mn": 6801.31,
      "total_mn": 28715.65,
      "dta_share_pct": 76.31497110460673,
      "sez_share_pct": 23.68502889539328
    }
  ],
  "fdi": [
    {
      "year": "FY 2015",
      "india_fdi_mn": 29737.0,
      "gj_fdi_mn": 263.16,
      "gj_share_pct": 0.8849581329656658,
      "gj_growth_pct": null
    },
    {
      "year": "FY2016",
      "india_fdi_mn": 40001.0,
      "gj_fdi_mn": 75.57,
      "gj_share_pct": 0.18892027699307515,
      "gj_growth_pct": -71.28362973096216
    },
    {
      "year": "FY2017",
      "india_fdi_mn": 43478.0,
      "gj_fdi_mn": 123.91,
      "gj_share_pct": 0.2849947099682598,
      "gj_growth_pct": 63.96718274447532
    },
    {
      "year": "FY2018",
      "india_fdi_mn": 44857.0,
      "gj_fdi_mn": 233.03,
      "gj_share_pct": 0.5194952850168313,
      "gj_growth_pct": 88.06391735937376
    },
    {
      "year": "FY 2019",
      "india_fdi_mn": 44366.0,
      "gj_fdi_mn": 29.01,
      "gj_share_pct": 0.06538790966055087,
      "gj_growth_pct": -87.55095910397803
    },
    {
      "year": "FY 2020*",
      "india_fdi_mn": 49977.0,
      "gj_fdi_mn": 18.87,
      "gj_share_pct": 0.03775736838945915,
      "gj_growth_pct": -34.95346432264736
    },
    {
      "year": "FY 2021*",
      "india_fdi_mn": 59636.0,
      "gj_fdi_mn": 13.82,
      "gj_share_pct": 0.02317392179220605,
      "gj_growth_pct": -26.76205617382088
    },
    {
      "year": "FY 2022*",
      "india_fdi_mn": 58773.0,
      "gj_fdi_mn": 22.22,
      "gj_share_pct": 0.03780647576268014,
      "gj_growth_pct": 60.781476121562946
    },
    {
      "year": "FY 2023*",
      "india_fdi_mn": 46034.0,
      "gj_fdi_mn": 25.55,
      "gj_share_pct": 0.05550245470739019,
      "gj_growth_pct": 14.986498649864988
    },
    {
      "year": "FY 2024*",
      "india_fdi_mn": 44423.0,
      "gj_fdi_mn": 37.97,
      "gj_share_pct": 0.08547374108007114,
      "gj_growth_pct": 48.61056751467709
    },
    {
      "year": "FY 2025*",
      "india_fdi_mn": 50018.0,
      "gj_fdi_mn": 150.163,
      "gj_share_pct": 0.3002179215482426,
      "gj_growth_pct": 295.47800895443777
    }
  ]
}"""
DATA = json.loads(RAW)

EXPORT_COUNTRY_HISTORY = [{"entity": "Abu Dhabi", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.06540893129821918}, {"entity": "Abu Dhabi", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 1.102720879252668}, {"entity": "Abu Dhabi", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.00023723420074349443}, {"entity": "Afghanistan", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.0691661732455248}, {"entity": "Afghanistan", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.4127917126583285}, {"entity": "Afghanistan", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.0005534669067987394}, {"entity": "Afghanistan", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.0010311948529411765}, {"entity": "Afghanistan", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.22728046807922955}, {"entity": "Afghanistan", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.2444819594204876}, {"entity": "Afghanistan", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.028012638392733085}, {"entity": "Afghanistan", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.35888763243614213}, {"entity": "Afghanistan", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.5170842204580939}, {"entity": "Afghanistan", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 1.2113963436878572}, {"entity": "Afghanistan", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 2.6300247241359664}, {"entity": "Afghanistan", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 1.4397871320395188}, {"entity": "Afghanistan", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.21912274810417717}, {"entity": "Afghanistan", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.018175323677664182}, {"entity": "Afghanistan", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.007119087183833901}, {"entity": "Afghanistan", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.002076635560828222}, {"entity": "Afghanistan", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.009078121021656395}, {"entity": "Albania", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.00026631531733572556}, {"entity": "Albania", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.0030031684805069568}, {"entity": "Albania", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.0002657560094077627}, {"entity": "Albania", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.00030933415822442193}, {"entity": "Albania", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.001375648606250754}, {"entity": "Albania", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.01488532022602004}, {"entity": "Albania", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.019613735134768877}, {"entity": "Algeria", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.00013151239251390996}, {"entity": "Algeria", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.003521336914353924}, {"entity": "Algeria", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.006178703247485252}, {"entity": "Algeria", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.005900986768333708}, {"entity": "Angola", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.14046634129596466}, {"entity": "Angola", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.004125566750629723}, {"entity": "Angola", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.0018225276366895728}, {"entity": "Angola", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.0015524653709000804}, {"entity": "Angola", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.00032228175482415506}, {"entity": "Angola", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.47336819424006726}, {"entity": "Angola", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.00015594074251784322}, {"entity": "Angola", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.0001788695444788934}, {"entity": "Antigua", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.003848584872533184}, {"entity": "Antigua", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.006210801924130792}, {"entity": "Antigua", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.06154716468301822}, {"entity": "Antigua & Barbuda", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.04578925956061839}, {"entity": "Antigua & Barbuda", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.04928125}, {"entity": "Antigua & Barbuda", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.008889811852124818}, {"entity": "Antigua & Barbuda", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.0020041826420355525}, {"entity": "Antigua & Barbuda", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.17368924300275948}, {"entity": "Argentina", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.05410564691790515}, {"entity": "Argentina", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.11081040682571022}, {"entity": "Argentina", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.07846556843410642}, {"entity": "Argentina", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.004898564356086412}, {"entity": "Argentina", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.005927370080636732}, {"entity": "Argentina", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.005278849477828765}, {"entity": "Argentina", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.043309196077254614}, {"entity": "Argentina", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.10925968485782861}, {"entity": "Argentina", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.13208691269627662}, {"entity": "Argentina", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.11543249261628762}, {"entity": "Argentina", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.06397287716584274}, {"entity": "Argentina", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.0006031459632576642}, {"entity": "Argentina", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.03950167145250585}, {"entity": "Argentina", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.04371270581932295}, {"entity": "Argentina", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.04361025129181848}, {"entity": "Argentina", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.49022203435106987}, {"entity": "Argentina", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.18459668610282365}, {"entity": "Armenia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 4.233810379289899}, {"entity": "Armenia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 7.365163537402044}, {"entity": "Armenia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 12.586208279611904}, {"entity": "Armenia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 10.265834232075653}, {"entity": "Armenia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 10.334810245469104}, {"entity": "Armenia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 8.757524181257377}, {"entity": "Armenia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 3.8639954075339666}, {"entity": "Armenia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 4.591890532863702}, {"entity": "Armenia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 5.196662452030789}, {"entity": "Armenia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 6.422700609802687}, {"entity": "Armenia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 6.1231062856784115}, {"entity": "Armenia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 5.016904173249129}, {"entity": "Armenia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 7.621115134524454}, {"entity": "Armenia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 9.553634846258388}, {"entity": "Armenia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 36.400576310718655}, {"entity": "Armenia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 22.992328638131532}, {"entity": "Armenia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 14.97946822066082}, {"entity": "Aruba", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.3146565153147575}, {"entity": "Aruba", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.5785514788403956}, {"entity": "Aruba", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.45866195625430106}, {"entity": "Aruba", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.2807581907755444}, {"entity": "Aruba", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.27929658705154525}, {"entity": "Aruba", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.1860102725649694}, {"entity": "Aruba", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.26163055083039805}, {"entity": "Aruba", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.1524760587302895}, {"entity": "Aruba", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.01836049766718507}, {"entity": "Aruba", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.009840270664039415}, {"entity": "Aruba", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.01256131602482452}, {"entity": "Aruba", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.09535886686419191}, {"entity": "Aruba", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.11346408099312186}, {"entity": "Aruba", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.24709271392866888}, {"entity": "Aruba", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.18346308732837668}, {"entity": "Aruba", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.7372779394322048}, {"entity": "Australia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 185.6769907397285}, {"entity": "Australia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 222.76260320560917}, {"entity": "Australia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 223.613843860475}, {"entity": "Australia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 246.43596538047052}, {"entity": "Australia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 250.05737478645938}, {"entity": "Australia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 232.43268100945556}, {"entity": "Australia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 262.24532814518545}, {"entity": "Australia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 213.18304624990606}, {"entity": "Australia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 222.1642655530286}, {"entity": "Australia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 230.2309677911015}, {"entity": "Australia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 191.39202389430443}, {"entity": "Australia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 189.75416050177603}, {"entity": "Australia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 252.513246654831}, {"entity": "Australia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 267.5359241909621}, {"entity": "Australia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 232.3170332265635}, {"entity": "Australia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 260.40514332862875}, {"entity": "Australia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 360.21028192800014}, {"entity": "Austria", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 4.6133386127108125}, {"entity": "Austria", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 5.088301895615707}, {"entity": "Austria", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 5.441286666349194}, {"entity": "Austria", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 2.755230600339183}, {"entity": "Austria", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 2.8590158769151355}, {"entity": "Austria", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 2.287342429610863}, {"entity": "Austria", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 3.037792593549189}, {"entity": "Austria", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 4.050010738348682}, {"entity": "Austria", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 2.320210590868638}, {"entity": "Austria", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 5.343779900509275}, {"entity": "Austria", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 7.856453665496375}, {"entity": "Austria", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 6.787366904007381}, {"entity": "Austria", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 6.422333390208595}, {"entity": "Austria", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 7.893106637784161}, {"entity": "Austria", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 5.326326895112876}, {"entity": "Austria", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 5.671390386918422}, {"entity": "Austria", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 6.285061568191751}, {"entity": "Azerbaijan", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.0019119010203616693}, {"entity": "Azerbaijan", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.0008875971385752743}, {"entity": "Azerbaijan", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.0007158088243641318}, {"entity": "Azerbaijan", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.01383368370183015}, {"entity": "Azerbaijan", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.016032095329949918}, {"entity": "Azerbaijan", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.013970745758545053}, {"entity": "Azerbaijan", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.008397523648058583}, {"entity": "Azerbaijan", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.0010842851991562294}, {"entity": "Azerbaijan", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.022521384865297017}, {"entity": "Azerbaijan", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.008733408955983762}, {"entity": "Azerbaijan", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.006406784387836126}, {"entity": "Azerbaijan", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.0011968419802920575}, {"entity": "Azerbaijan", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.0022465477992093157}, {"entity": "Azerbaijan", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.008092567405012087}, {"entity": "Azerbaijan", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.026807462591112077}, {"entity": "Azerbaijan", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.04982897283146556}, {"entity": "Bahamas", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.03425549227013833}, {"entity": "Bahamas", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.01632402866842701}, {"entity": "Bahamas", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.003189963110974485}, {"entity": "Bahamas", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.0208376891371871}, {"entity": "Bahamas", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.005544086188187877}, {"entity": "Bahamas", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.002936673625608908}, {"entity": "Bahamas", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.044319776182495337}, {"entity": "Bahamas", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.003249089600567343}, {"entity": "Bahamas", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.011702106395249752}, {"entity": "Bahamas", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.047162014200904254}, {"entity": "Bahamas", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.08306003532894954}, {"entity": "Bahamas", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.07256401053897223}, {"entity": "Bahamas", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 1.2910871577142904}, {"entity": "Bahrain", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 35.61660136811793}, {"entity": "Bahrain", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 47.00022581417973}, {"entity": "Bahrain", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 35.383076679572824}, {"entity": "Bahrain", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 34.24146757480651}, {"entity": "Bahrain", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 61.383651316997906}, {"entity": "Bahrain", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 109.97396900517708}, {"entity": "Bahrain", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 115.51660435424058}, {"entity": "Bahrain", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 18.135916026482302}, {"entity": "Bahrain", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 19.39712763816647}, {"entity": "Bahrain", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 41.907639169295855}, {"entity": "Bahrain", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 34.38602180310681}, {"entity": "Bahrain", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 6.9967843966418}, {"entity": "Bahrain", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 48.84860052035893}, {"entity": "Bahrain", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 75.71150519941854}, {"entity": "Bahrain", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 82.24413184489202}, {"entity": "Bahrain", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 95.02968139467444}, {"entity": "Bahrain", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 203.6613320607753}, {"entity": "Bangladesh", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.06845837805860625}, {"entity": "Bangladesh", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.09758621999529246}, {"entity": "Bangladesh", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 1.2340596783788225}, {"entity": "Bangladesh", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 4.404516181089044}, {"entity": "Bangladesh", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 1.370177854544336}, {"entity": "Bangladesh", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 2.4380415723342}, {"entity": "Bangladesh", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 6.946724120465393}, {"entity": "Bangladesh", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 1.4498154206543075}, {"entity": "Bangladesh", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.9155885817706096}, {"entity": "Bangladesh", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.9909893733823791}, {"entity": "Bangladesh", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.20141331992965864}, {"entity": "Bangladesh", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.1073415271469569}, {"entity": "Bangladesh", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.19364392695566376}, {"entity": "Bangladesh", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 1.0686013942169528}, {"entity": "Bangladesh", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.015559351484223263}, {"entity": "Bangladesh", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.009860480387399858}, {"entity": "Barbados", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0006274625757443086}, {"entity": "Barbados", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.0015437846050060384}, {"entity": "Barbados", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.0007690617446715008}, {"entity": "Belarus", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.33467997303631686}, {"entity": "Belarus", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.29293157333444214}, {"entity": "Belarus", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.057780851013119715}, {"entity": "Belarus", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.18142772571038485}, {"entity": "Belarus", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.14498155238892713}, {"entity": "Belarus", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.10048292683815534}, {"entity": "Belarus", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.005109226858311302}, {"entity": "Belarus", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.005271328779882024}, {"entity": "Belarus", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.004626553274962464}, {"entity": "Belarus", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.001296685488673527}, {"entity": "Belarus", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.03240550248545978}, {"entity": "Belgium", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 1672.9803619362717}, {"entity": "Belgium", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 2207.130824823}, {"entity": "Belgium", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 3115.7233754791177}, {"entity": "Belgium", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 2016.390645231274}, {"entity": "Belgium", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 2206.114244818285}, {"entity": "Belgium", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 2390.2198728580966}, {"entity": "Belgium", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 2226.134499185315}, {"entity": "Belgium", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 2085.4755756057707}, {"entity": "Belgium", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 1874.378746470404}, {"entity": "Belgium", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 1803.2250949475172}, {"entity": "Belgium", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 1899.7608981285093}, {"entity": "Belgium", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 1164.0620348567722}, {"entity": "Belgium", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 1851.7029699271748}, {"entity": "Belgium", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 2326.6168807454146}, {"entity": "Belgium", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 1984.860453693904}, {"entity": "Belgium", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 1189.9955640207957}, {"entity": "Belgium", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 1390.975438386701}, {"entity": "Benin", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.00014443909484833896}, {"entity": "Benin", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.00016893223564920656}, {"entity": "Bermuda", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.03875163364369069}, {"entity": "Bermuda", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.000411825505174539}, {"entity": "Bermuda", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.00014737041959369661}, {"entity": "Bermuda", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.00202167106752169}, {"entity": "Bermuda", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.00278358614082708}, {"entity": "Bermuda", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.007193081545465153}, {"entity": "Bermuda", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.009529150941373129}, {"entity": "Bermuda", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.0016449410304158908}, {"entity": "Bermuda", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 1.4138272303124559e-05}, {"entity": "Bermuda", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.0037666579702976943}, {"entity": "Bermuda", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.00744292822189289}, {"entity": "Bermuda", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.015571376480989791}, {"entity": "Bermuda", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.021591307939297626}, {"entity": "Bermuda", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.04605376530748705}, {"entity": "Bermuda", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.003782342932157129}, {"entity": "Bermuda", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.1890306708020673}, {"entity": "Bhutan", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.023692439560439562}, {"entity": "Bhutan", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.294433219470538}, {"entity": "Bhutan", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.0008200197935812243}, {"entity": "Bhutan", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.0016138793625176519}, {"entity": "Bhutan", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.0}, {"entity": "Bhutan", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0007466949933995533}, {"entity": "Bhutan", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.001360872577235787}, {"entity": "Bhutan", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.0013081514185266944}, {"entity": "Bolivia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.0013786318499448326}, {"entity": "Bolivia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.0018307888446215139}, {"entity": "Bolivia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 4.940055333538272e-05}, {"entity": "Bolivia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.008129822607750546}, {"entity": "Bolivia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.011756106825045074}, {"entity": "Bolivia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.006949483138063647}, {"entity": "Bolivia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.0027666962620590246}, {"entity": "Bolivia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.002026210456394935}, {"entity": "Bolivia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0017035162013988028}, {"entity": "Bolivia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.0008519420679393801}, {"entity": "Bosnia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.2939451996105161}, {"entity": "Bosnia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.000494456098291879}, {"entity": "Bosnia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.0007456889855522757}, {"entity": "Bosnia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.0007461956892880335}, {"entity": "Bosnia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.0005028635284257578}, {"entity": "Bosnia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.00016000184896589978}, {"entity": "Bosnia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0005427471661369163}, {"entity": "Bosnia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.0013068917557910891}, {"entity": "Botswana", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.005538461538461538}, {"entity": "Botswana", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.25120382912985934}, {"entity": "Botswana", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 10.664825736142067}, {"entity": "Botswana", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 3.642872302152151}, {"entity": "Botswana", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 4.879016577914789}, {"entity": "Botswana", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 6.458582816345482}, {"entity": "Botswana", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.6149637816926239}, {"entity": "Botswana", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.022830452006487145}, {"entity": "Botswana", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 2.3438157678770364}, {"entity": "Botswana", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 93.40512402361277}, {"entity": "Botswana", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 87.01441064952257}, {"entity": "Botswana", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 39.15544076571093}, {"entity": "Botswana", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 116.73649372949781}, {"entity": "Botswana", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 106.87546165148035}, {"entity": "Botswana", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 59.22601357261872}, {"entity": "Botswana", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 131.67084911533354}, {"entity": "Botswana", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 106.86253334448008}, {"entity": "Brazil", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 1.3375129188360941}, {"entity": "Brazil", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 1.312702155434473}, {"entity": "Brazil", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 1.8843637217397842}, {"entity": "Brazil", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 1.0430621926345978}, {"entity": "Brazil", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 1.2200013746882694}, {"entity": "Brazil", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.992717609734784}, {"entity": "Brazil", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.849470860757783}, {"entity": "Brazil", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 1.0865062554180474}, {"entity": "Brazil", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 1.1457578045615897}, {"entity": "Brazil", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.6576601326957988}, {"entity": "Brazil", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.6414347178362686}, {"entity": "Brazil", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.28404127876053825}, {"entity": "Brazil", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.6417043316196946}, {"entity": "Brazil", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 1.6063457906999046}, {"entity": "Brazil", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 1.0604235657569447}, {"entity": "Brazil", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 2.934403341385459}, {"entity": "Brazil", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 5.674528927697381}, {"entity": "Brunei Darussalam", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 3.886604739625712}, {"entity": "Brunei Darussalam", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.008284470274837207}, {"entity": "Brunei Darussalam", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.002819517747101271}, {"entity": "Brunei Darussalam", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 8.952551477170994e-05}, {"entity": "Brunei Darussalam", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.003096976163619072}, {"entity": "Brunei Darussalam", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.0007825837660286695}, {"entity": "Brunei Darussalam", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.0001437963939031781}, {"entity": "Brunei Darussalam", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.0009317818167744175}, {"entity": "Brunei Darussalam", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.0002046468477563884}, {"entity": "Brunei Darussalam", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.013106289397427076}, {"entity": "Brunei Darussalam", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 8.427135375910432e-05}, {"entity": "Brunei Darussalam", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.0002058625067191235}, {"entity": "Bulgaria", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.03957658781403995}, {"entity": "Bulgaria", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.018715314231492343}, {"entity": "Bulgaria", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.020423823047260203}, {"entity": "Bulgaria", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 1.258644793822164}, {"entity": "Bulgaria", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.03754417348728937}, {"entity": "Bulgaria", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.0332732561675657}, {"entity": "Bulgaria", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.03978407543076522}, {"entity": "Bulgaria", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.055424292090115436}, {"entity": "Bulgaria", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.04685444850889103}, {"entity": "Bulgaria", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.05711589175455414}, {"entity": "Bulgaria", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.10403730695670582}, {"entity": "Bulgaria", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.16094268719393312}, {"entity": "Bulgaria", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.12620230353779838}, {"entity": "Bulgaria", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.17398803753453282}, {"entity": "Bulgaria", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.14695719877766905}, {"entity": "Bulgaria", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.1930379252796307}, {"entity": "Bulgaria", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.26634715222480304}, {"entity": "Burundi", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.004342781001683853}, {"entity": "Cambodia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.001072216665023747}, {"entity": "Cambodia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.0005627339300244101}, {"entity": "Cambodia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.0005755461722048834}, {"entity": "Cambodia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.0620378074406136}, {"entity": "Cambodia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.03437469152320638}, {"entity": "Cambodia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.004476735402737862}, {"entity": "Cambodia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.006565523969317658}, {"entity": "Cambodia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.017811063717404842}, {"entity": "Cambodia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.012576688405634915}, {"entity": "Cambodia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.009204784283674942}, {"entity": "Cambodia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.041558258419428416}, {"entity": "Cambodia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.017381755078237256}, {"entity": "Cambodia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.07199850783663689}, {"entity": "Cambodia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.04903078148818597}, {"entity": "Cambodia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.06595500484717472}, {"entity": "Cameroon", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.11194533390410959}, {"entity": "Cameroon", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.028633368915456873}, {"entity": "Cameroon", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.08195687550854353}, {"entity": "Cameroon", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.00013254786450662737}, {"entity": "Cameroon", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 1.552312946289972e-05}, {"entity": "Cameroon", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.0027318475916606757}, {"entity": "Cameroon", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.00011607997910560375}, {"entity": "Cameroon", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.00098470964741924}, {"entity": "Cameroon", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0012054728467241276}, {"entity": "Cameroon", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.0038922904138900074}, {"entity": "Canada", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 53.19527271472304}, {"entity": "Canada", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 74.78230334417484}, {"entity": "Canada", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 104.74732700841062}, {"entity": "Canada", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 104.10059587649818}, {"entity": "Canada", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 114.66858310378183}, {"entity": "Canada", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 92.86339716628203}, {"entity": "Canada", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 101.85238214840648}, {"entity": "Canada", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 72.4401658994413}, {"entity": "Canada", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 57.12425042331358}, {"entity": "Canada", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 74.40533308100251}, {"entity": "Canada", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 66.55069170066591}, {"entity": "Canada", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 58.19456705849733}, {"entity": "Canada", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 142.7669601452141}, {"entity": "Canada", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 153.06003231662382}, {"entity": "Canada", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 136.72474021217067}, {"entity": "Canada", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 148.62924565128188}, {"entity": "Canada", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 319.56612153811346}, {"entity": "Canary Island", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.04121174110107482}, {"entity": "Canary Island", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.04830749468587815}, {"entity": "Canary Island", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.03175855096311113}, {"entity": "Canary Island", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.08235159671673106}, {"entity": "Canary Island", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.018551316207854263}, {"entity": "Canary Island", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.06957748030819777}, {"entity": "Canary Island", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.08881815112613113}, {"entity": "Canary Island", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.049025078282819455}, {"entity": "Canary Island", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.04753062361769041}, {"entity": "Canary Island", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.04667126132972699}, {"entity": "Canary Island", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.03889345813263658}, {"entity": "Canary Island", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.021311112189693077}, {"entity": "Canary Island", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.015215415932672591}, {"entity": "Canary Island", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.005850072478774073}, {"entity": "Canary Island", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.0044444444444444444}, {"entity": "Canary Island", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.004201562386204295}, {"entity": "Cayman Islands", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.007809061331930422}, {"entity": "Cayman Islands", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.11657235237089085}, {"entity": "Cayman Islands", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.15671589637615432}, {"entity": "Cayman Islands", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.30229200133613254}, {"entity": "Central African Republic", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.0018176169022836722}, {"entity": "Central African Republic", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.002742351128771448}, {"entity": "Chad", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 1.2021976172443227e-05}, {"entity": "Chad", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.00030156115892273076}, {"entity": "Chile", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.062222089143218196}, {"entity": "Chile", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.08969708507534804}, {"entity": "Chile", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.07886662761168671}, {"entity": "Chile", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.05681269732036569}, {"entity": "Chile", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.11914366934953348}, {"entity": "Chile", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.10356190394896704}, {"entity": "Chile", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.08142651821157496}, {"entity": "Chile", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.31263570109432187}, {"entity": "Chile", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.27261029935818076}, {"entity": "Chile", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.366534519260079}, {"entity": "Chile", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.30164130121729915}, {"entity": "Chile", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.25057882163081485}, {"entity": "Chile", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.3320514725512059}, {"entity": "Chile", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.23971841836930216}, {"entity": "Chile", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.391654260765432}, {"entity": "Chile", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.37155243699250107}, {"entity": "Chile", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.5237317849292411}, {"entity": "China P.Rp", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 419.53067703547595}, {"entity": "China P.Rp", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 50.6600901295262}, {"entity": "China P.Rp", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 65.3569699237509}, {"entity": "China P.Rp", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 37.64493041614717}, {"entity": "China P.Rp", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 63.83653975979139}, {"entity": "China P.Rp", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 87.83518707580255}, {"entity": "China P.Rp", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 63.396072470881315}, {"entity": "China P.Rp", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 114.6627871938079}, {"entity": "China P.Rp", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 124.87921911716995}, {"entity": "China P.Rp", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 169.24677160173866}, {"entity": "China P.Rp", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 82.89039458336369}, {"entity": "China P.Rp", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 139.66780748294966}, {"entity": "China P.Rp", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 180.02318118258765}, {"entity": "China P.Rp", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 140.24651957243339}, {"entity": "China P.Rp", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 103.56604847031483}, {"entity": "China P.Rp", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 101.43555445956322}, {"entity": "China P.Rp", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 66.3401750067797}, {"entity": "Colombia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.0039883026447632575}, {"entity": "Colombia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.00986885971415857}, {"entity": "Colombia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.16215122896132664}, {"entity": "Colombia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.02506762881592368}, {"entity": "Colombia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.01669326894636986}, {"entity": "Colombia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.016646798247564713}, {"entity": "Colombia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.07735800323369359}, {"entity": "Colombia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.3775906986329316}, {"entity": "Colombia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.11632526500881579}, {"entity": "Colombia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.14901290278537715}, {"entity": "Colombia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.4020018663227978}, {"entity": "Colombia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.09268013313496812}, {"entity": "Colombia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.42249025362383574}, {"entity": "Colombia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.766250234233159}, {"entity": "Colombia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 1.332676510459262}, {"entity": "Colombia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.15353148645888018}, {"entity": "Colombia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 1.3076148182633345}, {"entity": "Congo D. Rep", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.0072628301481640544}, {"entity": "Congo D. Rep", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 1.222155227827502}, {"entity": "Congo D. Rep", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.11984391701330312}, {"entity": "Congo D. Rep", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.0012909086562597116}, {"entity": "Congo D. Rep", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.0015243048161307316}, {"entity": "Congo P. Rep", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.5197010305688401}, {"entity": "Congo P. Rep", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.16557062921348314}, {"entity": "Congo P. Rep", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.00013195056220181856}, {"entity": "Congo P. Rep", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 1.49812734082397e-05}, {"entity": "Congo P. Rep", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.051457568536284574}, {"entity": "Congo P. Rep", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.0052994718099298775}, {"entity": "Congo P. Rep", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.04476177011863329}, {"entity": "Costa Rica", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.0004726973003914288}, {"entity": "Costa Rica", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.029753619070400836}, {"entity": "Costa Rica", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.0018604996867306325}, {"entity": "Costa Rica", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.013007027415574211}, {"entity": "Costa Rica", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.05803012281433215}, {"entity": "Costa Rica", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.03798102924260229}, {"entity": "Costa Rica", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.004601976163010807}, {"entity": "Costa Rica", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.019329594733703694}, {"entity": "Costa Rica", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.038707482559074594}, {"entity": "Costa Rica", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.032145026004265}, {"entity": "Costa Rica", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.012596287878723945}, {"entity": "Costa Rica", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.031723133543512895}, {"entity": "Costa Rica", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.04014637132141667}, {"entity": "Costa Rica", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.06377719477216863}, {"entity": "Costa Rica", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.04930652253344717}, {"entity": "Costa Rica", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.08052593114887234}, {"entity": "Costa Rica", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.3793666013219318}, {"entity": "Cote d'Ivoire", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.0003624851985210604}, {"entity": "Cote d'Ivoire", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 9.207467255944572e-05}, {"entity": "Croatia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.1430514269020217}, {"entity": "Croatia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.15836529875395688}, {"entity": "Croatia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.13229427614766248}, {"entity": "Croatia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.135588758772364}, {"entity": "Croatia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.22607904124685868}, {"entity": "Croatia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.09156596138609058}, {"entity": "Croatia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.12802266353283917}, {"entity": "Croatia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.23042157573739083}, {"entity": "Croatia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.22328861107947565}, {"entity": "Croatia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.15743789233386346}, {"entity": "Croatia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.6129979857392309}, {"entity": "Croatia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.024751550845465545}, {"entity": "Croatia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.08058426084738649}, {"entity": "Croatia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.12230245834511909}, {"entity": "Croatia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.20705978682579348}, {"entity": "Croatia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.4839688509107055}, {"entity": "Croatia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.19366693319316974}, {"entity": "Cuba", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.0005154639175257731}, {"entity": "Cuba", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.000585877274128893}, {"entity": "Cuba", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.0006507759319836408}, {"entity": "Cuba", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.000838414406450327}, {"entity": "Cyprus", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.4521406472671862}, {"entity": "Cyprus", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.401761881399444}, {"entity": "Cyprus", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.15975464268301154}, {"entity": "Cyprus", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.47362043851677715}, {"entity": "Cyprus", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.4495097169262968}, {"entity": "Cyprus", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.29749929879641385}, {"entity": "Cyprus", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.2093267879390502}, {"entity": "Cyprus", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.28339115348892513}, {"entity": "Cyprus", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.11851563568389972}, {"entity": "Cyprus", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.41989266845452355}, {"entity": "Cyprus", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.31035921866778216}, {"entity": "Cyprus", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.1336055297981646}, {"entity": "Cyprus", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.09656498774120738}, {"entity": "Cyprus", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.054938683606341285}, {"entity": "Cyprus", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.6347772293450615}, {"entity": "Cyprus", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.4792515171050714}, {"entity": "Cyprus", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 1.2533162245529084}, {"entity": "Czech Republic", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.5853253815043804}, {"entity": "Czech Republic", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 1.1767590609301997}, {"entity": "Czech Republic", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 11.85758932778849}, {"entity": "Czech Republic", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 3.6833898199983133}, {"entity": "Czech Republic", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 2.084625105993653}, {"entity": "Czech Republic", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 1.834328025792342}, {"entity": "Czech Republic", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 1.894009182544796}, {"entity": "Czech Republic", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 1.419170641334861}, {"entity": "Czech Republic", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 1.15312207429833}, {"entity": "Czech Republic", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 1.846006362188656}, {"entity": "Czech Republic", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 3.2248556296792716}, {"entity": "Czech Republic", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 2.7472693241818016}, {"entity": "Czech Republic", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 11.314019426981934}, {"entity": "Czech Republic", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 10.28925579501099}, {"entity": "Czech Republic", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 6.094819721423384}, {"entity": "Czech Republic", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 3.251491921767025}, {"entity": "Czech Republic", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 3.863115804047402}, {"entity": "Democratic Republic Of Laos", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.0017328366342804797}, {"entity": "Democratic Republic Of Laos", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.0005154934417778796}, {"entity": "Democratic Republic Of Laos", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.0024450149479322953}, {"entity": "Denmark", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 3.794783935843478}, {"entity": "Denmark", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 4.455254483338622}, {"entity": "Denmark", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 5.126487235006923}, {"entity": "Denmark", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 3.8005499050850924}, {"entity": "Denmark", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 4.810537991302316}, {"entity": "Denmark", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 4.850206137933815}, {"entity": "Denmark", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 5.406274885618575}, {"entity": "Denmark", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 6.842388903741223}, {"entity": "Denmark", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 7.297109687532289}, {"entity": "Denmark", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 9.189327300378917}, {"entity": "Denmark", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 12.136265936576113}, {"entity": "Denmark", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 13.05931529239236}, {"entity": "Denmark", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 16.801599383617546}, {"entity": "Denmark", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 13.010138725508165}, {"entity": "Denmark", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 13.54355981380538}, {"entity": "Denmark", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 13.71017939674154}, {"entity": "Denmark", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 18.012636183976298}, {"entity": "Dominican Rep", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.11178840182838039}, {"entity": "Dominican Rep", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 2.8009782025465917}, {"entity": "Dominican Rep", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.016641602839008784}, {"entity": "Dominican Rep", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.03417819931477326}, {"entity": "Dominican Rep", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.00733093024379832}, {"entity": "Dominican Rep", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.003122590252754685}, {"entity": "Dominican Rep", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.004522868066886586}, {"entity": "Dominican Rep", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.004201336502357805}, {"entity": "Dominican Rep", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.0014888281871811044}, {"entity": "Dominican Rep", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.0003841428041789365}, {"entity": "Dominican Rep", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.16643536955639332}, {"entity": "Dominican Rep", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.3383246514147037}, {"entity": "Dominican Rep", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.08180339968324256}, {"entity": "Dominican Rep", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.030688573905780326}, {"entity": "Dominican Rep", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 3.2140426604273222}, {"entity": "East Africa", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.005586189153101766}, {"entity": "East Africa", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.0015600819148444691}, {"entity": "East Africa", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.003855144008013912}, {"entity": "Ecuador", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.0017469750889679714}, {"entity": "Ecuador", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.023280241212766496}, {"entity": "Ecuador", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.0011297955209347615}, {"entity": "Ecuador", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.0004481727794893812}, {"entity": "Ecuador", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.000211125413755057}, {"entity": "Ecuador", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.009380684557287482}, {"entity": "Ecuador", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.001659219123505976}, {"entity": "Ecuador", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.0010309109979023076}, {"entity": "Ecuador", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.010113108904747132}, {"entity": "Ecuador", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.0022154962314510584}, {"entity": "Ecuador", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.00530402770752215}, {"entity": "Ecuador", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.005342273536497701}, {"entity": "Ecuador", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.00705349568377517}, {"entity": "Ecuador", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.0019046410124052015}, {"entity": "Ecuador", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.01311587523665371}, {"entity": "Egypt", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.21839686029410613}, {"entity": "Egypt", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.2447935884486115}, {"entity": "Egypt", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.04748840874353567}, {"entity": "Egypt", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.0007113163038723289}, {"entity": "Egypt", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.11578948611359545}, {"entity": "Egypt", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.062364056989425966}, {"entity": "Egypt", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.05785110017873459}, {"entity": "Egypt", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.1282691522703146}, {"entity": "Egypt", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.16306568981275618}, {"entity": "Egypt", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.236515539679739}, {"entity": "Egypt", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.1595719406871635}, {"entity": "Egypt", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 1.053089953433595}, {"entity": "Egypt", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 1.7400172882315934}, {"entity": "Egypt", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.0031093809065991457}, {"entity": "Egypt", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.4129267423238342}, {"entity": "Egypt", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.7666760402799987}, {"entity": "Egypt", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 1.67786900444397}, {"entity": "El Salvador", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.00017509990777743621}, {"entity": "El Salvador", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.004584909807165759}, {"entity": "El Salvador", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.4596184164818403}, {"entity": "El Salvador", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.4287369553050819}, {"entity": "El Salvador", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.10328473433285781}, {"entity": "El Salvador", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.1976782711051165}, {"entity": "El Salvador", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.061895374282298486}, {"entity": "El Salvador", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.05878159408914135}, {"entity": "El Salvador", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.05089038579819574}, {"entity": "El Salvador", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.26798898873297794}, {"entity": "Estonia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.25857292090324907}, {"entity": "Estonia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.5009486985471581}, {"entity": "Estonia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.8226406830413483}, {"entity": "Estonia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.4839190689912876}, {"entity": "Estonia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.6119743748747635}, {"entity": "Estonia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.4604920022358046}, {"entity": "Estonia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.34594257176818366}, {"entity": "Estonia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.42107809102679733}, {"entity": "Estonia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.549226512203684}, {"entity": "Estonia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.12368315214404417}, {"entity": "Estonia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.44132284472665684}, {"entity": "Estonia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.6131651728696161}, {"entity": "Estonia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 1.0451280605702133}, {"entity": "Estonia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.6314698267022477}, {"entity": "Estonia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.6689755694261394}, {"entity": "Estonia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.5630988686315691}, {"entity": "Estonia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.7095462201591052}, {"entity": "Ethiopia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.0010091047040971168}, {"entity": "Ethiopia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.00013428827215756492}, {"entity": "Ethiopia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 1.4938751120406334e-05}, {"entity": "Ethiopia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.001112684313097626}, {"entity": "Ethiopia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.0002720570231520527}, {"entity": "Ethiopia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.0002219859564673856}, {"entity": "Ethiopia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.009109278680650068}, {"entity": "Fiji Is", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 3.6231070211330105}, {"entity": "Fiji Is", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 4.8198629018406995}, {"entity": "Fiji Is", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 5.118918367041229}, {"entity": "Fiji Is", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 5.018443695079928}, {"entity": "Fiji Is", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 5.299407506611136}, {"entity": "Fiji Is", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 1.9541866455678176}, {"entity": "Fiji Is", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 1.537958773605139}, {"entity": "Fiji Is", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 1.4288866722786235}, {"entity": "Fiji Is", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.6582147379632501}, {"entity": "Fiji Is", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 2.7577334538651495}, {"entity": "Fiji Is", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 2.367928429654633}, {"entity": "Fiji Is", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.6402487359450455}, {"entity": "Fiji Is", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.5096753399800468}, {"entity": "Fiji Is", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 3.701424940897435}, {"entity": "Fiji Is", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 1.921025778280101}, {"entity": "Fiji Is", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 2.2992817053985335}, {"entity": "Fiji Is", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 5.5005121937070225}, {"entity": "Finland", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 4.735364259936249}, {"entity": "Finland", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 6.321245078432821}, {"entity": "Finland", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 5.097300396735958}, {"entity": "Finland", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 4.999300785158241}, {"entity": "Finland", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 5.925595196644554}, {"entity": "Finland", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 5.5931834068255295}, {"entity": "Finland", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 3.72903579778187}, {"entity": "Finland", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 4.27326025821373}, {"entity": "Finland", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 6.842017726121301}, {"entity": "Finland", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 4.225651766676971}, {"entity": "Finland", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 3.0471211123244757}, {"entity": "Finland", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 3.685077864087569}, {"entity": "Finland", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 3.4587327075329366}, {"entity": "Finland", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 3.511887815933782}, {"entity": "Finland", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 3.0921232214220957}, {"entity": "Finland", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 3.8046989641763953}, {"entity": "Finland", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 4.735751616919115}, {"entity": "France", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 60.75619770400798}, {"entity": "France", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 74.6682942825804}, {"entity": "France", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 94.48178337461758}, {"entity": "France", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 86.87069520178594}, {"entity": "France", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 69.47435908043158}, {"entity": "France", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 94.17501142647056}, {"entity": "France", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 98.2977939162449}, {"entity": "France", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 114.74193064676062}, {"entity": "France", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 134.31688469158135}, {"entity": "France", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 109.95302889200285}, {"entity": "France", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 105.19006766740395}, {"entity": "France", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 107.34638988337178}, {"entity": "France", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 161.94367693655414}, {"entity": "France", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 224.91833193705133}, {"entity": "France", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 209.61425117149642}, {"entity": "France", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 266.60238135370264}, {"entity": "France", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 356.119344554359}, {"entity": "French Polynesia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.0}, {"entity": "French Polynesia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.00045321814350384967}, {"entity": "French Polynesia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.008380491691251114}, {"entity": "French Polynesia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.06590224188693798}, {"entity": "Gabon", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.012697953081342589}, {"entity": "Gabon", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.0013923457624997987}, {"entity": "Gabon", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0006148949253083517}, {"entity": "Gabon", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.0017671152720889409}, {"entity": "Georgia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.006499988899331122}, {"entity": "Georgia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.0021290385863494124}, {"entity": "Georgia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.0004953308972797402}, {"entity": "Georgia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.002786681169866632}, {"entity": "Georgia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.007116367393872214}, {"entity": "Georgia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.00909092196666552}, {"entity": "Georgia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.03976305845891305}, {"entity": "Georgia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.017077098348942214}, {"entity": "Georgia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.01865088437576715}, {"entity": "Georgia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.017211159586316988}, {"entity": "Georgia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.032823927245972224}, {"entity": "Georgia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.01786628660396101}, {"entity": "Georgia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.04939424870725659}, {"entity": "Georgia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.049040945147730865}, {"entity": "Georgia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.45452889107333766}, {"entity": "Georgia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.030798469525236884}, {"entity": "Georgia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.32988469707987306}, {"entity": "Germany", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 110.88179914104295}, {"entity": "Germany", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 114.46629332911237}, {"entity": "Germany", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 139.5594841576037}, {"entity": "Germany", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 103.92776899381806}, {"entity": "Germany", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 113.74190530454707}, {"entity": "Germany", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 102.74616183666257}, {"entity": "Germany", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 100.9122666778535}, {"entity": "Germany", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 93.45152835450678}, {"entity": "Germany", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 91.15900316808573}, {"entity": "Germany", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 95.14415679002973}, {"entity": "Germany", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 87.60948445135764}, {"entity": "Germany", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 75.5392470750672}, {"entity": "Germany", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 106.00642785132338}, {"entity": "Germany", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 109.98531181934025}, {"entity": "Germany", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 110.46865428592436}, {"entity": "Germany", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 130.53032338664474}, {"entity": "Germany", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 189.11113952762082}, {"entity": "Ghana", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.052890173410404626}, {"entity": "Ghana", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.0007036474164133739}, {"entity": "Ghana", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.0005739378442171519}, {"entity": "Ghana", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.0020541719687329576}, {"entity": "Ghana", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.20043290043290043}, {"entity": "Ghana", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 1.4938751120406334e-05}, {"entity": "Ghana", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.3843679061411581}, {"entity": "Ghana", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.00646180614002441}, {"entity": "Ghana", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.010643796128562873}, {"entity": "Ghana", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.0016125907190476425}, {"entity": "Ghana", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 6.843221788818175e-05}, {"entity": "Ghana", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.023740185324683777}, {"entity": "Ghana", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.04222622469373012}, {"entity": "Gibraltar", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.09226657111019275}, {"entity": "Gibraltar", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.2744164884675454}, {"entity": "Gibraltar", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.37959193954396825}, {"entity": "Gibraltar", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.3097105303151535}, {"entity": "Gibraltar", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.2942147418972831}, {"entity": "Gibraltar", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.24884205682307214}, {"entity": "Gibraltar", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.24444851165656767}, {"entity": "Gibraltar", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.04143978356638112}, {"entity": "Gibraltar", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.08950230945767274}, {"entity": "Gibraltar", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.16236510355619577}, {"entity": "Gibraltar", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.03235584264005}, {"entity": "Gibraltar", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.09302160909382223}, {"entity": "Gibraltar", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.8936457958363695}, {"entity": "Greece", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 1.2005152545333926}, {"entity": "Greece", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.828414795316436}, {"entity": "Greece", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 3.8911480020418012}, {"entity": "Greece", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.34192581328352256}, {"entity": "Greece", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.670657726732561}, {"entity": "Greece", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.9748476782036377}, {"entity": "Greece", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 1.0437900221453347}, {"entity": "Greece", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.8889453436026182}, {"entity": "Greece", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 1.1461246044575728}, {"entity": "Greece", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 1.311983999476128}, {"entity": "Greece", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 1.489918723109275}, {"entity": "Greece", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.6192437814031634}, {"entity": "Greece", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 1.09981049060476}, {"entity": "Greece", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 2.1920389512491725}, {"entity": "Greece", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 1.643643891491639}, {"entity": "Greece", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 1.5551882040799074}, {"entity": "Greece", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 1.5083315780829214}, {"entity": "Guadeloupe", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.0065938564491580705}, {"entity": "Guadeloupe", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.009539777557123114}, {"entity": "Guadeloupe", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.006312782429358173}, {"entity": "Guadeloupe", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.0007710280373831777}, {"entity": "Guam", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.000333015628767957}, {"entity": "Guam", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.14590653735809456}, {"entity": "Guatemala Rp", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.051483600644491485}, {"entity": "Guatemala Rp", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.15121978297814315}, {"entity": "Guatemala Rp", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.030585749307809038}, {"entity": "Guatemala Rp", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.2545785434300202}, {"entity": "Guatemala Rp", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.19703162856150175}, {"entity": "Guatemala Rp", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.2352805309089302}, {"entity": "Guatemala Rp", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.5272732351509098}, {"entity": "Guinea", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.01690715141829804}, {"entity": "Guinea", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.0005121796037084167}, {"entity": "Guinea", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.00015886267392619478}, {"entity": "Guinea", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.0008964676114809206}, {"entity": "Guinea", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.012299188118440291}, {"entity": "Guinea", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.3955858209585724}, {"entity": "Guinea", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.00015975368885790635}, {"entity": "Guinea", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.5143765194833417}, {"entity": "Guinea", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.2559617224300826}, {"entity": "Guinea", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.003023606117579796}, {"entity": "Guinea Bissau", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 5.511843573879373e-05}, {"entity": "Guyana", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.0005771097634596388}, {"entity": "Guyana", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.04118173679498657}, {"entity": "Guyana", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 6.0177523694899956e-05}, {"entity": "Guyana", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.03130261499977196}, {"entity": "Guyana", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.01523689696482957}, {"entity": "Guyana", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.024410590704791294}, {"entity": "Guyana", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.013514018037619887}, {"entity": "Guyana", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.011376955941924106}, {"entity": "Guyana", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.010781190449888572}, {"entity": "Guyana", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.005057749202037558}, {"entity": "Guyana", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.0036475328641248543}, {"entity": "Guyana", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.00259091948179818}, {"entity": "Honduras", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.6792225010621189}, {"entity": "Honduras", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.4176164441645676}, {"entity": "Honduras", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.3017869265650817}, {"entity": "Honduras", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 1.2933212612914018}, {"entity": "Honduras", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.0014713107511045652}, {"entity": "Honduras", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.005088626498003173}, {"entity": "Honduras", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.0013500924813349714}, {"entity": "Honduras", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.003684918112252501}, {"entity": "Honduras", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.05798542874946077}, {"entity": "Hongkong", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 6733.495472325174}, {"entity": "Hongkong", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 9735.525583271821}, {"entity": "Hongkong", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 11776.54783718347}, {"entity": "Hongkong", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 10885.16582014946}, {"entity": "Hongkong", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 11216.970724168454}, {"entity": "Hongkong", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 12356.627883106163}, {"entity": "Hongkong", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 11003.604569884716}, {"entity": "Hongkong", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 12855.921272215577}, {"entity": "Hongkong", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 13320.208845714717}, {"entity": "Hongkong", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 11112.242983836293}, {"entity": "Hongkong", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 9489.359852446765}, {"entity": "Hongkong", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 8151.98457311829}, {"entity": "Hongkong", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 9371.030244747513}, {"entity": "Hongkong", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 8777.824627824002}, {"entity": "Hongkong", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 6730.729081564433}, {"entity": "Hongkong", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 4559.14445804418}, {"entity": "Hongkong", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 5972.238852763155}, {"entity": "Hungary", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 26.313075474125164}, {"entity": "Hungary", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.7620978353656785}, {"entity": "Hungary", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.5847208417867199}, {"entity": "Hungary", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.4967738162498413}, {"entity": "Hungary", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.2550317574705082}, {"entity": "Hungary", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.08436848603290284}, {"entity": "Hungary", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.2825079196473063}, {"entity": "Hungary", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 1.6986682642983195}, {"entity": "Hungary", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 1.6588441482555256}, {"entity": "Hungary", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.17404882891570583}, {"entity": "Hungary", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.4559805240443337}, {"entity": "Hungary", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.32900775844798213}, {"entity": "Hungary", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.21554149336901218}, {"entity": "Hungary", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.29037569046108214}, {"entity": "Hungary", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.27643367100657135}, {"entity": "Hungary", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.16447899358034077}, {"entity": "Hungary", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.22686121487646638}, {"entity": "Iceland", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.03583336624035597}, {"entity": "Iceland", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.001874095175087876}, {"entity": "Iceland", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.5788789985731133}, {"entity": "Iceland", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.10241115421054023}, {"entity": "Iceland", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.018832426825258985}, {"entity": "Iceland", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.08098692585418082}, {"entity": "Iceland", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.012163333257510706}, {"entity": "Iceland", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.003477649666935215}, {"entity": "Iceland", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.008874398903313301}, {"entity": "Iceland", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.007814095660345004}, {"entity": "Iceland", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.0002521667933100746}, {"entity": "Iceland", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.00024337014539725887}, {"entity": "Iceland", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.03696043941521073}, {"entity": "Iceland", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.0017309635901175198}, {"entity": "Iceland", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.01066751974678075}, {"entity": "Iceland", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.014897312082996307}, {"entity": "Iceland", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.05137119026749815}, {"entity": "Indonesia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.26481366611331}, {"entity": "Indonesia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.1013642911940449}, {"entity": "Indonesia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.12461256325454624}, {"entity": "Indonesia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 1.8297770751278135}, {"entity": "Indonesia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.11495913158434451}, {"entity": "Indonesia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.6731656713202928}, {"entity": "Indonesia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.0984957689571955}, {"entity": "Indonesia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.14403971670046428}, {"entity": "Indonesia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.9356096284975316}, {"entity": "Indonesia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 5.927934465288357}, {"entity": "Indonesia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 6.197891972902271}, {"entity": "Indonesia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 5.741126896724134}, {"entity": "Indonesia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 12.214305577391524}, {"entity": "Indonesia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 13.735508607032685}, {"entity": "Indonesia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 9.982686794206735}, {"entity": "Indonesia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 5.746747258592579}, {"entity": "Indonesia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 8.707312873213798}, {"entity": "Iran", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.048486550003821106}, {"entity": "Iran", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.5047011362246759}, {"entity": "Iran", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.21210352097124496}, {"entity": "Iran", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.02396858625378984}, {"entity": "Iran", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.01666273552418773}, {"entity": "Iran", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 17.561678432579814}, {"entity": "Iran", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.04146025920097497}, {"entity": "Iran", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.04626481951306669}, {"entity": "Iran", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.06842530704584994}, {"entity": "Iran", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.00045544862303819954}, {"entity": "Iran", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.0017134142848960422}, {"entity": "Iran", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0010814365306785515}, {"entity": "Iraq", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.0029945419520547947}, {"entity": "Iraq", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.01368982177367404}, {"entity": "Iraq", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.027855528345517883}, {"entity": "Iraq", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.0052128730863704896}, {"entity": "Iraq", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 1.5217018557036368}, {"entity": "Iraq", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.018204654529233907}, {"entity": "Iraq", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.011449021130091951}, {"entity": "Iraq", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.07416976982753874}, {"entity": "Iraq", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.04024238097805816}, {"entity": "Iraq", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.002926200049832216}, {"entity": "Iraq", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.004331657397674511}, {"entity": "Iraq", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0013998084392471551}, {"entity": "Iraq", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.00507513961787714}, {"entity": "Iraq", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.010834489323094474}, {"entity": "Ireland", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 1.4254429632610488}, {"entity": "Ireland", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.626891929749128}, {"entity": "Ireland", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.4787438750900126}, {"entity": "Ireland", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 1.2480818089522001}, {"entity": "Ireland", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 1.021687961017476}, {"entity": "Ireland", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 1.0056648469085552}, {"entity": "Ireland", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.8578139700898635}, {"entity": "Ireland", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.7710585993322743}, {"entity": "Ireland", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 1.2313409055476054}, {"entity": "Ireland", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 2.137609228575704}, {"entity": "Ireland", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 2.1215554790730415}, {"entity": "Ireland", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 1.9475908999347684}, {"entity": "Ireland", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 3.1785872264930815}, {"entity": "Ireland", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 4.302798043987652}, {"entity": "Ireland", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 5.878449514703215}, {"entity": "Ireland", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 2.534465465306323}, {"entity": "Ireland", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 4.04452119310672}, {"entity": "Israel", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 821.3329117444355}, {"entity": "Israel", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 1180.4622030770495}, {"entity": "Israel", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 1512.8887593601783}, {"entity": "Israel", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 1180.5427701201424}, {"entity": "Israel", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 1312.4389884884918}, {"entity": "Israel", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 1186.5029813546676}, {"entity": "Israel", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 996.9301104890977}, {"entity": "Israel", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 1001.7444339805513}, {"entity": "Israel", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 1022.9323380270262}, {"entity": "Israel", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 1006.598286832891}, {"entity": "Israel", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 911.1611355157959}, {"entity": "Israel", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 845.5447552471429}, {"entity": "Israel", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 1477.2864750316955}, {"entity": "Israel", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 1273.9050465704063}, {"entity": "Israel", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 713.7234998841761}, {"entity": "Israel", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 548.2704669628273}, {"entity": "Israel", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 596.6773143992317}, {"entity": "Italy", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 63.97102215290465}, {"entity": "Italy", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 83.86628237623032}, {"entity": "Italy", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 112.00510015151592}, {"entity": "Italy", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 77.22276824805212}, {"entity": "Italy", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 81.9554990803835}, {"entity": "Italy", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 100.97681482907004}, {"entity": "Italy", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 76.32898200824033}, {"entity": "Italy", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 93.40791039811073}, {"entity": "Italy", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 106.61691035327267}, {"entity": "Italy", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 96.61254423441014}, {"entity": "Italy", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 87.31645146642384}, {"entity": "Italy", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 69.77531787548509}, {"entity": "Italy", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 122.83675391064713}, {"entity": "Italy", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 176.22962923965747}, {"entity": "Italy", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 164.86732655866155}, {"entity": "Italy", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 158.60274637124667}, {"entity": "Italy", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 212.51243904582924}, {"entity": "Jamaica", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.018884818552716343}, {"entity": "Jamaica", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.001672267292912041}, {"entity": "Jamaica", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.10585870514524397}, {"entity": "Jamaica", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.0009850009179364788}, {"entity": "Jamaica", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.018439930390760955}, {"entity": "Jamaica", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.007102477477477479}, {"entity": "Jamaica", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.02444671195919016}, {"entity": "Jamaica", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.01880458085914884}, {"entity": "Jamaica", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.10495841680902103}, {"entity": "Jamaica", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.08725189687807214}, {"entity": "Jamaica", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.16773527107197883}, {"entity": "Jamaica", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.29445418002678975}, {"entity": "Jamaica", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.19749537028705982}, {"entity": "Jamaica", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.14096138539013595}, {"entity": "Jamaica", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.33427381581294224}, {"entity": "Japan", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 280.4002849319331}, {"entity": "Japan", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 329.40836908864634}, {"entity": "Japan", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 351.13977414555984}, {"entity": "Japan", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 372.77483491262166}, {"entity": "Japan", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 351.89901513867943}, {"entity": "Japan", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 369.39026061149923}, {"entity": "Japan", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 240.0900845987991}, {"entity": "Japan", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 267.5720309195255}, {"entity": "Japan", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 274.97589892812994}, {"entity": "Japan", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 405.64877458009283}, {"entity": "Japan", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 391.7879709318789}, {"entity": "Japan", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 320.0360256183551}, {"entity": "Japan", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 364.916304818963}, {"entity": "Japan", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 318.0408482922152}, {"entity": "Japan", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 243.22164105599398}, {"entity": "Japan", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 215.3197860721114}, {"entity": "Japan", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 204.77998984441084}, {"entity": "Jordon", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.2639672550310775}, {"entity": "Jordon", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.6204848060322058}, {"entity": "Jordon", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.2280380249926835}, {"entity": "Jordon", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.25038153760635684}, {"entity": "Jordon", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.12416737845988224}, {"entity": "Jordon", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.1229450611932738}, {"entity": "Jordon", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.029563166144200625}, {"entity": "Jordon", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.0107765424779063}, {"entity": "Jordon", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.06975136812386748}, {"entity": "Jordon", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.35550974879511665}, {"entity": "Jordon", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 1.2262353583783032}, {"entity": "Jordon", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 1.6470112289488312}, {"entity": "Jordon", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 1.9732568116551044}, {"entity": "Jordon", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 1.0749851106758008}, {"entity": "Jordon", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 3.1134640242130773}, {"entity": "Jordon", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 2.826510830452614}, {"entity": "Jordon", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 6.047024723960045}, {"entity": "Kazakhstan", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 1.0788971379330663}, {"entity": "Kazakhstan", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.6819907219860609}, {"entity": "Kazakhstan", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 1.3346573984187031}, {"entity": "Kazakhstan", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 1.9757784196213044}, {"entity": "Kazakhstan", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.28179070892618796}, {"entity": "Kazakhstan", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.8732316310472836}, {"entity": "Kazakhstan", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.19816204224197334}, {"entity": "Kazakhstan", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.027276991866374473}, {"entity": "Kazakhstan", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.2599742860980801}, {"entity": "Kazakhstan", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.19212766635445444}, {"entity": "Kazakhstan", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.05299410486878935}, {"entity": "Kazakhstan", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.0634959581020913}, {"entity": "Kazakhstan", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.08756947490370218}, {"entity": "Kazakhstan", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.06692928664246516}, {"entity": "Kazakhstan", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.10050421834546625}, {"entity": "Kazakhstan", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.03463592536259698}, {"entity": "Kazakhstan", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.094638088781927}, {"entity": "Kenya", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.008394019220733082}, {"entity": "Kenya", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.03924797041695066}, {"entity": "Kenya", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.010315983207538057}, {"entity": "Kenya", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.017526398199192265}, {"entity": "Kenya", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.02055968368345962}, {"entity": "Kenya", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.000288425171177046}, {"entity": "Kenya", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.003081888893429141}, {"entity": "Kenya", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.009805041511951149}, {"entity": "Kenya", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.002349709546656159}, {"entity": "Kenya", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.026653965559637276}, {"entity": "Kenya", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.012671829889102829}, {"entity": "Kenya", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.0034337503090623774}, {"entity": "Kenya", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.005351027809806111}, {"entity": "Kenya", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 7.444500693638538e-05}, {"entity": "Kenya", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0772006140453108}, {"entity": "Kenya", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.012748795430893332}, {"entity": "Kenya", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.005075520505363245}, {"entity": "Kiribati Rep", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 2.5837791641777814}, {"entity": "Kiribati Rep", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 4.822770107851671}, {"entity": "Kiribati Rep", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 15.950424958785147}, {"entity": "Kiribati Rep", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 9.609494180250086e-05}, {"entity": "Korea  R.P", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 26.654392157576318}, {"entity": "Korea  R.P", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 38.84571299224594}, {"entity": "Korea  R.P", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 47.352329779416976}, {"entity": "Korea  R.P", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 34.120293923221716}, {"entity": "Korea  R.P", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 41.319198213191385}, {"entity": "Korea  R.P", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 44.906256472885346}, {"entity": "Korea  R.P", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 41.404255376123224}, {"entity": "Korea  R.P", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 51.946523975116804}, {"entity": "Korea  R.P", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 51.16521302994868}, {"entity": "Korea  R.P", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 54.19104441233263}, {"entity": "Korea  R.P", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 50.85764920360942}, {"entity": "Korea  R.P", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 47.14118895009212}, {"entity": "Korea  R.P", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 74.05653338680062}, {"entity": "Korea  R.P", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 59.083338657218945}, {"entity": "Korea  R.P", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 37.905633094542566}, {"entity": "Korea  R.P", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 34.36818554188842}, {"entity": "Korea  R.P", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 41.17962151441515}, {"entity": "Korea R.P", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.011137538932930315}, {"entity": "Korea R.P", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.09962077867150641}, {"entity": "Korea R.P", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.08516150744292376}, {"entity": "Korea R.P", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.061323327253181306}, {"entity": "Korea R.P", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.025120741503784433}, {"entity": "Korea R.P", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.046024861734050966}, {"entity": "Kosovo", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.002402227074235808}, {"entity": "Kuwait", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 72.31882717335624}, {"entity": "Kuwait", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 31.74902711780217}, {"entity": "Kuwait", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 51.32987930083405}, {"entity": "Kuwait", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 57.807657549032754}, {"entity": "Kuwait", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 39.37619741037127}, {"entity": "Kuwait", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 56.839159852277625}, {"entity": "Kuwait", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 50.140285516382555}, {"entity": "Kuwait", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 12.525794370854486}, {"entity": "Kuwait", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 18.923971486559303}, {"entity": "Kuwait", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 28.1855649180307}, {"entity": "Kuwait", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 25.15229960847707}, {"entity": "Kuwait", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 34.850924363019516}, {"entity": "Kuwait", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 70.04643727490726}, {"entity": "Kuwait", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 60.171990727185225}, {"entity": "Kuwait", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 90.02898890985934}, {"entity": "Kuwait", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 99.00350631544266}, {"entity": "Kuwait", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 190.88563524487634}, {"entity": "Kyrgyzstan", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.0007866180570448209}, {"entity": "Kyrgyzstan", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.0010643330388692578}, {"entity": "Kyrgyzstan", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.09965594441910172}, {"entity": "Kyrgyzstan", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.016151083695743976}, {"entity": "Kyrgyzstan", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.05956839542722109}, {"entity": "Kyrgyzstan", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.11545078441708287}, {"entity": "Kyrgyzstan", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.04507204059334995}, {"entity": "Kyrgyzstan", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.016724475562890768}, {"entity": "Kyrgyzstan", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.09058642371018506}, {"entity": "Kyrgyzstan", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.010241890001878858}, {"entity": "Kyrgyzstan", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.013778619423168199}, {"entity": "Kyrgyzstan", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.19030980746936074}, {"entity": "Kyrgyzstan", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.12208248273882107}, {"entity": "Kyrgyzstan", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.07379238579196715}, {"entity": "Kyrgyzstan", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 1.6975340102594936}, {"entity": "Latvia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.06519091848514426}, {"entity": "Latvia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.06704130217621797}, {"entity": "Latvia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 23.394897102710832}, {"entity": "Latvia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.486091294190926}, {"entity": "Latvia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.2149694735963837}, {"entity": "Latvia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.18796160626654027}, {"entity": "Latvia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.18192172079138622}, {"entity": "Latvia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.1843399239918951}, {"entity": "Latvia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.21993934837581924}, {"entity": "Latvia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.35444557141603855}, {"entity": "Latvia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.35898050198770015}, {"entity": "Latvia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.3760134308702001}, {"entity": "Latvia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.604813220525273}, {"entity": "Latvia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 1.3080024890958635}, {"entity": "Latvia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 1.1388225479701148}, {"entity": "Latvia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 2.0562425056586693}, {"entity": "Latvia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 1.61145627827734}, {"entity": "Lebanon", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 12.272990987134245}, {"entity": "Lebanon", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 13.683019297840895}, {"entity": "Lebanon", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 11.35494010274849}, {"entity": "Lebanon", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 14.639134838571}, {"entity": "Lebanon", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 15.470935380085464}, {"entity": "Lebanon", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 16.099097615992566}, {"entity": "Lebanon", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 16.700600026856527}, {"entity": "Lebanon", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 14.33235582167851}, {"entity": "Lebanon", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 16.35798385739762}, {"entity": "Lebanon", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 16.652245690091764}, {"entity": "Lebanon", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 9.685780787714823}, {"entity": "Lebanon", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 4.521685100227592}, {"entity": "Lebanon", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 9.336240947111852}, {"entity": "Lebanon", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 11.802127666452542}, {"entity": "Lebanon", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 11.18582337919856}, {"entity": "Lebanon", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 6.342098820876515}, {"entity": "Lebanon", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 11.104768604362322}, {"entity": "Liberia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 8.674900565208289e-05}, {"entity": "Liberia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 2.9841838257236645e-05}, {"entity": "Liberia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 5.9521972141949346e-05}, {"entity": "Liberia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.0017097593437962663}, {"entity": "Liberia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.003550172287772789}, {"entity": "Libya", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.008854813367370928}, {"entity": "Libya", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.0019653483146067417}, {"entity": "Libya", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.0016187536514118792}, {"entity": "Libya", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.025898804716523987}, {"entity": "Libya", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 1.7324473213056053e-05}, {"entity": "Libya", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.000531099927004495}, {"entity": "Liechtenstein", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.019242915491178576}, {"entity": "Liechtenstein", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.046070635687573094}, {"entity": "Liechtenstein", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 5.352674329912082e-05}, {"entity": "Liechtenstein", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.0004924107197813697}, {"entity": "Liechtenstein", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.00953471711460547}, {"entity": "Lithuania", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.06723852480265066}, {"entity": "Lithuania", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.051369493967690694}, {"entity": "Lithuania", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.5874120944658927}, {"entity": "Lithuania", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.0019070721054135536}, {"entity": "Lithuania", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.11692322563083456}, {"entity": "Lithuania", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.3072977405125031}, {"entity": "Lithuania", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.1097478256500931}, {"entity": "Lithuania", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.10015295525613623}, {"entity": "Lithuania", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.27180524219639796}, {"entity": "Lithuania", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.6405203691646163}, {"entity": "Lithuania", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 2.8059014116749577}, {"entity": "Lithuania", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 1.0711204209308018}, {"entity": "Lithuania", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 3.4137124298016417}, {"entity": "Lithuania", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 2.707719783310337}, {"entity": "Lithuania", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 3.079658553511461}, {"entity": "Lithuania", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 2.859693559624848}, {"entity": "Lithuania", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 5.297631881848308}, {"entity": "Luxembourg", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.0794710562359152}, {"entity": "Luxembourg", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.03643159503918667}, {"entity": "Luxembourg", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.03378006849656369}, {"entity": "Luxembourg", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.011070026803705352}, {"entity": "Luxembourg", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.02142795634781839}, {"entity": "Luxembourg", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.07280615782789648}, {"entity": "Luxembourg", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.05054740031921987}, {"entity": "Luxembourg", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.028032180666258857}, {"entity": "Luxembourg", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.004415482799781643}, {"entity": "Luxembourg", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.008610165175257953}, {"entity": "Luxembourg", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.008570962777061715}, {"entity": "Luxembourg", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.0856510024711313}, {"entity": "Luxembourg", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.02847146765310542}, {"entity": "Luxembourg", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.014038590318030517}, {"entity": "Luxembourg", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.04735442010048187}, {"entity": "Luxembourg", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.01673411842454878}, {"entity": "Luxembourg", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.2492794361649736}, {"entity": "Macao", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.20765098052970618}, {"entity": "Macao", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.058410837481870224}, {"entity": "Macao", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.3100820340697725}, {"entity": "Macao", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.19556206539550408}, {"entity": "Macao", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 1.8777243850175043}, {"entity": "Macao", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.3206961177304821}, {"entity": "Macao", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.0015403075558184237}, {"entity": "Macao", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.012662185399405971}, {"entity": "Macao", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.00031917409337268375}, {"entity": "Macao", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.0014002653397108761}, {"entity": "Macao", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.01925538503888239}, {"entity": "Macao", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.07611089958300525}, {"entity": "Macao", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.009895492585505657}, {"entity": "Macao", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.019305278546291178}, {"entity": "Macao", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.05040163561182882}, {"entity": "Macao", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.2880347745086566}, {"entity": "Madagascar", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.00704586200483541}, {"entity": "Madagascar", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.051490947648585216}, {"entity": "Madagascar", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.045045706618962435}, {"entity": "Madagascar", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.048656766095288996}, {"entity": "Madagascar", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.05514803289211248}, {"entity": "Madagascar", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.0699535945343179}, {"entity": "Madagascar", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.004987930164703894}, {"entity": "Madagascar", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.03745855890101987}, {"entity": "Madagascar", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.02886795601175295}, {"entity": "Madagascar", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.20440682757100873}, {"entity": "Madagascar", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.09762145093219946}, {"entity": "Malawi", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.02671765584970111}, {"entity": "Malawi", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.0010242085661080075}, {"entity": "Malawi", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.000722820474996312}, {"entity": "Malawi", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.003967876506638041}, {"entity": "Malawi", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.0002656932282882425}, {"entity": "Malawi", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.00014641288433382135}, {"entity": "Malaysia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 81.65618043637234}, {"entity": "Malaysia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 67.9657426303938}, {"entity": "Malaysia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 62.70545829116227}, {"entity": "Malaysia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 136.66448955914368}, {"entity": "Malaysia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 133.29572452291467}, {"entity": "Malaysia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 69.73722832345106}, {"entity": "Malaysia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 31.712419635811766}, {"entity": "Malaysia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 64.91543173008279}, {"entity": "Malaysia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 70.85046936077741}, {"entity": "Malaysia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 72.60109944010955}, {"entity": "Malaysia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 99.17956089905613}, {"entity": "Malaysia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 80.31995769822773}, {"entity": "Malaysia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 170.177894136553}, {"entity": "Malaysia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 229.8490563157167}, {"entity": "Malaysia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 123.2344020061314}, {"entity": "Malaysia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 181.4937604871994}, {"entity": "Malaysia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 201.28721775507282}, {"entity": "Maldives", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.026184062815805865}, {"entity": "Maldives", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.23324148524743493}, {"entity": "Maldives", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.322650263019065}, {"entity": "Maldives", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.04117158775519365}, {"entity": "Maldives", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.2148395574865529}, {"entity": "Maldives", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.026207631078141717}, {"entity": "Maldives", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.002277104394816008}, {"entity": "Maldives", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.00032873779401381244}, {"entity": "Maldives", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.010906120945452891}, {"entity": "Maldives", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.006191199063701007}, {"entity": "Maldives", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.07829803740511389}, {"entity": "Maldives", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.023929144785783167}, {"entity": "Maldives", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.017268217167933034}, {"entity": "Maldives", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.00212260879813813}, {"entity": "Maldives", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.06723900384799145}, {"entity": "Maldives", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.05357027812211579}, {"entity": "Maldives", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.035842748318253764}, {"entity": "Mali", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.00010941218304658223}, {"entity": "Mali", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 1.368644357763635e-05}, {"entity": "Mali", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.00029974581554841496}, {"entity": "Malta", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.003447708647905985}, {"entity": "Malta", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.011979264621469938}, {"entity": "Malta", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.003609536272624917}, {"entity": "Malta", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.01101178147776529}, {"entity": "Malta", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.17730675459899145}, {"entity": "Malta", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.009743745019920319}, {"entity": "Malta", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.02159936333607267}, {"entity": "Malta", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.009969198324112293}, {"entity": "Malta", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.008144043230107598}, {"entity": "Malta", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.012269204983568878}, {"entity": "Malta", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.028052627844652362}, {"entity": "Malta", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.02355593783487405}, {"entity": "Malta", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.01458143146908158}, {"entity": "Malta", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.033203501649274665}, {"entity": "Malta", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.030865340183663773}, {"entity": "Malta", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.02028802662525725}, {"entity": "Malta", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.03846866602944953}, {"entity": "Martinique", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.02067496904515869}, {"entity": "Mauritania", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 2.639009843506716e-05}, {"entity": "Mauritania", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.001999782571932452}, {"entity": "Mauritania", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.005958376384347686}, {"entity": "Mauritius", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 2.5484622415484153}, {"entity": "Mauritius", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 2.0139388694595235}, {"entity": "Mauritius", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 2.4040254810386528}, {"entity": "Mauritius", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 1.5553049468739137}, {"entity": "Mauritius", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 1.931961149985097}, {"entity": "Mauritius", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 2.1804928047588805}, {"entity": "Mauritius", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 1.1790550182871118}, {"entity": "Mauritius", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 1.680237326925372}, {"entity": "Mauritius", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 1.3019185666708142}, {"entity": "Mauritius", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 1.1083196708045957}, {"entity": "Mauritius", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.5761173052443166}, {"entity": "Mauritius", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.2945114314065399}, {"entity": "Mauritius", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 4.423846745601461}, {"entity": "Mauritius", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 4.599662945768653}, {"entity": "Mauritius", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 2.2795161699901216}, {"entity": "Mauritius", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 2.142166065791456}, {"entity": "Mauritius", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 1.8374082674405336}, {"entity": "Mexico", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.7116655029076603}, {"entity": "Mexico", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.2082373356698032}, {"entity": "Mexico", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 1.0522412910766152}, {"entity": "Mexico", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.9319401403257747}, {"entity": "Mexico", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 1.2691458547098586}, {"entity": "Mexico", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.983153371696208}, {"entity": "Mexico", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 2.685905337373461}, {"entity": "Mexico", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 2.9609580776960662}, {"entity": "Mexico", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 2.7585442642215012}, {"entity": "Mexico", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 2.341111976641331}, {"entity": "Mexico", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 2.5308712794509876}, {"entity": "Mexico", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.9016336795968963}, {"entity": "Mexico", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 3.504314329479912}, {"entity": "Mexico", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 3.250408974059528}, {"entity": "Mexico", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 8.573245057114836}, {"entity": "Mexico", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 8.652775391626717}, {"entity": "Mexico", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 146.6690055438451}, {"entity": "Moldova", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.0051834399316685684}, {"entity": "Moldova", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.010337270987525798}, {"entity": "Moldova", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 9.33336432708145e-05}, {"entity": "Moldova", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.0028314011649285815}, {"entity": "Moldova", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.13294851442272512}, {"entity": "Moldova", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.32775015933630264}, {"entity": "Moldova", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.8113154624404456}, {"entity": "Mongolia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.0015420726306465899}, {"entity": "Mongolia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.009300482004501938}, {"entity": "Mongolia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.005171991364367262}, {"entity": "Mongolia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.0014947791164658635}, {"entity": "Mongolia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.011193435593155941}, {"entity": "Mongolia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.0011124078042934243}, {"entity": "Mongolia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.0004291674921710443}, {"entity": "Mongolia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.0006139209889530198}, {"entity": "Mongolia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.020783785257777788}, {"entity": "Mongolia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.005963967164669873}, {"entity": "Mongolia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.0046712872137884215}, {"entity": "Mongolia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.016962751504345668}, {"entity": "Mongolia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0008982108610686282}, {"entity": "Mongolia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.022236589882351238}, {"entity": "Mongolia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.0036314170806718707}, {"entity": "Montenegro", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.04689176371918202}, {"entity": "Montenegro", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.3412401611711875}, {"entity": "Montenegro", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.10157716887168866}, {"entity": "Montenegro", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.005683553504658902}, {"entity": "Montenegro", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0019705029013539653}, {"entity": "Montenegro", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.020238963729146724}, {"entity": "Morocco", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.03417542734341606}, {"entity": "Morocco", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.14207794667331977}, {"entity": "Morocco", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.27908910328940467}, {"entity": "Morocco", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.09492566756094098}, {"entity": "Morocco", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.11555525056769163}, {"entity": "Morocco", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.11999490260898907}, {"entity": "Morocco", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.0644633998116579}, {"entity": "Morocco", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.11112377828911749}, {"entity": "Morocco", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.07451872770666651}, {"entity": "Morocco", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.11663261005968982}, {"entity": "Morocco", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.15623238609455598}, {"entity": "Morocco", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 1.411341166140649}, {"entity": "Morocco", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.1460700412145351}, {"entity": "Morocco", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.2080672067191913}, {"entity": "Morocco", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.06682182496122638}, {"entity": "Morocco", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 1.2408031963860398}, {"entity": "Morocco", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.7355744388339305}, {"entity": "Mozambique", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.005376036901732863}, {"entity": "Mozambique", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.003850062695924765}, {"entity": "Mozambique", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 7.363770250368188e-05}, {"entity": "Mozambique", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 1.563232765358762e-05}, {"entity": "Mozambique", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.003231471931159312}, {"entity": "Mozambique", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.0027979445712354397}, {"entity": "Mozambique", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.00227260785034943}, {"entity": "Mozambique", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.0}, {"entity": "Mozambique", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0037960633139325654}, {"entity": "Mozambique", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 6.33887632852283e-05}, {"entity": "Myanmar", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.0012243223663106276}, {"entity": "Myanmar", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 2.9572674848440043e-05}, {"entity": "Myanmar", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.008753172444352994}, {"entity": "Myanmar", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.0018809397265149973}, {"entity": "Myanmar", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.000185386038771561}, {"entity": "Myanmar", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 2.1844948355692746e-05}, {"entity": "Myanmar", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 1.3787271590867312e-05}, {"entity": "Namibia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.1472761626055023}, {"entity": "Namibia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 1.138763428776517}, {"entity": "Namibia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 1.1770795613941174}, {"entity": "Namibia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.2948546407657957}, {"entity": "Namibia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.3181925046071655}, {"entity": "Namibia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.24034581622787224}, {"entity": "Namibia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.017536696264207053}, {"entity": "Namibia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.7795817409205197}, {"entity": "Namibia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.0229130324968112}, {"entity": "Namibia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.006154060772473089}, {"entity": "Namibia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.0025682695377114827}, {"entity": "Namibia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.029712196517919058}, {"entity": "Namibia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.49863694984387397}, {"entity": "Namibia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.8866529768502668}, {"entity": "Namibia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.005915499829243304}, {"entity": "Namibia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.011731382037058893}, {"entity": "Namibia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 1.696655629804802}, {"entity": "Nepal", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 2.8350832722759245}, {"entity": "Nepal", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 1.9488260690481591}, {"entity": "Nepal", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 3.0543297077492384}, {"entity": "Nepal", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 5.343374679504444}, {"entity": "Nepal", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 6.593241202546743}, {"entity": "Nepal", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 10.869518166327081}, {"entity": "Nepal", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 7.195739786102319}, {"entity": "Nepal", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 10.068123427650525}, {"entity": "Nepal", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 11.485762925481595}, {"entity": "Nepal", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 11.61733893859761}, {"entity": "Nepal", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 20.15360923410297}, {"entity": "Nepal", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 14.323811074271672}, {"entity": "Nepal", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 31.258667198212397}, {"entity": "Nepal", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 13.69658699538753}, {"entity": "Nepal", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 22.864636320726824}, {"entity": "Nepal", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 31.03581396786134}, {"entity": "Nepal", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 12.313601434816132}, {"entity": "Netherland", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 122.23591727298609}, {"entity": "Netherland", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 402.2884920586634}, {"entity": "Netherland", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 339.45348643366964}, {"entity": "Netherland", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 239.27474238812357}, {"entity": "Netherland", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 456.7013879807041}, {"entity": "Netherland", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 335.0055122413909}, {"entity": "Netherland", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 62.24420486335626}, {"entity": "Netherland", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 289.72684338881083}, {"entity": "Netherland", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 324.3668788692181}, {"entity": "Netherland", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 358.00859835403145}, {"entity": "Netherland", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 279.08967082493064}, {"entity": "Netherland", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 156.26064220051148}, {"entity": "Netherland", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 695.6311151086115}, {"entity": "Netherland", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 312.20859672183536}, {"entity": "Netherland", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 151.28348521340095}, {"entity": "Netherland", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 414.8931236810223}, {"entity": "Netherland", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 272.19669542153076}, {"entity": "Netherland Antilles", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 2.6581139209224975}, {"entity": "Netherland Antilles", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 1.2175872760708295}, {"entity": "Netherland Antilles", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 1.2138451301174469}, {"entity": "Netherland Antilles", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.9314047269411286}, {"entity": "Netherland Antilles", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 1.5424050523871813}, {"entity": "Netherland Antilles", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.42278531578618267}, {"entity": "Netherland Antilles", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.5723829679481585}, {"entity": "Netherland Antilles", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.923763193487869}, {"entity": "Netherland Antilles", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 1.0363187161682128}, {"entity": "Netherland Antilles", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 2.596103232973718}, {"entity": "Netherland Antilles", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 2.1719083682151714}, {"entity": "New Caledonia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.0012123441442821316}, {"entity": "New Caledonia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.03814622916609331}, {"entity": "New Caledonia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.015576451865801423}, {"entity": "New Caledonia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.015240382159017393}, {"entity": "New Caledonia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.005955797119170478}, {"entity": "New Caledonia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.02181419631598176}, {"entity": "New Caledonia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.023734181819141918}, {"entity": "New Zealand", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 11.519247565561166}, {"entity": "New Zealand", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 14.002408857330044}, {"entity": "New Zealand", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 14.552005714183935}, {"entity": "New Zealand", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 14.341144957479052}, {"entity": "New Zealand", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 13.790254011002412}, {"entity": "New Zealand", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 13.83735703151979}, {"entity": "New Zealand", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 12.82387623714753}, {"entity": "New Zealand", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 13.167628984502354}, {"entity": "New Zealand", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 15.827343289772354}, {"entity": "New Zealand", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 12.789617813389329}, {"entity": "New Zealand", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 10.887086616059474}, {"entity": "New Zealand", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 11.928602295804799}, {"entity": "New Zealand", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 18.461403347692602}, {"entity": "New Zealand", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 16.411789227525652}, {"entity": "New Zealand", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 13.28537049037827}, {"entity": "New Zealand", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 13.036548459747786}, {"entity": "New Zealand", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 23.988881679900683}, {"entity": "Niger", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.00014869492690674498}, {"entity": "Nigeria", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.02627030880259746}, {"entity": "Nigeria", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.025896300328380334}, {"entity": "Nigeria", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 5.612213870132516}, {"entity": "Nigeria", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.012706611047149808}, {"entity": "Nigeria", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.01925466449428377}, {"entity": "Nigeria", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.07444274547009679}, {"entity": "Nigeria", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.06999422225418338}, {"entity": "Nigeria", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.1253397978583349}, {"entity": "Nigeria", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.08797229906797702}, {"entity": "Nigeria", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.07970502486203833}, {"entity": "Nigeria", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.12177302645171473}, {"entity": "Nigeria", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.09472935121218792}, {"entity": "Nigeria", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.0719970401802483}, {"entity": "Nigeria", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.010311775668929022}, {"entity": "Nigeria", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0032099382125844933}, {"entity": "Nigeria", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.037718917857015165}, {"entity": "Nigeria", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.02647714619614991}, {"entity": "North Korea (Korea Dp. Rp)", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.3657130281690141}, {"entity": "North Korea (Korea Dp. Rp)", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 1.841271471548574}, {"entity": "North Korea (Korea Dp. Rp)", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.0006528926844806377}, {"entity": "North Korea (Korea Dp. Rp)", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 1.5515256188831318e-05}, {"entity": "North Korea (Korea Dp. Rp)", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.10643412997148115}, {"entity": "North Korea (Korea Dp. Rp)", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.40397220050031707}, {"entity": "North Korea (Korea Dp. Rp)", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.4366496138796461}, {"entity": "North Korea (Korea Dp. Rp)", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.14699868587792878}, {"entity": "Norway", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 4.569253006963838}, {"entity": "Norway", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 5.164086051738429}, {"entity": "Norway", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 6.946580962286172}, {"entity": "Norway", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 6.602716870181509}, {"entity": "Norway", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 7.670132263652191}, {"entity": "Norway", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 8.126639135167725}, {"entity": "Norway", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 5.412306667656771}, {"entity": "Norway", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 3.3471215268034036}, {"entity": "Norway", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 3.9862538828329415}, {"entity": "Norway", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 4.435340426630506}, {"entity": "Norway", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 5.65160769811794}, {"entity": "Norway", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 8.887866555061066}, {"entity": "Norway", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 13.093716197011572}, {"entity": "Norway", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 11.972342153178843}, {"entity": "Norway", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 11.01553386596545}, {"entity": "Norway", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 10.38425707810089}, {"entity": "Norway", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 11.24091674893717}, {"entity": "Oman", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 5.044842571071395}, {"entity": "Oman", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 7.331383918276101}, {"entity": "Oman", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 6.616468042809734}, {"entity": "Oman", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 10.235309111013642}, {"entity": "Oman", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 10.92648480167311}, {"entity": "Oman", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 4.141523594632192}, {"entity": "Oman", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 1.922304123901934}, {"entity": "Oman", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 2.7551400507970203}, {"entity": "Oman", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 2.4838116153795697}, {"entity": "Oman", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 3.1858659522420942}, {"entity": "Oman", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 4.483830462554031}, {"entity": "Oman", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 4.377870089837719}, {"entity": "Oman", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 3.6931750497833495}, {"entity": "Oman", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 6.725821266208105}, {"entity": "Oman", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 34.719703881466636}, {"entity": "Oman", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 27.400736508835685}, {"entity": "Oman", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 24.509480510358248}, {"entity": "Others", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 42.27031943392028}, {"entity": "Others", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 49.236691805713015}, {"entity": "Others", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 40.33393519551314}, {"entity": "Others", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 6.014470215203826}, {"entity": "Others", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 45.30801965339468}, {"entity": "Others", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.5774374580865383}, {"entity": "Others", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.1296702373785562}, {"entity": "Others", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.9402945361471423}, {"entity": "Others", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.680715010120474}, {"entity": "Others", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.5281708491769166}, {"entity": "Others", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.2375740942250118}, {"entity": "Others", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.27112828632901986}, {"entity": "Others", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 2.5292912375823495}, {"entity": "Others", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 2.870399312091801}, {"entity": "Others", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 14.089845659285205}, {"entity": "Others", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 5.318996744044777}, {"entity": "Others", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 9.655754404494026}, {"entity": "Pakistan Ir", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 2.6669740273980396}, {"entity": "Pakistan Ir", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 2.384356059771957}, {"entity": "Pakistan Ir", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 24.714372189137404}, {"entity": "Pakistan Ir", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.03412473630124333}, {"entity": "Pakistan Ir", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 22.43258353154837}, {"entity": "Pakistan Ir", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.010182984309512276}, {"entity": "Pakistan Ir", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.07605265341225116}, {"entity": "Pakistan Ir", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.03273316720463355}, {"entity": "Pakistan Ir", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.002197031975982437}, {"entity": "Panama Republic", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.7240318692200542}, {"entity": "Panama Republic", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.20143323176722353}, {"entity": "Panama Republic", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 1.262505752780248}, {"entity": "Panama Republic", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.06385509244424406}, {"entity": "Panama Republic", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.30350457947047327}, {"entity": "Panama Republic", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.6569142645898371}, {"entity": "Panama Republic", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 1.6490962801118967}, {"entity": "Panama Republic", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 1.9665196521632236}, {"entity": "Panama Republic", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.47369847705959983}, {"entity": "Panama Republic", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.5878342198819979}, {"entity": "Panama Republic", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.33814024406539894}, {"entity": "Panama Republic", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.4324632226252532}, {"entity": "Panama Republic", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 1.1589554715900796}, {"entity": "Panama Republic", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 2.2041462256051}, {"entity": "Panama Republic", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 1.8479982007127382}, {"entity": "Panama Republic", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 2.9475855756035125}, {"entity": "Panama Republic", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 5.209662253324658}, {"entity": "Papua N Gna", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.001320776973889528}, {"entity": "Papua N Gna", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.03589133071844425}, {"entity": "Papua N Gna", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.000529732654073306}, {"entity": "Paraguay", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.00017803956434763281}, {"entity": "Paraguay", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.005872248163969411}, {"entity": "Paraguay", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.03876441312798486}, {"entity": "Paraguay", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 8.635578583765112e-05}, {"entity": "Paraguay", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.00027031138674657104}, {"entity": "Peru", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.0029964001025909637}, {"entity": "Peru", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.008931549280338392}, {"entity": "Peru", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.6984847911303069}, {"entity": "Peru", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.002443866374589266}, {"entity": "Peru", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.0036723116438356165}, {"entity": "Peru", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.0006975072929334973}, {"entity": "Peru", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.07091771424616124}, {"entity": "Peru", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.11179703807605763}, {"entity": "Peru", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.04711051584699541}, {"entity": "Peru", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.022441822414626326}, {"entity": "Peru", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.09472788515055494}, {"entity": "Peru", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.024098662107088165}, {"entity": "Peru", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.09048551903134622}, {"entity": "Peru", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.05182618698926726}, {"entity": "Peru", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.05920900357493936}, {"entity": "Peru", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.31937605313499334}, {"entity": "Peru", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.9075630225856375}, {"entity": "Philippines", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 7.090582532849368}, {"entity": "Philippines", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 7.169308273592093}, {"entity": "Philippines", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 5.69396813381629}, {"entity": "Philippines", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.6368532872564898}, {"entity": "Philippines", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.026090644932785338}, {"entity": "Philippines", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.011396424067033792}, {"entity": "Philippines", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.030146754650626505}, {"entity": "Philippines", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.3466698276366423}, {"entity": "Philippines", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.22602308087107667}, {"entity": "Philippines", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.1254981828756251}, {"entity": "Philippines", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.18765962478524856}, {"entity": "Philippines", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.20365358903466751}, {"entity": "Philippines", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.15887791994495687}, {"entity": "Philippines", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.3309335299951113}, {"entity": "Philippines", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.886022712243515}, {"entity": "Philippines", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 1.1020164918149158}, {"entity": "Philippines", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 1.8417395887042967}, {"entity": "Poland", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 3.2458549831159544}, {"entity": "Poland", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 5.619948189205615}, {"entity": "Poland", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 8.035834098510266}, {"entity": "Poland", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 6.5042318637289265}, {"entity": "Poland", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 4.644358739518769}, {"entity": "Poland", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 6.609009888204662}, {"entity": "Poland", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 10.019896770825445}, {"entity": "Poland", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 9.925371199787481}, {"entity": "Poland", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 12.847459992987472}, {"entity": "Poland", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 11.075306495357026}, {"entity": "Poland", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 8.404871847506167}, {"entity": "Poland", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 8.150203935897745}, {"entity": "Poland", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 12.30743778357883}, {"entity": "Poland", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 12.838454586972453}, {"entity": "Poland", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 14.8052889771523}, {"entity": "Poland", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 17.70091511860833}, {"entity": "Poland", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 20.13978362970401}, {"entity": "Portugal", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 1.0422701851848135}, {"entity": "Portugal", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.9073525255388383}, {"entity": "Portugal", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.8965038573398719}, {"entity": "Portugal", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.35053919524503874}, {"entity": "Portugal", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.4212286869520417}, {"entity": "Portugal", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.10848922109118321}, {"entity": "Portugal", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.34758985349974175}, {"entity": "Portugal", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.844265907113628}, {"entity": "Portugal", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.880669718629138}, {"entity": "Portugal", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.7701202225653996}, {"entity": "Portugal", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.9018284778649682}, {"entity": "Portugal", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.4880570452127973}, {"entity": "Portugal", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.6577496909703368}, {"entity": "Portugal", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 1.135882223432003}, {"entity": "Portugal", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 1.2196576984252725}, {"entity": "Portugal", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 1.8406112174101135}, {"entity": "Portugal", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 2.5987432617275883}, {"entity": "Puerto Rico", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.0002454880060960788}, {"entity": "Puerto Rico", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.005136741822224723}, {"entity": "Puerto Rico", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.4532559194032692}, {"entity": "Puerto Rico", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.00031316877494352857}, {"entity": "Puerto Rico", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.002293415575053343}, {"entity": "Puerto Rico", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.014031574286064942}, {"entity": "Puerto Rico", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.01738212267261719}, {"entity": "Puerto Rico", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.12970037186435152}, {"entity": "Puerto Rico", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.13938668845308305}, {"entity": "Puerto Rico", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.11036498187235787}, {"entity": "Puerto Rico", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.07489695992908363}, {"entity": "Puerto Rico", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.038438652885331846}, {"entity": "Puerto Rico", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.8677322601239903}, {"entity": "Puerto Rico", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 2.390694584145157}, {"entity": "Puerto Rico", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 1.0370566448957284}, {"entity": "Puerto Rico", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 2.4115278169658545}, {"entity": "Puerto Rico", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.8267526938430584}, {"entity": "Qatar", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 2.651273890743033}, {"entity": "Qatar", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 3.4318990803165748}, {"entity": "Qatar", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 3.594894061346523}, {"entity": "Qatar", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 8.403871650298091}, {"entity": "Qatar", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 8.389138249017625}, {"entity": "Qatar", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 24.835069178909244}, {"entity": "Qatar", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 31.78626994536517}, {"entity": "Qatar", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 11.490178992316205}, {"entity": "Qatar", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 65.90987482631633}, {"entity": "Qatar", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 89.42505610111161}, {"entity": "Qatar", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 107.16373524886885}, {"entity": "Qatar", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 60.623600266532314}, {"entity": "Qatar", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 112.46985735818524}, {"entity": "Qatar", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 197.29438142877973}, {"entity": "Qatar", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 96.96973015918873}, {"entity": "Qatar", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 112.35714675921687}, {"entity": "Qatar", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 79.2606520929668}, {"entity": "Re-Union", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.00505066041207671}, {"entity": "Re-Union", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.0023420977027573476}, {"entity": "Re-Union", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.006761510590428705}, {"entity": "Re-Union", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.0020324469034445833}, {"entity": "Re-Union", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.006101794105369266}, {"entity": "Re-Union", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.0033203564173235264}, {"entity": "Re-Union", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.019745545004467742}, {"entity": "Re-Union", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.03625318719615286}, {"entity": "Re-Union", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.04320290638837547}, {"entity": "Re-Union", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.01513484373975428}, {"entity": "Re-Union", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.03941122149166843}, {"entity": "Re-Union", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.0871696941169708}, {"entity": "Re-Union", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.04324823854630345}, {"entity": "Re-Union", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.031997909144233554}, {"entity": "Re-Union", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.03235476382459914}, {"entity": "Re-Union", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.030046491258344507}, {"entity": "Re-Union", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.01130338192357649}, {"entity": "Rep. Of San Marino", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.002967093129232187}, {"entity": "Rep. Of San Marino", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.44172454392960825}, {"entity": "Rep. Of San Marino", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.008745925377826015}, {"entity": "Rep. Of San Marino", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.0043023166023166024}, {"entity": "Rep. Of San Marino", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.06816768159263278}, {"entity": "Rep. Of San Marino", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.036035106106849096}, {"entity": "Rep. Of San Marino", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.00773365250597596}, {"entity": "Rep. Of San Marino", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.028456647048421886}, {"entity": "Rep. Of San Marino", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.009556972552179608}, {"entity": "Rep. Of San Marino", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.04248152069527647}, {"entity": "Rep. Of San Marino", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.031478584041048786}, {"entity": "Rep. Of San Marino", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.010895688588738388}, {"entity": "Rep. Of San Marino", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.004380775485822325}, {"entity": "Rep. Of San Marino", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.0026695421353749448}, {"entity": "Romania", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.6271415118703914}, {"entity": "Romania", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.22101327048536298}, {"entity": "Romania", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.16790549384956396}, {"entity": "Romania", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.2211618015223142}, {"entity": "Romania", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.31787646566088684}, {"entity": "Romania", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.2784977229285192}, {"entity": "Romania", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.2776881088623181}, {"entity": "Romania", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.4561052075099887}, {"entity": "Romania", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 2.032913999854284}, {"entity": "Romania", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 2.1182295065020944}, {"entity": "Romania", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 1.8657724534942814}, {"entity": "Romania", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 3.5287109764455478}, {"entity": "Romania", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 4.770750392405523}, {"entity": "Romania", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 3.053106299658583}, {"entity": "Romania", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 4.0973060857469115}, {"entity": "Romania", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 6.992131865193336}, {"entity": "Romania", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 6.600643951514443}, {"entity": "Russia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 4.2784914190724885}, {"entity": "Russia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 8.53431628435993}, {"entity": "Russia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 8.731877105685127}, {"entity": "Russia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 10.141932379987445}, {"entity": "Russia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 7.343946229292446}, {"entity": "Russia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 4.1266500127198675}, {"entity": "Russia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 1.1063548273816703}, {"entity": "Russia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 1.599303391297543}, {"entity": "Russia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 1.6683902972147338}, {"entity": "Russia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 2.663724441313196}, {"entity": "Russia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 8.567871828684657}, {"entity": "Russia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 9.108539702148242}, {"entity": "Russia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 25.153901756759645}, {"entity": "Russia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 15.372760029128731}, {"entity": "Russia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 5.904309550605482}, {"entity": "Russia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 8.42267318922169}, {"entity": "Russia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 16.854252838693657}, {"entity": "Rwanda", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.0016151704444047831}, {"entity": "Rwanda", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.00012035504738979991}, {"entity": "Rwanda", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.00024748871742611735}, {"entity": "Rwanda", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.0}, {"entity": "Rwanda", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.6335441925994396}, {"entity": "Rwanda", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.002580183740447007}, {"entity": "Saint Lucia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 3.625920341741253}, {"entity": "Saudi Arabia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 9.957599823997768}, {"entity": "Saudi Arabia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 15.391237927436686}, {"entity": "Saudi Arabia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 31.8542189460001}, {"entity": "Saudi Arabia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 6.81139941410803}, {"entity": "Saudi Arabia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 9.145710507327188}, {"entity": "Saudi Arabia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 33.717998711136}, {"entity": "Saudi Arabia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 6.766191350117659}, {"entity": "Saudi Arabia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 33.072493321827196}, {"entity": "Saudi Arabia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 11.386802629521295}, {"entity": "Saudi Arabia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 30.913441719553305}, {"entity": "Saudi Arabia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 41.159607976825306}, {"entity": "Saudi Arabia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 47.46000829265062}, {"entity": "Saudi Arabia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 71.43524609759444}, {"entity": "Saudi Arabia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 69.20371856451447}, {"entity": "Saudi Arabia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 97.16668341667365}, {"entity": "Saudi Arabia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 142.34046313441291}, {"entity": "Saudi Arabia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 244.78645006034972}, {"entity": "Scotland", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.3034877491814781}, {"entity": "Scotland", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.0003684012400354296}, {"entity": "Scotland", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.010701276213938972}, {"entity": "Scotland", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.0007121274990569596}, {"entity": "Scotland", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.0002025744759102611}, {"entity": "Scotland", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.011614419452693628}, {"entity": "Scotland", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.005889395337818647}, {"entity": "Senegal", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.00042441819339322345}, {"entity": "Senegal", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.0017525799851282541}, {"entity": "Senegal", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.0029333647992705624}, {"entity": "Senegal", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0001085763231231376}, {"entity": "Senegal", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.044890499570069915}, {"entity": "Serbia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.006118171911497361}, {"entity": "Serbia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.13015931612312612}, {"entity": "Serbia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.0239140711410541}, {"entity": "Serbia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.016176047161907018}, {"entity": "Serbia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.0035867311102663634}, {"entity": "Serbia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.2607513779648183}, {"entity": "Serbia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.015973921711935932}, {"entity": "Serbia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.057725669230594585}, {"entity": "Serbia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.018514947257146544}, {"entity": "Serbia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.01017963997713432}, {"entity": "Serbia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.07301447237685327}, {"entity": "Serbia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.11450227075287732}, {"entity": "Serbia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.10216212326158441}, {"entity": "Serbia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.15176824044699272}, {"entity": "Serbia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.14239210864510451}, {"entity": "Seychelles", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.2309102706227584}, {"entity": "Seychelles", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.007926867506916692}, {"entity": "Seychelles", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.01835403280450604}, {"entity": "Seychelles", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.013317856797131017}, {"entity": "Seychelles", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.026166835313197443}, {"entity": "Seychelles", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.008601069512881625}, {"entity": "Seychelles", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.001540646267616955}, {"entity": "Seychelles", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.019032196205080266}, {"entity": "Seychelles", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.01589352818170584}, {"entity": "Seychelles", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.009913209698892493}, {"entity": "Seychelles", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.008352267806598217}, {"entity": "Sierra Leone", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.0004964645704829246}, {"entity": "Sierra Leone", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 5.4518195447730675e-05}, {"entity": "Sierra Leone", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 6.103888176768602e-05}, {"entity": "Singapore", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 749.938631366396}, {"entity": "Singapore", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 566.2261589683603}, {"entity": "Singapore", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 638.4657443244516}, {"entity": "Singapore", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 712.7399394171067}, {"entity": "Singapore", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 623.42287318253}, {"entity": "Singapore", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 492.37144857824154}, {"entity": "Singapore", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 472.238107269346}, {"entity": "Singapore", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 656.9240410087527}, {"entity": "Singapore", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 599.6323612907695}, {"entity": "Singapore", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 662.6595991886667}, {"entity": "Singapore", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 618.607983830036}, {"entity": "Singapore", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 366.9325394560419}, {"entity": "Singapore", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 803.4474334763075}, {"entity": "Singapore", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 1319.4016222362525}, {"entity": "Singapore", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 602.0472538446037}, {"entity": "Singapore", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 529.390348888467}, {"entity": "Singapore", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 550.9113327560224}, {"entity": "Slovak Repub", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.00016278590562538635}, {"entity": "Slovak Repub", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.004012017837235229}, {"entity": "Slovak Repub", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.01277670690305545}, {"entity": "Slovak Repub", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.004326675290970395}, {"entity": "Slovak Repub", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.014623743892474126}, {"entity": "Slovak Repub", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.013637066038999087}, {"entity": "Slovak Repub", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.014130126114173898}, {"entity": "Slovak Repub", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.006313597570723661}, {"entity": "Slovak Repub", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.13143643283760253}, {"entity": "Slovak Repub", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.472002938875277}, {"entity": "Slovak Repub", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.3076499069068774}, {"entity": "Slovak Repub", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.41672234954802784}, {"entity": "Slovak Repub", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 1.4146792352334185}, {"entity": "Slovak Repub", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 4.205818601402959}, {"entity": "Slovak Repub", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 4.051000044935708}, {"entity": "Slovakia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.0009993980505795573}, {"entity": "Slovakia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.03223572909507252}, {"entity": "Slovakia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.06705270113285958}, {"entity": "Slovakia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.0623121170101846}, {"entity": "Slovakia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.15507856067428613}, {"entity": "Slovakia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.16083607768575525}, {"entity": "Slovakia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.07240339373298575}, {"entity": "Slovakia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.12866017105164704}, {"entity": "Slovakia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.32422347337646285}, {"entity": "Slovakia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.22680554986654014}, {"entity": "Slovakia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.03157440197415407}, {"entity": "Slovakia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.017970081944673595}, {"entity": "Slovakia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.0204626240446104}, {"entity": "Slovakia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.0035512184880842294}, {"entity": "Slovakia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0009774345360202726}, {"entity": "Slovakia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.022866662018791273}, {"entity": "Slovakia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.040133998699400784}, {"entity": "Slovenia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.16432221788761475}, {"entity": "Slovenia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.460571264642116}, {"entity": "Slovenia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.5167102568041647}, {"entity": "Slovenia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.31134993815702267}, {"entity": "Slovenia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.8970739132832334}, {"entity": "Slovenia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.2505681284502781}, {"entity": "Slovenia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.20015562907122675}, {"entity": "Slovenia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.25996123545835126}, {"entity": "Slovenia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.2869932894189599}, {"entity": "Slovenia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.275236369550247}, {"entity": "Slovenia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.16153525847027556}, {"entity": "Slovenia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.12918780492464}, {"entity": "Slovenia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.23011685675963872}, {"entity": "Slovenia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.5577486644329164}, {"entity": "Slovenia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.5013736227283273}, {"entity": "Slovenia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.4689864786392109}, {"entity": "Slovenia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.9471862773156298}, {"entity": "Solomon Is", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.0001933949922073194}, {"entity": "Somalia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.0034065500406834826}, {"entity": "South Africa", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 43.96802564395403}, {"entity": "South Africa", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 62.161967763924345}, {"entity": "South Africa", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 85.24732761559507}, {"entity": "South Africa", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 74.24356418472975}, {"entity": "South Africa", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 87.60605167357511}, {"entity": "South Africa", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 78.90732428125952}, {"entity": "South Africa", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 61.61294045916784}, {"entity": "South Africa", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 83.60452198588601}, {"entity": "South Africa", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 106.70861243521257}, {"entity": "South Africa", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 80.18042991929083}, {"entity": "South Africa", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 74.17859941833912}, {"entity": "South Africa", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 141.52808125143812}, {"entity": "South Africa", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 311.66046037094}, {"entity": "South Africa", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 67.83169365301868}, {"entity": "South Africa", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 27.975113691377505}, {"entity": "South Africa", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 20.862867276265884}, {"entity": "South Africa", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 23.329717950109675}, {"entity": "Spain", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 36.57370778622142}, {"entity": "Spain", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 39.79257651713714}, {"entity": "Spain", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 35.4799280127395}, {"entity": "Spain", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 29.89751557509221}, {"entity": "Spain", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 32.82601000812259}, {"entity": "Spain", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 43.709137991868744}, {"entity": "Spain", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 55.13001076801596}, {"entity": "Spain", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 46.39352312970941}, {"entity": "Spain", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 44.06784967890246}, {"entity": "Spain", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 46.33168245074749}, {"entity": "Spain", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 44.86475984066927}, {"entity": "Spain", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 26.4222136256297}, {"entity": "Spain", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 55.23021408361601}, {"entity": "Spain", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 56.30296188690323}, {"entity": "Spain", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 52.065777527796236}, {"entity": "Spain", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 69.15809682557484}, {"entity": "Spain", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 73.01379963153116}, {"entity": "Srilanka Dsr", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 4.37953744342014}, {"entity": "Srilanka Dsr", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 2.501838327072013}, {"entity": "Srilanka Dsr", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 6.249479371387327}, {"entity": "Srilanka Dsr", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 2.3890016023800373}, {"entity": "Srilanka Dsr", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 13.047291989714555}, {"entity": "Srilanka Dsr", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 24.927638714002565}, {"entity": "Srilanka Dsr", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 19.640763866579057}, {"entity": "Srilanka Dsr", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 7.418620694674792}, {"entity": "Srilanka Dsr", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 12.549777229161698}, {"entity": "Srilanka Dsr", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 17.446392247074314}, {"entity": "Srilanka Dsr", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 14.720811538867618}, {"entity": "Srilanka Dsr", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 11.703247758109677}, {"entity": "Srilanka Dsr", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 18.636442909461277}, {"entity": "Srilanka Dsr", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 47.49814654265787}, {"entity": "Srilanka Dsr", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 43.07240464677389}, {"entity": "Srilanka Dsr", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 19.896096393634785}, {"entity": "Srilanka Dsr", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 35.73548101978901}, {"entity": "St. Lucia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.0009825258309210387}, {"entity": "Sudan", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.011435067654639175}, {"entity": "Sudan", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.00031175946365864554}, {"entity": "Sudan", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 3.1036623215394166e-05}, {"entity": "Sudan", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.1204528569167517}, {"entity": "Sudan", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.0}, {"entity": "Sudan", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.0100495827790543}, {"entity": "Suriname", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.000477626164710858}, {"entity": "Suriname", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.0004613646974376462}, {"entity": "Suriname", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.0015056860045601587}, {"entity": "Suriname", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.00039520795398301597}, {"entity": "Suriname", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.0008334873165750566}, {"entity": "Suriname", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.0009573040470166594}, {"entity": "Swaziland", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 9.509064576236215}, {"entity": "Swaziland", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 3.2835567665294922}, {"entity": "Swaziland", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 1.1248258153981245}, {"entity": "Swaziland", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.29914107787350586}, {"entity": "Swaziland", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 1.4001870915358516}, {"entity": "Swaziland", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.4131651141882625}, {"entity": "Swaziland", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.022933249128583594}, {"entity": "Swaziland", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.15515828537905804}, {"entity": "Swaziland", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.022028906121634075}, {"entity": "Swaziland", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.0052881719332447275}, {"entity": "Swaziland", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 2.2867861847757603e-05}, {"entity": "Swaziland", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.02659686318108743}, {"entity": "Swaziland", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.007932916886257392}, {"entity": "Swaziland", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.010020364908502465}, {"entity": "Swaziland", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 21.219437047996625}, {"entity": "Swaziland", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.009548455850531476}, {"entity": "Sweden", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 17.32840750168658}, {"entity": "Sweden", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 16.427548353457063}, {"entity": "Sweden", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 23.019079848504084}, {"entity": "Sweden", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 16.394922639144724}, {"entity": "Sweden", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 19.343112416289337}, {"entity": "Sweden", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 17.39391508406126}, {"entity": "Sweden", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 15.229526501244782}, {"entity": "Sweden", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 20.530414963755806}, {"entity": "Sweden", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 14.910645896441691}, {"entity": "Sweden", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 20.181774092308732}, {"entity": "Sweden", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 17.340856364107697}, {"entity": "Sweden", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 15.191491194526094}, {"entity": "Sweden", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 21.06031866369943}, {"entity": "Sweden", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 22.438064079144603}, {"entity": "Sweden", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 18.70944394870164}, {"entity": "Sweden", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 19.617240311889525}, {"entity": "Sweden", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 24.774700858916205}, {"entity": "Switzerland", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 141.91990575065915}, {"entity": "Switzerland", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 293.40059944478526}, {"entity": "Switzerland", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 450.2389973684221}, {"entity": "Switzerland", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 227.08207089985592}, {"entity": "Switzerland", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 406.35501487525886}, {"entity": "Switzerland", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 308.8721251976373}, {"entity": "Switzerland", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 305.04359608365985}, {"entity": "Switzerland", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 236.19119644236054}, {"entity": "Switzerland", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 294.31625633333647}, {"entity": "Switzerland", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 308.4916092990122}, {"entity": "Switzerland", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 243.61296950740652}, {"entity": "Switzerland", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 152.50401481573283}, {"entity": "Switzerland", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 275.0948974154253}, {"entity": "Switzerland", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 467.70428643300403}, {"entity": "Switzerland", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 686.8800947340635}, {"entity": "Switzerland", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 517.7381933243774}, {"entity": "Switzerland", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 306.63817660886724}, {"entity": "Syrian Arab Republic", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.04372032784973101}, {"entity": "Syrian Arab Republic", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.5479794275102731}, {"entity": "Syrian Arab Republic", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 2.6692385953171316}, {"entity": "Syrian Arab Republic", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.0008305136880959705}, {"entity": "Taiwan", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 19.799265178652462}, {"entity": "Taiwan", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 28.41847170866421}, {"entity": "Taiwan", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 14.169776174365142}, {"entity": "Taiwan", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 19.023583673269915}, {"entity": "Taiwan", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 21.36581959817375}, {"entity": "Taiwan", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 22.754628430669758}, {"entity": "Taiwan", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 17.001822376674422}, {"entity": "Taiwan", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 15.027542403705258}, {"entity": "Taiwan", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 14.7168530984572}, {"entity": "Taiwan", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 9.638272175108872}, {"entity": "Taiwan", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 8.76285464025735}, {"entity": "Taiwan", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 10.418738367786727}, {"entity": "Taiwan", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 7.996517003210377}, {"entity": "Taiwan", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 2.328336065502339}, {"entity": "Taiwan", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 2.2504301765184342}, {"entity": "Taiwan", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 2.505322680144274}, {"entity": "Taiwan", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 6.583482749316894}, {"entity": "Tajikistan", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.0003474650880388585}, {"entity": "Tajikistan", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 4.656938838869916e-05}, {"entity": "Tajikistan", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.0011427637947342762}, {"entity": "Tajikistan", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.0}, {"entity": "Tajikistan", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.000529750294974596}, {"entity": "Tanzania", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.01692090497670701}, {"entity": "Tanzania", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.1242301271457058}, {"entity": "Tanzania", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.9230805605471903}, {"entity": "Tanzania", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 5.809013528083065}, {"entity": "Tanzania", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 13.869000383373688}, {"entity": "Tanzania", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 51.63911910327878}, {"entity": "Tanzania", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.32380960669807485}, {"entity": "Tanzania", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 4.6777947612703255}, {"entity": "Tanzania", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 37.193780574417055}, {"entity": "Tanzania", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.0017268930158741698}, {"entity": "Tanzania", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.0040828772481576155}, {"entity": "Tanzania", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 6.504813496944613}, {"entity": "Tanzania", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 9.408458389336328}, {"entity": "Tanzania", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.1967551880557344}, {"entity": "Tanzania", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.011283951127437951}, {"entity": "Tanzania", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.0057729793668826425}, {"entity": "Tanzania", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.00867080223382021}, {"entity": "Thailand", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 340.83041186732623}, {"entity": "Thailand", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 470.1043307203684}, {"entity": "Thailand", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 651.9630860056823}, {"entity": "Thailand", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 650.5944033380675}, {"entity": "Thailand", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 766.2625602266978}, {"entity": "Thailand", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 680.4404725286013}, {"entity": "Thailand", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 628.4858301444091}, {"entity": "Thailand", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 606.7229735554442}, {"entity": "Thailand", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 546.0567375531706}, {"entity": "Thailand", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 593.5654996995316}, {"entity": "Thailand", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 637.4435912230606}, {"entity": "Thailand", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 649.9933440655269}, {"entity": "Thailand", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 1160.8778320838576}, {"entity": "Thailand", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 1064.7614633399464}, {"entity": "Thailand", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 654.9633421672895}, {"entity": "Thailand", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 525.5566076295394}, {"entity": "Thailand", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 675.2021845607096}, {"entity": "Togo", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.002115641730209824}, {"entity": "Togo", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.00224195530726257}, {"entity": "Togo", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.0001696592676374947}, {"entity": "Togo", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.006625032371878019}, {"entity": "Trinidad", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.00037194825406088896}, {"entity": "Trinidad & Tobago", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.000345992813884098}, {"entity": "Trinidad & Tobago", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.06616906259181801}, {"entity": "Trinidad & Tobago", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.07258941892614187}, {"entity": "Trinidad & Tobago", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.09503887029352477}, {"entity": "Trinidad & Tobago", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.04299153044810283}, {"entity": "Trinidad & Tobago", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.09134970091593198}, {"entity": "Trinidad & Tobago", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.108935188116946}, {"entity": "Trinidad & Tobago", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.1342520152958245}, {"entity": "Trinidad & Tobago", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.05700848473108291}, {"entity": "Trinidad & Tobago", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.13411304295104942}, {"entity": "Trinidad & Tobago", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.07808818312272783}, {"entity": "Trinidad & Tobago", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.13630259425739502}, {"entity": "Trinidad & Tobago", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.16285137364191513}, {"entity": "Trinidad & Tobago", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.40175294714470083}, {"entity": "Trinidad & Tobago", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.2509116044544971}, {"entity": "Trinidad & Tobago", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.19799540522109904}, {"entity": "Trinidad & Tobago", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.5332144909646122}, {"entity": "Tunisia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.015513371834740115}, {"entity": "Tunisia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.03649880305299754}, {"entity": "Tunisia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.13373354420831005}, {"entity": "Tunisia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.12310530769895617}, {"entity": "Tunisia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.06194211466020355}, {"entity": "Tunisia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.1288950388878546}, {"entity": "Tunisia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 1.6455192721283178}, {"entity": "Tunisia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.08133122407026726}, {"entity": "Tunisia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 3.024829945423516}, {"entity": "Tunisia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.06391880343269828}, {"entity": "Tunisia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.04668288697953973}, {"entity": "Turkey", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 12.241303655318594}, {"entity": "Turkey", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 16.139410926690484}, {"entity": "Turkey", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 23.06981934344566}, {"entity": "Turkey", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 16.565396086795076}, {"entity": "Turkey", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 14.796457809242009}, {"entity": "Turkey", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 30.237189127699423}, {"entity": "Turkey", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 21.793475877096313}, {"entity": "Turkey", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 30.782605355657488}, {"entity": "Turkey", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 83.00611490557095}, {"entity": "Turkey", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 364.85922315083377}, {"entity": "Turkey", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 636.0927139287014}, {"entity": "Turkey", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 225.59036574526436}, {"entity": "Turkey", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 162.34954930883876}, {"entity": "Turkey", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 449.582126058783}, {"entity": "Turkey", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 42.26192475327316}, {"entity": "Turkey", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 31.24877542478605}, {"entity": "Turkey", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 66.7893594442378}, {"entity": "Uganda", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.026287870079408797}, {"entity": "Uganda", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.007525827516325152}, {"entity": "Uganda", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.00987563643008835}, {"entity": "Uganda", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.0006983062650554606}, {"entity": "Uganda", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.0038968346010399796}, {"entity": "Uganda", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.0012412965389378037}, {"entity": "Uganda", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.009771955909304164}, {"entity": "Uganda", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.015447714991855179}, {"entity": "Uganda", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.004530669558979422}, {"entity": "Uganda", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.0016359391390257819}, {"entity": "Uganda", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.002293890099795398}, {"entity": "Uganda", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0019661268714523}, {"entity": "Uganda", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.034655471268320706}, {"entity": "Uganda", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.010726137685549862}, {"entity": "Ukraine", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.5000780100563307}, {"entity": "Ukraine", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.1982845199384062}, {"entity": "Ukraine", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.2669401200700196}, {"entity": "Ukraine", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.5681221620731373}, {"entity": "Ukraine", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.818934609724996}, {"entity": "Ukraine", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.41779037444694467}, {"entity": "Ukraine", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.4901832230027236}, {"entity": "Ukraine", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.8788383096602329}, {"entity": "Ukraine", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.7980538224279199}, {"entity": "Ukraine", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 1.881295416817526}, {"entity": "Ukraine", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.9471541023760288}, {"entity": "Ukraine", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.8137678191279288}, {"entity": "Ukraine", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.43422952642477974}, {"entity": "Ukraine", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.006779011872845653}, {"entity": "Ukraine", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0076953482183894145}, {"entity": "Ukraine", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.0006598423770674492}, {"entity": "United Arab Emirates", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 12932.155367651763}, {"entity": "United Arab Emirates", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 22177.26924385267}, {"entity": "United Arab Emirates", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 19096.79716818382}, {"entity": "United Arab Emirates", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 18898.09850255398}, {"entity": "United Arab Emirates", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 13009.564667011016}, {"entity": "United Arab Emirates", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 11419.23723000951}, {"entity": "United Arab Emirates", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 12451.736662309362}, {"entity": "United Arab Emirates", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 13646.31686365429}, {"entity": "United Arab Emirates", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 10360.649533862803}, {"entity": "United Arab Emirates", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 10404.69869968552}, {"entity": "United Arab Emirates", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 9492.984321490425}, {"entity": "United Arab Emirates", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 3105.986061290613}, {"entity": "United Arab Emirates", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 5807.227278182782}, {"entity": "United Arab Emirates", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 6025.037783644904}, {"entity": "United Arab Emirates", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 8124.874603371689}, {"entity": "United Arab Emirates", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 7868.164367768049}, {"entity": "United Arab Emirates", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 8614.937525144154}, {"entity": "United Kingdom", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 338.7847764021281}, {"entity": "United Kingdom", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 362.9943448284506}, {"entity": "United Kingdom", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 485.1240584794685}, {"entity": "United Kingdom", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 439.3583186772323}, {"entity": "United Kingdom", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 409.5995641406489}, {"entity": "United Kingdom", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 449.4195556378272}, {"entity": "United Kingdom", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 520.3917029470192}, {"entity": "United Kingdom", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 501.3211524981715}, {"entity": "United Kingdom", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 854.6878318845056}, {"entity": "United Kingdom", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 729.9704914021243}, {"entity": "United Kingdom", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 446.55689089266457}, {"entity": "United Kingdom", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 363.5946918567479}, {"entity": "United Kingdom", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 702.0944780865941}, {"entity": "United Kingdom", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 629.3978355207865}, {"entity": "United Kingdom", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 579.2304428419159}, {"entity": "United Kingdom", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 777.6862218453056}, {"entity": "United Kingdom", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 709.6897441679127}, {"entity": "United States Of America", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 5035.749514230394}, {"entity": "United States Of America", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 6658.97607866622}, {"entity": "United States Of America", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 6936.582308274692}, {"entity": "United States Of America", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 6717.832444539685}, {"entity": "United States Of America", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 8027.825944953914}, {"entity": "United States Of America", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 8535.136256508615}, {"entity": "United States Of America", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 9064.05380676163}, {"entity": "United States Of America", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 9788.619376367813}, {"entity": "United States Of America", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 10075.83470060769}, {"entity": "United States Of America", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 10479.124055782162}, {"entity": "United States Of America", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 9175.938365387541}, {"entity": "United States Of America", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 8709.57594172598}, {"entity": "United States Of America", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 14610.14929104811}, {"entity": "United States Of America", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 12484.573959138714}, {"entity": "United States Of America", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 9821.882976530987}, {"entity": "United States Of America", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 9236.455445361626}, {"entity": "United States Of America", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 5087.3285439103365}, {"entity": "Uruguay", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.0018388593857262233}, {"entity": "Uruguay", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.11765223881165908}, {"entity": "Uruguay", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.00013140298723897912}, {"entity": "Uruguay", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.02694133673183829}, {"entity": "Uruguay", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.06621882042364612}, {"entity": "Uruguay", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.13182662257640185}, {"entity": "Uruguay", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.13158479068187467}, {"entity": "Uruguay", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.1767063448044172}, {"entity": "Uruguay", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.03656936597445022}, {"entity": "Uruguay", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.01867299911935612}, {"entity": "Uruguay", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.0022142984112347164}, {"entity": "Uruguay", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.07269969532246137}, {"entity": "Uruguay", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.09527977504732063}, {"entity": "Uruguay", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.04514775133599593}, {"entity": "Uruguay", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.06123151326351322}, {"entity": "Uruguay", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.11591132155453585}, {"entity": "Uzbekistan", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.39792598008574925}, {"entity": "Uzbekistan", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.0609596568090544}, {"entity": "Uzbekistan", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.0001188707280832095}, {"entity": "Uzbekistan", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.2773712518927591}, {"entity": "Uzbekistan", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.0027394555813322614}, {"entity": "Uzbekistan", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.007501351085336864}, {"entity": "Uzbekistan", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.16055617388506796}, {"entity": "Uzbekistan", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 1.0202471597260048}, {"entity": "Uzbekistan", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.4899613649181361}, {"entity": "Uzbekistan", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.093735409502596}, {"entity": "Uzbekistan", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 2.4289821220079304}, {"entity": "Vanuatu Rep", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.000450052614390943}, {"entity": "Vanuatu Rep", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.0}, {"entity": "Venezuela", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.05245479002104482}, {"entity": "Venezuela", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.021131384043614244}, {"entity": "Venezuela", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.06582355964122867}, {"entity": "Venezuela", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.6046049704293834}, {"entity": "Venezuela", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.9031002470828755}, {"entity": "Venezuela", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 1.1610545769651426}, {"entity": "Venezuela", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.28833680719551735}, {"entity": "Venezuela", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.42519237459947756}, {"entity": "Venezuela", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.2144982721072644}, {"entity": "Venezuela", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 1.1985770840401961}, {"entity": "Venezuela", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.36696922828777573}, {"entity": "Venezuela", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.436673462814567}, {"entity": "Venezuela", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.00015514707159677618}, {"entity": "Vietnam", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.4280034404041061}, {"entity": "Vietnam", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.32790790341646303}, {"entity": "Vietnam", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 1.3805209761860366}, {"entity": "Vietnam", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.5767935572520517}, {"entity": "Vietnam", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 4.03314255394217}, {"entity": "Vietnam", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 1.0778543775044007}, {"entity": "Vietnam", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 1.6403205049073712}, {"entity": "Vietnam", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 2.119870987141404}, {"entity": "Vietnam", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 7.118958497417276}, {"entity": "Vietnam", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 8.206413452263707}, {"entity": "Vietnam", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 6.492621992749352}, {"entity": "Vietnam", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 3.5806285070078885}, {"entity": "Vietnam", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 18.208507736676488}, {"entity": "Vietnam", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 23.06854401374021}, {"entity": "Vietnam", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 6.418781797292838}, {"entity": "Vietnam", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 6.95777141400068}, {"entity": "Vietnam", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 8.15094930537015}, {"entity": "Virgin Is  Us", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 2.4004114457056316}, {"entity": "Virgin Is  Us", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 3.37269604621883}, {"entity": "Virgin Is  Us", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 1.5521403330513415}, {"entity": "Virgin Is  Us", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 2.8468516801337422}, {"entity": "Virgin Is  Us", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 5.037179089622632}, {"entity": "Virgin Is  Us", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.031353651823359294}, {"entity": "Virgin Is  Us", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 2.831871400279748}, {"entity": "Virgin Is  Us", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 3.598088968083773}, {"entity": "Virgin Is  Us", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.693486429548542}, {"entity": "Virgin Is  Us", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 1.0865797120403584}, {"entity": "Virgin Is  Us", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 10.930913179732153}, {"entity": "West Indies", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.04098121971381355}, {"entity": "West Indies", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.08577949055331269}, {"entity": "West Indies", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.13444409431787238}, {"entity": "West Indies", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.02787936004661521}, {"entity": "West Indies", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.03802004019480247}, {"entity": "West Indies", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.009589368748993424}, {"entity": "West Indies", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.01351177397179835}, {"entity": "West Indies", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.00851198779293527}, {"entity": "West Indies", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.01787718771926562}, {"entity": "Yemen Republic", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.0009256872852233677}, {"entity": "Yemen Republic", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.02419255613657336}, {"entity": "Yugoslavia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.03635070905905208}, {"entity": "Yugoslavia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.048952102648872946}, {"entity": "Yugoslavia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.10454828173773863}, {"entity": "Yugoslavia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 0.05249959908579388}, {"entity": "Yugoslavia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.25964619419146134}, {"entity": "Yugoslavia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.09979212740566669}, {"entity": "Yugoslavia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.013801613326148408}, {"entity": "Yugoslavia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 0.00809820182917377}, {"entity": "Yugoslavia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.03224960086766439}, {"entity": "Yugoslavia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.04454699605620825}, {"entity": "Yugoslavia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.04657655924226243}, {"entity": "Yugoslavia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.15866780790438925}, {"entity": "Yugoslavia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.024898263863806013}, {"entity": "Yugoslavia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.0077334291207978535}, {"entity": "Zambia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.10362405648597266}, {"entity": "Zambia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.26344158692082537}, {"entity": "Zambia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 2.844828422917418}, {"entity": "Zambia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 3.9632895431106596}, {"entity": "Zambia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.5111805807680753}, {"entity": "Zambia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.2253002721954648}, {"entity": "Zambia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 0.7955819012713173}, {"entity": "Zambia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 9.458329512809332}, {"entity": "Zambia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 7.167578226818013}, {"entity": "Zambia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.5352184790036301}, {"entity": "Zambia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.014834554600955814}, {"entity": "Zambia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.013124547604158949}, {"entity": "Zambia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.004382745351174063}, {"entity": "Zambia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.0002634180666666644}, {"entity": "Zambia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0016691711983138876}, {"entity": "Zambia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.0017750376937228228}, {"entity": "Zambia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.005498082834489667}, {"entity": "Zimbabwe", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.4732180177551604}, {"entity": "Zimbabwe", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 0.30834086970126445}, {"entity": "Zimbabwe", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 0.0046409650155022205}, {"entity": "Zimbabwe", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 6.522233041220383e-05}, {"entity": "Zimbabwe", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.16306117663260428}, {"entity": "Zimbabwe", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 0.0021078795381972667}, {"entity": "Zimbabwe", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 6.205398696866275e-05}, {"entity": "Zimbabwe", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 0.00402809108182243}, {"entity": "Zimbabwe", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 0.00048711653591197723}, {"entity": "Zimbabwe", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.004695470476327876}, {"entity": "Zimbabwe", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.0007692585069173167}, {"entity": "Zimbabwe", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 2.2553762531434306e-05}, {"entity": "Totals", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 30599.887046706528}, {"entity": "Totals", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 45546.43938213003}, {"entity": "Totals", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 46789.91403699261}, {"entity": "Totals", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 43574.60276505273}, {"entity": "Totals", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 40170.72073059579}, {"entity": "Totals", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 39980.587453769454}, {"entity": "Totals", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 39245.84200291254}, {"entity": "Totals", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 43157.07627076557}, {"entity": "Totals", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 40964.94916165319}, {"entity": "Totals", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 39722.92131712093}, {"entity": "Totals", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 35595.20084123989}, {"entity": "Totals", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 25505.582270113853}, {"entity": "Totals", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 39569.22434766178}, {"entity": "Totals", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 37737.0511062157}, {"entity": "Totals", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 32285.84599571967}, {"entity": "Totals", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 28671.060334237704}, {"entity": "Totals", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 27617.29634146023}]
EXPORT_REGION_HISTORY = [{"entity": "Africa", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 57.63128364530923}, {"entity": "Africa", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 70.29405230021077}, {"entity": "Africa", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 111.81988505013503}, {"entity": "Africa", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 90.07239679924204}, {"entity": "Africa", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 110.80791400795759}, {"entity": "Africa", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 141.01572765692197}, {"entity": "Africa", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 64.86300424729103}, {"entity": "Africa", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 100.93459356846067}, {"entity": "Africa", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 155.61275883037067}, {"entity": "Africa", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 176.2299260900265}, {"entity": "Africa", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 162.5387807589219}, {"entity": "Africa", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 190.00642373780582}, {"entity": "Africa", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 445.08503997024076}, {"entity": "Africa", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 181.83488742381746}, {"entity": "Africa", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 93.64787759484132}, {"entity": "Africa", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 177.8099852862633}, {"entity": "Africa", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 135.35130786425617}, {"entity": "Asia", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 8670.365461715577}, {"entity": "Asia", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 11302.994440388957}, {"entity": "Asia", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 13654.430400970738}, {"entity": "Asia", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 12864.309053332438}, {"entity": "Asia", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 13266.63193810707}, {"entity": "Asia", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 14168.125121065335}, {"entity": "Asia", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 12533.882098028093}, {"entity": "Asia", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 14655.685237752086}, {"entity": "Asia", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 15036.306805010527}, {"entity": "Asia", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 13125.351733434687}, {"entity": "Asia", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 11429.696629612541}, {"entity": "Asia", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 9804.056301370227}, {"entity": "Asia", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 12214.00489526315}, {"entity": "Asia", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 12011.145683791112}, {"entity": "Asia", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 8581.325230785826}, {"entity": "Asia", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 6214.141090873982}, {"entity": "Asia", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 7785.678442266425}, {"entity": "CIS Countries", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 9.355471671374728}, {"entity": "CIS Countries", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 16.393712550759748}, {"entity": "CIS Countries", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 21.644017496101814}, {"entity": "CIS Countries", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 21.16010318101649}, {"entity": "CIS Countries", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 18.663622687971174}, {"entity": "CIS Countries", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 13.42757051255896}, {"entity": "CIS Countries", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 5.514267262135819}, {"entity": "CIS Countries", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 7.10061608267679}, {"entity": "CIS Countries", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 7.688113070028248}, {"entity": "CIS Countries", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 11.017263005591653}, {"entity": "CIS Countries", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 15.680986238429726}, {"entity": "CIS Countries", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 14.973822036504622}, {"entity": "CIS Countries", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 33.2599308420397}, {"entity": "CIS Countries", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 24.987292781371835}, {"entity": "CIS Countries", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 42.9081511824436}, {"entity": "CIS Countries", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 31.800357918805872}, {"entity": "CIS Countries", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 33.05781553656879}, {"entity": "East Asia (Oceania)", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 203.40312449060048}, {"entity": "East Asia (Oceania)", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 246.4076450726316}, {"entity": "East Asia (Oceania)", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 259.2351929004853}, {"entity": "East Asia (Oceania)", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 265.79555403302953}, {"entity": "East Asia (Oceania)", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 269.1470363040729}, {"entity": "East Asia (Oceania)", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 248.22422468654315}, {"entity": "East Asia (Oceania)", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 276.6071631559381}, {"entity": "East Asia (Oceania)", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 227.77956190668704}, {"entity": "East Asia (Oceania)", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 238.6498235807642}, {"entity": "East Asia (Oceania)", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 245.778319058356}, {"entity": "East Asia (Oceania)", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 204.64703894001852}, {"entity": "East Asia (Oceania)", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 202.32433231049976}, {"entity": "East Asia (Oceania)", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 271.5202166732221}, {"entity": "East Asia (Oceania)", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 287.6491383593852}, {"entity": "East Asia (Oceania)", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 247.52397564277805}, {"entity": "East Asia (Oceania)", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 275.7409734937751}, {"entity": "East Asia (Oceania)", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 389.7003989292541}, {"entity": "Europe Union 27", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 2472.3684772541865}, {"entity": "Europe Union 27", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 3329.349119745988}, {"entity": "Europe Union 27", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 4412.099350233242}, {"entity": "Europe Union 27", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 3036.924542243826}, {"entity": "Europe Union 27", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 3415.5195069676124}, {"entity": "Europe Union 27", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 3558.9874543209335}, {"entity": "Europe Union 27", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 3182.867057753586}, {"entity": "Europe Union 27", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 3277.8045317209585}, {"entity": "Europe Union 27", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 3483.657877200575}, {"entity": "Europe Union 27", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 3299.674959656865}, {"entity": "Europe Union 27", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 3014.196898036918}, {"entity": "Europe Union 27", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 2022.6238688267367}, {"entity": "Europe Union 27", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 3782.6803414797955}, {"entity": "Europe Union 27", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 3922.634791104674}, {"entity": "Europe Union 27", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 3334.9479682361925}, {"entity": "Europe Union 27", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 3095.658369782266}, {"entity": "Europe Union 27", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 3311.026650711249}, {"entity": "Europe-Others", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 147.94848082927382}, {"entity": "Europe-Others", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 300.1721592977584}, {"entity": "Europe-Others", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 459.5912906167233}, {"entity": "Europe-Others", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 236.17357842141791}, {"entity": "Europe-Others", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 414.8568782462554}, {"entity": "Europe-Others", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 318.5319691335758}, {"entity": "Europe-Others", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 311.26923727688717}, {"entity": "Europe-Others", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 240.4206413724672}, {"entity": "Europe-Others", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 299.5448384433517}, {"entity": "Europe-Others", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 313.71386725507364}, {"entity": "Europe-Others", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 249.8503566140307}, {"entity": "Europe-Others", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 161.98189959166518}, {"entity": "Europe-Others", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 288.9736635080162}, {"entity": "Europe-Others", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 481.2742282788317}, {"entity": "Europe-Others", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 698.7945521876371}, {"entity": "Europe-Others", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 528.6372756513604}, {"entity": "Europe-Others", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 323.2780463424222}, {"entity": "Latin America", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 2.2971681414714373}, {"entity": "Latin America", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 2.6027204270626934}, {"entity": "Latin America", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 7.716609356791577}, {"entity": "Latin America", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 2.1520908456154686}, {"entity": "Latin America", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 3.973148815894854}, {"entity": "Latin America", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 3.0864610326399884}, {"entity": "Latin America", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 5.6646373330362465}, {"entity": "Latin America", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 7.978710751764195}, {"entity": "Latin America", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 4.289054020112578}, {"entity": "Latin America", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 6.619822485735102}, {"entity": "Latin America", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 7.880775402957663}, {"entity": "Latin America", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 1.284353186758202}, {"entity": "Latin America", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 6.644870603019868}, {"entity": "Latin America", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 9.450202177474258}, {"entity": "Latin America", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 6.011499379894387}, {"entity": "Latin America", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 8.809272962026503}, {"entity": "Latin America", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 30.6095056782807}, {"entity": "Middle East", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 13904.234693332368}, {"entity": "Middle East", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 23494.390225479536}, {"entity": "Middle East", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 20776.04609257078}, {"entity": "Middle East", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 20228.723291218168}, {"entity": "Middle East", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 14481.74885057432}, {"entity": "Middle East", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 12899.359061529109}, {"entity": "Middle East", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 13693.426828625232}, {"entity": "Middle East", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 14772.86279394442}, {"entity": "Middle East", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 11601.392028938077}, {"entity": "Middle East", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 11987.029952977799}, {"entity": "Middle East", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 11263.731137305647}, {"entity": "Middle East", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 4338.692398355291}, {"entity": "Middle East", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 7766.409060071194}, {"entity": "Middle East", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 8170.516927275632}, {"entity": "Middle East", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 9296.703961611924}, {"entity": "Middle East", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 8933.755505099472}, {"entity": "Middle East", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 10040.34824577904}, {"entity": "North America", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 5089.656452448025}, {"entity": "North America", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 6733.966619346064}, {"entity": "North America", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 7042.38187657418}, {"entity": "North America", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 6822.864980556509}, {"entity": "North America", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 8143.7636739124055}, {"entity": "North America", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 8628.982807046594}, {"entity": "North America", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 9168.592094247411}, {"entity": "North America", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 9864.02050034495}, {"entity": "North America", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 10135.717495295225}, {"entity": "North America", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 10555.870500839805}, {"entity": "North America", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 9245.01992836766}, {"entity": "North America", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 8768.672142464075}, {"entity": "North America", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 14756.420565522803}, {"entity": "North America", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 12640.884400429397}, {"entity": "North America", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 9967.180961800274}, {"entity": "North America", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 9393.737466404535}, {"entity": "North America", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 5553.563670992296}, {"entity": "Others", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 42.626433178342204}, {"entity": "Others", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 49.86868752106152}, {"entity": "Others", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 44.949321223435696}, {"entity": "Others", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 6.427174421471045}, {"entity": "Others", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 45.608160972229136}, {"entity": "Others", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 0.8470567852457704}, {"entity": "Others", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 3.1556149829302}, {"entity": "Others", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 2.489083321095432}, {"entity": "Others", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 2.090367264160819}, {"entity": "Others", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 1.6349723169873152}, {"entity": "Others", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 1.958309962768762}, {"entity": "Others", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.9555906953592884}, {"entity": "Others", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 4.126142949624973}, {"entity": "Others", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 6.58839308656685}, {"entity": "Others", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 16.74049397060575}, {"entity": "Others", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 10.94491602371262}, {"entity": "Others", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 14.636232498706695}, {"entity": "Not assigned", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 0.011137538932930315}, {"entity": "Not assigned", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 0.09962077867150641}, {"entity": "Not assigned", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 0.08516150744292376}, {"entity": "Not assigned", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 0.061323327253181306}, {"entity": "Not assigned", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 0.025120741503784433}, {"entity": "Not assigned", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 0.046024861734050966}, {"entity": "Totals", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 30599.887046706528}, {"entity": "Totals", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 45546.43938213003}, {"entity": "Totals", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 46789.91403699261}, {"entity": "Totals", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 43574.60276505273}, {"entity": "Totals", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 40170.72073059579}, {"entity": "Totals", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 39980.587453769454}, {"entity": "Totals", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 39245.84200291254}, {"entity": "Totals", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 43157.07627076557}, {"entity": "Totals", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 40964.94916165319}, {"entity": "Totals", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 39722.92131712093}, {"entity": "Totals", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 35595.20084123989}, {"entity": "Totals", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 25505.582270113853}, {"entity": "Totals", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 39569.22434766178}, {"entity": "Totals", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 37737.0511062157}, {"entity": "Totals", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 32285.84599571967}, {"entity": "Totals", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 28671.060334237704}, {"entity": "Totals", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 27617.29634146023}]
EXPORT_PORT_HISTORY = [{"entity": "Ahmedabad", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 128.56767617416236}, {"entity": "Ahmedabad", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 531.8724706415877}, {"entity": "Ahmedabad", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 205.0278993533958}, {"entity": "Ahmedabad", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 164.50761781543844}, {"entity": "Ahmedabad", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 416.7209784379926}, {"entity": "Ahmedabad", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 519.3345757398118}, {"entity": "Ahmedabad", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 295.2781492363731}, {"entity": "Ahmedabad", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 273.6873857752661}, {"entity": "Bangalore", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 500.70851255561934}, {"entity": "Bangalore", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 137.97615375101535}, {"entity": "Bangalore", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 27.378016134929396}, {"entity": "Bangalore", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 5.052645517223394}, {"entity": "Bangalore", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 2608.839759584708}, {"entity": "Bangalore", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 3376.0836324627503}, {"entity": "Bangalore", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 5029.494359705449}, {"entity": "Bangalore", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 5291.58233137299}, {"entity": "Bangalore", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 1515.313042869221}, {"entity": "Bangalore", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 63.09997904103268}, {"entity": "Bangalore", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 51.184855610833466}, {"entity": "Bangalore", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 28.16957084274661}, {"entity": "Bangalore", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 64.89063647581403}, {"entity": "Bangalore", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 168.31102019798197}, {"entity": "Bangalore", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 181.28827253833256}, {"entity": "Bangalore", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 238.27952062326307}, {"entity": "Bangalore", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 265.4932887699076}, {"entity": "Chennai", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 538.0748665268262}, {"entity": "Chennai", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 1052.8696278432333}, {"entity": "Chennai", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 1298.0628119903306}, {"entity": "Chennai", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 1026.4400665422083}, {"entity": "Chennai", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 327.1956910728164}, {"entity": "Chennai", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 340.31796604224405}, {"entity": "Chennai", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 447.56757795505433}, {"entity": "Chennai", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 523.0614213748916}, {"entity": "Chennai", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 550.2720653907761}, {"entity": "Chennai", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 451.54836722691533}, {"entity": "Chennai", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 578.9128128444804}, {"entity": "Chennai", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 541.6236847739289}, {"entity": "Chennai", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 1181.8038815755997}, {"entity": "Chennai", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 994.4559259765015}, {"entity": "Chennai", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 582.1166158683153}, {"entity": "Chennai", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 910.6834618388282}, {"entity": "Chennai", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 794.8029186702095}, {"entity": "Cochin", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 3306.3133878459107}, {"entity": "Cochin", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 3950.845405971075}, {"entity": "Cochin", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 5739.696403542245}, {"entity": "Cochin", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 5819.889380852993}, {"entity": "Cochin", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 694.6302226384574}, {"entity": "Cochin", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 217.0393230632045}, {"entity": "Cochin", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 715.9756227834303}, {"entity": "Cochin", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 1091.4828004112294}, {"entity": "Cochin", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 2986.4654172327596}, {"entity": "Cochin", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 5915.111509616956}, {"entity": "Cochin", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 6254.042418205071}, {"entity": "Cochin", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 282.7883559542801}, {"entity": "Cochin", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 102.58476413836028}, {"entity": "Cochin", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 100.86025065022994}, {"entity": "Cochin", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 164.03227376371515}, {"entity": "Cochin", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 164.5574047799245}, {"entity": "Cochin", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 159.5520206591902}, {"entity": "Coimbatore", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 0.8795349610732337}, {"entity": "Coimbatore", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 1.2155791414705617}, {"entity": "Coimbatore", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 1.5890817093318135}, {"entity": "Coimbatore", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 1.182132906851381}, {"entity": "Coimbatore", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 0.6781806814600355}, {"entity": "Coimbatore", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 72.82410521827529}, {"entity": "Coimbatore", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 69.70313728458756}, {"entity": "Coimbatore", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 16.55606911446339}, {"entity": "Coimbatore", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 1.0745939359668193}, {"entity": "Coimbatore", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 6.40915690151535}, {"entity": "Hyderabad", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 123.91604667075384}, {"entity": "Hyderabad", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 305.90314477772364}, {"entity": "Hyderabad", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 447.0079779141453}, {"entity": "Hyderabad", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 665.3699200898492}, {"entity": "Hyderabad", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 487.68425603837574}, {"entity": "Hyderabad", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 687.1315672498189}, {"entity": "Hyderabad", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 1242.9521735021367}, {"entity": "Hyderabad", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 1824.229756774562}, {"entity": "Hyderabad", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 1551.9944526732384}, {"entity": "Hyderabad", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 141.75822777126888}, {"entity": "Hyderabad", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 108.80873077584629}, {"entity": "Hyderabad", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 66.81714548267217}, {"entity": "Hyderabad", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 196.16298076650884}, {"entity": "Hyderabad", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 164.38266454649948}, {"entity": "Hyderabad", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 184.6318650156295}, {"entity": "Hyderabad", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 231.502179150604}, {"entity": "Hyderabad", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 214.54745241741105}, {"entity": "Jaipur", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 570.5121260655047}, {"entity": "Jaipur", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 647.43351259184}, {"entity": "Jaipur", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 766.7010502432373}, {"entity": "Jaipur", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 717.82464130774}, {"entity": "Jaipur", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 826.9891332454337}, {"entity": "Jaipur", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 846.1545844060664}, {"entity": "Jaipur", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 847.682419985806}, {"entity": "Jaipur", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 848.6354301550431}, {"entity": "Jaipur", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 825.7508323429442}, {"entity": "Jaipur", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 810.9912716441985}, {"entity": "Jaipur", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 729.0904465167307}, {"entity": "Jaipur", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 559.0869342695198}, {"entity": "Jaipur", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 950.8091421429806}, {"entity": "Jaipur", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 1177.4638980905747}, {"entity": "Jaipur", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 1360.801375262038}, {"entity": "Jaipur", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 2104.527938994421}, {"entity": "Jaipur", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 1908.0698073743063}, {"entity": "Kolkata", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 1018.1588731359889}, {"entity": "Kolkata", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 2099.0345770857925}, {"entity": "Kolkata", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 2585.58670579152}, {"entity": "Kolkata", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 2192.6911522788578}, {"entity": "Kolkata", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 2055.703509695289}, {"entity": "Kolkata", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 1162.4662836825707}, {"entity": "Kolkata", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 789.6889378548015}, {"entity": "Kolkata", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 792.540650365859}, {"entity": "Kolkata", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 802.6204511763553}, {"entity": "Kolkata", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 783.7003675287976}, {"entity": "Kolkata", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 571.4072986004041}, {"entity": "Kolkata", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 390.54677398571056}, {"entity": "Kolkata", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 985.8167183736217}, {"entity": "Kolkata", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 1158.269269470753}, {"entity": "Kolkata", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 1262.622539113342}, {"entity": "Kolkata", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 1650.5020787913234}, {"entity": "Kolkata", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 1509.950243672684}, {"entity": "Mumbai", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 17101.335553237444}, {"entity": "Mumbai", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 23789.016974934588}, {"entity": "Mumbai", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 26560.83596314297}, {"entity": "Mumbai", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 22930.949318115432}, {"entity": "Mumbai", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 26352.3838206716}, {"entity": "Mumbai", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 27124.23526350469}, {"entity": "Mumbai", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 25395.320248329623}, {"entity": "Mumbai", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 27516.67502714495}, {"entity": "Mumbai", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 28320.944450933603}, {"entity": "Mumbai", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 28563.324673913576}, {"entity": "Mumbai", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 23194.82231705443}, {"entity": "Mumbai", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 18813.55148506011}, {"entity": "Mumbai", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 30395.836129678362}, {"entity": "Mumbai", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 27974.688983404714}, {"entity": "Mumbai", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 22186.743828211776}, {"entity": "Mumbai", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 19653.23543408089}, {"entity": "Mumbai", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 18579.41402520839}, {"entity": "New Delhi", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 2011.9541007598916}, {"entity": "New Delhi", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 4762.388627646005}, {"entity": "New Delhi", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 3020.6082284648855}, {"entity": "New Delhi", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 1384.490162862771}, {"entity": "New Delhi", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 1779.9118696105804}, {"entity": "New Delhi", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 3347.3062707172894}, {"entity": "New Delhi", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 2046.5594680459972}, {"entity": "New Delhi", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 1996.0559842158327}, {"entity": "New Delhi", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 1933.6675835063897}, {"entity": "New Delhi", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 1937.4732899618402}, {"entity": "New Delhi", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 1714.4675333818018}, {"entity": "New Delhi", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 1021.7686289823909}, {"entity": "New Delhi", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 1300.770841423497}, {"entity": "New Delhi", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 1143.9658797473737}, {"entity": "New Delhi", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 3116.5388537612453}, {"entity": "New Delhi", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 1675.8034294066747}, {"entity": "New Delhi", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 1781.5794066847893}, {"entity": "SDB", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 42.22796942440087}, {"entity": "SDB", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 126.33629088715561}, {"entity": "Surat", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 5397.793240241442}, {"entity": "Surat", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 8728.86784897652}, {"entity": "Surat", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 6164.869212530488}, {"entity": "Surat", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 8697.681474748071}, {"entity": "Surat", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 4894.64822867425}, {"entity": "Surat", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 2707.196597331862}, {"entity": "Surat", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 2655.9716847167883}, {"entity": "Surat", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 3251.662063865975}, {"entity": "Surat", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 2470.6919797851374}, {"entity": "Surat", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 915.2930251417303}, {"entity": "Surat", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 1846.016475154839}, {"entity": "Surat", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 3576.2125860547544}, {"entity": "Surat", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 4214.3281989542875}, {"entity": "Surat", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 4421.600267840454}, {"entity": "Surat", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 2715.2912219832897}, {"entity": "Surat", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 1642.388280378205}, {"entity": "Surat", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 2000.5858577047359}, {"entity": "Visakhapatnam", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 30.240804706074062}, {"entity": "Visakhapatnam", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 70.8879294107647}, {"entity": "Visakhapatnam", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 177.5785855285285}, {"entity": "Visakhapatnam", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 133.03186983073311}, {"entity": "Visakhapatnam", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 142.05605868281836}, {"entity": "Visakhapatnam", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 99.83186009068585}, {"entity": "Visakhapatnam", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 4.926372748866455}, {"entity": "Visakhapatnam", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 4.594735969772399}, {"entity": "Visakhapatnam", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 6.154291806798473}, {"entity": "Visakhapatnam", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 5.643772198934176}, {"entity": "Visakhapatnam", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 14.575482453866284}, {"entity": "Visakhapatnam", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 19.98920535434259}, {"entity": "Visakhapatnam", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 11.713436317306664}, {"entity": "Visakhapatnam", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 16.331967852629706}, {"entity": "Visakhapatnam", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 12.44457446217063}, {"entity": "Visakhapatnam", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 62.07448753279526}, {"entity": "Visakhapatnam", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 3.2776436361877312}, {"entity": "Totals", "fy_start": 2009, "fy_label": "FY2010-11", "value_mn": 30599.887046706528}, {"entity": "Totals", "fy_start": 2010, "fy_label": "FY2011-12", "value_mn": 45546.43938213003}, {"entity": "Totals", "fy_start": 2011, "fy_label": "FY2012-13", "value_mn": 46789.91403699261}, {"entity": "Totals", "fy_start": 2012, "fy_label": "FY2013-14", "value_mn": 43574.60276505273}, {"entity": "Totals", "fy_start": 2013, "fy_label": "FY2014-15", "value_mn": 40170.72073059579}, {"entity": "Totals", "fy_start": 2014, "fy_label": "FY2015-16", "value_mn": 39980.587453769454}, {"entity": "Totals", "fy_start": 2015, "fy_label": "FY2016-17", "value_mn": 39245.84200291254}, {"entity": "Totals", "fy_start": 2016, "fy_label": "FY2017-18", "value_mn": 43157.07627076557}, {"entity": "Totals", "fy_start": 2017, "fy_label": "FY2018-19", "value_mn": 40964.94916165319}, {"entity": "Totals", "fy_start": 2018, "fy_label": "FY2019-20", "value_mn": 39722.92131712093}, {"entity": "Totals", "fy_start": 2019, "fy_label": "FY2020-21", "value_mn": 35595.20084123989}, {"entity": "Totals", "fy_start": 2020, "fy_label": "FY2021-22", "value_mn": 25505.582270113853}, {"entity": "Totals", "fy_start": 2021, "fy_label": "FY2022-23", "value_mn": 39569.22434766178}, {"entity": "Totals", "fy_start": 2022, "fy_label": "FY2023-24", "value_mn": 37737.0511062157}, {"entity": "Totals", "fy_start": 2023, "fy_label": "FY2024-25", "value_mn": 32285.84599571967}, {"entity": "Totals", "fy_start": 2024, "fy_label": "FY2025-26", "value_mn": 28671.060334237704}, {"entity": "Totals", "fy_start": 2025, "fy_label": "FY2026-27", "value_mn": 27617.29634146023}]

DATA["export_country_history"] = EXPORT_COUNTRY_HISTORY
DATA["export_region_history"] = EXPORT_REGION_HISTORY
DATA["export_port_history"] = EXPORT_PORT_HISTORY

def df_from(key: str) -> pd.DataFrame:
    return pd.DataFrame(DATA[key])

def hero(title: str, subtitle: str, chips: list[str]) -> None:
    chips_html = "".join([f"<span class='hero-chip'>{c}</span>" for c in chips])
    st.markdown(
        f"""
        <div class="hero">
          <h1>{title}</h1>
          <p>{subtitle}</p>
          <div class="hero-meta">{chips_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def kpi(label: str, value: str, sub: str = "") -> None:
    st.markdown(
        f"""
        <div class="kpi">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def fmt_num(x: Optional[float], decimals: int = 2) -> str:
    if x is None or pd.isna(x):
        return "—"
    return f"{float(x):,.{decimals}f}"

def fmt_pct(x: Optional[float], decimals: int = 2, signed: bool = True) -> str:
    if x is None or pd.isna(x):
        return "—"
    return f"{float(x):+.{decimals}f}%" if signed else f"{float(x):.{decimals}f}%"

def short(x: str, n: int = 36) -> str:
    x = str(x)
    return x if len(x) <= n else x[:n-1] + "…"

def add_line_labels(fig, fmt: str = "{:,.2f}"):
    for tr in getattr(fig, "data", []):
        ys = getattr(tr, "y", None)
        if ys is None:
            continue
        try:
            vals = list(ys)
        except Exception:
            vals = [ys]
        txt = []
        for v in vals:
            if v is None or (isinstance(v, float) and np.isnan(v)):
                txt.append("")
            else:
                try:
                    txt.append(fmt.format(float(v)))
                except Exception:
                    txt.append(str(v))
        tr.text = txt
        tr.textposition = "top center"
        mode = getattr(tr, "mode", "") or ""
        if "text" not in mode:
            tr.mode = mode + "+text" if mode else "lines+text"

def add_bar_labels(fig, orientation: str = "h", fmt: str = "{:,.2f}"):
    for tr in getattr(fig, "data", []):
        arr = getattr(tr, "x", None) if orientation == "h" else getattr(tr, "y", None)
        if arr is None:
            continue
        try:
            vals = list(arr)
        except Exception:
            vals = [arr]
        txt = []
        for v in vals:
            if v is None or (isinstance(v, float) and np.isnan(v)):
                txt.append("")
            else:
                try:
                    txt.append(fmt.format(float(v)))
                except Exception:
                    txt.append(str(v))
        tr.text = txt
        tr.textposition = "outside"
        tr.cliponaxis = False

def _trace_has_labels(tr) -> bool:
    txt = getattr(tr, "text", None)
    if txt is None:
        return False
    try:
        vals = list(txt)
    except Exception:
        vals = [txt]
    return any(str(v).strip() not in ("", "None", "nan") for v in vals if v is not None)


def auto_apply_data_labels(fig):
    for tr in getattr(fig, "data", []):
        ttype = getattr(tr, "type", "") or ""
        if ttype == "bar":
            if not _trace_has_labels(tr):
                orientation = getattr(tr, "orientation", "v") or "v"
                arr = getattr(tr, "x", None) if orientation == "h" else getattr(tr, "y", None)
                if arr is not None:
                    try:
                        vals = list(arr)
                    except Exception:
                        vals = [arr]
                    labels = []
                    for v in vals:
                        if v is None or pd.isna(v):
                            labels.append("")
                        else:
                            try:
                                labels.append(f"{float(v):,.2f}")
                            except Exception:
                                labels.append(str(v))
                    tr.text = labels
            tr.textposition = "outside"
            tr.cliponaxis = False
        elif ttype == "scatter":
            if not _trace_has_labels(tr):
                ys = getattr(tr, "y", None)
                if ys is not None:
                    try:
                        vals = list(ys)
                    except Exception:
                        vals = [ys]
                    labels = []
                    for v in vals:
                        if v is None or pd.isna(v):
                            labels.append("")
                        else:
                            try:
                                labels.append(f"{float(v):,.2f}")
                            except Exception:
                                labels.append(str(v))
                    tr.text = labels
            tr.textposition = getattr(tr, "textposition", None) or "top center"
            mode = getattr(tr, "mode", "") or ""
            if "text" not in mode:
                tr.mode = mode + "+text" if mode else "lines+text"
        elif ttype == "pie":
            tr.textinfo = "label+percent"
            tr.textposition = "inside"


def render_table(df: pd.DataFrame, formatters: dict[str, object] | None = None, height: int = 420):
    show = df.copy()
    if formatters:
        styler = show.style.format(formatters)
        try:
            st.dataframe(styler, use_container_width=True, height=height, hide_index=True)
            return
        except Exception:
            pass
    st.dataframe(show, use_container_width=True, height=height, hide_index=True)



def resolve_local_file(filename: str) -> Path:
    candidates = [
        Path(filename),
        Path.cwd() / filename,
        Path("/mnt/data") / filename,
        Path("/content") / filename,
    ]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]

def fy_label_generic(y: int) -> str:
    return f"FY{int(y)}-{str(int(y)+1)[-2:]}"

def span_from_single_year_label(value: str) -> str:
    s = str(value).strip()
    m = re.match(r"^FY\s*(\d{4})([^\d]*)$", s)
    if m:
        yr = int(m.group(1))
        suffix = m.group(2) or ""
        return f"FY{yr}-{str(yr+1)[-2:]}{suffix}"
    return s

def shift_range_label(value: str) -> str:
    s = str(value).strip()
    m = re.match(r"^(\d{4})-(\d{2})(.*)$", s)
    if m:
        start = int(m.group(1))
        suffix = m.group(3) or ""
        return f"{start+1}-{str(start+2)[-2:]}{suffix}"
    return s

def annual_report_range_label(value: str) -> str:
    s = str(value).strip()
    m = re.match(r"^(\d{4})-(\d{2})(.*)$", s)
    if m:
        start = int(m.group(1))
        suffix = m.group(3) or ""
        return f"{start-1}-{str(start)[-2:]}{suffix}"
    return s

@st.cache_data(show_spinner=False)
def load_product_workbook(filename: str) -> dict[str, pd.DataFrame]:
    path = resolve_local_file(filename)
    if not path.exists():
        return {}
    xl = pd.ExcelFile(path)
    out: dict[str, pd.DataFrame] = {}
    for sheet in xl.sheet_names:
        raw = pd.read_excel(path, sheet_name=sheet, header=None)
        if raw.shape[0] < 5 or raw.shape[1] < 2:
            continue
        year_cells = [str(x).strip() for x in raw.iloc[2, 1:].tolist()]
        year_cols = []
        for cell in year_cells:
            m = re.search(r"(\d{4})$", cell)
            year_cols.append(int(m.group(1)) if m else None)
        value_cols = [y for y in year_cols if y is not None]
        if not value_cols:
            continue
        df = raw.iloc[4:].copy()
        df.columns = ["country"] + year_cols
        df["country"] = df["country"].astype(str).str.strip()
        df = df[df["country"].ne("")].copy()
        for y in value_cols:
            df[y] = pd.to_numeric(df[y], errors="coerce").fillna(0.0)
        total_like = {"total", "totals", "sub total", "sub-total", "sub  total", "grand total", "gross exports", "gross imports"}
        df = df[~df["country"].str.strip().str.lower().isin(total_like)].copy()
        df = df[(df[value_cols].sum(axis=1) > 0)].copy()
        out[sheet] = df[["country"] + value_cols].reset_index(drop=True)
    return out


@st.cache_data(show_spinner=False)
def load_entity_year_wide_workbook(filename: str, sheet_name: str, entity_col: str) -> pd.DataFrame:
    path = resolve_local_file(filename)
    if not path.exists():
        return pd.DataFrame()
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None)
    if raw.shape[0] < 4 or raw.shape[1] < 2:
        return pd.DataFrame()

    year_pairs = []
    for col_idx, cell in enumerate(raw.iloc[1, 1:].tolist(), start=1):
        m = re.search(r"(\d{4})$", str(cell).strip())
        if m:
            year_pairs.append((col_idx, int(m.group(1))))
    if not year_pairs:
        return pd.DataFrame()

    use_cols = [0] + [idx for idx, _ in year_pairs]
    years = [yr for _, yr in year_pairs]
    df = raw.iloc[3:, use_cols].copy()
    df.columns = [entity_col] + years
    df[entity_col] = df[entity_col].astype(str).str.strip()
    df = df[df[entity_col].ne("")].copy()

    for yr in years:
        df[yr] = pd.to_numeric(df[yr], errors="coerce").fillna(0.0)

    total_like = {"total", "totals", "sub total", "sub-total", "sub  total", "grand total", "gross exports", "gross imports"}
    df = df[~df[entity_col].str.strip().str.lower().isin(total_like)].copy()
    df = df[(df[years].sum(axis=1) > 0)].copy()
    return df[[entity_col] + years].reset_index(drop=True)

def compare_country_product(df: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
    work = df.copy()
    if start_year not in work.columns:
        work[start_year] = 0.0
    if end_year not in work.columns:
        work[end_year] = 0.0
    out = work[["country", start_year, end_year]].copy()
    out.columns = ["Country", "Start Value", "End Value"]
    out["Start Value"] = pd.to_numeric(out["Start Value"], errors="coerce").fillna(0.0)
    out["End Value"] = pd.to_numeric(out["End Value"], errors="coerce").fillna(0.0)
    out = out[(out["Start Value"] > 0) | (out["End Value"] > 0)].copy()
    out["Change (US$ mn)"] = out["End Value"] - out["Start Value"]
    out["Growth (%)"] = np.where(out["Start Value"] != 0, ((out["End Value"] / out["Start Value"]) - 1) * 100, np.nan)
    start_total = out["Start Value"].sum()
    end_total = out["End Value"].sum()
    out["Start Share (%)"] = np.where(start_total != 0, (out["Start Value"] / start_total) * 100, np.nan)
    out["End Share (%)"] = np.where(end_total != 0, (out["End Value"] / end_total) * 100, np.nan)
    out = out.sort_values("End Value", ascending=False).reset_index(drop=True)
    return out

def pie_with_others(df: pd.DataFrame, value_col: str, label_col: str = "Country", top_n: int = 10) -> pd.DataFrame:
    work = df[[label_col, value_col]].copy()
    work = work[work[value_col] > 0].sort_values(value_col, ascending=False)
    if work.empty:
        return pd.DataFrame({label_col: [], value_col: []})
    if len(work) <= top_n:
        return work
    top = work.head(top_n).copy()
    others_val = work.iloc[top_n:][value_col].sum()
    if others_val > 0:
        top = pd.concat([top, pd.DataFrame([{label_col: "Others", value_col: others_val}])], ignore_index=True)
    return top

EXPORT_PRODUCT_LABELS = {
    "CPD": "Cut & Polished Diamonds",
    "Gold Jewellery": "Gold Jewellery",
    "Silver Jewellery": "Silver Jewellery",
    "Plain Gold Jewellery": "Plain Gold Jewellery",
    "Studded Gold Jewellery": "Studded Gold Jewellery",
    "Coloured Gemstones Worked": "Coloured Gemstones Worked",
    "Synthetic Stones Worked": "Synthetic Stones Worked",
    "Pearls Worked": "Pearls Worked",
    "Platinum Jewellery": "Platinum Jewellery",
    "IMITATION JEWELLERY": "Imitation Jewellery",
}
IMPORT_PRODUCT_LABELS = {
    "Rough LGD": "Rough Lab Grown Diamonds",
    "Rough Diamonds": "Rough Diamonds",
    "Gold Bar": "Gold Bar",
    "Silver Bar": "Silver Bar",
    "Rough Coloured Gemstones": "Rough Coloured Gemstones",
}



@st.cache_data(show_spinner=False)
def load_export_basket_history() -> pd.DataFrame:
    """
    Reconstruct the multi-year 3.6 basket table from the EXPORT PRODUCTS workbook.
    This keeps the annual-report basket-change logic (value + share versus total)
    but extends it across all years that are continuously available in the product workbook.
    """
    books = load_product_workbook("EXPORT PRODUCTS.xlsx")
    if not books:
        return pd.DataFrame()

    category_map = {
        "CPD": "Cut & Pol Diamonds",
        "Gold Jewellery": "Gold Jewellery",
        "Silver Jewellery": "Silver Jewellery",
        "Coloured Gemstones Worked": "Coloured Gemstones",
        "Synthetic Stones Worked": "Polished Synthetic Stones",
        "Pearls Worked": "Pearls - Worked",
        "Platinum Jewellery": "Platinum Jewellery",
        "IMITATION JEWELLERY": "Imitation Jewellery",
    }

    available_years = sorted(
        {
            int(col)
            for sheet_name, df in books.items()
            if sheet_name in category_map
            for col in df.columns
            if isinstance(col, int)
        }
    )
    if not available_years:
        return pd.DataFrame()

    rows = []
    for year in available_years:
        year_values = {}
        for sheet_name, label in category_map.items():
            if sheet_name not in books:
                continue
            df = books[sheet_name]
            value = float(pd.to_numeric(df.get(year, 0.0), errors="coerce").fillna(0.0).sum())
            year_values[label] = value

        gross_total = float(sum(year_values.values()))
        if gross_total <= 0:
            continue

        for label, value in year_values.items():
            rows.append(
                {
                    "fy_start": int(year),
                    "commodity": label,
                    "value_mn": float(value),
                    "share_pct": float((value / gross_total) * 100) if gross_total else np.nan,
                }
            )

        rows.append(
            {
                "fy_start": int(year),
                "commodity": "Gross Exports",
                "value_mn": gross_total,
                "share_pct": 100.0,
            }
        )

    out = pd.DataFrame(rows)
    order = [
        "Cut & Pol Diamonds",
        "Gold Jewellery",
        "Silver Jewellery",
        "Coloured Gemstones",
        "Polished Synthetic Stones",
        "Pearls - Worked",
        "Platinum Jewellery",
        "Imitation Jewellery",
        "Gross Exports",
    ]
    out["sort_order"] = out["commodity"].map({name: i for i, name in enumerate(order)}).fillna(999)
    out = out.sort_values(["fy_start", "sort_order", "commodity"]).drop(columns="sort_order").reset_index(drop=True)
    return out

def render_product_country_tab(tab_title: str, df: pd.DataFrame, kind: str, key_prefix: str):
    years = sorted([c for c in df.columns if isinstance(c, int)])
    if not years:
        st.info("No year columns available for this product.")
        return
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        start_year = st.selectbox("Start year", years, index=0, format_func=fy_label_generic, key=f"{key_prefix}_start")
    with c2:
        end_options = [y for y in years if y >= start_year]
        end_year = st.selectbox("End year", end_options, index=len(end_options) - 1, format_func=fy_label_generic, key=f"{key_prefix}_end")
    with c3:
        max_n = max(5, min(25, len(df)))
        top_n = st.slider("Top N countries", 5, max_n, min(10, max_n), key=f"{key_prefix}_topn")

    comp = compare_country_product(df, start_year, end_year)
    if comp.empty:
        st.info("No country-wise values available for the selected years.")
        return

    start_label = fy_label_generic(start_year)
    end_label = fy_label_generic(end_year)
    total_start = comp["Start Value"].sum()
    total_end = comp["End Value"].sum()
    overall_growth = ((total_end / total_start) - 1) * 100 if total_start else np.nan
    top_country = comp.iloc[0]["Country"] if not comp.empty else "—"

    r = st.columns(4)
    with r[0]:
        kpi(f"{start_label} Total", f"{fmt_num(total_start)} US$ mn", tab_title)
    with r[1]:
        kpi(f"{end_label} Total", f"{fmt_num(total_end)} US$ mn", tab_title)
    with r[2]:
        kpi("Overall Growth", fmt_pct(overall_growth), f"{start_label} to {end_label}")
    with r[3]:
        kpi("Top Country", short(top_country, 24), f"{end_label} ranking")

    top_df = comp.head(top_n).copy()
    top_df = top_df.rename(columns={
        "Start Value": f"{start_label} (US$ mn)",
        "End Value": f"{end_label} (US$ mn)",
        "Start Share (%)": f"{start_label} Share (%)",
        "End Share (%)": f"{end_label} Share (%)",
    })

    render_table(
        top_df[["Country", f"{start_label} (US$ mn)", f"{end_label} (US$ mn)", "Change (US$ mn)", "Growth (%)", f"{start_label} Share (%)", f"{end_label} Share (%)"]],
        {
            f"{start_label} (US$ mn)": "{:,.2f}",
            f"{end_label} (US$ mn)": "{:,.2f}",
            "Change (US$ mn)": "{:+,.2f}",
            "Growth (%)": "{:+,.2f}",
            f"{start_label} Share (%)": "{:,.2f}",
            f"{end_label} Share (%)": "{:,.2f}",
        },
        height=420,
    )

    c4, c5 = st.columns(2)
    with c4:
        plot_bar = top_df.sort_values(f"{end_label} (US$ mn)")
        fig = go.Figure()
        fig.add_trace(go.Bar(y=plot_bar["Country"], x=plot_bar[f"{start_label} (US$ mn)"], orientation="h", name=start_label, marker_color="#d9ead3"))
        fig.add_trace(go.Bar(y=plot_bar["Country"], x=plot_bar[f"{end_label} (US$ mn)"], orientation="h", name=end_label, marker_color="#274e3d" if kind == "Export" else "#b88746"))
        fig.update_layout(
            barmode="group",
            template="plotly_white",
            height=420,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="US$ mn",
            yaxis_title="",
            legend_title_text="",
        )
        st.plotly_chart(fig, use_container_width=True)
    with c5:
        fig2 = px.bar(
            top_df.sort_values("Growth (%)"),
            x="Growth (%)",
            y="Country",
            orientation="h",
            color="Growth (%)",
            color_continuous_scale="RdYlGn",
        )
        fig2.update_layout(
            template="plotly_white",
            height=420,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Growth (%)",
            yaxis_title="",
            coloraxis_showscale=False,
        )
        if show_labels:
            add_bar_labels(fig2, "h", "{:+,.2f}")
        st.plotly_chart(fig2, use_container_width=True)

    c6, c7 = st.columns(2)
    with c6:
        pie_start = pie_with_others(comp, "Start Value", top_n=top_n)
        if not pie_start.empty:
            fig3 = px.pie(pie_start, names="Country", values="Start Value", hole=0.35, title=f"{start_label} country share")
            fig3.update_layout(template="plotly_white", height=420, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig3, use_container_width=True)
    with c7:
        pie_end = pie_with_others(comp, "End Value", top_n=top_n)
        if not pie_end.empty:
            fig4 = px.pie(pie_end, names="Country", values="End Value", hole=0.35, title=f"{end_label} country share")
            fig4.update_layout(template="plotly_white", height=420, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig4, use_container_width=True)

def render_product_workbook_page(kind: str):
    filename = "EXPORT PRODUCTS.xlsx" if kind == "Export" else "Import Products.xlsx"
    books = load_product_workbook(filename)
    label_map = EXPORT_PRODUCT_LABELS if kind == "Export" else IMPORT_PRODUCT_LABELS

    hero(
        f"{kind} Products",
        f"Country-wise {kind.lower()} product analysis using the dedicated product workbook. Each product gets its own tab with start-year, end-year, top-N country filters, detailed tables, and pie charts similar to the annual report style.",
        [
            f"{kind} products",
            "Country-wise tabs",
            "Start vs end year logic",
            "Pie charts included",
        ],
    )

    if not books:
        st.error(f"{filename} was not found next to the app, so the product tabs cannot be rendered.")
        return

    ordered_sheets = [s for s in label_map.keys() if s in books] + [s for s in books.keys() if s not in label_map]
    tabs = st.tabs([label_map.get(s, s) for s in ordered_sheets])
    for tab, sheet in zip(tabs, ordered_sheets):
        with tab:
            st.markdown(f"<div class='report-band'>{label_map.get(sheet, sheet)} — Country-wise {kind.lower()} analysis</div>", unsafe_allow_html=True)
            render_product_country_tab(label_map.get(sheet, sheet), books[sheet], kind, f"{kind.lower()}_{sheet.replace(' ', '_').replace('&', 'and')}")
            st.caption("Top-N is applied to the detailed table and charts. Pie charts group the remaining countries into Others.")

show_labels = st.sidebar.checkbox("Show data labels", value=True)
if not hasattr(st, "_orig_plotly_chart"):
    st._orig_plotly_chart = st.plotly_chart


def _plotly_chart_with_auto_labels(fig, *args, **kwargs):
    if show_labels and fig is not None:
        try:
            auto_apply_data_labels(fig)
        except Exception:
            pass
    return st._orig_plotly_chart(fig, *args, **kwargs)


st.plotly_chart = _plotly_chart_with_auto_labels
page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "3.1 Annual Trends",
        "3.2 Gross vs Net Exports",
        "3.3–3.4 Targets & Achievement",
        "3.5–3.9 Export Structure",
        "3.10–3.13 Import Structure",
        "Export Products",
        "Import Products",
        "3.14 DTA / SEZ",
        "3.15 FDI Inflows",
    ],
    index=0,
)

st.sidebar.markdown(
    "<div class='note'>This version is standalone for the embedded annual-report sections. Product pages read the bundled Export Products and Import Products workbooks if they are placed next to the app.</div>",
    unsafe_allow_html=True,
)

annual_df = df_from("annual_trends").copy()
annual_df["year_display"] = annual_df["year"].astype(str).map(annual_report_range_label)
latest = annual_df.iloc[-1]
prev = annual_df.iloc[-2]

def overview():
    hero(
        "Annual Report Dashboard",
        "Standalone report-style dashboard built from the annual report section logic from sheet 3.1 onward. Tables and charts are organized as report sections, without requiring the Excel workbook at runtime.",
        [
            "Standalone version",
            "Annual Report template logic",
            "Section-wise navigation",
            "No workbook upload needed",
        ],
    )

    r1 = st.columns(4)
    with r1[0]:
        kpi("Latest Exports", f"{fmt_num(latest['exports_bn'])} US$ bn", f"{latest['year_display']} • YoY {fmt_pct(latest['export_growth_pct'])}")
    with r1[1]:
        kpi("Latest Imports", f"{fmt_num(latest['imports_bn'])} US$ bn", f"{latest['year_display']} • YoY {fmt_pct(latest['import_growth_pct'])}")
    with r1[2]:
        kpi("Balance of Trade", f"{fmt_num(latest['bot_bn'])} US$ bn", f"{latest['year_display']}")
    with r1[3]:
        achieved = DATA["overall_target"]["achieved_pct"]
        kpi("Target Achievement", f"{fmt_num(achieved)}%", "FY2025-26 overall export target")

    st.markdown("<div class='report-band'>Section 3.1 — India’s Annual Trends of Gem & Jewellery Products</div>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=annual_df["year_display"], y=annual_df["exports_bn"], mode="lines+markers", name="Exports", line=dict(color="#274e3d", width=3)))
    fig.add_trace(go.Scatter(x=annual_df["year_display"], y=annual_df["imports_bn"], mode="lines+markers", name="Imports", line=dict(color="#7a1f5c", width=3)))
    fig.add_trace(go.Scatter(x=annual_df["year_display"], y=annual_df["bot_bn"], mode="lines+markers", name="BoT", line=dict(color="#b88746", width=2, dash="dot")))
    fig.update_layout(template="plotly_white", height=420, margin=dict(l=10,r=10,t=10,b=10), xaxis_title="", yaxis_title="US$ bn")
    if show_labels:
        add_line_labels(fig, "{:,.2f}")
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='report-band'>Section 3.4 — Region-wise Target Achievement</div>", unsafe_allow_html=True)
        region_df = df_from("region_targets")
        plot_df = region_df[region_df["region"].str.upper() != "TOTAL"].nlargest(8, "actual_mn").sort_values("actual_mn")
        fig2 = px.bar(plot_df, x="actual_mn", y="region", orientation="h")
        fig2.update_traces(marker_color="#5a7d4d")
        fig2.update_layout(template="plotly_white", height=400, margin=dict(l=10,r=10,t=10,b=10), xaxis_title="Actual exports (US$ mn)", yaxis_title="")
        if show_labels:
            add_bar_labels(fig2, "h", "{:,.0f}")
        st.plotly_chart(fig2, use_container_width=True)
    with c2:
        st.markdown("<div class='report-band'>Section 3.5 — Key Export Commodities</div>", unsafe_allow_html=True)
        exp_commod = df_from("export_key_commodities")
        plot_df = exp_commod[~exp_commod["commodity"].isin(["Gross Exports","Net Exports","Return Consignment Others","Return Consignment CPD","Sub - Total"])].nlargest(8, "fy2025_mn").sort_values("fy2025_mn")
        fig3 = px.bar(plot_df, x="fy2025_mn", y="commodity", orientation="h")
        fig3.update_traces(marker_color="#7a1f5c")
        fig3.update_layout(template="plotly_white", height=400, margin=dict(l=10,r=10,t=10,b=10), xaxis_title="FY2025-26 (US$ mn)", yaxis_title="")
        if show_labels:
            add_bar_labels(fig3, "h", "{:,.0f}")
        st.plotly_chart(fig3, use_container_width=True)

def section_31():
    df = df_from("annual_trends").copy()
    df["year_display"] = df["year"].astype(str).map(annual_report_range_label)
    years = df["year_display"].tolist()
    c1, c2 = st.columns(2)
    with c1:
        start_year = st.selectbox("Start year", years, index=0)
    with c2:
        start_idx = years.index(start_year)
        end_year = st.selectbox("End year", years[start_idx:], index=len(years[start_idx:])-1)
    end_idx = years.index(end_year)
    view = df.iloc[start_idx:end_idx+1].copy()

    hero(
        "3.1 Annual Trends",
        "Report-style annual trends table with exports, imports, growth and balance of trade.",
        [f"Start: {start_year}", f"End: {end_year}", "Values in US$ bn", "Growth computed YoY"],
    )

    table = view.rename(columns={
        "year_display":"Year",
        "exports_bn":"Exports (US$ bn)",
        "export_growth_pct":"% Exports Growth",
        "imports_bn":"Imports (US$ bn)",
        "import_growth_pct":"% Import Growth",
        "bot_bn":"BoT (US$ bn)",
    })
    table = table[["Year", "Exports (US$ bn)", "Imports (US$ bn)", "BoT (US$ bn)", "% Exports Growth", "% Import Growth"]]
    render_table(table, {
        "Exports (US$ bn)":"{:,.2f}",
        "% Exports Growth":"{:+,.2f}",
        "Imports (US$ bn)":"{:,.2f}",
        "% Import Growth":"{:+,.2f}",
        "BoT (US$ bn)":"{:,.2f}",
    }, height=420)

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=view["year_display"], y=view["exports_bn"], mode="lines+markers", name="Exports", line=dict(color="#274e3d", width=3)))
        fig.add_trace(go.Scatter(x=view["year_display"], y=view["imports_bn"], mode="lines+markers", name="Imports", line=dict(color="#7a1f5c", width=3)))
        fig.update_layout(template="plotly_white", height=360, margin=dict(l=10,r=10,t=10,b=10), xaxis_title="", yaxis_title="US$ bn", legend_title_text="")
        if show_labels:
            add_line_labels(fig, "{:,.2f}")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        growth = view.copy()
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=growth["year_display"], y=growth["export_growth_pct"], mode="lines+markers", name="Export growth", line=dict(color="#274e3d", width=3)))
        fig2.add_trace(go.Scatter(x=growth["year_display"], y=growth["import_growth_pct"], mode="lines+markers", name="Import growth", line=dict(color="#b88746", width=3)))
        fig2.add_hline(y=0, line_dash="dot", line_color="gray")
        fig2.update_layout(template="plotly_white", height=360, margin=dict(l=10,r=10,t=10,b=10), xaxis_title="", yaxis_title="YoY growth (%)", legend_title_text="")
        if show_labels:
            add_line_labels(fig2, "{:,.2f}")
        st.plotly_chart(fig2, use_container_width=True)


def section_32():
    gross_net = df_from("gross_net_exports").copy()
    monthly = df_from("monthly_exports").copy()

    gross_net["metric"] = gross_net["metric"].replace({"Return Consignment": "Re-imports"})
    if "fy2026p_mn" in gross_net.columns and "fy2026_mn" not in gross_net.columns:
        gross_net["fy2026_mn"] = gross_net["fy2026p_mn"]
    for col in ["fy2024_mn", "fy2025_mn", "fy2026_mn", "growth_fy25_vs_fy24_pct"]:
        if col in gross_net.columns:
            gross_net[col] = pd.to_numeric(gross_net[col], errors="coerce")

    hero(
        "3.2 Gross vs Net Exports",
        "Overall gross exports, re-imports (return consignments) and net exports, followed by the monthly gross exports view used in the report.",
        ["Table 7", "Table 8", "Values in US$ mn", "Monthly export trend"],
    )
    t1, t2 = st.tabs(["Gross vs Net", "Monthly Gross Exports"])

    with t1:
        table = gross_net.rename(columns={
            "metric": "Exports Performance",
            "fy2024_mn": "FY2023-24 (US$ mn)",
            "fy2025_mn": "FY2024-25 (US$ mn)",
            "fy2026_mn": "FY2025-26 (US$ mn)",
            "growth_fy25_vs_fy24_pct": "% Growth FY2024-25 vs FY2023-24",
        })
        table = table[[
            "Exports Performance",
            "FY2023-24 (US$ mn)",
            "FY2024-25 (US$ mn)",
            "FY2025-26 (US$ mn)",
            "% Growth FY2024-25 vs FY2023-24",
        ]].copy()
        render_table(
            table,
            {
                "FY2023-24 (US$ mn)": "{:,.2f}",
                "FY2024-25 (US$ mn)": "{:,.2f}",
                "FY2025-26 (US$ mn)": "{:,.2f}",
                "% Growth FY2024-25 vs FY2023-24": "{:+,.2f}",
            },
            height=250,
        )
        st.caption("Re-imports are shown in place of return consignments. FY2025-26 re-import and net-export values are left blank where the standalone source does not provide a matched figure.")

        plot_df = gross_net.copy()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=plot_df["metric"], y=plot_df["fy2024_mn"], name="FY2023-24", marker_color="#8fb996"))
        fig.add_trace(go.Bar(x=plot_df["metric"], y=plot_df["fy2025_mn"], name="FY2024-25", marker_color="#7a1f5c"))
        if "fy2026_mn" in plot_df.columns:
            fig.add_trace(go.Bar(x=plot_df["metric"], y=plot_df["fy2026_mn"], name="FY2025-26", marker_color="#274e3d"))
        fig.update_layout(
            barmode="group",
            template="plotly_white",
            height=360,
            margin=dict(l=10, r=10, t=10, b=10),
            yaxis_title="US$ mn",
            legend_title_text="",
        )
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        monthly_tbl = monthly.rename(columns={
            "month": "Months",
            "fy2025_mn": "FY2024-25 (US$ mn)",
            "fy2026_mn": "FY2025-26 (US$ mn)",
            "growth_pct": "% Export Growth (Y-o-Y)",
        })
        render_table(
            monthly_tbl,
            {
                "FY2024-25 (US$ mn)": "{:,.2f}",
                "FY2025-26 (US$ mn)": "{:,.2f}",
                "% Export Growth (Y-o-Y)": "{:+,.2f}",
            },
            height=420,
        )
        monthly_plot = monthly[~monthly["month"].astype(str).str.contains("Total", case=False, na=False)].copy()
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=monthly_plot["month"], y=monthly_plot["fy2025_mn"], name="FY2024-25", marker_color="#8fb996"))
            fig.add_trace(go.Bar(x=monthly_plot["month"], y=monthly_plot["fy2026_mn"], name="FY2025-26", marker_color="#274e3d"))
            fig.update_layout(
                barmode="group",
                template="plotly_white",
                height=370,
                margin=dict(l=10, r=10, t=10, b=10),
                yaxis_title="US$ mn",
                xaxis_title="",
                legend_title_text="",
            )
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.line(monthly_plot, x="month", y="growth_pct", markers=True)
            fig2.update_traces(line=dict(color="#7a1f5c", width=3))
            fig2.add_hline(y=0, line_dash="dot", line_color="gray")
            fig2.update_layout(template="plotly_white", height=370, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="YoY growth (%)", xaxis_title="")
            if show_labels:
                add_line_labels(fig2, "{:,.2f}")
            st.plotly_chart(fig2, use_container_width=True)

def section_targets():
    hero(
        "3.3–3.4 Targets & Achievement",
        "Overall export target achievement along with region-wise, country-wise and commodity-wise target views.",
        ["Overall target", "Region-wise", "Country-wise", "Commodity-wise"],
    )
    view = st.radio("Choose target section", ["Overall", "Region-wise", "Country-wise", "Commodity-wise"], horizontal=True)
    if view == "Overall":
        d = DATA["overall_target"]
        r = st.columns(3)
        with r[0]:
            kpi("Annual Target FY2025-26", f"{fmt_num(d['target_bn'])} US$ bn", "")
        with r[1]:
            kpi("Actual Exports FY2025-26", f"{fmt_num(d['actual_bn'])} US$ bn", "")
        with r[2]:
            kpi("% Target Achieved", f"{fmt_num(d['achieved_pct'])}%", "")
    elif view == "Region-wise":
        df = df_from("region_targets")
        top_n = st.slider("Top regions", 5, 10, 10, key="rtop")
        render_table(df.rename(columns={
            "region":"Region",
            "target_mn":"Export Target 2025-26 (US$ mn)",
            "actual_mn":"Actual Exports 2025-26 (US$ mn)",
            "deficit_surplus_mn":"Deficit / Surplus (US$ mn)",
            "achieved_pct":"% Achieved",
        }), {
            "Export Target 2025-26 (US$ mn)":"{:,.2f}",
            "Actual Exports 2025-26 (US$ mn)":"{:,.2f}",
            "Deficit / Surplus (US$ mn)":"{:,.2f}",
            "% Achieved":"{:,.2f}",
        }, height=430)
        plot_df = df[df["region"].str.upper()!="TOTAL"].nlargest(top_n, "actual_mn").sort_values("actual_mn")
        fig = px.bar(plot_df, x="actual_mn", y="region", orientation="h", color="achieved_pct", color_continuous_scale="Greens")
        fig.update_layout(template="plotly_white", height=400, margin=dict(l=10,r=10,t=10,b=10), xaxis_title="Actual exports (US$ mn)", yaxis_title="")
        if show_labels:
            add_bar_labels(fig, "h", "{:,.0f}")
        st.plotly_chart(fig, use_container_width=True)
    elif view == "Country-wise":
        df = df_from("country_targets")
        render_table(df.rename(columns={
            "country":"Country",
            "target_mn":"Target 2025-26 (US$ mn)",
            "actual_mn":"Achievement (US$ mn)",
            "deficit_surplus_mn":"Deficit / Surplus (US$ mn)",
            "achieved_pct":"% Target Achieved",
        }), {
            "Target 2025-26 (US$ mn)":"{:,.2f}",
            "Achievement (US$ mn)":"{:,.2f}",
            "Deficit / Surplus (US$ mn)":"{:,.2f}",
            "% Target Achieved":"{:,.2f}",
        }, height=430)
        plot_df = df[df["country"] != "Sub Total"].sort_values("actual_mn").copy()
        fig = px.bar(plot_df, x="actual_mn", y="country", orientation="h")
        fig.update_traces(marker_color="#7a1f5c")
        fig.update_layout(template="plotly_white", height=460, margin=dict(l=10,r=10,t=10,b=10), xaxis_title="Actual exports (US$ mn)", yaxis_title="")
        if show_labels:
            add_bar_labels(fig, "h", "{:,.0f}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        df = df_from("commodity_targets")
        render_table(df.rename(columns={
            "commodity":"Commodity",
            "target_mn":"Export Target FY2025-26 (US$ mn)",
            "actual_mn":"Actual Exports FY2025-26 (US$ mn)",
            "deficit_surplus_mn":"Deficit / Surplus FY2025-26 (US$ mn)",
            "share_pct":"% Share FY2025-26",
            "achieved_pct":"% Target Achieved FY2025-26",
        }), {
            "Export Target FY2025-26 (US$ mn)":"{:,.2f}",
            "Actual Exports FY2025-26 (US$ mn)":"{:,.2f}",
            "Deficit / Surplus FY2025-26 (US$ mn)":"{:,.2f}",
            "% Share FY2025-26":"{:,.2f}",
            "% Target Achieved FY2025-26":"{:,.2f}",
        }, height=460)
        fig = px.bar(df.sort_values("actual_mn"), x="actual_mn", y="commodity", orientation="h")
        fig.update_traces(marker_color="#5a7d4d")
        fig.update_layout(template="plotly_white", height=480, margin=dict(l=10,r=10,t=10,b=10), xaxis_title="Actual exports (US$ mn)", yaxis_title="")
        if show_labels:
            add_bar_labels(fig, "h", "{:,.0f}")
        st.plotly_chart(fig, use_container_width=True)




def section_exports():
    commodity_rows = [
        {"commodity": 'Cut & Polished Diamonds', "fy2024_mn": 15967.0155910242, "fy2025_mn": 13292.4306358316, "fy2026_mn": 12159.826533725809},
        {"commodity": 'Polished Lab Grown Diamonds', "fy2024_mn": 1402.43621641437, "fy2025_mn": 1267.27774263363, "fy2026_mn": 1133.0040368021612},
        {"commodity": 'Coloured Gemstones', "fy2024_mn": 478.70955814074, "fy2025_mn": 440.443629575932, "fy2026_mn": 437.30725664670615},
        {"commodity": 'Polished Synthetic Stones', "fy2024_mn": 13.8914534588718, "fy2025_mn": 11.5249714561311, "fy2026_mn": 16.90086028856919},
        {"commodity": 'Pearls - Worked', "fy2024_mn": 8.28190903357442, "fy2025_mn": 4.86980026125159, "fy2026_mn": 5.571821335856648},
        {"commodity": 'Plain Gold Jewellery', "fy2024_mn": 5873.20414936061, "fy2025_mn": 5231.76813682332, "fy2026_mn": 4843.63},
        {"commodity": 'Studded Gold Jewellery', "fy2024_mn": 5356.96795570596, "fy2025_mn": 6136.00223949568, "fy2026_mn": 6520.69},
        {"commodity": 'Total Gold Jewellery', "fy2024_mn": 11230.17210506657, "fy2025_mn": 11367.770376319, "fy2026_mn": 11364.321054649175},
        {"commodity": 'Silver Jewellery', "fy2024_mn": 1618.97495959602, "fy2025_mn": 964.658801921387, "fy2026_mn": 1467.470438605242},
        {"commodity": 'Platinum Jewellery', "fy2024_mn": 163.478501392917, "fy2025_mn": 182.752189075454, "fy2026_mn": 254.60217260948133},
        {"commodity": 'Imitation Jewellery', "fy2024_mn": 66.4145726296881, "fy2025_mn": 65.6984476877835, "fy2026_mn": 71.8973946728683},
        {"commodity": 'Articles of Gold, Silver & Others', "fy2024_mn": 54.2792947092569, "fy2025_mn": 56.3682473007683, "fy2026_mn": 21.698000189805267},
        {"commodity": 'Gold Medallions & Coin', "fy2024_mn": 200.779907648462, "fy2025_mn": 120.404896159701, "fy2026_mn": 6.449841222636965},
        {"commodity": 'Sales to Foreign Tourist', "fy2024_mn": 42.1, "fy2025_mn": 44.58, "fy2026_mn": np.nan},
        {"commodity": 'Sub - Total', "fy2024_mn": 31246.534069114667, "fy2025_mn": 27818.779738222638, "fy2026_mn": 26939.048356099138},
        {"commodity": 'Exports of Rough-Diamonds', "fy2024_mn": 917.315951412623, "fy2025_mn": 416.51, "fy2026_mn": 289.1487610105049},
        {"commodity": 'Rgh Lab Grown Syn. Diamonds', "fy2024_mn": 83.4393338400182, "fy2025_mn": 56.06, "fy2026_mn": 50.63078687666443},
        {"commodity": 'Others', "fy2024_mn": 80.65664135228872, "fy2025_mn": 424.2905960150638, "fy2026_mn": 438.5720952506924},
        {"commodity": 'Gross Exports', "fy2024_mn": 32327.945995719598, "fy2025_mn": 28715.6403342377, "fy2026_mn": 27717.4},
        {"commodity": 'Re-imports Others', "fy2024_mn": 5386.992857197, "fy2025_mn": 4446.76281811982, "fy2026_mn": np.nan},
        {"commodity": 'Re-imports CPD', "fy2024_mn": 850.870950223379, "fy2025_mn": 750.657764237216, "fy2026_mn": np.nan},
        {"commodity": 'Net Exports', "fy2024_mn": 26090.082188299217, "fy2025_mn": 23518.219751880664, "fy2026_mn": np.nan},
    ]
    gross_2025 = 28715.6403342377
    gross_2026 = 27717.40
    for row in commodity_rows:
        row["growth_pct"] = ((row["fy2026_mn"] / row["fy2025_mn"]) - 1) * 100 if row["fy2025_mn"] else np.nan
        row["share_2025_pct"] = (row["fy2025_mn"] / gross_2025) * 100 if gross_2025 else np.nan
        row["share_2026_pct"] = (row["fy2026_mn"] / gross_2026) * 100 if gross_2026 else np.nan
        row["share_change_pp"] = row["share_2026_pct"] - row["share_2025_pct"]

    band_summary_rows = [
        {"band": "0-30 Mn", "products_count": 11, "products_total_mn": 66.13075159462392, "markets_count": 123, "markets_total_mn": 341.7299541841581},
        {"band": "30-50 Mn", "products_count": 2, "products_total_mn": 81.02790293545189, "markets_count": 2, "markets_total_mn": 76.91510253420417},
        {"band": "50-70 Mn", "products_count": 2, "products_total_mn": 106.9802884116678, "markets_count": 2, "markets_total_mn": 133.1295344510175},
        {"band": "70-100 Mn", "products_count": 2, "products_total_mn": 151.4213997322662, "markets_count": 2, "markets_total_mn": 153.2570251257729},
        {"band": "100-200 Mn", "products_count": 0, "products_total_mn": 0.0, "markets_count": 4, "markets_total_mn": 633.5283136608223},
        {"band": ">200 Mn", "products_count": 8, "products_total_mn": 27311.83645114338, "markets_count": 18, "markets_total_mn": 26378.83686386141},
    ]

    significance_rows = [
        {"product": "Synthetic Stones, unworked", "fy2026_mn": 0.1136739676889556, "band": "0-30 Mn"},
        {"product": "Articles of Pearls", "fy2026_mn": 0.8210730792208252, "band": "0-30 Mn"},
        {"product": "Pearls, unworked", "fy2026_mn": 1.006657312033514, "band": "0-30 Mn"},
        {"product": "Other Articles of Precious Metal", "fy2026_mn": 2.458850250631438, "band": "0-30 Mn"},
        {"product": "Articles of Gold Smith", "fy2026_mn": 2.73483808591963, "band": "0-30 Mn"},
        {"product": "Dust and Powder", "fy2026_mn": 3.167165657290536, "band": "0-30 Mn"},
        {"product": "Pearls, worked", "fy2026_mn": 5.571821335856648, "band": "0-30 Mn"},
        {"product": "Gold Medallions & Coins", "fy2026_mn": 6.449841222636965, "band": "0-30 Mn"},
        {"product": "Coloured Gemstones, unworked", "fy2026_mn": 10.401658541522, "band": "0-30 Mn"},
        {"product": "Articles of Silver Smith", "fy2026_mn": 16.5043118532542, "band": "0-30 Mn"},
        {"product": "Synthetic Stones, worked", "fy2026_mn": 16.90086028856919, "band": "0-30 Mn"},
        {"product": "Articles of Precious/Semi Precious Stones", "fy2026_mn": 38.56299017833854, "band": "30-50 Mn"},
        {"product": "Waste and Scrap", "fy2026_mn": 42.46491275711335, "band": "30-50 Mn"},
        {"product": "Lab Grown Diamonds, unworked", "fy2026_mn": 50.63078687666443, "band": "50-70 Mn"},
        {"product": "Silver Bar", "fy2026_mn": 56.34950153500333, "band": "50-70 Mn"},
        {"product": "Imitation Jewellery", "fy2026_mn": 71.8973946728683, "band": "70-100 Mn"},
        {"product": "Platinum Bar", "fy2026_mn": 79.5240050593979, "band": "70-100 Mn"},
        {"product": "Cut & Polished Diamonds", "fy2026_mn": 12159.826533725809, "band": ">200 Mn"},
        {"product": "Gold Jewellery", "fy2026_mn": 11364.321054649175, "band": ">200 Mn"},
        {"product": "Silver Jewellery", "fy2026_mn": 1467.470438605242, "band": ">200 Mn"},
        {"product": "Lab Grown Diamonds, worked", "fy2026_mn": 1133.0040368021612, "band": ">200 Mn"},
        {"product": "Coloured Gemstones, worked", "fy2026_mn": 437.30725664670615, "band": ">200 Mn"},
        {"product": "Rough Diamonds", "fy2026_mn": 289.1487610105049, "band": ">200 Mn"},
        {"product": "Platinum Jewellery", "fy2026_mn": 254.60217260948133, "band": ">200 Mn"},
        {"product": "Gold Bar", "fy2026_mn": 206.15619709429615, "band": ">200 Mn"},
    ]

    key_df = pd.DataFrame(commodity_rows)
    basket_df = key_df[key_df["commodity"] != "Gross Exports"].copy()
    band_df = pd.DataFrame(band_summary_rows)
    significance_df = pd.DataFrame(significance_rows)
    country_hist = pd.DataFrame(DATA["export_country_history"]).copy()
    region_hist = pd.DataFrame(DATA["export_region_history"]).copy()
    port_hist = pd.DataFrame(DATA["export_port_history"]).copy()

    base_basket = df_from("export_basket").copy()
    base_basket["commodity"] = base_basket["commodity"].replace({
        "Cut & Polished Diamonds": "Cut & Pol Diamonds",
        "Polished Lab Grown Diamonds ": "Pol. Lab Grown Diamonds",
        "Coloured Gem Stone": "Coloured Gemstones",
        "Gold Medallions": "Gold Medallions & Coins",
        "Total Exports": "Gross Exports",
    })
    sig_map = significance_df.set_index("product")["fy2026_mn"].to_dict()
    basket_2026 = {
        "Cut & Pol Diamonds": float(basket_df.loc[basket_df["commodity"] == "Cut & Polished Diamonds", "fy2026_mn"].sum()),
        "Gold Jewellery": float(basket_df.loc[basket_df["commodity"].isin(["Plain Gold Jewellery", "Studded Gold Jewellery"]), "fy2026_mn"].sum()),
        "Silver Jewellery": float(basket_df.loc[basket_df["commodity"] == "Silver Jewellery", "fy2026_mn"].sum()),
        "Pol. Lab Grown Diamonds": float(basket_df.loc[basket_df["commodity"] == "Polished Lab Grown Diamonds", "fy2026_mn"].sum()),
        "Coloured Gemstones": float(basket_df.loc[basket_df["commodity"] == "Coloured Gemstones", "fy2026_mn"].sum()),
        "Imitation Jewellery": float(sig_map.get("Imitation Jewellery", np.nan)),
        "Gold Medallions & Coins": float(sig_map.get("Gold Medallions & Coins", np.nan)),
    }
    basket_2026["Others"] = gross_2026 - sum(v for v in basket_2026.values() if pd.notna(v))
    basket_2026["Gross Exports"] = gross_2026
    total_2026 = basket_2026["Gross Exports"]

    basket_compare_rows = []
    ordered_basket = [
        "Cut & Pol Diamonds",
        "Gold Jewellery",
        "Silver Jewellery",
        "Pol. Lab Grown Diamonds",
        "Coloured Gemstones",
        "Imitation Jewellery",
        "Gold Medallions & Coins",
        "Others",
        "Gross Exports",
    ]
    for name in ordered_basket:
        src = base_basket.loc[base_basket["commodity"] == name]
        row = {
            "commodity": name,
            "fy2020_mn": float(src["fy2020_mn"].iloc[0]) if not src.empty and "fy2020_mn" in src.columns else np.nan,
            "fy2025_mn": float(src["fy2025_mn"].iloc[0]) if not src.empty and "fy2025_mn" in src.columns else np.nan,
            "fy2020_share_pct": float(src["fy2020_share_pct"].iloc[0]) if not src.empty and "fy2020_share_pct" in src.columns else np.nan,
            "fy2025_share_pct": float(src["fy2025_share_pct"].iloc[0]) if not src.empty and "fy2025_share_pct" in src.columns else np.nan,
            "fy2026_mn": basket_2026.get(name, np.nan),
        }
        row["fy2026_share_pct"] = (row["fy2026_mn"] / total_2026) * 100 if pd.notna(row["fy2026_mn"]) and total_2026 else np.nan
        basket_compare_rows.append(row)
    basket_compare = pd.DataFrame(basket_compare_rows)

    def fy_label(y: int) -> str:
        return f"FY{int(y)}-{str(int(y)+1)[-2:]}"

    def choose_year_block(prefix: str, years: list[int], default_start: int | None = None, default_end: int | None = None):
        years = sorted([int(y) for y in years])
        if not years:
            return None, None, "", ""
        default_start = years[-2] if default_start is None and len(years) >= 2 else years[0] if default_start is None else default_start
        default_end = years[-1] if default_end is None else default_end
        with st.container():
            c1, c2 = st.columns(2)
            with c1:
                start_year = st.selectbox(
                    "Start year",
                    years,
                    index=years.index(default_start) if default_start in years else 0,
                    format_func=fy_label,
                    key=f"{prefix}_start",
                )
            end_options = [y for y in years if y >= start_year]
            with c2:
                end_year = st.selectbox(
                    "End year",
                    end_options,
                    index=end_options.index(default_end) if default_end in end_options else len(end_options) - 1,
                    format_func=fy_label,
                    key=f"{prefix}_end",
                )
        return start_year, end_year, fy_label(start_year), fy_label(end_year)

    def compare_history(df_hist: pd.DataFrame, start_year: int, end_year: int, exclude: list[str] | None = None) -> pd.DataFrame:
        exclude = exclude or []
        pivot = df_hist.pivot_table(index="entity", columns="fy_start", values="value_mn", aggfunc="sum")
        if start_year not in pivot.columns:
            pivot[start_year] = 0.0
        if end_year not in pivot.columns:
            pivot[end_year] = 0.0
        out = pivot[[start_year, end_year]].copy().reset_index().rename(columns={"entity": "name", start_year: "start_mn", end_year: "end_mn"})
        out["start_mn"] = out["start_mn"].fillna(0.0)
        out["end_mn"] = out["end_mn"].fillna(0.0)
        out["change_mn"] = out["end_mn"] - out["start_mn"]
        out["growth_pct"] = np.where(out["start_mn"] != 0, ((out["end_mn"] / out["start_mn"]) - 1) * 100, np.nan)
        total_end = out.loc[out["name"].str.strip().str.lower().isin(["totals", "total"]), "end_mn"].sum()
        out["end_share_pct"] = np.where(total_end != 0, (out["end_mn"] / total_end) * 100, np.nan)
        out = out[~out["name"].isin(exclude)].copy()
        return out.sort_values("end_mn", ascending=False).reset_index(drop=True)

    hero(
        "3.5–3.9 Export Structure",
        "Top-N filters now control the tables as well, and basket change can start from earlier benchmark years instead of only the latest two years.",
        ["Year comparison filters", "Standalone", "No runtime Excel needed", "Export structure"],
    )
    tabs = st.tabs(["3.5 Key Commodities", "3.6 Basket Change", "3.7 Regions", "3.8 Top Destinations", "3.9 Port Performance"])

    with tabs[0]:
        chart_source = basket_df[~basket_df["commodity"].isin([
            "Total Gold Jewellery", "Sub - Total", "Gross Exports", "Re-imports Others", "Re-imports CPD", "Net Exports"
        ])].copy()
        top_n = st.slider("Top commodities for charts", 5, len(chart_source), min(10, len(chart_source)), key="exp25_topn")
        full_table = basket_df.rename(columns={
            "commodity": "Commodity",
            "fy2024_mn": "FY2023-24 (US$ mn)",
            "fy2025_mn": "FY2024-25 (US$ mn)",
            "fy2026_mn": "FY2025-26 (US$ mn)",
            "growth_pct": "% Growth / Decline (Y-o-Y)",
            "share_2025_pct": "FY2024-25 Share (%)",
            "share_2026_pct": "FY2025-26 Share (%)",
        })
        render_table(
            full_table[["Commodity", "FY2023-24 (US$ mn)", "FY2024-25 (US$ mn)", "FY2025-26 (US$ mn)", "% Growth / Decline (Y-o-Y)", "FY2024-25 Share (%)", "FY2025-26 Share (%)"]],
            {
                "FY2023-24 (US$ mn)": "{:,.2f}",
                "FY2024-25 (US$ mn)": "{:,.2f}",
                "FY2025-26 (US$ mn)": "{:,.2f}",
                "% Growth / Decline (Y-o-Y)": "{:+,.2f}",
                "FY2024-25 Share (%)": "{:,.2f}",
                "FY2025-26 Share (%)": "{:,.2f}",
            },
            height=720,
        )

        latest_top = chart_source.nlargest(top_n, "fy2026_mn").copy()
        left, right = st.columns(2)
        with left:
            pie_25 = px.pie(latest_top, values="fy2025_mn", names="commodity", hole=0.35)
            pie_25.update_traces(textinfo="percent+label")
            pie_25.update_layout(template="plotly_white", height=430, margin=dict(l=10, r=10, t=50, b=10), title="FY2024-25 Share of Selected Commodities")
            st.plotly_chart(pie_25, use_container_width=True)
        with right:
            pie_26 = latest_top.dropna(subset=["fy2026_mn"]).copy()
            pie_26 = px.pie(pie_26, values="fy2026_mn", names="commodity", hole=0.35)
            pie_26.update_traces(textinfo="percent+label")
            pie_26.update_layout(template="plotly_white", height=430, margin=dict(l=10, r=10, t=50, b=10), title="FY2025-26 Share of Selected Commodities")
            st.plotly_chart(pie_26, use_container_width=True)

        compare_plot = latest_top.sort_values("fy2026_mn")
        fig = go.Figure()
        fig.add_trace(go.Bar(y=compare_plot["commodity"], x=compare_plot["fy2025_mn"], orientation="h", name="FY2024-25", marker_color="#d9ead3"))
        fig.add_trace(go.Bar(y=compare_plot["commodity"], x=compare_plot["fy2026_mn"], orientation="h", name="FY2025-26", marker_color="#274e3d"))
        fig.update_layout(
            barmode="group",
            template="plotly_white",
            height=480,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Exports (US$ mn)",
            yaxis_title="",
        )
        if show_labels:
            fig.for_each_trace(lambda tr: tr.update(text=[f"{v:,.0f}" if pd.notna(v) else "" for v in tr.x], textposition="outside"))
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        basket_hist = load_export_basket_history()
        if basket_hist.empty:
            st.warning("The multi-year basket history could not be reconstructed because the EXPORT PRODUCTS workbook is not available next to the app.")
        else:
            years = sorted(basket_hist["fy_start"].dropna().astype(int).unique().tolist())
            default_start = years[0] if years else None
            default_end = years[-1] if years else None
            start_year, end_year, start_label, end_label = choose_year_block("exp_basket", years, default_start, default_end)

            value_pivot = basket_hist.pivot_table(index="commodity", columns="fy_start", values="value_mn", aggfunc="sum")
            share_pivot = basket_hist.pivot_table(index="commodity", columns="fy_start", values="share_pct", aggfunc="sum")

            for y in [start_year, end_year]:
                if y not in value_pivot.columns:
                    value_pivot[y] = np.nan
                if y not in share_pivot.columns:
                    share_pivot[y] = np.nan

            ordered_rows = [
                "Cut & Pol Diamonds",
                "Gold Jewellery",
                "Silver Jewellery",
                "Coloured Gemstones",
                "Polished Synthetic Stones",
                "Pearls - Worked",
                "Platinum Jewellery",
                "Imitation Jewellery",
                "Gross Exports",
            ]
            basket_table = pd.DataFrame({
                "Commodity": ordered_rows,
                f"{start_label} (US$ mn)": [float(value_pivot.loc[row, start_year]) if row in value_pivot.index else np.nan for row in ordered_rows],
                f"{end_label} (US$ mn)": [float(value_pivot.loc[row, end_year]) if row in value_pivot.index else np.nan for row in ordered_rows],
                f"{start_label} Share (%)": [float(share_pivot.loc[row, start_year]) if row in share_pivot.index else np.nan for row in ordered_rows],
                f"{end_label} Share (%)": [float(share_pivot.loc[row, end_year]) if row in share_pivot.index else np.nan for row in ordered_rows],
            })
            basket_table["Change in Share (pp)"] = basket_table[f"{end_label} Share (%)"] - basket_table[f"{start_label} Share (%)"]
            basket_table["Growth / Decline (%)"] = np.where(
                basket_table[f"{start_label} (US$ mn)"] != 0,
                ((basket_table[f"{end_label} (US$ mn)"] / basket_table[f"{start_label} (US$ mn)"]) - 1) * 100,
                np.nan,
            )

            st.caption("3.6 is reconstructed across multiple years from the annual-report export-products workbook. Shares are recalculated against the reconstructed basket total for each selected year so the year-comparison logic stays consistent.")

            left, right = st.columns(2)
            with left:
                render_table(
                    basket_table[["Commodity", f"{start_label} (US$ mn)", f"{end_label} (US$ mn)", f"{start_label} Share (%)", f"{end_label} Share (%)", "Change in Share (pp)", "Growth / Decline (%)"]],
                    {
                        f"{start_label} (US$ mn)": "{:,.2f}",
                        f"{end_label} (US$ mn)": "{:,.2f}",
                        f"{start_label} Share (%)": "{:,.2f}",
                        f"{end_label} Share (%)": "{:,.2f}",
                        "Change in Share (pp)": "{:+,.2f}",
                        "Growth / Decline (%)": "{:+,.2f}",
                    },
                    height=420,
                )

                compare_plot = basket_table[basket_table["Commodity"] != "Gross Exports"].copy()
                fig = go.Figure()
                fig.add_trace(go.Bar(x=compare_plot["Commodity"], y=compare_plot[f"{start_label} Share (%)"], name=f"{start_label} share", marker_color="#d9ead3"))
                fig.add_trace(go.Bar(x=compare_plot["Commodity"], y=compare_plot[f"{end_label} Share (%)"], name=f"{end_label} share", marker_color="#7a1f5c"))
                fig.update_layout(
                    barmode="group",
                    template="plotly_white",
                    height=360,
                    margin=dict(l=10, r=10, t=10, b=10),
                    yaxis_title="Share of reconstructed basket (%)",
                    xaxis_title="",
                )
                st.plotly_chart(fig, use_container_width=True)

            with right:
                if end_year == 2025:
                    render_table(
                        band_df.rename(columns={
                            "band": "Value Band",
                            "products_count": "Products Count",
                            "products_total_mn": "Products FY2025-26 Total (US$ mn)",
                            "markets_count": "Markets Count",
                            "markets_total_mn": "Markets FY2025-26 Total (US$ mn)",
                        }),
                        {
                            "Products FY2025-26 Total (US$ mn)": "{:,.2f}",
                            "Markets FY2025-26 Total (US$ mn)": "{:,.2f}",
                        },
                        height=400,
                    )
                    fig2 = go.Figure()
                    fig2.add_trace(go.Bar(x=band_df["band"], y=band_df["products_count"], name="Products Count", marker_color="#5a7d4d"))
                    fig2.add_trace(go.Bar(x=band_df["band"], y=band_df["markets_count"], name="Markets Count", marker_color="#b88746"))
                    fig2.update_layout(barmode="group", template="plotly_white", height=360, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Count", xaxis_title="FY2025-26 export band")
                    if show_labels:
                        add_bar_labels(fig2, "v", "{:,.0f}")
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("The basket-significance ladder is currently available only for FY2025-26 in the embedded SAP extract, so it is shown when FY2025-26 is selected as the end year.")

            if end_year == 2025:
                st.markdown("<div class='report-band'>FY2025-26 product significance ladder</div>", unsafe_allow_html=True)
                render_table(
                    significance_df.rename(columns={
                        "product": "Product",
                        "fy2026_mn": "FY2025-26 Export Value (US$ mn)",
                        "band": "Value Band",
                    }),
                    {"FY2025-26 Export Value (US$ mn)": "{:,.2f}"},
                    height=420,
                )

    with tabs[2]:
        country_hist = load_entity_year_wide_workbook(
            "Country-wise (exports, imports, re-imports).xlsx",
            "Country-Imports",
            "country",
        )
        if not country_hist.empty:
            years = sorted([c for c in country_hist.columns if isinstance(c, int)])
            default_start = 2020 if 2020 in years else years[0]
            default_end = 2025 if 2025 in years else years[-1]
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                start_year = st.selectbox(
                    "Start year",
                    years,
                    index=years.index(default_start),
                    format_func=fy_label_generic,
                    key="imp_country_hist_start",
                )
            with c2:
                end_options = [y for y in years if y >= start_year]
                end_year = st.selectbox(
                    "End year",
                    end_options,
                    index=end_options.index(default_end) if default_end in end_options else len(end_options) - 1,
                    format_func=fy_label_generic,
                    key="imp_country_hist_end",
                )
            with c3:
                max_n = max(5, min(25, len(country_hist)))
                top_n = st.slider("Top N countries", 5, max_n, min(10, max_n), key="imp_country_hist_topn")

            comp = compare_country_product(country_hist, start_year, end_year)
            start_label = fy_label_generic(start_year)
            end_label = fy_label_generic(end_year)

            top_df = comp.head(top_n).copy().rename(columns={
                "Start Value": f"{start_label} (US$ mn)",
                "End Value": f"{end_label} (US$ mn)",
                "Start Share (%)": f"{start_label} % Share",
                "End Share (%)": f"{end_label} % Share",
            })
            render_table(
                top_df[["Country", f"{start_label} (US$ mn)", f"{start_label} % Share", f"{end_label} (US$ mn)", f"{end_label} % Share", "Change (US$ mn)", "Growth (%)"]],
                {
                    f"{start_label} (US$ mn)": "{:,.2f}",
                    f"{start_label} % Share": "{:,.2f}",
                    f"{end_label} (US$ mn)": "{:,.2f}",
                    f"{end_label} % Share": "{:,.2f}",
                    "Change (US$ mn)": "{:+,.2f}",
                    "Growth (%)": "{:+,.2f}",
                },
                height=460,
            )

            left, right = st.columns(2)
            with left:
                plot_df = top_df.sort_values(f"{end_label} (US$ mn)")
                fig = go.Figure()
                fig.add_trace(go.Bar(y=plot_df["Country"], x=plot_df[f"{start_label} (US$ mn)"], orientation="h", name=start_label, marker_color="#d9ead3"))
                fig.add_trace(go.Bar(y=plot_df["Country"], x=plot_df[f"{end_label} (US$ mn)"], orientation="h", name=end_label, marker_color="#b88746"))
                fig.update_layout(barmode="group", template="plotly_white", height=430, margin=dict(l=10, r=10, t=10, b=10), xaxis_title="US$ mn", yaxis_title="")
                st.plotly_chart(fig, use_container_width=True)
            with right:
                pie_end = pie_with_others(comp, "End Value", top_n=top_n)
                if not pie_end.empty:
                    fig = px.pie(pie_end, names="Country", values="End Value", hole=0.35, title=f"{end_label} country share")
                    fig.update_layout(template="plotly_white", height=430, margin=dict(l=10, r=10, t=40, b=10))
                    st.plotly_chart(fig, use_container_width=True)
        else:
            year_map = {
                "FY2020-21": "fy2020",
                "FY2025-26": "fy2025",
            }
            available_years = list(year_map.keys())
            c1, c2 = st.columns(2)
            with c1:
                start_year = st.selectbox("Start year", available_years, index=0, key="imp_country_start")
            with c2:
                end_year = st.selectbox("End year", available_years, index=len(available_years)-1, key="imp_country_end")
            start_df = pd.DataFrame(DATA["top_import_countries"][year_map[start_year]]).rename(columns={
                "amount_mn": f"{start_year} (US$ mn)",
                "share_pct": f"{start_year} % Share",
            })
            end_df = pd.DataFrame(DATA["top_import_countries"][year_map[end_year]]).rename(columns={
                "amount_mn": f"{end_year} (US$ mn)",
                "share_pct": f"{end_year} % Share",
            })
            compare = start_df.merge(end_df, on="country", how="outer")
            value_cols = [f"{start_year} (US$ mn)", f"{end_year} (US$ mn)", f"{start_year} % Share", f"{end_year} % Share"]
            for col in value_cols:
                compare[col] = pd.to_numeric(compare[col], errors="coerce")
            compare["Change (US$ mn)"] = compare[f"{end_year} (US$ mn)"].fillna(0) - compare[f"{start_year} (US$ mn)"].fillna(0)
            compare["Growth (%)"] = np.where(
                compare[f"{start_year} (US$ mn)"].fillna(0) != 0,
                (compare[f"{end_year} (US$ mn)"].fillna(0) - compare[f"{start_year} (US$ mn)"].fillna(0)) / compare[f"{start_year} (US$ mn)"].fillna(0) * 100,
                np.nan,
            )
            order = compare[f"{end_year} (US$ mn)"].fillna(compare[f"{start_year} (US$ mn)"]).sort_values(ascending=False).index
            compare = compare.loc[order].copy()
            render_table(compare.rename(columns={"country": "Country"}), {
                f"{start_year} (US$ mn)": "{:,.2f}",
                f"{end_year} (US$ mn)": "{:,.2f}",
                f"{start_year} % Share": "{:,.2f}",
                f"{end_year} % Share": "{:,.2f}",
                "Change (US$ mn)": "{:+,.2f}",
                "Growth (%)": "{:+,.2f}",
            }, height=420)

    with tabs[3]:
        region_hist = load_entity_year_wide_workbook(
            "Regionwise (exports, imports, re-imports).xlsx",
            "Regionwise - Imports",
            "region",
        )
        if not region_hist.empty:
            years = sorted([c for c in region_hist.columns if isinstance(c, int)])
            default_start = 2020 if 2020 in years else years[0]
            default_end = 2025 if 2025 in years else years[-1]
            r1, r2 = st.columns(2)
            with r1:
                start_year = st.selectbox(
                    "Start year",
                    years,
                    index=years.index(default_start),
                    format_func=fy_label_generic,
                    key="imp_region_hist_start",
                )
            with r2:
                end_options = [y for y in years if y >= start_year]
                end_year = st.selectbox(
                    "End year",
                    end_options,
                    index=end_options.index(default_end) if default_end in end_options else len(end_options) - 1,
                    format_func=fy_label_generic,
                    key="imp_region_hist_end",
                )
            comp = compare_country_product(region_hist.rename(columns={"region": "country"}), start_year, end_year).rename(columns={"Country": "Region"})
            start_label = fy_label_generic(start_year)
            end_label = fy_label_generic(end_year)

            render_table(
                comp[["Region", "Start Value", "End Value", "Start Share (%)", "End Share (%)", "Change (US$ mn)", "Growth (%)"]].rename(columns={
                    "Start Value": f"{start_label} (US$ mn)",
                    "End Value": f"{end_label} (US$ mn)",
                    "Start Share (%)": f"{start_label} % Share",
                    "End Share (%)": f"{end_label} % Share",
                }),
                {
                    f"{start_label} (US$ mn)": "{:,.2f}",
                    f"{end_label} (US$ mn)": "{:,.2f}",
                    f"{start_label} % Share": "{:,.2f}",
                    f"{end_label} % Share": "{:,.2f}",
                    "Change (US$ mn)": "{:+,.2f}",
                    "Growth (%)": "{:+,.2f}",
                },
                height=430,
            )
            plot_df = comp.sort_values("End Value")
            fig = go.Figure()
            fig.add_trace(go.Bar(y=plot_df["Region"], x=plot_df["Start Value"], orientation="h", name=start_label, marker_color="#d9ead3"))
            fig.add_trace(go.Bar(y=plot_df["Region"], x=plot_df["End Value"], orientation="h", name=end_label, marker_color="#7a1f5c"))
            fig.update_layout(barmode="group", template="plotly_white", height=430, margin=dict(l=10, r=10, t=10, b=10), xaxis_title="US$ mn", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            df = df_from("import_regions")
            region_years = ["FY2020-21", "FY2025-26"]
            r1, r2 = st.columns(2)
            with r1:
                start_year = st.selectbox("Start year", region_years, index=0, key="imp_region_start")
            with r2:
                end_year = st.selectbox("End year", region_years, index=len(region_years)-1, key="imp_region_end")
            year_to_cols = {
                "FY2020-21": ("fy2020_mn", "fy2020_share_pct"),
                "FY2025-26": ("fy2025_mn", "fy2025_share_pct"),
            }
            start_val_col, start_share_col = year_to_cols[start_year]
            end_val_col, end_share_col = year_to_cols[end_year]
            table = df.rename(columns={
                "region": "Region",
                start_val_col: f"{start_year} (US$ mn)",
                start_share_col: f"{start_year} % Share",
                end_val_col: f"{end_year} (US$ mn)",
                end_share_col: f"{end_year} % Share",
            })[["Region", f"{start_year} (US$ mn)", f"{end_year} (US$ mn)", f"{start_year} % Share", f"{end_year} % Share"]]
            render_table(table, {
                f"{start_year} (US$ mn)": "{:,.2f}",
                f"{start_year} % Share": "{:,.2f}",
                f"{end_year} (US$ mn)": "{:,.2f}",
                f"{end_year} % Share": "{:,.2f}",
            }, height=430)


def section_imports():
    hero(
        "3.10–3.13 Import Structure",
        "Monthly import trend, import commodity structure, top import countries and import region mix.",
        ["Monthly trend", "Commodity-wise", "Country-wise", "Region-wise"],
    )
    tabs = st.tabs(["3.10 Monthly Imports", "3.11 Commodities", "3.12 Countries", "3.13 Regions"])

    with tabs[0]:
        df = df_from("monthly_imports").copy()
        df["month"] = df["month"].astype(str)
        total_mask = df["month"].str.contains("total", case=False, na=False)
        monthly = df.loc[~total_mask].copy()
        total_row = df.loc[total_mask].copy()
        table = monthly.rename(columns={
            "month": "Month",
            "fy2025_mn": "FY2024-25 (US$ mn)",
            "fy2026_mn": "FY2025-26 (US$ mn)",
            "growth_pct": "% Import Growth (Y-o-Y)",
        })
        if not total_row.empty:
            total_disp = total_row.rename(columns={
                "month": "Month",
                "fy2025_mn": "FY2024-25 (US$ mn)",
                "fy2026_mn": "FY2025-26 (US$ mn)",
                "growth_pct": "% Import Growth (Y-o-Y)",
            })[["Month", "FY2024-25 (US$ mn)", "FY2025-26 (US$ mn)", "% Import Growth (Y-o-Y)"]]
            st.markdown("<div class='report-band'>Monthly imports</div>", unsafe_allow_html=True)
            render_table(
                pd.concat([table[["Month", "FY2024-25 (US$ mn)", "FY2025-26 (US$ mn)", "% Import Growth (Y-o-Y)"]], total_disp], ignore_index=True),
                {
                    "FY2024-25 (US$ mn)": "{:,.2f}",
                    "FY2025-26 (US$ mn)": "{:,.2f}",
                    "% Import Growth (Y-o-Y)": "{:+,.2f}",
                },
                height=430,
            )
        else:
            render_table(
                table[["Month", "FY2024-25 (US$ mn)", "FY2025-26 (US$ mn)", "% Import Growth (Y-o-Y)"]],
                {
                    "FY2024-25 (US$ mn)": "{:,.2f}",
                    "FY2025-26 (US$ mn)": "{:,.2f}",
                    "% Import Growth (Y-o-Y)": "{:+,.2f}",
                },
                height=390,
            )
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=monthly["month"], y=monthly["fy2025_mn"], name="FY2024-25", marker_color="#d9ead3"))
            fig.add_trace(go.Bar(x=monthly["month"], y=monthly["fy2026_mn"], name="FY2025-26", marker_color="#b88746"))
            fig.update_layout(barmode="group", template="plotly_white", height=380, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="US$ mn", xaxis_title="")
            if show_labels:
                add_bar_labels(fig, "v", "{:,.0f}")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            line_df = monthly.melt(id_vars="month", value_vars=["fy2025_mn", "fy2026_mn"], var_name="series", value_name="value")
            line_df["series"] = line_df["series"].replace({"fy2025_mn": "FY2024-25", "fy2026_mn": "FY2025-26"})
            fig2 = px.line(line_df, x="month", y="value", color="series", markers=True)
            fig2.update_layout(template="plotly_white", height=380, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="US$ mn", xaxis_title="", legend_title_text="")
            if show_labels:
                add_line_labels(fig2, "{:,.0f}")
            st.plotly_chart(fig2, use_container_width=True)

    with tabs[1]:
        df = df_from("import_commodities").copy()
        top_n = st.slider("Top import commodities", 5, len(df), min(10, len(df)), key="imp_commod_topn")
        full_table = df.rename(columns={
            "commodity": "Commodity",
            "fy2024_mn": "FY2024-25 (US$ mn)",
            "fy2025_mn": "FY2025-26 (US$ mn)",
            "growth_pct": "% Growth / Decline (Y-o-Y)",
        })
        render_table(
            full_table[["Commodity", "FY2024-25 (US$ mn)", "FY2025-26 (US$ mn)", "% Growth / Decline (Y-o-Y)"]],
            {
                "FY2024-25 (US$ mn)": "{:,.2f}",
                "FY2025-26 (US$ mn)": "{:,.2f}",
                "% Growth / Decline (Y-o-Y)": "{:+,.2f}",
            },
            height=620,
        )
        chart_df = df[~df["commodity"].str.contains("sub total|gross imports", case=False, na=False)].nlargest(top_n, "fy2025_mn")
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            plot_df = chart_df.sort_values("fy2025_mn")
            fig.add_trace(go.Bar(y=plot_df["commodity"], x=plot_df["fy2024_mn"], orientation="h", name="FY2024-25", marker_color="#d9ead3"))
            fig.add_trace(go.Bar(y=plot_df["commodity"], x=plot_df["fy2025_mn"], orientation="h", name="FY2025-26", marker_color="#7a1f5c"))
            fig.update_layout(barmode="group", template="plotly_white", height=460, margin=dict(l=10, r=10, t=10, b=10), xaxis_title="US$ mn", yaxis_title="")
            if show_labels:
                add_bar_labels(fig, "h", "{:,.0f}")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            pie = px.pie(chart_df, names="commodity", values="fy2025_mn", hole=0.35, title="FY2025-26 share of selected import commodities")
            pie.update_traces(textinfo="percent+label")
            pie.update_layout(template="plotly_white", height=460, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(pie, use_container_width=True)

    with tabs[2]:
        country_hist = load_entity_year_wide_workbook(
            "Country-wise (exports, imports, re-imports).xlsx",
            "Country-Imports",
            "country",
        )
        if not country_hist.empty:
            years = sorted([c for c in country_hist.columns if isinstance(c, int)])
            default_start = 2020 if 2020 in years else years[0]
            default_end = 2025 if 2025 in years else years[-1]
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                start_year = st.selectbox("Start year", years, index=years.index(default_start), format_func=fy_label_generic, key="imp_country_hist_start")
            with c2:
                end_options = [y for y in years if y >= start_year]
                end_year = st.selectbox("End year", end_options, index=end_options.index(default_end) if default_end in end_options else len(end_options)-1, format_func=fy_label_generic, key="imp_country_hist_end")
            with c3:
                max_n = max(5, min(25, len(country_hist)))
                top_n = st.slider("Top N countries", 5, max_n, min(10, max_n), key="imp_country_hist_topn")
            comp = compare_country_product(country_hist, start_year, end_year)
            start_label = fy_label_generic(start_year)
            end_label = fy_label_generic(end_year)
            top_df = comp.head(top_n).copy().rename(columns={
                "Start Value": f"{start_label} (US$ mn)",
                "End Value": f"{end_label} (US$ mn)",
                "Start Share (%)": f"{start_label} % Share",
                "End Share (%)": f"{end_label} % Share",
            })
            render_table(
                top_df[["Country", f"{start_label} (US$ mn)", f"{start_label} % Share", f"{end_label} (US$ mn)", f"{end_label} % Share", "Change (US$ mn)", "Growth (%)"]],
                {
                    f"{start_label} (US$ mn)": "{:,.2f}",
                    f"{start_label} % Share": "{:,.2f}",
                    f"{end_label} (US$ mn)": "{:,.2f}",
                    f"{end_label} % Share": "{:,.2f}",
                    "Change (US$ mn)": "{:+,.2f}",
                    "Growth (%)": "{:+,.2f}",
                },
                height=460,
            )
            left, right = st.columns(2)
            with left:
                plot_df = top_df.sort_values(f"{end_label} (US$ mn)")
                fig = go.Figure()
                fig.add_trace(go.Bar(y=plot_df["Country"], x=plot_df[f"{start_label} (US$ mn)"], orientation="h", name=start_label, marker_color="#d9ead3"))
                fig.add_trace(go.Bar(y=plot_df["Country"], x=plot_df[f"{end_label} (US$ mn)"], orientation="h", name=end_label, marker_color="#b88746"))
                fig.update_layout(barmode="group", template="plotly_white", height=430, margin=dict(l=10, r=10, t=10, b=10), xaxis_title="US$ mn", yaxis_title="")
                if show_labels:
                    add_bar_labels(fig, "h", "{:,.0f}")
                st.plotly_chart(fig, use_container_width=True)
            with right:
                pie_end = pie_with_others(comp, "End Value", top_n=top_n)
                if not pie_end.empty:
                    fig = px.pie(pie_end, names="Country", values="End Value", hole=0.35, title=f"{end_label} country share")
                    fig.update_traces(textinfo="percent+label")
                    fig.update_layout(template="plotly_white", height=430, margin=dict(l=10, r=10, t=40, b=10))
                    st.plotly_chart(fig, use_container_width=True)
        else:
            year_map = {2020: "fy2020", 2025: "fy2025"}
            years = sorted(year_map.keys())
            c1, c2 = st.columns(2)
            with c1:
                start_year = st.selectbox("Start year", years, format_func=fy_label_generic, key="imp_country_start_fallback")
            with c2:
                end_options = [y for y in years if y >= start_year]
                end_year = st.selectbox("End year", end_options, index=len(end_options)-1, format_func=fy_label_generic, key="imp_country_end_fallback")
            start_label = fy_label_generic(start_year)
            end_label = fy_label_generic(end_year)
            start_df = pd.DataFrame(DATA["top_import_countries"][year_map[start_year]]).rename(columns={"country": "Country", "amount_mn": f"{start_label} (US$ mn)", "share_pct": f"{start_label} % Share"})
            end_df = pd.DataFrame(DATA["top_import_countries"][year_map[end_year]]).rename(columns={"country": "Country", "amount_mn": f"{end_label} (US$ mn)", "share_pct": f"{end_label} % Share"})
            compare = start_df.merge(end_df, on="Country", how="outer")
            for col in [f"{start_label} (US$ mn)", f"{end_label} (US$ mn)", f"{start_label} % Share", f"{end_label} % Share"]:
                compare[col] = pd.to_numeric(compare[col], errors="coerce")
            compare["Change (US$ mn)"] = compare[f"{end_label} (US$ mn)"].fillna(0) - compare[f"{start_label} (US$ mn)"].fillna(0)
            compare["Growth (%)"] = np.where(compare[f"{start_label} (US$ mn)"].fillna(0) != 0, ((compare[f"{end_label} (US$ mn)"].fillna(0) / compare[f"{start_label} (US$ mn)"].fillna(0)) - 1) * 100, np.nan)
            compare = compare.sort_values(f"{end_label} (US$ mn)", ascending=False)
            render_table(compare, {f"{start_label} (US$ mn)": "{:,.2f}", f"{start_label} % Share": "{:,.2f}", f"{end_label} (US$ mn)": "{:,.2f}", f"{end_label} % Share": "{:,.2f}", "Change (US$ mn)": "{:+,.2f}", "Growth (%)": "{:+,.2f}"}, height=430)

    with tabs[3]:
        region_hist = load_entity_year_wide_workbook(
            "Regionwise (exports, imports, re-imports).xlsx",
            "Regionwise - Imports",
            "region",
        )
        if not region_hist.empty:
            years = sorted([c for c in region_hist.columns if isinstance(c, int)])
            default_start = 2020 if 2020 in years else years[0]
            default_end = 2025 if 2025 in years else years[-1]
            r1, r2 = st.columns(2)
            with r1:
                start_year = st.selectbox("Start year", years, index=years.index(default_start), format_func=fy_label_generic, key="imp_region_hist_start")
            with r2:
                end_options = [y for y in years if y >= start_year]
                end_year = st.selectbox("End year", end_options, index=end_options.index(default_end) if default_end in end_options else len(end_options)-1, format_func=fy_label_generic, key="imp_region_hist_end")
            comp = compare_country_product(region_hist.rename(columns={"region": "country"}), start_year, end_year).rename(columns={"Country": "Region"})
            start_label = fy_label_generic(start_year)
            end_label = fy_label_generic(end_year)
            render_table(
                comp[["Region", "Start Value", "End Value", "Start Share (%)", "End Share (%)", "Change (US$ mn)", "Growth (%)"]].rename(columns={
                    "Start Value": f"{start_label} (US$ mn)",
                    "End Value": f"{end_label} (US$ mn)",
                    "Start Share (%)": f"{start_label} % Share",
                    "End Share (%)": f"{end_label} % Share",
                }),
                {
                    f"{start_label} (US$ mn)": "{:,.2f}",
                    f"{end_label} (US$ mn)": "{:,.2f}",
                    f"{start_label} % Share": "{:,.2f}",
                    f"{end_label} % Share": "{:,.2f}",
                    "Change (US$ mn)": "{:+,.2f}",
                    "Growth (%)": "{:+,.2f}",
                },
                height=430,
            )
            fig = go.Figure()
            plot_df = comp.sort_values("End Value")
            fig.add_trace(go.Bar(y=plot_df["Region"], x=plot_df["Start Value"], orientation="h", name=start_label, marker_color="#d9ead3"))
            fig.add_trace(go.Bar(y=plot_df["Region"], x=plot_df["End Value"], orientation="h", name=end_label, marker_color="#7a1f5c"))
            fig.update_layout(barmode="group", template="plotly_white", height=430, margin=dict(l=10, r=10, t=10, b=10), xaxis_title="US$ mn", yaxis_title="")
            if show_labels:
                add_bar_labels(fig, "h", "{:,.0f}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            df = df_from("import_regions")
            region_years = [2020, 2025]
            r1, r2 = st.columns(2)
            with r1:
                start_year = st.selectbox("Start year", region_years, format_func=fy_label_generic, key="imp_region_start_fallback")
            with r2:
                end_options = [y for y in region_years if y >= start_year]
                end_year = st.selectbox("End year", end_options, index=len(end_options)-1, format_func=fy_label_generic, key="imp_region_end_fallback")
            start_label = fy_label_generic(start_year)
            end_label = fy_label_generic(end_year)
            year_to_cols = {2020: ("fy2020_mn", "fy2020_share_pct"), 2025: ("fy2025_mn", "fy2025_share_pct")}
            start_val_col, start_share_col = year_to_cols[start_year]
            end_val_col, end_share_col = year_to_cols[end_year]
            table = df.rename(columns={
                "region": "Region",
                start_val_col: f"{start_label} (US$ mn)",
                start_share_col: f"{start_label} % Share",
                end_val_col: f"{end_label} (US$ mn)",
                end_share_col: f"{end_label} % Share",
            })[["Region", f"{start_label} (US$ mn)", f"{end_label} (US$ mn)", f"{start_label} % Share", f"{end_label} % Share"]]
            render_table(table, {f"{start_label} (US$ mn)": "{:,.2f}", f"{end_label} (US$ mn)": "{:,.2f}", f"{start_label} % Share": "{:,.2f}", f"{end_label} % Share": "{:,.2f}"}, height=430)



def section_dta():
    hero(
        "3.14 DTA / SEZ",
        "India’s exports of gems and jewellery from DTA and SEZ, both recent two-year comparison and longer annual trend.",
        ["Recent view", "Long trend", "Shares in total exports"],
    )
    tabs = st.tabs(["3.14a FY2024-25 to FY2025-26", "3.14b Long Trend"])

    with tabs[0]:
        recent = df_from("dta_sez_recent").copy()
        recent["year_display"] = recent["year"].astype(str).map(span_from_single_year_label)
        table = recent.rename(columns={
            "year_display": "Year",
            "dta_mn": "DTA (US$ mn)",
            "sez_mn": "SEZ (US$ mn)",
            "total_mn": "Total Exports (US$ mn)",
            "dta_share_pct": "DTA % Share",
            "sez_share_pct": "SEZ % Share",
            "dta_growth_pct": "DTA Growth (%)",
            "sez_growth_pct": "SEZ Growth (%)",
        })
        render_table(
            table[["Year", "DTA (US$ mn)", "SEZ (US$ mn)", "Total Exports (US$ mn)", "DTA % Share", "SEZ % Share", "DTA Growth (%)", "SEZ Growth (%)"]],
            {
                "DTA (US$ mn)": "{:,.2f}",
                "SEZ (US$ mn)": "{:,.2f}",
                "Total Exports (US$ mn)": "{:,.2f}",
                "DTA % Share": "{:,.2f}",
                "SEZ % Share": "{:,.2f}",
                "DTA Growth (%)": "{:+,.2f}",
                "SEZ Growth (%)": "{:+,.2f}",
            },
            height=260,
        )
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=recent["year_display"], y=recent["dta_mn"], name="DTA", marker_color="#5a7d4d"))
            fig.add_trace(go.Bar(x=recent["year_display"], y=recent["sez_mn"], name="SEZ", marker_color="#7a1f5c"))
            fig.update_layout(barmode="group", template="plotly_white", height=360, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="US$ mn", xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            share_df = recent.melt(id_vars="year_display", value_vars=["dta_share_pct", "sez_share_pct"], var_name="series", value_name="share")
            share_df["series"] = share_df["series"].replace({"dta_share_pct": "DTA % Share", "sez_share_pct": "SEZ % Share"})
            fig2 = px.line(share_df, x="year_display", y="share", color="series", markers=True)
            fig2.update_layout(template="plotly_white", height=360, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Share in total exports (%)", xaxis_title="", legend_title_text="")
            if show_labels:
                add_line_labels(fig2, "{:,.2f}")
            st.plotly_chart(fig2, use_container_width=True)

    with tabs[1]:
        df = df_from("dta_sez_long").copy()
        df["year_display"] = df["year"].astype(str).map(span_from_single_year_label)
        render_table(df.rename(columns={
            "year_display":"Year",
            "dta_mn":"DTA (US$ mn)",
            "sez_mn":"SEZ (US$ mn)",
            "total_mn":"Total Exports (US$ mn)",
            "dta_share_pct":"DTA % share",
            "sez_share_pct":"SEZ % share",
        })[["Year","DTA (US$ mn)","SEZ (US$ mn)","Total Exports (US$ mn)","DTA % share","SEZ % share"]], {
            "DTA (US$ mn)":"{:,.2f}",
            "SEZ (US$ mn)":"{:,.2f}",
            "Total Exports (US$ mn)":"{:,.2f}",
            "DTA % share":"{:,.2f}",
            "SEZ % share":"{:,.2f}",
        }, height=460)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year_display"], y=df["dta_share_pct"], mode="lines+markers", name="DTA % share", line=dict(color="#5a7d4d", width=3)))
        fig.add_trace(go.Scatter(x=df["year_display"], y=df["sez_share_pct"], mode="lines+markers", name="SEZ % share", line=dict(color="#7a1f5c", width=3)))
        fig.update_layout(template="plotly_white", height=380, margin=dict(l=10,r=10,t=10,b=10), yaxis_title="Share in total exports (%)", xaxis_title="")
        if show_labels:
            add_line_labels(fig, "{:,.2f}")
        st.plotly_chart(fig, use_container_width=True)

def section_fdi():
    hero(
        "3.15 FDI Inflows",
        "FDI equity inflow in India versus the Gem & Jewellery sector, including sector growth and sector share in total FDI inflows.",
        ["FY2015 to FY2025", "Sector inflow", "Sector share"],
    )
    df = df_from("fdi")
    df["year_display"] = df["year"].astype(str).map(span_from_single_year_label)
    render_table(df.rename(columns={
        "year_display":"Year",
        "india_fdi_mn":"FDI Equity Inflows in India (US$ mn)",
        "gj_fdi_mn":"FDI Equity Inflows in G&J Sector (US$ mn)",
        "gj_growth_pct":"% Growth of FDI in G&J Sector",
        "gj_share_pct":"% Share of FDI Inflows in G&J Sector",
    }), {
        "FDI Equity Inflows in India (US$ mn)":"{:,.2f}",
        "FDI Equity Inflows in G&J Sector (US$ mn)":"{:,.2f}",
        "% Growth of FDI in G&J Sector":"{:+,.2f}",
        "% Share of FDI Inflows in G&J Sector":"{:,.3f}",
    }, height=430)

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["year_display"], y=df["gj_fdi_mn"], name="G&J sector FDI", marker_color="#7a1f5c"))
        fig.update_layout(template="plotly_white", height=360, margin=dict(l=10,r=10,t=10,b=10), yaxis_title="US$ mn", xaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df["year_display"], y=df["gj_share_pct"], mode="lines+markers", name="G&J share of India FDI", line=dict(color="#274e3d", width=3)))
        fig2.update_layout(template="plotly_white", height=360, margin=dict(l=10,r=10,t=10,b=10), yaxis_title="Share (%)", xaxis_title="")
        if show_labels:
            add_line_labels(fig2, "{:,.3f}")
        st.plotly_chart(fig2, use_container_width=True)

if page == "Overview":
    overview()
elif page == "3.1 Annual Trends":
    section_31()
elif page == "3.2 Gross vs Net Exports":
    section_32()
elif page == "3.3–3.4 Targets & Achievement":
    section_targets()
elif page == "3.5–3.9 Export Structure":
    section_exports()
elif page == "3.10–3.13 Import Structure":
    section_imports()
elif page == "Export Products":
    render_product_workbook_page("Export")
elif page == "Import Products":
    render_product_workbook_page("Import")
elif page == "3.14 DTA / SEZ":
    section_dta()
else:
    section_fdi()
