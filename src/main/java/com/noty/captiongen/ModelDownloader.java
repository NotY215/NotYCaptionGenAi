package com.noty.captiongen;

import java.io.*;
import java.net.*;
import java.nio.file.Files;

public class ModelDownloader {
    private volatile boolean cancelled = false;
    private Thread downloadThread;

    public void downloadModel(String urlString, String fileName, long expectedSize, DownloadCallback callback) {
        cancelled = false;

        downloadThread = new Thread(() -> {
            HttpURLConnection connection = null;
            InputStream in = null;
            FileOutputStream out = null;

            try {
                URL url = new URL(urlString);
                connection = (HttpURLConnection) url.openConnection();
                connection.setRequestMethod("GET");
                connection.setConnectTimeout(30000);
                connection.setReadTimeout(60000);
                connection.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
                connection.connect();

                int responseCode = connection.getResponseCode();
                if (responseCode != HttpURLConnection.HTTP_OK) {
                    callback.onComplete(false);
                    return;
                }

                long fileSize = connection.getContentLengthLong();
                if (fileSize <= 0) fileSize = expectedSize;

                File outputFile = new File(fileName);
                File tempFile = new File(fileName + ".tmp");

                in = connection.getInputStream();
                out = new FileOutputStream(tempFile);

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
                        double speed = (totalRead / 1024.0) / (elapsedTime / 1000.0);
                        callback.onProgress(percent, totalRead, fileSize, speed);
                    }
                }

                if (cancelled) {
                    tempFile.delete();
                    callback.onCancel();
                    return;
                }

                out.flush();
                out.close();
                in.close();

                if (outputFile.exists()) {
                    outputFile.delete();
                }
                boolean renamed = tempFile.renameTo(outputFile);
                if (!renamed) {
                    // Try alternative rename method
                    Files.move(tempFile.toPath(), outputFile.toPath(), java.nio.file.StandardCopyOption.REPLACE_EXISTING);
                }

                callback.onComplete(true);

            } catch (Exception e) {
                e.printStackTrace();
                callback.onComplete(false);
            } finally {
                try {
                    if (in != null) in.close();
                    if (out != null) out.close();
                    if (connection != null) connection.disconnect();
                } catch (IOException e) {
                    e.printStackTrace();
                }
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