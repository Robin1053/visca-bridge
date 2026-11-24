package de.robineb.server;

import de.robineb.handler.ClientHandler;

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
                System.out.println("Client connected: " + client.getRemoteSocketAddress());

                // Ein Virtual Thread pro Client
                Thread.ofVirtual().start(new ClientHandler(client));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
