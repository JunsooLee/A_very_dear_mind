package com.example.a_very_dear_mind;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.FragmentActivity;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.Window;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.List;

public class StartPage extends FragmentActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_start);

        Handler hd = new Handler();
        hd.postDelayed(new Splashhandler(), 3000);

    }
    private class Splashhandler implements Runnable{
        public void run(){
            startActivity(new Intent(getApplication(), MainPage.class));
            StartPage.this.finish();
        }
    }
    @Override
    public void onBackPressed() {
    }
}
