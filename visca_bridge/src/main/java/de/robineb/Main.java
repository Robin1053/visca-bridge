package de.robineb;

import de.robineb.Server.ViscaIpServer;

import java.io.InputStream;
import java.net.ServerSocket;
import java.net.Socket;

//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
public class Main {
    public static void main(String[] args) {
        int port = 10000;
        System.out.println("Hello and welcome to Visca Bridge!");

        ViscaIpServer server = new ViscaIpServer(port);

        
        server.start();
    }
}