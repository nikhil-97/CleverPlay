import camera_manager
import data_manager
import roi_controller
import web_postman


class ExecutionController(object):
    # ExecutionController class is responsible for controlling everything related to execution. It's the CEO of the program.
    # .start() starts the execution

    def __init__(self):
        pass

    def start(self):
        ca = camera_manager.CameraManager()
        data_mgr = data_manager.DataManager()
        shared_data_pool = None

        videoframes_list = ca.get_video_frames_list()

        r_ctrlr_0 = roi_controller.RoiController()
        videoframes_list[0].attach_roi_controller(r_ctrlr_0)
        r_ctrlr_0.attach_video_processors_to_rois()
        v0 = None
        data_mgr.register_video_processor(v0)
        data_mgr.set_shared_data_pool(shared_data_pool)

        postman = web_postman.WebPostman()
        postman.set_server_url('www.findmysport.in/tennisfinal.php')
        postman.set_shared_data_pool(shared_data_pool)
        postman.startRun()

    def stop(self):
        pass


if __name__ == '__main__':
    controller = ExecutionController()
    controller.start()
