from socket import *
import sys
import re
import os


def createRequest(host, url, originalRequest):
    try:
        hostInd = url.index(host)
        if len(url[hostInd + len(host):]) < 3:
            pass
        else:
            url = url[hostInd + len(host):]
    except ValueError:
        pass
    url = url.replace("www.","")
    httpHeader = "GET " + url + " HTTP/1.1\r\n"
    httpHeader += ("Host: " + host + '\r\n')
    httpHeader += "Connection: close\r\n"
    for line in originalRequest.split('\r\n'):
        if 'User-Agent' in line:
            httpHeader += (line + '\r\n')
        if 'Accept:' in line:
            httpHeader += (line + '\r\n')
        if 'Referer:' in line:
            httpHeader += (line + '\r\n')
        if 'Accept-Encoding:' in line:
            httpHeader += (line + '\r\n')
        if 'Accept-Language:' in line:
            httpHeader += (line + '\r\n')
        if 'Cookie:' in line:
            httpHeader += (line + '\r\n')
    httpHeader += '\r\n\r\n'
    return httpHeader

def createResponse(filename, data):
    httpHeader = 'HTTP/1.1 200 OK\r\n'
    if '.jpg' in filename:
        httpHeader += 'Content-Type: image/jpeg\r\n'
    elif 'html' or 'htm' in filename:
        httpHeader += 'Content-Type: text/html\r\n'
    elif '.ico' in filename:
        httpHeader += 'Content-Type: image/x-icon\r\n'
    elif '.css' in filename:
        httpHeader += 'Content-Type: text/css\r\n'
    elif '.js' in filename:
        httpHeader += 'Content-Type: application/javascript\r\n'
    elif '.txt' in filename:
        httpHeader += 'Content-Type: text/plain\r\n'
    else:
        httpHeader += 'Content-Type: application/octet-stream\r\n'
    httpHeader += ('Content-Length: ' + str(len(data)))
    httpHeader += '\r\n\r\n'
    print ('RESPONSE HEADER FROM PROXY TO CLIENT')
    print (httpHeader)
    print ('END OF HEADER\n')
    httpHeader += data
    return httpHeader

def create404(data):
    httpHeader = 'HTTP/1.1 404 Not Found\r\n'
    httpHeader += 'Content-Type: text/html; charset=UTF-8\r\n'
    print ('RESPONSE HEADER FROM PROXY TO CLIENT')
    print (httpHeader)
    print ('END OF HEADER\n')
    httpHeader += '\r\n\r\n'
    httpHeader += data
    return httpHeader


def createForbidden():
    httpHeader = 'HTTP/1.1 403 Forbidden\r\n'
    httpHeader += 'Content-Type: text/html; charset=UTF-8\r\n'
    print ('RESPONSE HEADER FROM PROXY TO CLIENT')
    print (httpHeader)
    print ('END OF HEADER\n')
    httpHeader += '\r\n\r\n'
    httpHeader += "<h1> THIS URL IS BLOCKED</h1>"
    return httpHeader


if len(sys.argv) <= 1:
  print ('Usage : "python proxyserver.py server_ip"\n[server_ip : Address of the proxy server')
  sys.exit(2)

serverIP = sys.argv[1]
# buffer size
BUFFER_SIZE = 1048576
#port number is arbituary
welcomePort = 8000
# holds names of files sent with special encoding i.e gzip
encodeFlag = []
encodeDict = {}

try:
    #create welcoming socket
    welcomeSocket = socket(AF_INET, SOCK_STREAM)

    #bind to the server address
    welcomeSocket.bind((serverIP, welcomePort))

    #begin listening (argument is number of allowed queued connections)
    welcomeSocket.listen(100)


#listening loop
    while True:
        # Start receiving data from client
        print('WEB PROXY SERVER IS LISTENING')

        # Accept() returns a new connection socket along with the address
        clientSocket, clientAddress = welcomeSocket.accept()
        print('WEB PROXY SERVER CONNECTED WITH ' + str(clientAddress))

        # wait 100ms second to hear from client
        try:
            clientSocket.settimeout(0.1)
            request = clientSocket.recv(BUFFER_SIZE).decode()
        except timeout:
            clientSocket.shutdown(SHUT_RDWR)
            clientSocket.close()
            continue

        # do not parse empty message
        if(len(request) > 0):
            print('MESSAGE RECEIVED FROM CLIENT:')
            print(request)
            print ('END OF MESSAGE RECEIVED FROM CLIENT')
        else:
            clientSocket.shutdown(SHUT_RDWR)
            clientSocket.close()
            continue

        # Parse Request Header

        method = request.split(" ")[0]
        url = request.split(" ")[1]
        url = url[1:]
        try:
            domainIndex = url.index('.')
            host=url.partition("/")[0]
        except ValueError:
            pass
        for line in request.split('\r\n'):
            if "Referer:" in line:
                print(line)
                temp = line.split("Referer: http://192.168.1.11:8000    z/")[1]
                host = temp.partition("/")[0]
                url = "/" + url

        print ('[PARSE MESSAGE HEADER]:')
        url = url.replace("www.","")
        print ('METHOD = ' + method + ', DESTADDRESS = ' + url + ', HTTPVersion = ' + str(request.split()[2]))
        host = host.replace("www.","")

        # check Forbidden urls (URL filtering)

        file1 = open('ForbiddenUrls.txt', 'r')
        Lines = file1.readlines()
        forbidden = False
        for line in Lines:
            if url in line:
                forbidden = True
                response = createForbidden()
                response = bytes(response, 'utf-8')
                clientSocket.send(response)
        if (forbidden):
            continue


        writefile = True
        # See if the URL contains a filename
        filematcher = re.compile("((.?)*\.(jpg|htm|html|png|ico|js|css|gif)$)")
        fmatch = filematcher.match(url)
        if (fmatch):
            filename = url.split('/')[-1]
            if filename in os.listdir("."):
                # Cache Hit
                print ('Cache Hit')
                with open(filename, 'r') as file:
                    # Assemble HTTP response
                    httpHeader = 'HTTP/1.1 200 OK\r\n'
                    if '.jpg' in filename:
                        httpHeader += 'Content-Type: image/jpeg\r\n'
                    elif 'html' or 'htm' in filename:
                        httpHeader += 'Content-Type: text/html\r\n'
                    elif '.ico' in filename:
                        httpHeader += 'Content-Type: image/x-icon\r\n'
                    elif '.css' in filename:
                        httpHeader += 'Content-Type: text/css\r\n'
                    elif '.js' in filename:
                        httpHeader += 'Content-Type: application/javascript\r\n'
                    elif '.txt' in filename:
                        httpHeader += 'Content-Type: text/plain\r\n'
                    else:
                        httpHeader += 'Content-Type: application/octet-stream\r\n'

                    data = file.read()
                    httpHeader += ('Content-Length: ' + str(len(data)))
                    if filename in encodeFlag:
                        httpHeader += (encodeDict[filename] + '\r\n')

                    httpHeader += '\r\n\r\n'

                    print ('HTTP Header sent to Client:')
                    print (httpHeader)
                    httpHeader += data
                    httpHeader = bytes(httpHeader, 'utf-8')
                    clientSocket.send(httpHeader)
                    clientSocket.close()
                    continue
        else:
            writefile = True
            filename = url
            # if url[0] == '/':
            #     url = url[1:]
            # url = "/"
            # if here then the request was not for a specific file (metadata?)

# Cache miss must send request to original destination

        try:
            print ('[LOOK UP IN CACHE]: NOT FOUND, BUILD REQUEST TO SEND TO ORIGINAL SERVER')
            forwardSocket = socket(AF_INET, SOCK_STREAM)
            # Connect on port 80
            if host[0] == '/':
                host = host[1:]
            host = host
            print ('[PARSE REQUEST HEADER] HOSTNAME IS ' + host)
            hostIP = gethostbyname(host)
            address = (hostIP, 80)
            forwardSocket.connect(address)
            newRequest = createRequest(host, url, request)
            print ('REQUEST MESSAGE SENT TO ORIGINAL SERVER:')
            print (newRequest)
            print ('END OF MESSAGE SENT TO ORIGINAL SERVER.\n')
            mynewrequest = newRequest.encode('utf-8')
            forwardSocket.send(mynewrequest)
            # keep reading and forwarding until nothing server stops
#            count = 0
            error404 = False
            if(writefile):
                with open(filename, 'w') as file:
                    while True:
                        forwardSocket.settimeout(0.5) # 500ms
                        response = forwardSocket.recv(BUFFER_SIZE).decode()
                        if(len(response) > 0):
                            try:
                                if '404' in response.split('\r\n\r\n')[0]:
                                    temp = response.split('\r\n\r\n')
                                    header = temp[0]
                                    print ('RESPONSE HEADER FROM ORIGINAL SERVER')
                                    print (header)
                                    print ('END OF HEADER')
                                    if len(temp) < 3:
                                        data = temp[1]
                                    else:
                                        data = '\r\n\r\n'.join(temp[1:])
                                    proxy_response = create404(data)
                                    response = bytes(response , 'utf-8')
                                    clientSocket.send(response)
                                    error404 = True
                                    break

                                if 'HTTP' in response.split('\r\n\r\n')[0]:
                                    temp = response.split('\r\n\r\n')
                                    header = temp[0]
                                    print ('RESPONSE HEADER FROM ORIGINAL SERVER')
                                    print (header)
                                    print ('END OF HEADER')
                                    print ('[WRITE FILE INTO CACHE]: ' + filename +'\n')
                                    if len(temp) < 3:
                                        data = temp[1]
                                    else:
                                        data = '\r\n\r\n'.join(temp[1:])
                                    file.write(data)
                                else:
                                    file.write(response)
                                # See if there is special encoding to note
                                for line in response.split('\r\n'):
                                    if 'Content-Encoding:' in line:
                                        encodeFlag.append(filename)
                                        encodeDict[filename] = line
                            except IndexError:
                                file.write(response)
                                response = bytes(response, 'utf-8')
                                clientSocket.send(response)
                        else:
                            break
            else:
                while True:
                        forwardSocket.settimeout(1.0)
                        response = forwardSocket.recv(BUFFER_SIZE)

                        if(len(response) > 0):
                            response = bytes(response,'utf-8')
                            clientSocket.send(response)
                        else:
                            break
            if error404:
                with open(filename, 'r') as file:
                    data = file.read()
                    proxy_response = create404(data)
                    proxy_response = bytes(proxy_response,'utf-8')
                    clientSocket.send(proxy_response)
            else:
                with open(filename, 'r') as file:
                    data = file.read()
                    proxy_response = createResponse(filename, data)
                    proxy_response = bytes(proxy_response,'utf-8')
                    clientSocket.send(proxy_response)
            forwardSocket.close()
            clientSocket.close()
        except timeout:
            print ('timeout')
            forwardSocket.close()
            clientSocket.close()
        except Exception as e:
            print(e)
            print("Illegal Request")
except KeyboardInterrupt:
    print('Exiting Gracefully')
    welcomeSocket.shutdown(SHUT_RDWR)
    welcomeSocket.close()
    sys.exit()






