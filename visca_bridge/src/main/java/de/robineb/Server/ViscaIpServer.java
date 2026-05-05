package de.robineb.Server;

import de.robineb.Handler.ClientHandler;

import java.io.InputStream;
import java.net.ServerSocket;
import java.net.Socket;

public class ViscaIpServer {
    private final int port;

    public ViscaIpServer(int port) {
        this.port = port;
    }

    public void start() {
        System.out.println("Listening on port " + port + " ...");
        try (ServerSocket server = new ServerSocket(port)) {
            while (true) {
                Socket client = server.accept();
                System.out.println("Client connected: " + client.getLocalAddress());

                InputStream in = client.getInputStream();
                byte[] buffer = new byte[1024];

                new ClientHandler(client).start();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}