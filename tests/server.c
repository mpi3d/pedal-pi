#include <stdio.h>
#include <sys/socket.h>
#include <unistd.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <string.h>

#define PORT 8080

#define BUFFER_SIZE 1000

int main() {
    int server_fd, new_socket; long valread;
    struct sockaddr_in address;
    int addrlen = sizeof(address);

    char *hello = "HTTP/1.1 200 OK\r\n\r\n<html>Hello from server</html>";
    char buffer[BUFFER_SIZE] = {};

    char *method;
    char *uri;

    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Socket error");
        exit(EXIT_FAILURE);
    }


    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    memset(address.sin_zero, '\0', sizeof address.sin_zero);


    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        perror("Bind error");
        exit(EXIT_FAILURE);
    }
    if (listen(server_fd, 10) < 0) {
        perror("Listen error");
        exit(EXIT_FAILURE);
    }
    printf("\033[0mServer running on \033[4;32mhttp://127.0.0.1:%d\033[0m \033[5;31m⬤\033[0m\n", PORT);
    while(1) {
        if ((new_socket = accept(server_fd, (struct sockaddr*)&address, (socklen_t*)&addrlen)) < 0) {
            perror("Accept error");
            exit(EXIT_FAILURE);
        }

        valread = read(new_socket , buffer, BUFFER_SIZE);
        method = strtok(buffer, " \t\r\n");
        uri = strtok(NULL, " \t");
        printf("\033[0m\033[35m%s\033[0m \033[4;33m%s\033[0m\n", method, uri);
        write(new_socket, hello, strlen(hello));
        close(new_socket);
    }
    return 0;
}
