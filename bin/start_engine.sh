/etc/init.d/libvirt-bin restart
engine-api restart &
engine-compute restart --instances_path=../engine/instances &
engine-volume restart &
engine-network restart &
engine-scheduler restart &
engine-objectstore restart &
