#start tank-api
tank-control api start /etc/tank/tank-api.conf --pid-file=../run/tank/tank-api.pid

#start tank-registry
tank-control registry start /etc/tank/tank-registry.conf --pid-file=../run/tank/tank-registry.pid


