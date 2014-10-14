package com.fortiguard.poc.payload;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;
import android.widget.ImageView;

public class PayloadActivity extends Activity
{
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
	setContentView(R.layout.main);
	TextView txtView = (TextView) findViewById(R.id.textView);
	txtView.setText("You've just installed Darth Vader ;)");
	ImageView image = (ImageView) findViewById(R.id.imageView);
    }
}
