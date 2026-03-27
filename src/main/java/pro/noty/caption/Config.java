package pro.noty.caption;

import java.io.File;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;

public class Config {
    // Base path for resources
    private static String basePath = null;

    public static String getBasePath() {
        if (basePath == null) {
            try {
                // Get the directory where the JAR is located
                String jarPath = Config.class.getProtectionDomain().getCodeSource().getLocation().getPath();
                File jarFile = new File(jarPath);

                if (jarFile.isFile()) {
                    // Running from JAR - use the directory containing the JAR
                    basePath = jarFile.getParentFile().getAbsolutePath();
                } else {
                    // Running from IDE - use the project root
                    basePath = new File("").getAbsolutePath();
                }
            } catch (Exception e) {
                basePath = new File("").getAbsolutePath();
            }
        }
        return basePath;
    }

    // Resources directory (where we extract files to)
    public static final String RESOURCES_DIR = getBasePath() + File.separator + "resources" + File.separator;

    // Application paths - these will be in the resources folder
    public static String WHISPER_EXE_PATH;
    public static String FFMPEG_PATH;
    public static String FFPROBE_PATH;
    public static String MODELS_DIR;

    static {
        // Initialize paths
        WHISPER_EXE_PATH = RESOURCES_DIR + "whisper" + File.separator + "whisper-cli.exe";
        FFMPEG_PATH = RESOURCES_DIR + "files" + File.separator + "ffmpeg.exe";
        FFPROBE_PATH = RESOURCES_DIR + "files" + File.separator + "ffprobe.exe";
        MODELS_DIR = RESOURCES_DIR + "models" + File.separator;

        // Extract resources from JAR if running from JAR
        extractResourceIfNeeded("/whisper/whisper-cli.exe", WHISPER_EXE_PATH);
        extractResourceIfNeeded("/files/ffmpeg.exe", FFMPEG_PATH);
        extractResourceIfNeeded("/files/ffprobe.exe", FFPROBE_PATH);

        // Create models directory if it doesn't exist
        File modelsDir = new File(MODELS_DIR);
        if (!modelsDir.exists()) {
            modelsDir.mkdirs();
        }
    }

    private static void extractResourceIfNeeded(String resourcePath, String destinationPath) {
        File destFile = new File(destinationPath);
        if (destFile.exists()) {
            return;
        }

        // Create parent directories
        destFile.getParentFile().mkdirs();

        // Extract from JAR
        try (InputStream is = Config.class.getResourceAsStream(resourcePath)) {
            if (is != null) {
                Files.copy(is, destFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
                destFile.setExecutable(true);
                System.out.println("✓ Extracted: " + resourcePath + " to " + destinationPath);
            } else {
                System.err.println("⚠️ Resource not found in JAR: " + resourcePath);
            }
        } catch (Exception e) {
            System.err.println("⚠️ Failed to extract " + resourcePath + ": " + e.getMessage());
        }
    }

    // Download URLs for Whisper models
    public static final String MODEL_BASE_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-";

    // Browser links
    public static final String TELEGRAM_LINK = "https://t.me/NotY215";
    public static final String YOUTUBE_LINK = "https://www.youtube.com/@NotY215";

    // Subtitle modes
    public static final int MODE_NORMAL = 1;
    public static final int MODE_TRANSLATION = 2;
    public static final int MODE_TRANSLITERATION = 3;

    // Languages for transliteration
    public static final String[] TRANSLITERATION_LANGUAGES = {"ja", "hi"};
}