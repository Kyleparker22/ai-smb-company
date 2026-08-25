window.STORM_DEMO = {
  "generated": "2026-07-02",
  "state": "FL",
  "window_days": 8,
  "demo_mode": true,
  "totals": {
    "raw": 71,
    "verified": 51,
    "relevant": 12
  },
  "ai_stats": {
    "cleared": 11,
    "held": 1
  },
  "sources": [
    {
      "label": "NOAA Local Storm Reports",
      "tier": "free",
      "status": "live",
      "note": "NOAA ground truth \u2014 the insurance source of record (hail size, wind, tornado + county/lat-lon)"
    },
    {
      "label": "NOAA SPC (national)",
      "tier": "free",
      "status": "live",
      "note": "NOAA national compiled storm reports \u2014 corroboration"
    },
    {
      "label": "NWS Live Alerts",
      "tier": "free",
      "status": "live",
      "note": "official forecaster/radar warnings \u2014 the speed layer"
    },
    {
      "label": "Xweather",
      "tier": "premium",
      "status": "live",
      "note": "NOAA-verified live alerts API \u2014 Nick HAS a key; set XWEATHER_CLIENT_ID/SECRET in .env to turn on"
    },
    {
      "label": "HailTrace",
      "tier": "premium",
      "status": "live",
      "note": "hail-specific, radar-verified \u2014 one of Nick's three (needs API key)"
    },
    {
      "label": "Interactive Hail Maps",
      "tier": "premium",
      "status": "live",
      "note": "hail swath maps \u2014 one of Nick's three (needs access)"
    },
    {
      "label": "Predictive weather guidance",
      "tier": "premium",
      "status": "live",
      "note": "predictive sales-AI weather tool Nick uses \u2014 clarify which, then integrate"
    }
  ],
  "triggers": [
    {
      "key": "knock_all",
      "label": "Door-knock \u2014 all crews",
      "desc": "Big event \u2014 every crew to the area now."
    },
    {
      "key": "knock",
      "label": "Door-knock \u2014 area",
      "desc": "Send the area's crew to door-knock."
    },
    {
      "key": "monitor",
      "label": "Monitor \u2014 reports pending",
      "desc": "Waiting on more reports; hold for the go."
    }
  ],
  "storms": [
    {
      "county": "Osceola",
      "date": "2026-06-24",
      "confidence": "HIGH",
      "hazard": "HAIL to 1.25\" + WIND 60mph",
      "sources_list": [
        "HailTrace",
        "Interactive Hail Maps",
        "Xweather"
      ],
      "sources": "HailTrace + Interactive Hail Maps + Xweather",
      "lat": 28.29,
      "lon": -81.41,
      "trigger": "knock_all",
      "max_hail_in": 1.25,
      "max_wind_mph": 60,
      "avg_hail_in": null,
      "avg_wind_mph": null,
      "grade": "B",
      "tornado": false,
      "messages": {
        "knock_all": "\ud83d\udea8 VERIFIED: Osceola Co 06-24 \u2014 HAIL to 1.25\" + WIND 60mph (HIGH). Big one \u2014 all crews door-knock now, get there first. \u2014Nick",
        "knock": "VERIFIED storm: Osceola Co 06-24 \u2014 HAIL to 1.25\" + WIND 60mph (HIGH). Door-knock priority \u2014 beat everyone there. \u2014Nick",
        "monitor": "Watching Osceola Co 06-24 \u2014 HAIL to 1.25\" + WIND 60mph (HIGH). Reports still coming in \u2014 hold for the go. \u2014Nick"
      },
      "ai": {
        "verdict": "GO",
        "confidence": "HIGH",
        "claim_grade": true,
        "reason": "Cross-verified across sources; radar hail confirms the swath.",
        "flags": []
      }
    },
    {
      "county": "Sumter",
      "date": "2026-06-24",
      "confidence": "HIGH",
      "hazard": "HAIL to 1.25\" + WIND 59mph",
      "sources_list": [
        "HailTrace",
        "Interactive Hail Maps",
        "Xweather"
      ],
      "sources": "HailTrace + Interactive Hail Maps + Xweather",
      "lat": 28.85,
      "lon": -82.05,
      "trigger": "knock_all",
      "max_hail_in": 1.25,
      "max_wind_mph": 59,
      "avg_hail_in": null,
      "avg_wind_mph": null,
      "grade": "B",
      "tornado": false,
      "messages": {
        "knock_all": "\ud83d\udea8 VERIFIED: Sumter Co 06-24 \u2014 HAIL to 1.25\" + WIND 59mph (HIGH). Big one \u2014 all crews door-knock now, get there first. \u2014Nick",
        "knock": "VERIFIED storm: Sumter Co 06-24 \u2014 HAIL to 1.25\" + WIND 59mph (HIGH). Door-knock priority \u2014 beat everyone there. \u2014Nick",
        "monitor": "Watching Sumter Co 06-24 \u2014 HAIL to 1.25\" + WIND 59mph (HIGH). Reports still coming in \u2014 hold for the go. \u2014Nick"
      },
      "ai": {
        "verdict": "GO",
        "confidence": "HIGH",
        "claim_grade": true,
        "reason": "Cross-verified across sources; radar hail confirms the swath.",
        "flags": []
      }
    },
    {
      "county": "Flagler",
      "date": "2026-06-26",
      "confidence": "HIGH",
      "hazard": "HAIL to 1.25\"",
      "sources_list": [
        "HailTrace",
        "Interactive Hail Maps"
      ],
      "sources": "HailTrace + Interactive Hail Maps",
      "lat": 29.47,
      "lon": -81.26,
      "trigger": "knock_all",
      "max_hail_in": 1.25,
      "max_wind_mph": null,
      "avg_hail_in": null,
      "avg_wind_mph": null,
      "grade": "B",
      "tornado": false,
      "messages": {
        "knock_all": "\ud83d\udea8 VERIFIED: Flagler Co 06-26 \u2014 HAIL to 1.25\" (HIGH). Big one \u2014 all crews door-knock now, get there first. \u2014Nick",
        "knock": "VERIFIED storm: Flagler Co 06-26 \u2014 HAIL to 1.25\" (HIGH). Door-knock priority \u2014 beat everyone there. \u2014Nick",
        "monitor": "Watching Flagler Co 06-26 \u2014 HAIL to 1.25\" (HIGH). Reports still coming in \u2014 hold for the go. \u2014Nick"
      },
      "ai": {
        "verdict": "GO",
        "confidence": "HIGH",
        "claim_grade": true,
        "reason": "Cross-verified across sources; radar hail confirms the swath.",
        "flags": []
      }
    },
    {
      "county": "Lee",
      "date": "2026-06-28",
      "confidence": "HIGH",
      "hazard": "TORNADO",
      "sources_list": [
        "NOAA LSR",
        "NOAA SPC",
        "Xweather"
      ],
      "sources": "NOAA LSR + NOAA SPC + Xweather",
      "lat": 26.7,
      "lon": -81.91,
      "trigger": "knock_all",
      "max_hail_in": null,
      "max_wind_mph": null,
      "avg_hail_in": null,
      "avg_wind_mph": null,
      "grade": "A",
      "tornado": true,
      "messages": {
        "knock_all": "\ud83d\udea8 VERIFIED: Lee Co 06-28 \u2014 TORNADO (HIGH). Big one \u2014 all crews door-knock now, get there first. \u2014Nick",
        "knock": "VERIFIED storm: Lee Co 06-28 \u2014 TORNADO (HIGH). Door-knock priority \u2014 beat everyone there. \u2014Nick",
        "monitor": "Watching Lee Co 06-28 \u2014 TORNADO (HIGH). Reports still coming in \u2014 hold for the go. \u2014Nick"
      },
      "ai": {
        "verdict": "GO",
        "confidence": "HIGH",
        "claim_grade": true,
        "reason": "Cross-verified across sources; radar hail confirms the swath.",
        "flags": []
      }
    },
    {
      "county": "Calhoun",
      "date": "2026-06-30",
      "confidence": "HIGH",
      "hazard": "HAIL to 1.00\" (avg 0.62\") + WIND 69mph",
      "sources_list": [
        "NOAA LSR",
        "NOAA SPC",
        "Xweather",
        "HailTrace",
        "Interactive Hail Maps"
      ],
      "sources": "NOAA LSR + NOAA SPC + Xweather + HailTrace + Interactive Hail Maps",
      "lat": 30.5,
      "lon": -85.11,
      "trigger": "knock",
      "max_hail_in": 1.0,
      "max_wind_mph": 69.0,
      "avg_hail_in": 0.62,
      "avg_wind_mph": 69,
      "grade": "B",
      "tornado": false,
      "messages": {
        "knock_all": "\ud83d\udea8 VERIFIED: Calhoun Co 06-30 \u2014 HAIL to 1.00\" (avg 0.62\") + WIND 69mph (HIGH). Big one \u2014 all crews door-knock now, get there first. \u2014Nick",
        "knock": "VERIFIED storm: Calhoun Co 06-30 \u2014 HAIL to 1.00\" (avg 0.62\") + WIND 69mph (HIGH). Door-knock priority \u2014 beat everyone there. \u2014Nick",
        "monitor": "Watching Calhoun Co 06-30 \u2014 HAIL to 1.00\" (avg 0.62\") + WIND 69mph (HIGH). Reports still coming in \u2014 hold for the go. \u2014Nick"
      },
      "ai": {
        "verdict": "GO",
        "confidence": "HIGH",
        "claim_grade": true,
        "reason": "Wind is measured ASOS 69mph + 911 downed trees. (Hail 1\u2033 is a lone estimate \u2014 dispatch for wind.)",
        "flags": [
          "hail 1\u2033 is a single estimated media report"
        ]
      }
    },
    {
      "county": "Hillsborough",
      "date": "2026-06-27",
      "confidence": "HIGH",
      "hazard": "HAIL to 0.88\" + WIND 40mph",
      "sources_list": [
        "NOAA LSR",
        "Xweather",
        "HailTrace",
        "Interactive Hail Maps"
      ],
      "sources": "NOAA LSR + Xweather + HailTrace + Interactive Hail Maps",
      "lat": 27.84,
      "lon": -82.19,
      "trigger": "knock",
      "max_hail_in": 0.88,
      "max_wind_mph": 40.0,
      "avg_hail_in": 0.88,
      "avg_wind_mph": 40,
      "grade": "C",
      "tornado": false,
      "messages": {
        "knock_all": "\ud83d\udea8 VERIFIED: Hillsborough Co 06-27 \u2014 HAIL to 0.88\" + WIND 40mph (HIGH). Big one \u2014 all crews door-knock now, get there first. \u2014Nick",
        "knock": "VERIFIED storm: Hillsborough Co 06-27 \u2014 HAIL to 0.88\" + WIND 40mph (HIGH). Door-knock priority \u2014 beat everyone there. \u2014Nick",
        "monitor": "Watching Hillsborough Co 06-27 \u2014 HAIL to 0.88\" + WIND 40mph (HIGH). Reports still coming in \u2014 hold for the go. \u2014Nick"
      },
      "ai": {
        "verdict": "GO",
        "confidence": "MEDIUM",
        "claim_grade": true,
        "reason": "Cross-verified across sources.",
        "flags": []
      }
    },
    {
      "county": "Pasco",
      "date": "2026-06-26",
      "confidence": "HIGH",
      "hazard": "HAIL to 0.75\"",
      "sources_list": [
        "HailTrace",
        "Xweather"
      ],
      "sources": "HailTrace + Xweather",
      "lat": 28.24,
      "lon": -82.33,
      "trigger": "knock",
      "max_hail_in": 0.75,
      "max_wind_mph": null,
      "avg_hail_in": null,
      "avg_wind_mph": null,
      "grade": "C",
      "tornado": false,
      "messages": {
        "knock_all": "\ud83d\udea8 VERIFIED: Pasco Co 06-26 \u2014 HAIL to 0.75\" (HIGH). Big one \u2014 all crews door-knock now, get there first. \u2014Nick",
        "knock": "VERIFIED storm: Pasco Co 06-26 \u2014 HAIL to 0.75\" (HIGH). Door-knock priority \u2014 beat everyone there. \u2014Nick",
        "monitor": "Watching Pasco Co 06-26 \u2014 HAIL to 0.75\" (HIGH). Reports still coming in \u2014 hold for the go. \u2014Nick"
      },
      "ai": {
        "verdict": "GO",
        "confidence": "MEDIUM",
        "claim_grade": true,
        "reason": "Cross-verified across sources.",
        "flags": []
      }
    },
    {
      "county": "Brevard",
      "date": "2026-06-24",
      "confidence": "HIGH",
      "hazard": "WIND 55mph (avg 50)",
      "sources_list": [
        "NOAA LSR",
        "Xweather"
      ],
      "sources": "NOAA LSR + Xweather",
      "lat": 27.96,
      "lon": -80.56,
      "trigger": "knock",
      "max_hail_in": null,
      "max_wind_mph": 55.0,
      "avg_hail_in": null,
      "avg_wind_mph": 50,
      "grade": "C",
      "tornado": false,
      "messages": {
        "knock_all": "\ud83d\udea8 VERIFIED: Brevard Co 06-24 \u2014 WIND 55mph (avg 50) (HIGH). Big one \u2014 all crews door-knock now, get there first. \u2014Nick",
        "knock": "VERIFIED storm: Brevard Co 06-24 \u2014 WIND 55mph (avg 50) (HIGH). Door-knock priority \u2014 beat everyone there. \u2014Nick",
        "monitor": "Watching Brevard Co 06-24 \u2014 WIND 55mph (avg 50) (HIGH). Reports still coming in \u2014 hold for the go. \u2014Nick"
      },
      "ai": {
        "verdict": "GO",
        "confidence": "MEDIUM",
        "claim_grade": true,
        "reason": "Cross-verified across sources.",
        "flags": []
      }
    },
    {
      "county": "Marion",
      "date": "2026-06-24",
      "confidence": "MEDIUM",
      "hazard": "WIND 59mph",
      "sources_list": [
        "NOAA LSR",
        "Xweather"
      ],
      "sources": "NOAA LSR + Xweather",
      "lat": 29.17,
      "lon": -82.22,
      "trigger": "monitor",
      "max_hail_in": null,
      "max_wind_mph": 59.0,
      "avg_hail_in": null,
      "avg_wind_mph": 59,
      "grade": "C",
      "tornado": false,
      "messages": {
        "knock_all": "\ud83d\udea8 VERIFIED: Marion Co 06-24 \u2014 WIND 59mph (MEDIUM). Big one \u2014 all crews door-knock now, get there first. \u2014Nick",
        "knock": "VERIFIED storm: Marion Co 06-24 \u2014 WIND 59mph (MEDIUM). Door-knock priority \u2014 beat everyone there. \u2014Nick",
        "monitor": "Watching Marion Co 06-24 \u2014 WIND 59mph (MEDIUM). Reports still coming in \u2014 hold for the go. \u2014Nick"
      },
      "ai": {
        "verdict": "GO",
        "confidence": "MEDIUM",
        "claim_grade": true,
        "reason": "Cross-verified across sources.",
        "flags": []
      }
    },
    {
      "county": "St. Lucie",
      "date": "2026-06-24",
      "confidence": "MEDIUM",
      "hazard": "WIND 58mph",
      "sources_list": [
        "NOAA LSR",
        "Xweather"
      ],
      "sources": "NOAA LSR + Xweather",
      "lat": 27.45,
      "lon": -80.67,
      "trigger": "monitor",
      "max_hail_in": null,
      "max_wind_mph": 58.0,
      "avg_hail_in": null,
      "avg_wind_mph": 58,
      "grade": "C",
      "tornado": false,
      "messages": {
        "knock_all": "\ud83d\udea8 VERIFIED: St. Lucie Co 06-24 \u2014 WIND 58mph (MEDIUM). Big one \u2014 all crews door-knock now, get there first. \u2014Nick",
        "knock": "VERIFIED storm: St. Lucie Co 06-24 \u2014 WIND 58mph (MEDIUM). Door-knock priority \u2014 beat everyone there. \u2014Nick",
        "monitor": "Watching St. Lucie Co 06-24 \u2014 WIND 58mph (MEDIUM). Reports still coming in \u2014 hold for the go. \u2014Nick"
      },
      "ai": {
        "verdict": "GO",
        "confidence": "MEDIUM",
        "claim_grade": true,
        "reason": "Cross-verified across sources.",
        "flags": []
      }
    },
    {
      "county": "Martin",
      "date": "2026-06-24",
      "confidence": "MEDIUM",
      "hazard": "WIND 56mph",
      "sources_list": [
        "NOAA LSR",
        "Xweather"
      ],
      "sources": "NOAA LSR + Xweather",
      "lat": 27.12,
      "lon": -80.43,
      "trigger": "monitor",
      "max_hail_in": null,
      "max_wind_mph": 56.0,
      "avg_hail_in": null,
      "avg_wind_mph": 56,
      "grade": "C",
      "tornado": false,
      "messages": {
        "knock_all": "\ud83d\udea8 VERIFIED: Martin Co 06-24 \u2014 WIND 56mph (MEDIUM). Big one \u2014 all crews door-knock now, get there first. \u2014Nick",
        "knock": "VERIFIED storm: Martin Co 06-24 \u2014 WIND 56mph (MEDIUM). Door-knock priority \u2014 beat everyone there. \u2014Nick",
        "monitor": "Watching Martin Co 06-24 \u2014 WIND 56mph (MEDIUM). Reports still coming in \u2014 hold for the go. \u2014Nick"
      },
      "ai": {
        "verdict": "GO",
        "confidence": "MEDIUM",
        "claim_grade": true,
        "reason": "Cross-verified across sources.",
        "flags": []
      }
    },
    {
      "county": "Palm Beach",
      "date": "2026-06-24",
      "confidence": "HIGH",
      "hazard": "HAIL to 1.00\" + WIND damage",
      "sources_list": [
        "NOAA LSR",
        "Xweather",
        "HailTrace",
        "Interactive Hail Maps"
      ],
      "sources": "NOAA LSR + Xweather + HailTrace + Interactive Hail Maps",
      "lat": 26.68,
      "lon": -80.21,
      "trigger": "knock",
      "max_hail_in": 1.0,
      "max_wind_mph": null,
      "avg_hail_in": 1.0,
      "avg_wind_mph": null,
      "grade": "B",
      "tornado": false,
      "messages": {
        "knock_all": "\ud83d\udea8 VERIFIED: Palm Beach Co 06-24 \u2014 HAIL to 1.00\" + WIND damage (HIGH). Big one \u2014 all crews door-knock now, get there first. \u2014Nick",
        "knock": "VERIFIED storm: Palm Beach Co 06-24 \u2014 HAIL to 1.00\" + WIND damage (HIGH). Door-knock priority \u2014 beat everyone there. \u2014Nick",
        "monitor": "Watching Palm Beach Co 06-24 \u2014 HAIL to 1.00\" + WIND damage (HIGH). Reports still coming in \u2014 hold for the go. \u2014Nick"
      },
      "ai": {
        "verdict": "REJECT",
        "confidence": "LOW",
        "claim_grade": false,
        "reason": "Only hail report is a single public \u201cpea to quarter size\u201d estimate \u2014 the 1\u2033 flag overstates it. Not worth a crew.",
        "flags": [
          "single unverified public report",
          "remark says pea-to-quarter, not 1\u2033"
        ]
      }
    }
  ]
};
