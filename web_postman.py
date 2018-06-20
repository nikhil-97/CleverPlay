import threading

import logging
import requests
import time


class WebPostman:

    POST_TO_SERVER_DELAY = 60

    def __init__(self):
        self.server_url = 'hardcodedstringsarebad.com'
        self.web_postman_thread = threading.Thread(name="WebPostmanThread",target=self.run)
        self._shared_data = None
        self._thread_running = True

    def get_running_thread(self):
        return self.web_postman_thread

    def set_post_to_server_delay(self,int_delay):
        self.POST_TO_SERVER_DELAY = int_delay

    def set_server_url(self,string_url):
        self.server_url = string_url

    def set_shared_data_pool(self,shared_data_pool):
        self._shared_data = shared_data_pool

    def data_sweep(self,datapool):
        pass
        # Ensure synchronous sweep of data, i.e. the shared data pool should be locked

    def encode_data(self,data_to_encode):
        return 'encoded data'

    def post_to_server(self,query_args):
        try:
            #print query_args
            response = requests.post(self.server_url, params=query_args)
            print "response = ", response
            return True,response
        except requests.ConnectionError as e:
            print "Error sending response"
            return False,e

    def run(self):
        # periodic sweep of shared data pool
        # post this data to server
        while(self._thread_running):
            # TODO : acquire lock on the shared data pool
            data = self.data_sweep(self._shared_data)
            # release acquired lock here itself
            encoded_query = self.encode_data(data)
            post_successful,response = self.post_to_server(encoded_query)
            if(post_successful==False):
                logging.error('Couldn\'t post data to server')
            time.sleep(self.POST_TO_SERVER_DELAY)

    def start_run(self):
        self.web_postman_thread.start()

    def stop_postman(self):

        # TODO : release lock on shared data pool if it is locked
        self._thread_running=False

if __name__=='__main__':

    postman = WebPostman()
    postman.set_server_url('http://127.0.0.1')
    #postman.set_shared_data_pool(shared_data_pool)
    postman.set_post_to_server_delay(60)
    postman.start_run()
    #time.sleep(10)
    #postman.stopPostman()


