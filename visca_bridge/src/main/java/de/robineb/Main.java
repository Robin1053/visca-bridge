package de.robineb;

import de.robineb.server.ViscaIpServer;

public class Main {
    public static void main(String[] args) {
        int port = 10000;
        System.out.println("Hello and welcome to Visca Bridge!");

        ViscaIpServer server = new ViscaIpServer(port);
        server.start();
    }
}
