import psutil
import datetime


def get_time():
	return datetime.datetime.now().strftime('%H%M')


def if_in_rest(time, rest):
	for r in rest:
		if r[0] <= time < r[1]:
			return True
	return False


def get_processes():
	processes: dict[str, list[int]] = {}
	# with open('./processes.txt', 'w') as f:
	for p in psutil.process_iter(['name', 'pid']):
		# f.write((str(p)) + '\n')
		if p.name() in processes.keys():
			processes[p.name()].append(p.pid)
		else:
			processes[p.name()] = [p.pid]
	
	return processes


def limit_processes(processes, app):
	if app in processes.keys():
		for pid in processes[app]:
			psutil.Process(pid).kill()
		return True
	return False


def find_app():
	pid = input('PIDs use comma separated: ')
	pids = pid.split(',')
	pids = [int(p) for p in pids]
	
	processes = get_processes()
	res = []
	for p in pids:
		for app in processes.keys():
			if int(p) in processes[app]:
				res.append(app)
	print(str(res))

if __name__ == '__main__':
	find_app()