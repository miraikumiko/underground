#!/sbin/openrc-run

description="underground.pm"

name=$RC_SVCNAME

command="underground_run"
pidfile="/run/$name.pid"

depend() {
	need net
	need redis
}

start() {
	ebegin "Starting $name"
	start-stop-daemon -bm -S -u root:root -p $pidfile -x $command
	eend $?
}

stop() {
	ebegin "Stopping $name"
	start-stop-daemon -K -p $pidfile
	eend $?
}

restart() {
	stop
	sleep 1
	start
}
