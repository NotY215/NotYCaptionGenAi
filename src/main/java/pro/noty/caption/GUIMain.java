package pro.noty.caption;

import pro.noty.caption.model.CaptionConfig;
import pro.noty.caption.service.*;
import pro.noty.caption.ui.ConsoleGUI;
import pro.noty.caption.util.FileValidator;

import java.io.File;

public class GUIMain {
    private static final String[] ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mkv", ".mov", ".mp3", ".wav", ".m4a", ".flac", ".webm", ".m4v", ".mpg", ".mpeg"};

    public static void main(String[] args) {
        ConsoleGUI.clearScreen();
        ConsoleGUI.printHeader("NOTY CAPTION GENERATOR AI v1.0");
        ConsoleGUI.printInfo("Powered by Whisper.cpp");
        ConsoleGUI.printSeparator();

        // Check required files
        if (!checkRequiredFiles()) {
            ConsoleGUI.printError("Required files are missing!");
            ConsoleGUI.printBox(
                    "Expected file locations:",
                    Config.WHISPER_EXE_PATH,
                    Config.FFMPEG_PATH,
                    Config.FFPROBE_PATH
            );
            ConsoleGUI.pause();
            return;
        }

        ConsoleGUI.printSuccess("All required files found!");
        ConsoleGUI.pause();

        boolean continueApp = true;

        while (continueApp) {
            try {
                // Get media path
                ConsoleGUI.clearScreen();
                ConsoleGUI.printHeader("Select Media File");
                ConsoleGUI.printInfo("You can drag and drop a file here");
                ConsoleGUI.printInfo("Allowed extensions: " + String.join(", ", ALLOWED_EXTENSIONS));

                String mediaPath = ConsoleGUI.getInput("Enter video/audio path: ");
                while (!FileValidator.validateMediaFile(mediaPath, ALLOWED_EXTENSIONS)) {
                    ConsoleGUI.printError("Invalid file! File doesn't exist or has wrong extension.");
                    mediaPath = ConsoleGUI.getInput("Enter video/audio path: ");
                }

                ConsoleGUI.printSuccess("Selected: " + mediaPath);
                ConsoleGUI.pause();

                boolean continueToNext = true;

                while (continueToNext) {
                    // Model selection
                    ConsoleGUI.clearScreen();
                    ConsoleGUI.printHeader("Select Model");

                    String[] models = {
                            "Tiny (75 MB) - Fastest",
                            "Base (150 MB) - Balanced",
                            "Small (500 MB) - Good",
                            "Medium (1.5 GB) - Accurate",
                            "Large (2.9 GB) - Best"
                    };

                    int modelChoice = ConsoleGUI.showMenu("Choose Model", models);
                    if (modelChoice == -1) continueToNext = false;
                    if (!continueToNext) break;

                    modelChoice++; // Convert to 1-based
                    String modelName = getModelName(modelChoice);
                    String modelSize = getModelSize(modelChoice);
                    String modelPath = Config.MODELS_DIR + "ggml-" + modelName + ".bin";

                    // Check model
                    boolean modelExists = ModelManager.checkModelExists(modelPath);
                    if (!modelExists) {
                        ConsoleGUI.clearScreen();
                        ConsoleGUI.printHeader("Download Model");
                        ConsoleGUI.printWarning("Model not found: " + modelName);
                        ConsoleGUI.printInfo("Size: " + modelSize);

                        if (ConsoleGUI.confirm("Do you want to download this model?")) {
                            ConsoleGUI.showLoading("Downloading model");
                            boolean downloaded = ModelManager.downloadModel(modelName, modelPath);
                            if (!downloaded) {
                                ConsoleGUI.printError("Download failed!");
                                ConsoleGUI.pause();
                                continue;
                            }
                        } else {
                            continue;
                        }
                    }

                    // Line preference
                    ConsoleGUI.clearScreen();
                    ConsoleGUI.printHeader("Line Preference");
                    String[] preferences = {"Words", "Letters"};
                    int preferenceChoice = ConsoleGUI.showMenu("How to split lines?", preferences);
                    if (preferenceChoice == -1) continue;

                    // Subtitle mode
                    ConsoleGUI.clearScreen();
                    ConsoleGUI.printHeader("Subtitle Mode");
                    String[] modes = {
                            "Normal (Original language)",
                            "Translation (English)",
                            "Transliteration (Japanese/Hindi)"
                    };
                    int modeChoice = ConsoleGUI.showMenu("Select Mode", modes);
                    if (modeChoice == -1) continue;
                    modeChoice++; // Convert to 1-based

                    // Number per line
                    ConsoleGUI.clearScreen();
                    ConsoleGUI.printHeader("Line Settings");
                    String type = preferenceChoice == 0 ? "words" : "letters";
                    int numberPerLine = ConsoleGUI.getNumberInput(
                            "How many " + type + " per line?",
                            1, 30
                    );

                    // Confirm
                    CaptionConfig config = new CaptionConfig(
                            mediaPath, modelPath, modelName,
                            type, numberPerLine, modeChoice
                    );

                    ConsoleGUI.clearScreen();
                    ConsoleGUI.printHeader("Confirm Generation");
                    ConsoleGUI.printBox(config.toString().split("\n"));

                    if (!ConsoleGUI.confirm("Generate captions?")) {
                        continue;
                    }

                    // Generate
                    ConsoleGUI.clearScreen();
                    ConsoleGUI.printHeader("Generating Captions");
                    ConsoleGUI.printInfo("This may take several minutes...");

                    CaptionGenerator generator = new CaptionGenerator();
                    boolean success = generator.generateCaptions(config);

                    if (success) {
                        ConsoleGUI.printSuccess("Captions generated successfully!");
                        ConsoleGUI.printInfo("Output: " + config.getOutputPath());

                        // Open browser links
                        BrowserOpener.openLinks();

                        // Next video or quit
                        ConsoleGUI.clearScreen();
                        ConsoleGUI.printHeader("Complete!");
                        String[] nextOptions = {"Next Video", "Quit App"};
                        int nextChoice = ConsoleGUI.showMenu("What would you like to do?", nextOptions);

                        if (nextChoice == 1) {
                            continueApp = false;
                        } else {
                            continueToNext = false; // Go back to video selection
                        }
                    } else {
                        ConsoleGUI.printError("Failed to generate captions!");
                        ConsoleGUI.pause();
                        continueToNext = false;
                    }
                }
            } catch (Exception e) {
                ConsoleGUI.printError("Error: " + e.getMessage());
                e.printStackTrace();
                ConsoleGUI.pause();
            }
        }

        ConsoleGUI.clearScreen();
        ConsoleGUI.printHeader("Thank You!");
        ConsoleGUI.printSuccess("Thanks for using NotY Caption Generator AI!");
        ConsoleGUI.printInfo("Visit us at: " + Config.YOUTUBE_LINK);
        ConsoleGUI.pause();
    }

    private static boolean checkRequiredFiles() {
        boolean allGood = true;

        File whisper = new File(Config.WHISPER_EXE_PATH);
        File ffmpeg = new File(Config.FFMPEG_PATH);
        File ffprobe = new File(Config.FFPROBE_PATH);

        if (!whisper.exists()) {
            ConsoleGUI.printError("Missing: " + Config.WHISPER_EXE_PATH);
            allGood = false;
        }

        if (!ffmpeg.exists()) {
            ConsoleGUI.printError("Missing: " + Config.FFMPEG_PATH);
            allGood = false;
        }

        if (!ffprobe.exists()) {
            ConsoleGUI.printError("Missing: " + Config.FFPROBE_PATH);
            allGood = false;
        }

        // Create models directory
        File modelsDir = new File(Config.MODELS_DIR);
        if (!modelsDir.exists()) {
            modelsDir.mkdirs();
        }

        return allGood;
    }

    private static String getModelName(int choice) {
        switch (choice) {
            case 1: return "tiny";
            case 2: return "base";
            case 3: return "small";
            case 4: return "medium";
            case 5: return "large";
            default: return "base";
        }
    }

    private static String getModelSize(int choice) {
        switch (choice) {
            case 1: return "75 MB";
            case 2: return "150 MB";
            case 3: return "500 MB";
            case 4: return "1.5 GB";
            case 5: return "2.9 GB";
            default: return "150 MB";
        }
    }
}