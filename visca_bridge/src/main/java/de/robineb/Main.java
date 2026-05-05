package de.robineb;

import java.io.InputStream;
import java.net.ServerSocket;
import java.net.Socket;

//TIP To <b>Run</b> code, press <shortcut actionId="Run"/> or
// click the <icon src="AllIcons.Actions.Execute"/> icon in the gutter.
public class Main {
    public static void main(String[] args) {
        int port = 10000;
        System.out.println("Hello and welcome to Visca Bridge!");

        try(ServerSocket server = new ServerSocket(port)) {
            System.out.println("Listening on port "+ port + " ..." );

            Socket client  = server.accept();
            System.out.println("Client connected: " + client.getInetAddress());


            InputStream in = client.getInputStream();
            byte[] buffer = new byte[1024];

            while (true){
                int len = in.read(buffer);
                if (len == -1) break;

                System.out.println("Received: ");
                for (int i = 0; i < len; i++) {
                    System.out.printf("%02X ", buffer[i]);
                }
                System.out.println();
            }
        } catch ( Exception e) {
            e.printStackTrace();
        }
    }
}