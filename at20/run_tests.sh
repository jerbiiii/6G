echo '=== AT20 RESULTS CAPTURE ===' > /home/ubuntu/at20/captures/at20_results.txt
echo '1. GET /api/v1/twin/state' >> /home/ubuntu/at20/captures/at20_results.txt
curl -s http://localhost:8090/api/v1/twin/state >> /home/ubuntu/at20/captures/at20_results.txt
echo '' >> /home/ubuntu/at20/captures/at20_results.txt

echo '2. POST /api/v1/twin/simulate (traffic_surge embb +250)' >> /home/ubuntu/at20/captures/at20_results.txt
curl -s -X POST http://localhost:8090/api/v1/twin/simulate -H 'Content-Type: application/json' -d '{"scenario":"traffic_surge","slice":"embb","load_mbps":250}' >> /home/ubuntu/at20/captures/at20_results.txt
echo '' >> /home/ubuntu/at20/captures/at20_results.txt

echo '3. POST /api/v1/twin/simulate (cell_failure gNB-2)' >> /home/ubuntu/at20/captures/at20_results.txt
curl -s -X POST http://localhost:8090/api/v1/twin/simulate -H 'Content-Type: application/json' -d '{"scenario":"cell_failure","slice":"urllc","load_mbps":85}' >> /home/ubuntu/at20/captures/at20_results.txt
echo '' >> /home/ubuntu/at20/captures/at20_results.txt

echo '4. POST /api/v1/twin/simulate (mass_ue 100 UEs)' >> /home/ubuntu/at20/captures/at20_results.txt
curl -s -X POST http://localhost:8090/api/v1/twin/simulate -H 'Content-Type: application/json' -d '{"scenario":"mass_ue","slice":"mmtc","load_mbps":100}' >> /home/ubuntu/at20/captures/at20_results.txt
echo '' >> /home/ubuntu/at20/captures/at20_results.txt

echo '5. GET /api/v1/twin/compare' >> /home/ubuntu/at20/captures/at20_results.txt
curl -s http://localhost:8090/api/v1/twin/compare >> /home/ubuntu/at20/captures/at20_results.txt
echo '' >> /home/ubuntu/at20/captures/at20_results.txt

cat /home/ubuntu/at20/captures/at20_results.txt
