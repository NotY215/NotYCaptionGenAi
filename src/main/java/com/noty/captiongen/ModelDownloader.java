package com.noty.captiongen;

import javax.swing.*;
import java.io.*;
import java.net.*;
import java.nio.file.*;

public class ModelDownloader {
    private static final String MODEL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin";
    private static final String MODEL_FILE = "ggml-base.bin";

    public void downloadModel(JFrame parent, DownloadCallback callback) {
        SwingWorker<Void, Integer> worker = new SwingWorker<Void, Integer>() {
            @Override
            protected Void doInBackground() throws Exception {
                try {
                    URL url = new URL(MODEL_URL);
                    HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                    connection.setRequestMethod("GET");
                    connection.connect();

                    int fileSize = connection.getContentLength();
                    File outputFile = new File(MODEL_FILE);

                    try (InputStream in = connection.getInputStream();
                         FileOutputStream out = new FileOutputStream(outputFile)) {

                        byte[] buffer = new byte[8192];
                        int bytesRead;
                        long totalRead = 0;

                        while ((bytesRead = in.read(buffer)) != -1) {
                            out.write(buffer, 0, bytesRead);
                            totalRead += bytesRead;

                            if (fileSize > 0) {
                                int percent = (int) ((totalRead * 100) / fileSize);
                                publish(percent);
                            }
                        }
                    }

                    callback.onComplete(true);
                } catch (Exception e) {
                    e.printStackTrace();
                    callback.onComplete(false);
                }
                return null;
            }

            @Override
            protected void process(java.util.List<Integer> chunks) {
                int latest = chunks.get(chunks.size() - 1);
                callback.onProgress(latest);
            }
        };

        worker.execute();
    }

    public interface DownloadCallback {
        void onProgress(int percent);
        void onComplete(boolean success);
    }
}