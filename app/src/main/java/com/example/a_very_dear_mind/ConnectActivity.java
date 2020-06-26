package com.example.a_very_dear_mind;

import androidx.appcompat.app.AppCompatActivity;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.Socket;
import java.net.URL;
import java.util.ArrayList;

public class ConnectActivity extends AppCompatActivity {

    private Handler handler;
    private Bitmap image;

    private Socket socket;

    private DataOutputStream dos;
    private DataInputStream dis;
    ByteArrayOutputStream baos;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_connect);

        byte[] byteArray = getIntent().getByteArrayExtra("image");
        image = BitmapFactory.decodeByteArray(byteArray, 0, byteArray.length);
        Log.d("log1", Integer.toString(byteArray.length));

        request();
    }

    public void request(){
        handler = new Handler();

        baos = new ByteArrayOutputStream();
        image.compress(Bitmap.CompressFormat.JPEG, 100, baos);
        final byte[] byteArray = baos.toByteArray();
        Log.d("log1", Integer.toString(byteArray.length));

        new Thread(new Runnable() {
            @Override
            public void run() {
                Log.d("log1", "Start Thread to connect");
                String newIP = "125.130.219.8";
                int port = 5001;

                try {
                    socket = new Socket(newIP, port);
                    Log.d("log1", "Correct Connect");
                } catch (IOException e) {
                    Log.d("log1", "Not Connect");
                    e.printStackTrace();
                }

                try {
                    dos = new DataOutputStream(socket.getOutputStream());
                    dis = new DataInputStream(socket.getInputStream());

                    dos.write(byteArray);
                    Log.d("log1", "Trying Fucking");
                    dos.close();
                } catch (IOException e) {
                    e.printStackTrace();
                    Log.d("Buffer", "Incorrect Buffer");
                }

                while(true) {
                    try {
                        String line = "";
                        line = dis.readUTF();
                        Log.d("log1",line);

                        socket.close();
                        break;
                    } catch (IOException e) {
                        e.printStackTrace();
                        Log.d("log1", "Reading from server is error.");
                    }
                }
            }
        }).start();
    }
}
