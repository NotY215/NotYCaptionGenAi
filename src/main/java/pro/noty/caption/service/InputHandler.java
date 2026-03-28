package pro.noty.caption.service;

import pro.noty.caption.model.CaptionConfig;
import pro.noty.caption.util.FileValidator;
import pro.noty.caption.Config;
import java.io.*;

public class InputHandler {
    private static final BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));

    private static final String[] LANGUAGES = {
            "English (en)",
            "Hindi (hi)",
            "Japanese (ja)",
            "Chinese (zh)",
            "Urdu (ur)"
    };

    private static final String[] LANGUAGE_CODES = {"en", "hi", "ja", "zh", "ur"};

    private static String readLine() {
        try {
            String line = reader.readLine();
            return line != null ? line : "";
        } catch (IOException e) {
            return "";
        }
    }

    public static String getMediaPath(String[] allowedExtensions) {
        while (true) {
            try {
                System.out.print("\n📂 Provide Video/Audio Path");
                System.out.print("\n   Allowed extensions: ");
                System.out.print(String.join(", ", allowedExtensions));
                System.out.print("\n➤ ");
                System.out.flush();

                String path = readLine();
                if (path == null || path.trim().isEmpty()) {
                    System.out.println("❌ Path cannot be empty! Please enter a valid path.");
                    continue;
                }

                path = path.trim().replace("\"", "");

                if (FileValidator.validateMediaFile(path, allowedExtensions)) {
                    return path;
                }

                System.out.println("❌ Invalid file! File doesn't exist or has wrong extension.");
                System.out.println("   Please try again.\n");
            } catch (Exception e) {
                System.err.println("Error: " + e.getMessage());
            }
        }
    }

    public static int showMainMenu(boolean modelSelected, boolean languageSelected) {
        while (true) {
            try {
                System.out.println("\n┌─────────────────────────────────┐");
                System.out.println("│         MAIN MENU               │");
                System.out.println("├─────────────────────────────────┤");

                if (!modelSelected) {
                    System.out.println("│  1) Choose Model               │");
                } else {
                    System.out.println("│  ✓ Model Selected               │");
                }

                if (!languageSelected) {
                    System.out.println("│  2) Choose Language            │");
                } else {
                    System.out.println("│  ✓ Language Selected            │");
                }

                System.out.println("│  0) Go Back (Resend video path)│");
                System.out.println("└─────────────────────────────────┘");
                System.out.print("➤ Choose option (0-2): ");
                System.out.flush();

                String input = readLine();
                if (input == null) continue;
                input = input.trim();

                if (input.matches("[0-2]")) {
                    int choice = Integer.parseInt(input);
                    // Don't allow selecting already selected options
                    if (choice == 1 && modelSelected) {
                        System.out.println("❌ Model already selected! Continue with next step.");
                        continue;
                    }
                    if (choice == 2 && languageSelected) {
                        System.out.println("❌ Language already selected! Continue with next step.");
                        continue;
                    }
                    return choice;
                }
                System.out.println("❌ Invalid input! Please enter 0, 1, or 2.");
            } catch (Exception e) {
                System.err.println("Error: " + e.getMessage());
            }
        }
    }

    public static int selectModel() {
        while (true) {
            try {
                System.out.println("\n┌─────────────────────────────────┐");
                System.out.println("│       SELECT MODEL             │");
                System.out.println("├─────────────────────────────────┤");
                System.out.println("│  1) Tiny (75 MB) - Fastest     │");
                System.out.println("│  2) Base (150 MB) - Balanced   │");
                System.out.println("│  3) Small (500 MB) - Good      │");
                System.out.println("│  4) Medium (1.5 GB) - Accurate │");
                System.out.println("│  5) Large (2.9 GB) - Best      │");
                System.out.println("│  0) Back                       │");
                System.out.println("└─────────────────────────────────┘");
                System.out.print("➤ Choose model (0-5): ");
                System.out.flush();

                String input = readLine();
                if (input == null) continue;
                input = input.trim();

                if (input.matches("[0-5]")) {
                    return Integer.parseInt(input);
                }
                System.out.println("❌ Invalid input! Please enter 0-5.");
            } catch (Exception e) {
                System.err.println("Error: " + e.getMessage());
            }
        }
    }

    public static int selectLanguage() {
        while (true) {
            try {
                System.out.println("\n┌─────────────────────────────────┐");
                System.out.println("│       SELECT LANGUAGE          │");
                System.out.println("├─────────────────────────────────┤");
                for (int i = 0; i < LANGUAGES.length; i++) {
                    System.out.printf("│  %d) %-30s │\n", i + 1, LANGUAGES[i]);
                }
                System.out.println("│  0) Back                       │");
                System.out.println("└─────────────────────────────────┘");
                System.out.print("➤ Choose language (0-" + LANGUAGES.length + "): ");
                System.out.flush();

                String input = readLine();
                if (input == null) continue;
                input = input.trim();

                int choice = Integer.parseInt(input);
                if (choice >= 0 && choice <= LANGUAGES.length) {
                    return choice;
                }
                System.out.println("❌ Invalid input! Please enter 0-" + LANGUAGES.length + ".");
            } catch (Exception e) {
                System.out.println("❌ Invalid input! Please enter a number.");
            }
        }
    }

    public static String getLanguageCode(int choice) {
        if (choice > 0 && choice <= LANGUAGE_CODES.length) {
            return LANGUAGE_CODES[choice - 1];
        }
        return "auto";
    }

    public static String getLanguageName(int choice) {
        if (choice > 0 && choice <= LANGUAGES.length) {
            return LANGUAGES[choice - 1];
        }
        return "Auto Detect";
    }

    public static int choosePreference() {
        while (true) {
            try {
                System.out.println("\n┌─────────────────────────────────┐");
                System.out.println("│       LINE PREFERENCE          │");
                System.out.println("├─────────────────────────────────┤");
                System.out.println("│  1) Words                      │");
                System.out.println("│  2) Letters                    │");
                System.out.println("│  0) Back                       │");
                System.out.println("└─────────────────────────────────┘");
                System.out.print("➤ Choose preference (0-2): ");
                System.out.flush();

                String input = readLine();
                if (input == null) continue;
                input = input.trim();

                if (input.matches("[0-2]")) {
                    return Integer.parseInt(input);
                }
                System.out.println("❌ Invalid input! Please enter 0, 1, or 2.");
            } catch (Exception e) {
                System.err.println("Error: " + e.getMessage());
            }
        }
    }

    public static int chooseSubtitleMode() {
        while (true) {
            try {
                System.out.println("\n┌─────────────────────────────────────────┐");
                System.out.println("│         SUBTITLE MODE                   │");
                System.out.println("├─────────────────────────────────────────┤");
                System.out.println("│  1) Normal                              │");
                System.out.println("│     (Generate in selected language)     │");
                System.out.println("│                                         │");
                System.out.println("│  2) Translation                         │");
                System.out.println("│     (Translate to English)              │");
                System.out.println("│                                         │");
                System.out.println("│  3) Transliteration                    │");
                System.out.println("│     (Convert Japanese/Hindi to English)│");
                System.out.println("│     ⚠️  Works only for Japanese/Hindi  │");
                System.out.println("│                                         │");
                System.out.println("│  0) Back                                │");
                System.out.println("└─────────────────────────────────────────┘");
                System.out.print("➤ Choose mode (0-3): ");
                System.out.flush();

                String input = readLine();
                if (input == null) continue;
                input = input.trim();

                if (input.matches("[0-3]")) {
                    int choice = Integer.parseInt(input);
                    if (choice == 3) {
                        System.out.println("\n⚠️  Note: Transliteration works best for:");
                        System.out.println("   • Japanese (Romaji conversion)");
                        System.out.println("   • Hindi (Romanized Hindi)");
                        System.out.print("   Press Enter to continue...");
                        System.out.flush();
                        readLine();
                    }
                    return choice;
                }
                System.out.println("❌ Invalid input! Please enter 0, 1, 2, or 3.");
            } catch (Exception e) {
                System.err.println("Error: " + e.getMessage());
            }
        }
    }

    public static int getNumberPerLine(int preferenceChoice) {
        String type = preferenceChoice == 1 ? "words" : "letters";

        while (true) {
            try {
                System.out.printf("\n┌─────────────────────────────────┐\n");
                System.out.printf("│  How many %s per line?     │\n", type);
                System.out.println("├─────────────────────────────────┤");
                System.out.println("│  Range: 1-30                   │");
                System.out.println("│  0) Back                       │");
                System.out.println("└─────────────────────────────────┘");
                System.out.printf("➤ Enter number (0-30): ");
                System.out.flush();

                String input = readLine();
                if (input == null) continue;
                input = input.trim();

                if (input.matches("0|([1-9]|[1-2][0-9]|30)")) {
                    return Integer.parseInt(input);
                }
                System.out.println("❌ Invalid input! Please enter 0-30.");
            } catch (Exception e) {
                System.err.println("Error: " + e.getMessage());
            }
        }
    }

    public static boolean confirmGeneration(CaptionConfig config) {
        while (true) {
            try {
                System.out.println("\n╔═══════════════════════════════════════════╗");
                System.out.println("║         CONFIRM GENERATION                ║");
                System.out.println("╠═══════════════════════════════════════════╣");

                String[] lines = config.toString().split("\n");
                for (String line : lines) {
                    if (line.length() > 45) {
                        while (line.length() > 45) {
                            String part = line.substring(0, 45);
                            System.out.printf("║ %-45s ║\n", part);
                            line = line.substring(45);
                        }
                        System.out.printf("║ %-45s ║\n", line);
                    } else {
                        System.out.printf("║ %-45s ║\n", line);
                    }
                }

                System.out.println("╠═══════════════════════════════════════════╣");
                System.out.println("║  1) Continue                             ║");
                System.out.println("║  0) Back                                 ║");
                System.out.println("╚═══════════════════════════════════════════╝");
                System.out.print("➤ Are you sure? (0-1): ");
                System.out.flush();

                String input = readLine();
                if (input == null) continue;
                input = input.trim();

                if (input.matches("[01]")) {
                    return input.equals("1");
                }
                System.out.println("❌ Invalid input! Please enter 0 or 1.");
            } catch (Exception e) {
                System.err.println("Error: " + e.getMessage());
            }
        }
    }

    public static int handleNextVideo() {
        while (true) {
            try {
                System.out.println("\n┌─────────────────────────────────┐");
                System.out.println("│         WHAT'S NEXT?           │");
                System.out.println("├─────────────────────────────────┤");
                System.out.println("│  1) Quit App                   │");
                System.out.println("│  0) Next Video                 │");
                System.out.println("└─────────────────────────────────┘");
                System.out.print("➤ Choose option (0-1): ");
                System.out.flush();

                String input = readLine();
                if (input == null) continue;
                input = input.trim();

                if (input.matches("[01]")) {
                    return Integer.parseInt(input);
                }
                System.out.println("❌ Invalid input! Please enter 0 or 1.");
            } catch (Exception e) {
                System.err.println("Error: " + e.getMessage());
            }
        }
    }
}