package com.example.bootstrapreader;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.util.Base64;
import android.webkit.JavascriptInterface;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {

    private WebView web;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        web = findViewById(R.id.web);
        web.getSettings().setJavaScriptEnabled(true);
        web.getSettings().setDomStorageEnabled(true);
        web.getSettings().setAllowFileAccess(true);
        // 允许 file:// 页面读取同目录 assets 里的 dict.json
        web.getSettings().setAllowFileAccessFromFileURLs(true);
        web.getSettings().setAllowUniversalAccessFromFileURLs(true);
        web.setWebViewClient(new WebViewClient());
        web.addJavascriptInterface(new Bridge(web), "Android");
        web.loadUrl("file:///android_asset/index.html");
    }

    @Override
    public void onBackPressed() {
        if (web == null) {
            super.onBackPressed();
            return;
        }
        web.evaluateJavascript(
                "(window.onAndroidBack && window.onAndroidBack()) ? '1' : '0'",
                new android.webkit.ValueCallback<String>() {
                    @Override
                    public void onReceiveValue(String value) {
                        if (!"\"1\"".equals(value)) {
                            finish();
                        }
                    }
                });
    }
}

/** 原生抓取桥：让页面里的 JS 可以跨域拉文章（绕开 WebView 的 CORS）。 */
class Bridge {

    private final WebView web;

    Bridge(WebView web) {
        this.web = web;
    }

    @JavascriptInterface
    public String dict() {
        return assetBase64("dict.json");
    }

    @JavascriptInterface
    public String general() {
        return assetBase64("general.json");
    }

    @JavascriptInterface
    public String grammar() {
        return assetBase64("grammar.json");
    }

    /** 用系统默认浏览器打开链接（图片搜索等），返回后仍在 App 内。 */
    @JavascriptInterface
    public void openUrl(final String url) {
        web.post(new Runnable() {
            @Override
            public void run() {
                try {
                    Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    web.getContext().startActivity(intent);
                } catch (Exception ignored) {
                }
            }
        });
    }

    private String assetBase64(String name) {
        try {
            java.io.InputStream is = web.getContext().getAssets().open(name);
            java.io.ByteArrayOutputStream bos = new java.io.ByteArrayOutputStream();
            byte[] buf = new byte[8192];
            int n;
            while ((n = is.read(buf)) != -1) {
                bos.write(buf, 0, n);
            }
            is.close();
            return Base64.encodeToString(bos.toByteArray(), Base64.NO_WRAP);
        } catch (Exception e) {
            return "";
        }
    }

    @JavascriptInterface
    public void fetch(final String url) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                String result;
                try {
                    java.net.HttpURLConnection conn =
                            (java.net.HttpURLConnection) new java.net.URL(url).openConnection();
                    conn.setConnectTimeout(15000);
                    conn.setReadTimeout(15000);
                    conn.setRequestProperty(
                            "User-Agent",
                            "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 " +
                                    "(KHTML, like Gecko) Chrome/120 Mobile Safari/537.36");
                    java.io.BufferedReader reader = new java.io.BufferedReader(
                            new java.io.InputStreamReader(conn.getInputStream(), "UTF-8"));
                    StringBuilder sb = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        sb.append(line).append('\n');
                    }
                    reader.close();
                    result = sb.toString();
                } catch (Exception e) {
                    result = "ERROR:" + (e.getMessage() == null ? "network error" : e.getMessage());
                }
                final String b64 = Base64.encodeToString(
                        result.getBytes(java.nio.charset.StandardCharsets.UTF_8), Base64.NO_WRAP);
                web.post(new Runnable() {
                    @Override
                    public void run() {
                        web.evaluateJavascript("window.onFetch(atob('" + b64 + "'))", null);
                    }
                });
            }
        }).start();
    }
}
