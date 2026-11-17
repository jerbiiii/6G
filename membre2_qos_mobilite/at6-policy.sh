#!/bin/bash
# Usage : at6-policy.sh clear|static|show
EMBB_RATE=${EMBB_RATE:-100mbit}
MMTC_RATE=${MMTC_RATE:-5mbit}
clear_all() {
  for ns in ue1 ue2 ue3; do
    sudo ip netns exec $ns tc qdisc del dev uesimtun0 root 2>/dev/null
  done
}
case "$1" in
  clear) clear_all ;;
  static)
    clear_all
    sudo ip netns exec ue1 tc qdisc add dev uesimtun0 root tbf rate $EMBB_RATE burst 256kb latency 50ms
    sudo ip netns exec ue2 tc qdisc add dev uesimtun0 root tbf rate $MMTC_RATE burst 32kb latency 50ms
    ;;
  show)
    for ns in ue1 ue2 ue3; do
      echo "== $ns =="; sudo ip netns exec $ns tc qdisc show dev uesimtun0
    done ;;
  *) echo "usage: $0 clear|static|show"; exit 1 ;;
esac
