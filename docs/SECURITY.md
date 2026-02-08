# Security & Vulnerability Considerations (Simulation-Based IIoT)

Even in a simulation, documenting security is important because the **same architecture** would later connect
to real OT/IT networks. This file gives concrete items you can reference in the report Section 6.

## 1) Key trust boundaries (documented)
- Simulated OT devices → gateway/edge process
- OT/Edge → OT-DMZ (MQTT broker boundary)
- OT-DMZ → IT analytics (DB + dashboards)
- User endpoints → management interfaces (InfluxDB/Grafana)

## 2) High-impact vulnerabilities (what is risky and why)

### MQTT messaging layer
**Risk:** broker allows anonymous publish/subscribe (default in this repo for demo).  
**Impact:** data spoofing, data poisoning, unauthorized topic reads, DoS.  
**Mitigation (implementation steps):**
1) Enable username/password + topic ACLs
2) Prefer mTLS for clients (cert-based identity)
3) Rate-limit or monitor auth failures

### Time-series DB (InfluxDB)
**Risk:** weak credentials / exposed port / token leaks.  
**Impact:** KPI manipulation, data deletion, leakage of operational patterns.  
**Mitigation:**
- strong password + long token in `.env` (do not commit)
- bind ports only to localhost when possible
- least-privilege tokens (write-only for ingestion, read-only for analytics)

### Dashboard (Grafana)
**Risk:** default admin/admin, over-privileged dashboards, public sharing.  
**Impact:** misleading KPIs, data exfiltration.  
**Mitigation:**
- change admin password immediately
- configure RBAC and per-folder permissions
- disable anonymous access

### Supply chain / dependencies
**Risk:** vulnerable Python packages or container images.  
**Impact:** compromise of host, data theft.  
**Mitigation:**
- pin dependencies (requirements.txt)
- run `pip-audit` or `safety` (optional for assignment)
- update container images periodically

### Data quality attacks (simulation still relevant)
**Risk:** attacker injects biased sensor values; ML baseline drifts.  
**Impact:** false alarms, missed inefficiency, unsafe decisions.  
**Mitigation:**
- range checks and schema validation at ingestion
- store raw + derived features separately (traceability)
- anomaly rules + human-in-the-loop review

## 3) Optional hardening for MQTT (fast demo steps)
If you want to show “mitigation started”, do this later:

1) Create password file (inside container):
```bash
docker exec -it steelplant_mosquitto sh
mosquitto_passwd -c /mosquitto/config/passwordfile twinuser
# enter password
exit
```

2) Replace `docker/mosquitto/mosquitto.conf` with:
- `allow_anonymous false`
- `password_file /mosquitto/config/passwordfile`
- (optional) `acl_file /mosquitto/config/aclfile`

3) Restart:
```bash
docker compose restart mosquitto
```

Then update python scripts to use username/password.

