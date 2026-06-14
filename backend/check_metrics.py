import urllib.request
r = urllib.request.urlopen("http://localhost:8000/api/v1/metrics")
content = r.read().decode()
lines = [l for l in content.split("\n") if "greencache_hit" in l or "greencache_entr" in l]
print("\n".join(lines))
