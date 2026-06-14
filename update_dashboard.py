import json, urllib.request

UID = "PBFA97CFB590B2093"
ds = {"type": "prometheus", "uid": UID}

dashboard = {
  "dashboard": {
    "title": "Green Cache Dashboard",
    "uid": "green-cache-main",
    "timezone": "browser",
    "refresh": "10s",
    "panels": [
      {"id":1,"title":"Cache Hit Rate","type":"gauge","gridPos":{"h":8,"w":6,"x":0,"y":0},"fieldConfig":{"defaults":{"min":0,"max":1,"thresholds":{"steps":[{"color":"red","value":0},{"color":"yellow","value":0.5},{"color":"green","value":0.8}]},"unit":"percentunit"}},"targets":[{"expr":'greencache_hit_rate{cache_backend="memory"}',"datasource":ds}],"datasource":ds},
      {"id":2,"title":"Total Requests","type":"stat","gridPos":{"h":4,"w":6,"x":6,"y":0},"fieldConfig":{"defaults":{"unit":"short"}},"targets":[{"expr":"sum(greencache_requests_total)","datasource":ds}],"datasource":ds},
      {"id":3,"title":"Water Saved (Liters)","type":"stat","gridPos":{"h":4,"w":6,"x":12,"y":0},"fieldConfig":{"defaults":{"unit":"short","decimals":6,"color":{"mode":"fixed","fixedColor":"blue"}}},"targets":[{"expr":"sum(greencache_water_saved_liters)","datasource":ds}],"datasource":ds},
      {"id":4,"title":"Energy Saved (Wh)","type":"stat","gridPos":{"h":4,"w":6,"x":18,"y":0},"fieldConfig":{"defaults":{"unit":"watth","color":{"mode":"fixed","fixedColor":"yellow"}}},"targets":[{"expr":"sum(greencache_energy_saved_wh_total)","datasource":ds}],"datasource":ds},
      {"id":5,"title":"Request Latency","type":"timeseries","gridPos":{"h":8,"w":12,"x":0,"y":8},"fieldConfig":{"defaults":{"unit":"s"}},"targets":[{"expr":"rate(greencache_request_latency_seconds_sum[1m])/rate(greencache_request_latency_seconds_count[1m])","legendFormat":"avg latency","datasource":ds}],"datasource":ds},
      {"id":6,"title":"Tokens Saved","type":"timeseries","gridPos":{"h":8,"w":12,"x":12,"y":8},"fieldConfig":{"defaults":{"unit":"short"}},"targets":[{"expr":"sum(greencache_tokens_saved_total)","legendFormat":"tokens saved","datasource":ds}],"datasource":ds},
      {"id":7,"title":"Cache Entries","type":"stat","gridPos":{"h":4,"w":6,"x":6,"y":4},"fieldConfig":{"defaults":{"unit":"short"}},"targets":[{"expr":'greencache_entries_count{cache_backend="memory"}',"datasource":ds}],"datasource":ds},
      {"id":8,"title":"Carbon Saved (g)","type":"stat","gridPos":{"h":4,"w":6,"x":12,"y":4},"fieldConfig":{"defaults":{"unit":"short","color":{"mode":"fixed","fixedColor":"green"}}},"targets":[{"expr":"sum(greencache_carbon_saved_g_total)","datasource":ds}],"datasource":ds}
    ],
    "schemaVersion": 38
  },
  "overwrite": True,
  "folderId": 0
}

data = json.dumps(dashboard).encode("utf-8")
req = urllib.request.Request("http://localhost:3000/api/dashboards/db", data=data, headers={"Content-Type": "application/json", "Authorization": "Basic YWRtaW46Z3JlZW5jYWNoZQ=="}, method="POST")
res = urllib.request.urlopen(req)
print("Updated!", res.read().decode())
