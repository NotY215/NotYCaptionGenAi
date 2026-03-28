package pro.noty.caption;

import pro.noty.caption.model.CaptionConfig;
import pro.noty.caption.service.*;
import pro.noty.caption.util.ConsoleUtils;
import java.io.File;
import java.util.Scanner;

public class Main {
    private static final String[] ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mkv", ".mov", ".mp3", ".wav", ".m4a", ".flac", ".webm", ".m4v", ".mpg", ".mpeg"};
    private static Scanner scanner = null;
    private static int selectedLanguage = 0;
    private static String languageCode = "auto";
    private static String languageName = "Auto Detect";
    private static int selectedModel = 0;
    private static String selectedModelName = "";
    private static String selectedModelPath = "";

    private static Scanner getScanner() {
        if (scanner == null) {
            scanner = new Scanner(System.in);
        }
        return scanner;
    }

    public static void main(String[] args) {
        ConsoleUtils.clearScreen();
        System.out.println("╔═══════════════════════════════════════════╗");
        System.out.println("║     NOTY CAPTION GENERATOR AI v1.0       ║");
        System.out.println("║     Powered by Whisper.cpp               ║");
        System.out.println("╚═══════════════════════════════════════════╝");
        System.out.println();

        // Show current paths
        System.out.println("📁 Resource Directory: " + Config.RESOURCES_DIR);
        System.out.println("📁 Models Directory: " + Config.MODELS_DIR);
        System.out.println("🔧 Checking required files...\n");

        // Check if required executables exist
        if (!checkRequiredFiles()) {
            System.out.println("\n❌ Required files are missing! Please check the installation.");
            System.out.println("\nPress Enter to exit...");
            getScanner().nextLine();
            return;
        }

        System.out.println("✅ All required files found!\n");

        boolean continueApp = true;

        while (continueApp) {
            try {
                // Step a: Get video/audio path
                System.out.println("\n💡 Tip: You can drag and drop a file here, then press Enter");
                System.out.println("   Or type the full path (e.g., C:\\Videos\\test.mp4)");
                String mediaPath = InputHandler.getMediaPath(ALLOWED_EXTENSIONS);

                System.out.println("\n✅ Selected file: " + mediaPath);

                // Reset selections for new video
                selectedModel = 0;
                selectedLanguage = 0;
                languageCode = "auto";
                languageName = "Auto Detect";

                while (true) {
                    // Step b: Main menu - only show options that haven't been selected
                    int choice = InputHandler.showMainMenu(selectedModel > 0, selectedLanguage > 0);

                    if (choice == 0) {
                        // Go back to path selection
                        break;
                    } else if (choice == 1 && selectedModel == 0) {
                        // Select model
                        selectedModel = InputHandler.selectModel();
                        if (selectedModel > 0) {
                            selectedModelName = getModelName(selectedModel);
                            String modelSize = getModelSize(selectedModel);
                            selectedModelPath = Config.MODELS_DIR + "ggml-" + selectedModelName + ".bin";

                            if (selectedModelName.equals("large")) {
                                selectedModelPath = Config.MODELS_DIR + "ggml-large-v1.bin";
                            }

                            // Check if model exists
                            boolean modelExists = ModelManager.checkModelExists(selectedModelPath);
                            if (!modelExists) {
                                System.out.println("\n📥 Model not found. Downloading...");
                                boolean downloaded = ModelManager.downloadModel(selectedModelName, selectedModelPath);
                                if (!downloaded) {
                                    System.out.println("\n❌ Failed to download model. Please check your internet connection.");
                                    selectedModel = 0;
                                    continue;
                                }
                            }
                            System.out.println("\n✅ Model selected: " + selectedModelName.toUpperCase());
                        }
                        continue;
                    } else if (choice == 2 && selectedLanguage == 0) {
                        // Select language
                        selectedLanguage = InputHandler.selectLanguage();
                        if (selectedLanguage > 0) {
                            languageCode = InputHandler.getLanguageCode(selectedLanguage);
                            languageName = InputHandler.getLanguageName(selectedLanguage);
                            System.out.println("\n✅ Language selected: " + languageName);
                        }
                        continue;
                    }

                    // If we get here, both model and language are selected
                    if (selectedModel == 0) {
                        System.out.println("\n⚠️ Please select a model first!");
                        continue;
                    }
                    if (selectedLanguage == 0) {
                        System.out.println("\n⚠️ Please select a language first!");
                        continue;
                    }

                    // Step c: Choose word or letter preference
                    int preferenceChoice = InputHandler.choosePreference();
                    if (preferenceChoice == 0) {
                        continue;
                    }

                    // Step d: Choose subtitle mode
                    int modeChoice = InputHandler.chooseSubtitleMode();
                    if (modeChoice == 0) {
                        continue;
                    }

                    // Step e: Number per line
                    int numberPerLine = InputHandler.getNumberPerLine(preferenceChoice);
                    if (numberPerLine == 0) {
                        continue;
                    }

                    // Step f: Confirm and generate
                    CaptionConfig config = new CaptionConfig(
                            mediaPath, selectedModelPath, selectedModelName,
                            preferenceChoice == 1 ? "words" : "letters",
                            numberPerLine,
                            modeChoice,
                            languageCode,
                            languageName
                    );

                    boolean confirmed = InputHandler.confirmGeneration(config);
                    if (!confirmed) {
                        continue;
                    }

                    // Generate captions
                    System.out.println("\n🎬 Generating captions... This may take several minutes.");
                    CaptionGenerator generator = new CaptionGenerator();
                    boolean success = generator.generateCaptions(config);

                    if (success) {
                        System.out.println("\n✅ Thanks For using NotY Caption Generator AI!");
                        System.out.println("Your caption has been generated successfully!");
                        System.out.println("📄 Output file: " + config.getOutputPath());

                        // Open browser links
                        BrowserOpener.openLinks();

                        // Step g: Next video or quit
                        int nextChoice = InputHandler.handleNextVideo();
                        if (nextChoice == 1) {
                            continueApp = false;
                            System.out.println("\n╔═══════════════════════════════════════════╗");
                            System.out.println("║     Thank you for using our app!         ║");
                            System.out.println("║     Visit us again!                      ║");
                            System.out.println("╚═══════════════════════════════════════════╝");
                            break;
                        } else {
                            break; // Go back to start for next video
                        }
                    } else {
                        System.out.println("\n❌ Failed to generate captions. Please try again.");
                        Thread.sleep(2000);
                        break;
                    }
                }
            } catch (Exception e) {
                System.err.println("Error: " + e.getMessage());
                e.printStackTrace();
                System.out.println("\nPress Enter to continue...");
                getScanner().nextLine();
            }
        }

        if (scanner != null) {
            scanner.close();
        }
    }

    private static boolean checkRequiredFiles() {
        boolean allGood = true;

        File resourcesDir = new File(Config.RESOURCES_DIR);
        if (!resourcesDir.exists()) {
            System.err.println("❌ Resources directory not found: " + Config.RESOURCES_DIR);
            allGood = false;
        } else {
            System.out.println("✓ Resources directory found");
        }

        File whisper = new File(Config.WHISPER_EXE_PATH);
        if (!whisper.exists()) {
            System.err.println("❌ Missing: " + Config.WHISPER_EXE_PATH);
            allGood = false;
        } else {
            System.out.println("✓ Found: " + whisper.getName());
        }

        File whisperDll = new File(Config.WHISPER_DLL_PATH);
        if (!whisperDll.exists()) {
            System.err.println("⚠️ Missing: " + Config.WHISPER_DLL_PATH + " (required for whisper-cli.exe)");
            allGood = false;
        } else {
            System.out.println("✓ Found: " + whisperDll.getName());
        }

        File ffmpeg = new File(Config.FFMPEG_PATH);
        if (!ffmpeg.exists()) {
            System.err.println("❌ Missing: " + Config.FFMPEG_PATH);
            allGood = false;
        } else {
            System.out.println("✓ Found: " + ffmpeg.getName());
        }

        File ffprobe = new File(Config.FFPROBE_PATH);
        if (!ffprobe.exists()) {
            System.err.println("❌ Missing: " + Config.FFPROBE_PATH);
            allGood = false;
        } else {
            System.out.println("✓ Found: " + ffprobe.getName());
        }

        File modelsDir = new File(Config.MODELS_DIR);
        if (!modelsDir.exists()) {
            modelsDir.mkdirs();
            System.out.println("✓ Created models directory: " + Config.MODELS_DIR);
        } else {
            System.out.println("✓ Models directory found");
            File[] models = modelsDir.listFiles((dir, name) -> name.endsWith(".bin"));
            if (models != null && models.length > 0) {
                System.out.println("   Existing models:");
                for (File model : models) {
                    System.out.println("   - " + model.getName());
                }
            }
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