package pro.noty.caption.service;

import pro.noty.caption.util.ProgressBar;
import pro.noty.caption.Config;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URL;

public class ModelManager {

    public static boolean checkModelExists(String modelPath) {
        File modelFile = new File(modelPath);
        return modelFile.exists() && modelFile.length() > 0;
    }

    public static boolean downloadModel(String modelName, String modelPath) {
        String downloadUrl;

        // Use the correct URL based on model name
        switch (modelName) {
            case "tiny":
                downloadUrl = Config.MODEL_TINY_URL;
                break;
            case "base":
                downloadUrl = Config.MODEL_BASE_URL_ACTUAL;
                break;
            case "small":
                downloadUrl = Config.MODEL_SMALL_URL;
                break;
            case "medium":
                downloadUrl = Config.MODEL_MEDIUM_URL;
                break;
            case "large":
                downloadUrl = Config.MODEL_LARGE_URL;
                break;
            default:
                downloadUrl = Config.MODEL_BASE_URL + modelName + ".bin";
        }

        System.out.println("\n📥 Downloading " + modelName.toUpperCase() + " model...");
        System.out.println("🔗 URL: " + downloadUrl);

        HttpURLConnection connection = null;
        try {
            URL url = URI.create(downloadUrl).toURL();
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36");
            connection.setConnectTimeout(30000);
            connection.setReadTimeout(60000);
            connection.setRequestMethod("GET");
            connection.connect();

            int responseCode = connection.getResponseCode();
            if (responseCode != HttpURLConnection.HTTP_OK) {
                System.err.println("❌ Failed to connect. HTTP response code: " + responseCode);
                return false;
            }

            int fileSize = connection.getContentLength();
            if (fileSize <= 0) {
                System.err.println("❌ Invalid file size received.");
                return false;
            }

            System.out.println("📦 Total size: " + formatSize(fileSize));

            // Create directories if they don't exist
            File modelFile = new File(modelPath);
            File parentDir = modelFile.getParentFile();
            if (parentDir != null && !parentDir.exists()) {
                if (!parentDir.mkdirs()) {
                    System.err.println("❌ Failed to create directory: " + parentDir);
                    return false;
                }
            }

            try (InputStream inputStream = connection.getInputStream();
                 FileOutputStream outputStream = new FileOutputStream(modelFile);
                 BufferedInputStream bufferedInputStream = new BufferedInputStream(inputStream)) {

                byte[] buffer = new byte[8192];
                int bytesRead;
                long totalBytesRead = 0;
                int lastProgress = -1;

                while ((bytesRead = bufferedInputStream.read(buffer)) != -1) {
                    outputStream.write(buffer, 0, bytesRead);
                    totalBytesRead += bytesRead;

                    int progress = (int) ((totalBytesRead * 100) / fileSize);
                    if (progress != lastProgress && progress % 5 == 0) {
                        ProgressBar.showProgress(progress, 100);
                        lastProgress = progress;
                    }
                }
            }

            // Verify file was downloaded successfully
            if (modelFile.exists() && modelFile.length() == fileSize) {
                System.out.println("\n✅ Model downloaded successfully!");
                return true;
            } else {
                System.err.println("\n❌ Downloaded file size mismatch. Download may be corrupted.");
                if (modelFile.exists()) {
                    modelFile.delete();
                }
                return false;
            }

        } catch (Exception e) {
            System.err.println("\n❌ Download failed: " + e.getMessage());
            return false;
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }

    private static String formatSize(long bytes) {
        if (bytes < 1024) return bytes + " B";
        int exp = (int) (Math.log(bytes) / Math.log(1024));
        String pre = "KMGTPE".charAt(exp - 1) + "";
        return String.format("%.1f %sB", bytes / Math.pow(1024, exp), pre);
    }
}