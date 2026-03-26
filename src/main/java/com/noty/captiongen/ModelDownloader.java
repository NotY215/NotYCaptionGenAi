package com.noty.captiongen;

import java.io.*;
import java.net.*;
import java.util.concurrent.*;
import javax.net.ssl.HttpsURLConnection;

public class ModelDownloader {
    private volatile boolean cancelled = false;
    private Thread downloadThread;

    public void downloadModel(String urlString, String fileName, long expectedSize, DownloadCallback callback) {
        cancelled = false;

        downloadThread = new Thread(() -> {
            try {
                URL url = new URL(urlString);
                HttpsURLConnection connection = (HttpsURLConnection) url.openConnection();
                connection.setRequestMethod("GET");
                connection.setConnectTimeout(10000);
                connection.setReadTimeout(30000);
                connection.connect();

                int responseCode = connection.getResponseCode();
                if (responseCode != HttpsURLConnection.HTTP_OK) {
                    callback.onComplete(false);
                    return;
                }

                long fileSize = connection.getContentLength();
                if (fileSize <= 0) fileSize = expectedSize;

                File outputFile = new File(fileName);
                File tempFile = new File(fileName + ".tmp");

                try (InputStream in = connection.getInputStream();
                     FileOutputStream out = new FileOutputStream(tempFile)) {

                    byte[] buffer = new byte[8192];
                    int bytesRead;
                    long totalRead = 0;
                    long startTime = System.currentTimeMillis();

                    while ((bytesRead = in.read(buffer)) != -1 && !cancelled) {
                        out.write(buffer, 0, bytesRead);
                        totalRead += bytesRead;

                        if (fileSize > 0) {
                            int percent = (int) ((totalRead * 100) / fileSize);
                            long elapsedTime = System.currentTimeMillis() - startTime;
                            double speed = (totalRead / 1024.0) / (elapsedTime / 1000.0); // KB/s
                            callback.onProgress(percent, totalRead, fileSize, speed);
                        }
                    }

                    if (cancelled) {
                        tempFile.delete();
                        callback.onCancel();
                        return;
                    }

                    out.flush();
                }

                // Rename temp file to final file
                if (outputFile.exists()) {
                    outputFile.delete();
                }
                tempFile.renameTo(outputFile);

                callback.onComplete(true);

            } catch (Exception e) {
                e.printStackTrace();
                callback.onComplete(false);
            }
        });

        downloadThread.start();
    }

    public void cancelDownload() {
        cancelled = true;
        if (downloadThread != null) {
            downloadThread.interrupt();
        }
    }

    public interface DownloadCallback {
        void onProgress(int percent, long downloaded, long total, double speed);
        void onComplete(boolean success);
        void onCancel();
    }
}