#include <stdio.h>
#include <sys/socket.h>
#include <unistd.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <string.h>

#define PORT 8080

#define BUFFER_SIZE 1000

void serve() {
    int server, client_socket;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    char client_ip[INET_ADDRSTRLEN];

    char *hello = "HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\n\r\n";
    char *hi = "HTTP/1.1 200 OK\r\n\r\n<html>Hello from server</html>";
    char buffer[BUFFER_SIZE] = {};

    char *method, *path;

    if ((server = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Socket error");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    memset(address.sin_zero, '\0', sizeof address.sin_zero);


    if (bind(server, (struct sockaddr*)&address, sizeof(address)) < 0) {
        perror("Bind error");
        exit(EXIT_FAILURE);
    }
    if (listen(server, 10) < 0) {
        perror("Listen error");
        exit(EXIT_FAILURE);
    }
    printf("\033[0mServer running on \033[4;32mhttp://127.0.0.1:%d\033[0m \033[5;31m⬤\033[0m\n", PORT);
    while(1) {
        if ((client_socket = accept(server, (struct sockaddr*)&address, (socklen_t*)&addrlen)) < 0) {
            perror("Accept error");
            exit(EXIT_FAILURE);
        }
        inet_ntop(AF_INET, &address.sin_addr, client_ip, INET_ADDRSTRLEN);
        if (read(client_socket, buffer, BUFFER_SIZE) < 0) printf("Failed to read socket");
        printf("%s\n", buffer);
        method = strtok(buffer, " \t\r\n");
        path = strtok(NULL, " \t");
        printf("%s \033[0m\033[35m%s\033[0m \033[4;33m%s\033[0m\n", client_ip, method, path);
        if (strcmp(path, "/socket")) {
            if (write(client_socket, hi, strlen(hi)) < 0) printf("Failed to write socket");
        }
        else {
            if (write(client_socket, hello, strlen(hello)) < 0) printf("Failed to write socket");
            close(client_socket);
        }
    }
}

int main() {
    serve();
}
