package de.robineb.Handler;

import java.io.InputStream;
import java.net.Socket;

public class ClientHandler extends Thread {

    private final Socket client;

    public ClientHandler(Socket client) {
        this.client = client;
    }

    @Override
    public void run() {
        try {
            InputStream in = client.getInputStream();
            byte[] buffer = new byte[1024];

            while (true) {
                int len = in.read(buffer);

                if (len == -1) {
                    System.out.println("Client disconnected");
                    break;
                }

                onData(buffer, len);
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void onData(byte[] buffer, int len) {
        System.out.print("Received: ");

        for (int i = 0; i < len; i++) {
            System.out.printf("%02X ", buffer[i]);
        }

        System.out.println();
    }
}