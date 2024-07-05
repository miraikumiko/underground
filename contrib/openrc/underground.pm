#!/sbin/openrc-run

description="underground.pm BE"

name=$RC_SVCNAME

command="/var/www/$name/venv/bin/python /var/www/$name/run.py"
pidfile="/run/$name.pid"

depend() {
	need net
	need postgresql
	need redis
}

start() {
	ebegin "Starting $name"
	cd /var/www/$name
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
