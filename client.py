"""Client.py script is used for running client console GUI"""
import httplib # sending data to servers
import json # parsing data received from servers
import time # measuring execution time
import socket # testing ip addresses
from threading import Thread
from Queue import Queue
from PIL import Image, ImageDraw

# Iterations
MAX_N = 64
# Size of the image
WIDTH = 1024
HEIGHT = 1024
# Plot
MIN_C_RE = -2.0
MAX_C_RE = 2.0
MIN_C_IM = -2.0
MAX_C_IM = 2.0
# Divisions - width/height for sub-pictures
DIV = 4
# List of servers
SERVER_LIST = ['127.0.0.1:1111', '127.0.0.1:2222', '127.0.0.1:3333']

# Welcome line :)
print '--- Welcome to Mandelbrot Set | Python 2.17.7 ---\n'

def mandelbrot(z_0):
    """
    Computing the Mandelbrot iteration sequence starting at z_0
    :param z_0: complex
    :return: the number of iterations for which the magnitude stays less than 2, up to the 255
    """
    z_n = z_0
    for itr in range(MAX_N):
        if abs(z_n) > 2.0:
            return itr
        z_n = z_n * z_n + z_0
    return 255

def generate_image_on_client_using_mandelbrot():
    """#Debug: Generating image on client only"""
    # picture to manipulate
    image = Image.new('RGB', (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    # calculations for each pixel
    for y in range(HEIGHT):
        c_y = y * (MAX_C_IM - MIN_C_IM) / (HEIGHT - 1)  + MIN_C_IM
        for x in range(WIDTH):
            c_x = x * (MAX_C_RE - MIN_C_RE) / (WIDTH - 1) + MIN_C_RE
            color = 255 - mandelbrot(complex(c_x, c_y))
            draw.point([x, y], (color, color, color))
    # saving image in a file
    image.save('client_mandelbrot.png', 'PNG')

def collect_starting_points():
    """
    #Debug: Collect starting points for sub-pictures
    :return: list of start points for sub-pictures
    """
    start_points = []
    for i in range(0, WIDTH, DIV):
        for j in range(0, HEIGHT, DIV):
            start_points.append([i, j])
    return start_points

def calculate_colors_for_sub_picture(sp_x, sp_y):
    """
    Calculation of pixel colors for sub-picture
    :param sp_x, sp_y: starting point in the matrix
    return: list of colors for sub-picture
    """
    colors_list = [sp_x, sp_y]
    for j in range(sp_y, sp_y + DIV):
        c_y = j * (MAX_C_IM - MIN_C_IM) / (HEIGHT - 1)  + MIN_C_IM
        for i in range(sp_x, sp_x + DIV):
            c_x = i * (MAX_C_RE - MIN_C_RE) / (WIDTH - 1) + MIN_C_RE
            color = 255 - mandelbrot(complex(c_x, c_y))
            colors_list.append(color)
    return colors_list

def generate_image_on_client_from_sub_pictures():
    """
    Generating image from sub-pictures using client;
    Representing the way of how servers should work
    """
    # collecting starting points for sub-pictures
    start_points = collect_starting_points()
    # merge all sub-picutre colors into one list
    start_point_colors = []
    for point in start_points:
        start_point_colors.append(calculate_colors_for_sub_picture(point[0], point[1]))
    # image to be generated from complete list of merged colors of sub-pictures
    draw_image_from_start_point_color_list(start_point_colors, 'client_sub_pictures.png')

def send_data_to_server(http_server, sp_x, sp_y):
    """
    Sending data to defined server
    :param http_server: server ip address and port
    :param sp_x, sp_y: start points of sub-picture
    :return: list of colors returned from the server
    """
    # create a connection
    conn = httplib.HTTPConnection(http_server)
    # create path with parameters for sending
    params = '%s/%s/%s/%s/%s/%s/%s/%s/%s/%s' % (MAX_N, WIDTH, HEIGHT, \
        MIN_C_RE, MAX_C_RE, MIN_C_IM, MAX_C_IM, DIV, sp_x, sp_y)
    # request command to server
    conn.request("GET", params)
    # get response from server
    rsp = conn.getresponse()
    # print server response and data
    #print(rsp.status, rsp.reason)
    data_received = rsp.read()
    # get data in list from json format
    colors_list = json.loads(data_received)
    # closing connection
    conn.close()
    # return received list
    return colors_list

def generate_image_from_servers_sub_pictures_single_thread():
    """
    Generating image by sending data to servers and collecting them
    by using multiple threads
    """
    # collecting list of starting points for sub-pictures
    # and splitting workload on the number of servers
    start_points = collect_starting_points()
    # index % number of servers allows distribution of jobs between servers
    num_of_servers = len(SERVER_LIST)
    # complete list with colors per each pixel
    start_point_colors = []
    for index, point in enumerate(start_points):
        start_point_colors.append(send_data_to_server(SERVER_LIST[index % num_of_servers], \
            point[0], point[1]))
    # generate image from collected colors
    draw_image_from_start_point_color_list(start_point_colors, 'servers_sub_pics_single_thread.png')

def do_work(queue, async_colors_list):
    """Representation of the job defined to process the sub-picture"""
    while True:
        server, sp_x, sp_y = queue.get()
        async_colors_list.append(send_data_to_server(server, sp_x, sp_y))
        queue.task_done()

def generate_image_from_servers_sub_pictures_multi_threaded():
    """Generating image by sending data to servers using multiple threads"""
    # collecting starting points
    start_points = collect_starting_points()
    # number of servers and number of jobs needed for splitting the work
    num_of_servers = len(SERVER_LIST)
    num_of_jobs = len(start_points)
    print 'Starting %s jobs on %s servers.\n' % (num_of_jobs, num_of_servers)
    # defining and putting the jobs in the queue
    async_colors_list = []
    queue = Queue(num_of_jobs)
    for _ in range(num_of_servers * 2):
        thread = Thread(target=do_work, args=(queue, async_colors_list,))
        thread.daemon = True
        thread.start()
    try:
        for index, point in enumerate(start_points):
            queue.put((SERVER_LIST[index % num_of_servers], point[0], point[1]))
        queue.join()
    except KeyboardInterrupt:
        print 'KeyboardInterrupt'
        quit()
    # after completition, drawing the image
    draw_image_from_start_point_color_list(async_colors_list, 'servers_sub_pics_multi_threaded.png')

def draw_image_from_start_point_color_list(start_point_colors, name):
    """
    Drawing the image from list of colors from sub-pictures
    :params start_point_colors: list of sub-pictures' colors
    :params name: name for the image
    """
    image = Image.new('RGB', (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    for point_list in start_point_colors:
        sp_x = point_list[0]
        sp_y = point_list[1]
        color_index = 2
        for j in range(sp_y, sp_y + DIV):
            for i in range(sp_x, sp_x + DIV):
                color = point_list[color_index]
                draw.point([i, j], (color, color, color))
                color_index += 1
    image.save(name, 'PNG')

def print_defined_parameters():
    """Printing data/parameters in the menu"""
    print 'Data defined for the calculations:\n'
    print 'MAX_N = %s\t#Iterations' % (MAX_N)
    print 'WIDTH = %s, HEIGHT = %s\t#Image' % (WIDTH, HEIGHT)
    print 'MIN_C_RE = %s, MAX_C_RE = %s, MIN_C_IM = %s, MAX_C_IM = %s\t#Plot' % (MIN_C_RE, \
        MAX_C_RE, MIN_C_IM, MAX_C_IM)
    print 'DIV = %s \t#Width/height of sub-pictures' % (DIV)
    print 'SERVER_LIST = ' + ' '.join(str(s) for s in SERVER_LIST) + ' #List of servers\n'

def validate_positive_integer(prompt_printout):
    """
    Validate positive integer
    :params prompt_printout: printing message
    """
    while True:
        try:
            value = int(raw_input(prompt_printout))
        except ValueError:
            print "Invalid value: the number must be an integer."
            continue

        if value <= 0:
            print "Invalid value: the number cannot be negative or zero."
            continue
        else:
            break
    return value

def validate_plot_value(prompt_printout):
    """
    Validate float value for the plot [-2, 2]
    :params prompt_printout: printing message
    """
    while True:
        try:
            value = float(raw_input(prompt_printout))
        except ValueError:
            print "Invalid value: the number must be a float."
            continue

        if value > 2.0 or value < -2.0:
            print "Invalid value: the number must be in a range [-2, 2]."
            continue
        else:
            break
    return value

def validate_division(prompt_printout):
    """
    Validation of dimension of width/height for sub-pictures
    Dimension should be divisible with image width/height
    :params prompt_printout: printing message
    """
    while True:
        value = validate_positive_integer(prompt_printout)
        if WIDTH % value != 0 or HEIGHT % value != 0:
            print "Invalid value: the division number must be divisible" + \
                "with width/height [%s, %s]." % (WIDTH, HEIGHT)
            continue
        else:
            break
    return value

def validate_ip_addresses():
    """Function for updating list of servers."""
    list_of_servers = []
    done = False

    print 'Enter IP address and a port in this format [127.0.0.1:8080]. One per line.'
    print 'When all addresses are saved, finish with entering 0.'

    while done != True:
        value = raw_input('IP: ')
        if value == '0':
            done = True
            break
        else:
            try:
                socket.inet_aton(value.split(':')[0])
                list_of_servers.append(value)
            except socket.error:
                print 'IP address cannot be reached. Try again.'
    return list_of_servers

def update_parameters():
    """Updating data/parameters used in calculations"""
    print '\nEnter each parameter in another line:\n'
    global MAX_N, WIDTH, HEIGHT, MIN_C_RE, MAX_C_RE, MIN_C_IM, MAX_C_IM, DIV, SERVER_LIST
    # MAX_N = validate_positive_integer('Maximum number of iterations [MAX_N]: ')
    # WIDTH = validate_positive_integer('Image width in pixels [WIDTH]: ')
    # HEIGHT = validate_positive_integer('Image height in pixels [height]: ')
    # MIN_C_RE = validate_plot_value('Minimal real number for the plot [MIN_C_RE]: ')
    # MAX_C_RE = validate_plot_value('Maximal real number for the plot [MAX_C_RE]: ')
    # MIN_C_IM = validate_plot_value('Minimal imaginary number for the plot [MIN_C_IM]: ')
    # MAX_C_IM = validate_plot_value('Maximal imaginary number for the plot [MAX_C_IM]: ')
    # DIV = validate_division('Dimensions of sub-pictures in pixels [DIV]: ')
    list_of_servers = validate_ip_addresses()
    if not list_of_servers:
        print 'Entered server list is empty. Default one will be used.'
        SERVER_LIST = list_of_servers
    else:
        SERVER_LIST = list_of_servers
    print '\nData for the calculations updated.'

def run_loop():
    """Main function to loop until exit"""
    #saving user input
    menu_num = None

    while menu_num != 0:
        print '\n-------------------- Menu --------------------\n'
        print_defined_parameters()
        print '[0] - Exit.\n'
        print '[1] - Change parameters used for calculations.'
        print '[2] - #Debug: Mandelbrot function iterations.'
        print 'Generate image by:'
        print '[3] - #Debug: Use mandelbrot function (client only).'
        print '[4] - #Debug: Collect start points & calculate colors of sub-pictures (client only).'
        print '[5] - Send start points of sub-pictures to defined servers (single-thread).'
        print '[6] - Send start points of sub-pictures to defined servers (multi-threaded).\n'
        menu_num = raw_input('Enter menu number to continue: ')

        if menu_num == '0':
            quit()
        elif menu_num == '1':
            update_parameters()
        elif menu_num == '2': # debugging
            for c_re in range(-10, 10, 5):
                for c_im in range(-10, 10, 5):
                    cplx = complex(c_re / 10, c_im / 10)
                    print(cplx, mandelbrot(cplx))
        elif menu_num == '3': # debugging
            start_time = time.time()
            generate_image_on_client_using_mandelbrot()
            print "\n# Execution time: %s seconds" % (time.time() - start_time)
        elif menu_num == '4': # debugging
            start_time = time.time()
            generate_image_on_client_from_sub_pictures()
            print "\n# Execution time: %s seconds" % (time.time() - start_time)
        elif menu_num == '5':
            start_time = time.time()
            generate_image_from_servers_sub_pictures_single_thread()
            print "\n# Execution time: %s seconds" % (time.time() - start_time)
        elif menu_num == '6':
            start_time = time.time()
            generate_image_from_servers_sub_pictures_multi_threaded()
            print "\n# Execution time: %s seconds" % (time.time() - start_time)
        else:
            print 'Wrong character input. Only defined menu numbers can be entered.'

if __name__ == "__main__":
    run_loop()
