package com.example.a_very_dear_mind;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.Socket;
import java.net.URL;

public class ConnectActivity extends AppCompatActivity {

    Handler handler = new Handler();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_connect);

        new Thread(new Runnable() {
            @Override
            public void run() {
                request("URL");
            }
        }).start();
    }

    public void handlerView(final String data){
        Log.d("Connect", data);

        handler.post(new Runnable() {
            @Override
            public void run() {

            }
        });
    }
    public void request(String data){
        try{
            int portNumber = 5001;
            Socket socket = new Socket("localhost", portNumber);

            DataOutputStream outStream = new DataOutputStream(socket.getOutputStream());
            outStream.writeChars(data);
            outStream.flush();

            DataInputStream inStream = new DataInputStream(socket.getInputStream());
            socket.close();
        }catch(Exception e){
            e.printStackTrace();
        }

    }
}
