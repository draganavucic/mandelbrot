# mandelbrot
Client/Server python scripts for mandelbrot set calculations.

Client script can generate image on multiple ways:
1. Localy, by using mandelbrot functions
2. Localy, by extracting starting points of sub-images and calculating each sub-image color values
3. By sending starting points of sub-images to multiple servers (where each server calculates color values for assigned sub-images)
4. The same as 3. just by using multiple threads to distribute data to defined servers

## Server script

- Created using standard python libraries and *BaseHTTPRequestHandler* and *HTTPServer* from *BaseHTTPServer*
- Starting localhost server with a port defined as an argument. Example: `server.py 8080`
- Function `serve_forever()` makes the server to always run
- After running the server on specified port the output is following:
  ```
  HTTP server is starting on port 1111...
  HTTP server is running...
  ```
## Client script

- Created using standard python libraries
- For the creation of the image, needed Image module from Python Image Library (PIL). Install with: `pip install image`
- The script is started without any arguments: `client.py`
- Output after opening the script looks like this:
```
-------------------- Menu --------------------

Data defined for the calculations:

MAX_N = 255      #Iterations
WIDTH = 1024, HEIGHT = 1024     #Image
MIN_C_RE = -2.0, MAX_C_RE = 2.0, MIN_C_IM = -2.0, MAX_C_IM = 2.0        #Plot
DIV = 4         #Width/height of sub-pictures
SERVER_LIST = 127.0.0.1:1111 127.0.0.1:2222 127.0.0.1:3333 #List of servers

[0] - Exit.

[1] - Change parameters used for calculations.
[2] - #Debug: Mandelbrot function iterations.
Generate image by:
[3] - #Debug: Use mandelbrot function (client only).
[4] - #Debug: Collect start points & calculate colors of sub-pictures (client only).
[5] - Send start points of sub-pictures to defined servers (single-thread).
[6] - Send start points of sub-pictures to defined servers (multi-threaded).

Enter menu number to continue:
```

### Menu choices

1. Updating of the parameters used for calculations:
    - Iterations, width, height, div must be integers greater then 0
    - Div must be divisible with width/height of the image, as it represents the size of the sub-images
    - Plot parameters must be in the range [-2, 2]
    - List of servers has to contain valid ip addresses and port numbers
2. Prints output from the mandelbrot function. #for debugging and better understanding
3. Generation of the image on the client side only. #for debugging and comparison
4. The job that should be done through servers is done here on client side. #for debugging and comparison
5. In single thread sends the data to defined servers and collects the data retreived. Image is generated after all servers are finished.
6. Using multiple threads distributes the data to defined servers and collects the data retreived. Image is generated after all servers are finished.

### Parameters

On the image below, comparison when using different iteration parameter is shown: `max_n = [10, 50, 255, 1024]`

![Imgur Image](https://i.imgur.com/1neSkZu.png)

License
----

© 2019 Dragana Vučić

**Contact or feedback on: dragana.vucic@live.com**
