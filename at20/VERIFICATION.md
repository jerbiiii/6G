# VERIFICATION ANTI-HALLUCINATION - ATELIER 20 (DIGITAL TWIN 6G)

Ce document consigne les preuves formelles d'exécution et de validation du Digital Twin Intelligent sur le testbed réel AWS EC2.

---

## 1. Preuve des adresses IP et interfaces réseau réelles

Source de vérité : `ip.txt`
- `6g` : `172.31.41.25` / `16.171.171.2`
- `vmcp` : `172.31.47.81` / `13.48.43.145`
- `vmran` : `172.31.34.222` / `13.61.175.249`
- `vmupf` : `172.31.38.166` / `16.171.162.162`

### Commande de vérification sur `vmran` :
```bash
ip -br a | grep -E 'enp|uesimtun'
```
**Sortie constatée :**
```text
enp39s0          UP             172.31.34.222/20 metric 100 fe80::8ff:e6ff:fe70:713b/64 
uesimtun0        UNKNOWN        10.45.0.3/24 fe80::caa6:b2f0:4:be17/64 
```

### Commande de vérification sur `vmupf` :
```bash
ip -br a | grep -E 'enp|ogstun'
```
**Sortie constatée :**
```text
enp39s0          UP             172.31.38.166/20 metric 100 fe80::8ff:ceff:feb4:96cd/64 
ogstun           UP             10.45.0.1/16 2001:db8:cafe::1/48 fe80::5c7b:b6af:4778:c46b/64 
```

---

## 2. Évolution temporelle dynamique de `metrics.csv`

### Commande de contrôle :
```bash
tail -n 5 /home/ubuntu/at20/data/metrics.csv | cut -d',' -f1,2,3,4,15,18,21,24
```
**Sortie constatée :**
```text
1795102111.15,2026-11-19T15:28:31.146075Z,591.7,1.366,129,1864,767,REAL
1795102116.15,2026-11-19T15:28:36.146177Z,570.0,1.8,129,1864,767,REAL
1795102121.15,2026-11-19T15:28:41.146306Z,584.7,1.506,116,1935,777,REAL
1795102126.15,2026-11-19T15:28:46.146394Z,542.65,2.347,116,1935,777,REAL
1795102131.15,2026-11-19T15:28:51.146501Z,542.6,2.348,116,1935,777,REAL
```
*Constat : Le timestamp évolue de 5s en 5s, les débits varient entre 542 et 591 Mbps, les latences entre 1.36 et 2.35 ms, prouvant l'absence de valeurs figées.*

---

## 3. Absence de valeurs simulées ou codées en dur

### Commande de recherche (grep) :
```bash
grep -E 'rtt_avg = [0-9]|latency_ms = [0-9]|loss_pct = [0-9]' /home/ubuntu/at20/collector.py
```
**Sortie constatée :**
*Aucune constante suspecte.* Toutes les mesures proviennent du parsing dynamique des commandes `ping`, `iperf3` et `kubectl top`.

---

## 4. Exécution réelle des 4 scénarios What-If (`comparison.csv`)

### Sortie réelle de `data/comparison.csv` :
```csv
scenario_id,scenario_desc,pred_latency_ms,meas_latency_ms,mape_latency_pct,pred_throughput_mbps,meas_throughput_mbps,mape_throughput_pct,pred_cpu_pct,meas_cpu_pct,mape_cpu_pct,pred_loss_pct,meas_loss_pct,diff_loss_abs,meas_duration_s,sla_violated_pred,sla_violated_meas,data_origin
S1_eMBB_Burst,Explosion de trafic eMBB (+250 Mbps),1.383,1.953,29.19,775.0,680.0,13.97,69.2,65.0,6.46,0.3,0.0,0.3,6.4,False,False,REAL_MEASURED_VS_PREDICTED
S2_URLLC_Critical,Charge critique URLLC (80 Mbps),2.656,1.605,65.48,490.0,490.0,0.0,49.3,45.0,9.56,0.0,0.0,0.0,6.0,False,False,REAL_MEASURED_VS_PREDICTED
S3_gNB_Failure,Panne du gNB-B et ré-aiguillage des UE,6.035,6.08,0.74,325.0,310.0,4.84,37.8,27.0,40.0,0.0,0.0,0.0,10.0,True,False,REAL_MEASURED_VS_PREDICTED
S4_UPF_CPU_Limit,Réduction du CPU alloué à l'UPF (35%),97.696,30.99,215.25,350.0,360.0,2.78,100.0,95.0,5.26,6.67,4.8,1.87,4.3,True,True,REAL_MEASURED_VS_PREDICTED
```

- **MAPE Débit Global** : 5.40 % (RMSE : 48.35 Mbps)
- **MAPE Latence Globale** : 77.66 % (RMSE : 33.358 ms, dominé par le pic de saturation du scénario S4).

---

## 5. Données de mobilité étiquetées explicitement comme générées

### Commande de contrôle :
```bash
head -n 5 /home/ubuntu/at20/data/mobility.csv
```
**Sortie constatée :**
```text
timestamp,ue_id,x_pos,y_pos,speed_kmh,serving_cell,target_cell,rsrp_dbm,sinr_db,data_origin
1795101911.7,ue-01,10.50,20.30,35,gnb-a,none,-85.4,18.2,GENERATED
1795101911.7,ue-02,21.00,40.60,40,gnb-a,none,-85.4,18.2,GENERATED
1795101911.7,ue-03,31.50,60.90,45,gnb-a,none,-85.4,18.2,GENERATED
```

---

## 6. Rétablissement strict de l'état nominal du réseau

### Commande de test après exécution :
```bash
ssh -i ~/.ssh/6g-team-key.pem ubuntu@172.31.34.222 "ping -c 2 -I uesimtun0 10.45.0.1"
```
**Sortie constatée :**
```text
PING 10.45.0.1 (10.45.0.1) from 10.45.0.3 uesimtun0: 56(84) bytes of data.
64 bytes from 10.45.0.1: icmp_seq=1 ttl=64 time=2.29 ms
64 bytes from 10.45.0.1: icmp_seq=2 ttl=64 time=2.38 ms

--- 10.45.0.1 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 2.292/2.336/2.381/0.044 ms
```
*Le tunnel UE -> UPF fonctionne parfaitement sans dégradation ni résidu de charge.*
