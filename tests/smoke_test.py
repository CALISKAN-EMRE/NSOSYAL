import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"


def execute_live_check(name, path, method="GET", body=None):
    url = BASE_URL + path
    headers = {"Content-Type": "application/json"}
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            res_json = json.loads(resp.read().decode("utf-8"))
            print(f"[SUCCESS] {name} | {method} {path} -> HTTP {status}")
            if isinstance(res_json, list):
                print(f"  Returned {len(res_json)} items. First item summary: id={res_json[0].get('id', 'N/A')}")
            elif isinstance(res_json, dict):
                print(f"  Response keys: {list(res_json.keys())}")
                if "status" in res_json:
                    print(f"  Status: {res_json.get('status')}")
                if "risk_vector" in res_json:
                    rv = res_json["risk_vector"]
                    print(f"  Risk Level: {rv.get('risk_level')}, Score: {rv.get('overall_risk_score')}, Signals: {len(rv.get('signals', []))}")
                if "final_score" in res_json:
                    print(f"  Final Score: {res_json.get('final_score')}, Reason: {res_json.get('summary_reason')}")
            return status, res_json
    except urllib.error.HTTPError as e:
        status = e.code
        err_body = e.read().decode("utf-8")
        print(f"[EXPECTED HTTP {status}] {name} | {method} {path} -> HTTP {status}: {err_body}")
        return status, err_body
    except Exception as e:
        print(f"[FAILED] {name} | {method} {path} -> Error: {e}")
        return 0, str(e)


if __name__ == "__main__":
    print("==================================================")
    print("  NSOSYAL PUSULA - LIVE HTTP RUNTIME SMOKE TESTS  ")
    print("==================================================")
    execute_live_check("1. Health Check", "/health")
    execute_live_check("2. List Posts", "/api/posts")
    execute_live_check("3. List Topics", "/api/topics")
    execute_live_check("4. Valid Context Card", "/api/context/yapay-zeka-egitim")
    execute_live_check("5. Invalid Context Card (Expect 404)", "/api/context/nonexistent-topic-999")
    execute_live_check("6. Safety Analysis (Spam & Upper)", "/api/safety/analyze", method="POST", body={"text": "BEDAVA KAZANÇ FIRSATI!!! HEMEN TIKLA: http://bit.ly/spam123 http://link.xyz BEDAVA!!!"})
    execute_live_check("7. Safety Analysis (Clean Text)", "/api/safety/analyze", method="POST", body={"text": "Yapay zekâ ve eğitim teknolojileri üzerine yeni bir araştırma yayınlandı."})
    execute_live_check("8. Recommendations Feed", "/api/recommendations")
    execute_live_check("9. Explain Recommendation", "/api/recommendations/explain/post-001")
    print("==================================================")
