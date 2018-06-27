import subprocess
from sys import version_info

cam_info = {}

def get_py_version():
	return int(version_info[0])
	
def run_shell_command(str_command):
	py_ver = get_py_version()
	
	if py_ver<3 :
		process1 = subprocess.Popen(str_command,shell=True,stdout=subprocess.PIPE,stderr = subprocess.PIPE)
		process1.wait()
		output, error = process1.communicate()
		output, error = str(output),str(error)
	
	else:
    	#changed Popen to run() on Python 3
    	# 2x slower than python 2. idk why. doesn't matter anyway, as time ~ 1 ms. lite.
		process1 = subprocess.run(str_command,shell=True,stdout=subprocess.PIPE,stderr = subprocess.PIPE)
		output, error = process1.stdout, process1.stderr
		output, error = str(output,encoding='utf-8'),str(error,encoding='utf-8')
	return output, error

def get_connected_video_devices_paths():
	command = "ls -a /dev/video*"
	output,error = run_shell_command(command)
	meh = output.strip('').split('\n')
	connected = []
	for i in meh:
		if(not len(i)==0):
		    connected.append(i)
	return connected

def get_v4l_name_from_dev_path(str_devpath):
    
    shell_command = "cat /sys/class/video4linux/"+str_devpath+"/name"
    
    out, error = run_shell_command(shell_command)
    return out.strip('\n')

if __name__=='__main__':
    cam_info = dict.fromkeys(get_connected_video_devices_paths())

    for cam_i in cam_info.keys():
        cam_path = cam_i.split('/')[-1]
        cam_name = get_v4l_name_from_dev_path(cam_path)
        cam_info.update( { cam_i : cam_name} )

    print(cam_info)
