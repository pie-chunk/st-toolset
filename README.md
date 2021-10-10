# st-toolset
Socket-Based TCP File Transmission Tool

USAGE INFO

----------

-s, --server = server mode*

-h, --help = usage

-v, --version = version

-c, --client = client mode*

-p, --port <PORT> = port (default=8080)
  
-t, --target <TARGET> = target host (default=0.0.0.0)*
  
-g, --getip = get ip address
  
-f, --file <PATH> = send a file
  
-c, --chunksize = chunk size (default=1024 byte)
  
* REQUIRED (client OR server mode)
  
** REQUIRED IN CLIENT MODE
  
----------
  
In client text mode type ":end" to end sending.
  

EXAMPLE
1. python3 st-toolset.py --server --chunksize 1024
  
  (server mode, chunk size: 1024 bytes)
  
  
2. python3 st-toolset.py --client --port 8080 --target 192.168.0.186
  
  (client mode, port: 8080, send data to 192.168.0.186)
  
3. python3 st-toolset.py --client --port 3333 --target 192.168.0.186 --file ./example.png
  
  (client mode, port: 3333, send data to 192.168.0.186, file to send: ./example.png)
  
  
