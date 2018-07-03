"""
Create and manipulate wiremock sessions in python.
Create Json mappings for stubbing and verification.
"""
from subprocess import Popen, PIPE, STDOUT

import requests
import time
import json
import os
import random
import socket
from six import text_type


class WireMockServerException(Exception):
    pass


class WireMockServerAlreadyStartedError(WireMockServerException):
    pass


class WireMockServerNotStartedError(WireMockServerException):
    pass


class WiremockLocal(object):
    """
    All configurable items for the wiremock session should be configurable.
    """

    def __init__(self):
        # Set the path in your project to the directory containing the
        # wiremock .jar
        self.wiremock_file, self.wiremock_dir = self.find_jar_path()
        # self.wiremock_file = 'wiremock-standalone-2.6.0.jar'
        # self.wiremock_dir = './'

        # Specify the port you want to run wiremock on. Defaults to Wiremock's
        # default 8080
        self.wiremock_port = self.port_picker()  # random.randint(10001, 15000)

        # URLs for wiremock interaction
        self.base_url = "http://localhost:{}".format(self.wiremock_port)

        # Shell command to start wiremock
        self.wiremock_cmd = ["java", '-jar', str(self.wiremock_file), '--port',
                             str(self.wiremock_port)]

        self.__subprocess = None
        self.__running = False

    def port_scan(self, ip, port):

        """
        Check the wiremock port is open or not
        If it is open, use another port and check three times
        :return:
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        res = s.connect_ex(('localhost', int(port)))
        if res == 0:
            s.close()
            return False
        else:
            s.close()
            return True

    def port_picker(self):
        """
        Return a port which is not used
        :param ip:
        :return:
        """
        for num in range(1, 50):
            port = random.randint(10000, 15000)
            # print(port)
            if self.port_scan("localhost", port):
                return port
        return None

    def find_jar_path(self):
        """

        :return:
        """
        rootdir = os.getcwd()

        for (dirpath, dirnames, filenames) in os.walk(rootdir):
            for filename in filenames:
                if filename == 'wiremock-standalone-2.6.0.jar':
                    return os.path.join(dirpath, filename), dirpath

    def start(self):
        """
        Set status print to False in the call to this method is you don't
        want the wiremock details output to the console
        :param status_print:
        :return:
        """
        if self.__running:
            raise WireMockServerAlreadyStartedError(
                'WireMockServer already started on port {}'.format(self.wiremock_port)
            )

        try:
            self.__subprocess = Popen(self.wiremock_cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        except OSError as e:
            raise WireMockServerNotStartedError(str(e))

        time.sleep(0.1)
        if self.__subprocess.poll() is not None:
            # Process complete - server not started
            raise WireMockServerNotStartedError("\n".join([
                "returncode: {}".format(self.__subprocess.returncode),
                "stdout:",
                text_type(self.__subprocess.stdout.read())
            ]))

        self.__running = True

    def stop(self, raise_on_error=True):
        try:
            self.__subprocess.kill()
        except AttributeError:
            if raise_on_error:
                raise WireMockServerNotStartedError()

    def reset(self):
        """
        Reset the current use mappings for when mapping creation is needed
        on the fly
        :return:
        """
        requests.post(url="{}/__admin/mappings/reset".format(self.base_url))

    def save(self):
        """
        Save the mappings created while Wiremock was running.
        :return:
        """
        requests.post(url="{}/__admin/mappings/save".format(self.base_url))

    def new(self, data):
        """

        :return:
        """
        requests.post(url="{}/__admin/mappings/new".format(self.base_url), data=data)

    def get(self, url, params=None):
        """
        Post a get to the specified URL. Pass the extension after local host
        as the url argument.
        Literally just a pass-through for the requests module get function, so
        you don't have to import requests into the main project file as well.
        :param url:
        :param params:
        :return:
        """
        return requests.get(url="{a}{b}".format(a=self.base_url, b=url),
                            params=params)

    def add_fixed_delay(self, delay_ms):
        """
        Add a fixed delay to the response times. Times in MS.
        :param delay_ms:
        :return:
        """
        delay_json = {'fixedDelay': delay_ms}
        requests.post(url="{}/__admin/socket-delay".format(self.base_url),
                      json=delay_json)

    def create_mapping_file(self, request_method, url, response_headers,
                            status, response_body, file_name=None):
        """
        Create a JSON mapping file in wiremock's mapping directory (using the
        directory specified in __init__) for verification without having the
        mappings created prior.
        The response may contain a number of items, so should be passed a
        dictionary of everything required in the response.
        :param request_method:
        :param url:
        :param response_dict:
        :param file_name:
        :return:
        """
        j_file = json.dumps({"request": {"url": '{}'.format(url),
                                         "method": '{}'.format(
                                             request_method)},
                             "response": {"status": status,
                                          "headers": response_headers,
                                          "jsonBody": response_body}},
                            sort_keys=True, indent=4)

        if file_name is None:
            file_name = "mapping.json".format()

        json_path = os.path.abspath(r"mappings/{b}".format(b=file_name))

        with open(json_path, 'w') as json_file:
            json_file.write(j_file)

        # print("Mapping File Created: {}".format(json_path))
