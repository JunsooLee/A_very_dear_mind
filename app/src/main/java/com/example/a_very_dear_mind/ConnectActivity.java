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

    private TextView tv;
    private ImageView imageView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_connect);

        byte[] byteArray = getIntent().getByteArrayExtra("image");
        image = BitmapFactory.decodeByteArray(byteArray, 0, byteArray.length);

        tv = (TextView)findViewById(R.id.textView);

        imageView = (ImageView) findViewById(R.id.image1) ;
        imageView.setImageBitmap(image) ;
        request();
    }

    public void request(){
        handler = new Handler();

        baos = new ByteArrayOutputStream();
        image.compress(Bitmap.CompressFormat.PNG, 100, baos);
        final byte[] byteArray = baos.toByteArray();

        new Thread(new Runnable() {
            @Override
            public void run() {
                Log.d("log1", "Start Thread to connect");
                String newIP = "125.130.219.8";
                int port = 5001;

                try {
                    socket = new Socket(newIP, port);
                    Log.d("log2", "Correct Connect");
                } catch (IOException e) {
                    Log.d("log2", "Not Connect");
                    e.printStackTrace();
                }

                try {
                    dos = new DataOutputStream(socket.getOutputStream());
                    dis = new DataInputStream(socket.getInputStream());
                    dos.write(byteArray);

                } catch (IOException e) {
                    e.printStackTrace();
                    Log.d("Buffer", "Incorrect Buffer");
                }

                while(true) {
                    try {
                        String line = "";
                        line = dis.readUTF();
                        Log.d("log1",line);
                        tv.append(line);

                        socket.close();
                        break;
                    } catch (IOException e) {
                        e.printStackTrace();
                        Log.d("InLine", "Reading from server is error.");
                    }
                }
            }
        }).start();
    }
}
