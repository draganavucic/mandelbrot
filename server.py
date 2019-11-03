"""Server.py script is used for running localhost servers with the port accepted as an argument"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json # parsing data for sending
import sys # reading arguments

# getting http server port from the arguments
PORT = sys.argv[1]

def mandelbrot(z_0, max_n):
    """
    Computing the Mandelbrot iteration sequence starting at z_0
    :param z_0: complex
    :param max_n: maximal number of interations
    :return: the number of iterations for which the magnitude stays less than 2, up to the 255
    """
    z_n = z_0
    for itr in range(max_n):
        if abs(z_n) > 2.0:
            return itr
        z_n = z_n * z_n + z_0
    return 255

def calculate_colors_for_sub_picture(path):
    """
    Calculation of color for every pixel in sub-picture
    :param path: string, complete path with parameter values
    :return: list, list of colors of the sub-picture
    """
    # getting parameters from path
    params = path.split('/')
    # taking values of parameters
    # max_n = int(params[0])
    # width, height = int(params[1]), int(params[2])
    min_c_re, max_c_re = float(params[3]), float(params[4])
    min_c_im, max_c_im = float(params[5]), float(params[6])
    div = int(params[7])
    sp_x, sp_y = int(params[8]), int(params[9])

    colors_list = [sp_x, sp_y]
    for j in range(sp_y, sp_y + div):
        c_y = j * (max_c_im - min_c_im) / (int(params[2]) - 1)  + min_c_im
        for i in range(sp_x, sp_x + div):
            c_x = i * (max_c_re - min_c_re) / (int(params[1]) - 1) + min_c_re
            color = 255 - mandelbrot(complex(c_x, c_y), int(params[0]))
            colors_list.append(color)
    # returning the list for sub-picture
    return colors_list

class KodeFunHTTPRequestHandler(BaseHTTPRequestHandler):
    """Custom HTTPRequestHandler class"""
    # handle GET command
    def do_GET(self):
        """Overriding do_GET() function"""
        # print received data
        #print self.path
        # send code 200 response
        self.send_response(200)
        # send header first
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # getting the list of colors for sub-picture
        colors_list = calculate_colors_for_sub_picture(self.path)
        # send list content to client in json format
        self.wfile.write(json.dumps(colors_list))
        return

def run():
    """Making that the server is always running"""
    print '# HTTP server is starting on port %s...' % PORT
    # http server port is defined through argument
    server_address = ('127.0.0.1', int(PORT))
    httpd = HTTPServer(server_address, KodeFunHTTPRequestHandler)
    print '# HTTP server is running...'
    httpd.serve_forever()

if __name__ == '__main__':
    run()
